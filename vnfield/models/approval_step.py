# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════
# ═               📋 VNFIELD APPROVAL STEP MODEL             ═
# ═           Sequential Approval Step Processing            ═
# ═══════════════════════════════════════════════════════════

"""
=================================================================
🎯 CHỨC NĂNG: APPROVAL STEP WORKFLOW MANAGEMENT
=================================================================
- Quản lý từng bước trong quy trình phê duyệt
- Sequential processing với next/prev step relationships
- Approval/Rejection logic với proper notifications
- Permission control dựa trên approver assignment
=================================================================
"""

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


# ┌─────────────────────────────────────────────────────────┐
# │              📋 APPROVAL STEP MODEL CLASS              │
# └─────────────────────────────────────────────────────────┘

class ApprovalStep(models.Model):
    """
    ==========================================================
    📋 VNFIELD APPROVAL STEP MODEL
    ==========================================================
    
    🎯 **Mục đích**: 
    - Quản lý từng bước trong approval workflow
    - Sequential processing với strict ordering
    - Approval/Rejection với proper state management
    
    📋 **Step States**:
    - waiting: Chờ đến lượt xử lý
    - in-progress: Đang chờ approver xử lý
    - approved: Đã được phê duyệt
    - rejected: Bị từ chối
    
    🔐 **Permission Logic**:
    - Chỉ approver được assign mới có quyền approve/reject
    - Admin có thể override approval decisions
    - Requester không thể modify steps sau khi submit
    ==========================================================
    """
    _name = "vnfield.approval.step"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "VN Field Approval Step"
    _order = "approval_id, id"

    # ┌───────────────────────────────────────────────────────┐
    # │                🗂️ BASIC FIELDS                       │
    # └───────────────────────────────────────────────────────┘

    name = fields.Char(
        required=True,
        string="Step Name",
        tracking=True,
        help="Name/title of this approval step"
    )
    
    description = fields.Text(
        string="Description",
        help="Detailed description of what needs to be approved in this step"
    )
    
    comment = fields.Text(
        string="Approval Comment",
        help="Comment from approver when approving/rejecting"
    )
    
    # ┌───────────────────────────────────────────────────────┐
    # │              📊 STATUS & WORKFLOW FIELDS             │
    # └───────────────────────────────────────────────────────┘
    
    status = fields.Selection(
        selection=[
            ("waiting", "⏳ Waiting"),
            ("in-progress", "🔄 In Progress"),
            ("approved", "✅ Approved"),
            ("rejected", "❌ Rejected"),
        ],
        default="waiting",
        readonly=True,
        tracking=True,
        string="Status",
        help="Current status of this approval step"
    )
    
    # ┌───────────────────────────────────────────────────────┐
    # │               👥 USER RELATIONSHIP FIELDS            │
    # └───────────────────────────────────────────────────────┘
    
    approver_id = fields.Many2one(
        comodel_name="res.users",
        string="👤 Approver",
        required=True,
        tracking=True,
        help="User responsible for approving this step"
    )
    
    # ┌───────────────────────────────────────────────────────┐
    # │               📅 DATETIME FIELDS                     │
    # └───────────────────────────────────────────────────────┘
    
    come_at = fields.Datetime(
        string="📅 Started At",
        readonly=True,
        tracking=True,
        help="When this step became active for approval"
    )
    
    approval_at = fields.Datetime(
        string="✅ Approved/Rejected At",
        readonly=True,
        tracking=True,
        help="When this step was approved or rejected"
    )
    
    approval_step_period = fields.Float(
        string="⏱️ Expected Duration (Hours)",
        required=True, 
        default=24.0,
        help="Expected time for this step completion"
    )
    
    # ┌───────────────────────────────────────────────────────┐
    # │              🔗 RELATIONSHIP FIELDS                  │
    # └───────────────────────────────────────────────────────┘
    
    approval_id = fields.Many2one(
        comodel_name="vnfield.approval", 
        string="📋 Approval",
        readonly=True,
        required=True,
        ondelete="cascade",
        help="Parent approval this step belongs to"
    )
    
    root_of_approval_id = fields.Many2one(
        comodel_name="vnfield.approval", 
        string="🌱 Root Approval",
        readonly=True,
        help="Root approval for workflow consistency"
    )
    
    next_step_ids = fields.Many2many(
        comodel_name="vnfield.approval.step",
        relation="step_nextstep_rel",
        column1="step_id",
        column2="next_step_id",
        string="➡️ Next Steps",
        help="Steps that will be activated after this step is approved"
    )
    
    prev_step_ids = fields.Many2many(
        comodel_name="vnfield.approval.step",
        relation="step_nextstep_rel",
        column1="next_step_id",
        column2="step_id",
        readonly=True,
        string="⬅️ Previous Steps",
        help="Steps that must be completed before this step can start"
    )
    
    step_type_id = fields.Many2one(
        comodel_name="vnfield.approval.step.type",
        string="📂 Step Type",
        help="Type/category of this approval step"
    )
    
    attachment_ids = fields.Many2many(
        comodel_name="ir.attachment",
        relation="step_attachment_rel",
        column1="approval_step_id",
        column2="attachment_id",
        string="📎 Attachments",
        help="Files attached to this approval step"
    )
    
    # ┌───────────────────────────────────────────────────────┐
    # │               📊 COMPUTED FIELDS                     │
    # └───────────────────────────────────────────────────────┘
    
    can_user_approve = fields.Boolean(
        compute="_compute_can_user_approve",
        string="🎯 Can Approve",
        help="Whether current user can approve/reject this step"
    )
    
    is_overdue = fields.Boolean(
        compute="_compute_is_overdue",
        string="⚠️ Overdue",
        help="Whether this step is overdue"
    )
    
    duration_hours = fields.Float(
        compute="_compute_duration",
        string="⏱️ Actual Duration (Hours)",
        help="Actual time spent on this step"
    )
    
    requester_id = fields.Many2one(
        related="approval_id.requester_id",
        string="👤 Requester",
        readonly=True,
        help="Original requester of the approval"
    )

    # ┌───────────────────────────────────────────────────────┐
    # │               📊 COMPUTED METHODS                    │
    # └───────────────────────────────────────────────────────┘

    @api.depends('approver_id', 'status')
    def _compute_can_user_approve(self):
        """🎯 Kiểm tra quyền approve của user hiện tại"""
        for record in self:
            current_user = self.env.user
            
            # Admin luôn có quyền
            if current_user.has_group('vnfield.group_contractor_admin'):
                record.can_user_approve = True
            # Approver được assign và step đang in-progress
            elif (current_user == record.approver_id and 
                  record.status == 'in-progress'):
                record.can_user_approve = True
            else:
                record.can_user_approve = False

    @api.depends('come_at', 'approval_step_period', 'status')
    def _compute_is_overdue(self):
        """⚠️ Kiểm tra step có overdue không"""
        for record in self:
            if (record.come_at and 
                record.approval_step_period > 0 and 
                record.status == 'in-progress'):
                
                from datetime import timedelta
                deadline = record.come_at + timedelta(hours=record.approval_step_period)
                record.is_overdue = fields.Datetime.now() > deadline
            else:
                record.is_overdue = False

    @api.depends('come_at', 'approval_at')
    def _compute_duration(self):
        """⏱️ Tính thời gian thực tế xử lý step"""
        for record in self:
            if record.come_at and record.approval_at:
                delta = record.approval_at - record.come_at
                record.duration_hours = delta.total_seconds() / 3600
            elif record.come_at and record.status == 'in-progress':
                delta = fields.Datetime.now() - record.come_at
                record.duration_hours = delta.total_seconds() / 3600
            else:
                record.duration_hours = 0

    # ┌───────────────────────────────────────────────────────┐
    # │              🔄 RECORD LIFECYCLE METHODS             │
    # └───────────────────────────────────────────────────────┘

    @api.model
    def create(self, vals):
        """🆕 Create step with default status"""
        if 'status' not in vals:
            vals['status'] = 'waiting'
            
        step = super().create(vals)
        
        # Auto-set root_of_approval_id if not provided
        if 'root_of_approval_id' not in vals and step.approval_id:
            step.root_of_approval_id = step.approval_id
            
        return step

    def write(self, vals):
        """✏️ Enhanced write with status change notifications"""
        # Track status changes for notifications
        status_changes = {}
        for record in self:
            old_status = record.status
            if 'status' in vals and vals['status'] != old_status:
                status_changes[record.id] = (old_status, vals['status'])
        
        result = super().write(vals)
        
        # Handle status change notifications and workflow
        for record in self:
            if record.id in status_changes:
                old_status, new_status = status_changes[record.id]
                record._handle_status_change(old_status, new_status)
        
        return result

    def unlink(self):
        """🗑️ Delete validation"""
        for record in self:
            if record.status not in ('waiting', 'draft'):
                raise UserError(
                    f'Cannot delete step "{record.name}" because it is not in waiting status.'
                )
        return super().unlink()

    # ┌───────────────────────────────────────────────────────┐
    # │               🔧 VALIDATION METHODS                  │
    # └───────────────────────────────────────────────────────┘

    @api.constrains('next_step_ids')
    def _check_next_step(self):
        """🔗 Kiểm tra tính hợp lệ của next steps"""
        for record in self:
            for next_step in record.next_step_ids:
                # Same approval check
                if next_step.approval_id != record.approval_id:
                    raise ValidationError(
                        f"Next step '{next_step.name}' must belong to the same approval!"
                    )
                
                # Circular dependency check
                if record._check_circular_dependency_with_step(next_step):
                    raise ValidationError(
                        f"Circular dependency detected between '{record.name}' and '{next_step.name}'"
                    )

    @api.constrains('approval_id', 'root_of_approval_id')
    def _check_approval_consistency(self):
        """🔗 Kiểm tra tính nhất quán của approval references"""
        for record in self:
            if record.root_of_approval_id and record.approval_id:
                if record.root_of_approval_id != record.approval_id:
                    raise ValidationError(
                        "'Approval' must be the same as 'Root of approval'!"
                    )

    def _check_circular_dependency(self):
        """🔄 Kiểm tra circular dependency trong workflow"""
        self.ensure_one()
        return self._check_circular_dependency_with_step(self)

    def _check_circular_dependency_with_step(self, target_step):
        """🔄 Kiểm tra circular dependency với step cụ thể"""
        visited = set()
        
        def traverse(step):
            if step.id in visited:
                return step.id == target_step.id
            visited.add(step.id)
            
            for next_step in step.next_step_ids:
                if traverse(next_step):
                    return True
            return False
        
        return traverse(self)

    # ┌───────────────────────────────────────────────────────┐
    # │               🎯 WORKFLOW ACTION METHODS              │
    # └───────────────────────────────────────────────────────┘

    def action_approve(self):
        """✅ Approve this step"""
        self.ensure_one()
        
        if not self.can_user_approve:
            raise UserError("You don't have permission to approve this step!")
        
        if self.status != 'in-progress':
            raise UserError("Only in-progress steps can be approved!")
        
        # Update step status
        self.write({
            'status': 'approved',
            'approval_at': fields.Datetime.now(),
        })
        
        # 📧 Notify approval
        self.message_post(
            body=f"✅ Step approved by {self.env.user.name}",
            partner_ids=[self.requester_id.partner_id.id]
        )
        
        # Handle approval workflow in parent approval
        self.approval_id._handle_step_approved(self)
        
        return True

    def action_reject(self):
        """❌ Reject this step"""
        self.ensure_one()
        
        if not self.can_user_approve:
            raise UserError("You don't have permission to reject this step!")
        
        if self.status != 'in-progress':
            raise UserError("Only in-progress steps can be rejected!")
        
        # Update step status
        self.write({
            'status': 'rejected',
            'approval_at': fields.Datetime.now(),
        })
        
        # 📧 Notify rejection
        self.message_post(
            body=f"❌ Step rejected by {self.env.user.name}. Reason: {self.comment or 'No reason provided'}",
            partner_ids=[self.requester_id.partner_id.id]
        )
        
        # Handle rejection workflow in parent approval
        self.approval_id._handle_step_rejected(self)
        
        return True

    def action_reset_to_waiting(self):
        """🔄 Reset step to waiting status"""
        self.ensure_one()
        
        if not self.env.user.has_group('vnfield.group_contractor_admin'):
            raise UserError("Only administrators can reset steps!")
        
        self.write({
            'status': 'waiting',
            'come_at': False,
            'approval_at': False,
            'comment': '',
        })
        
        return True

    # ┌───────────────────────────────────────────────────────┐
    # │               🔔 NOTIFICATION METHODS                │
    # └───────────────────────────────────────────────────────┘

    def _handle_status_change(self, old_status, new_status):
        """🔔 Xử lý thông báo khi status thay đổi"""
        self.ensure_one()
        
        status_messages = {
            'in-progress': f"🔄 Step '{self.name}' is now ready for your approval",
            'approved': f"✅ Step '{self.name}' has been approved",
            'rejected': f"❌ Step '{self.name}' has been rejected",
            'waiting': f"⏳ Step '{self.name}' is now waiting",
        }
        
        message = status_messages.get(new_status)
        if message:
            # Notify approver for in-progress
            if new_status == 'in-progress' and self.approver_id:
                self.message_post(
                    body=message,
                    partner_ids=[self.approver_id.partner_id.id]
                )
            # Notify requester for approved/rejected
            elif new_status in ('approved', 'rejected') and self.requester_id:
                self.message_post(
                    body=message,
                    partner_ids=[self.requester_id.partner_id.id]
                )

    # ┌───────────────────────────────────────────────────────┐
    # │               🎯 ACTION METHODS                       │
    # └───────────────────────────────────────────────────────┘

    def open_form_view(self):
        """📝 Open step form view"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "vnfield.approval.step",
            "views": [[False, "form"]],
            "name": f"Approval Step: {self.name}",
            "res_id": self.id,
            "target": "current",
        }

    def handle_click_review(self):
        """📋 Open review wizard"""
        self.ensure_one()
        
        if not self.can_user_approve:
            raise UserError("You are not authorized to review this step!")
        
        return {
            "type": "ir.actions.act_window",
            "name": "Review Approval Step",
            "res_model": "vnfield.approval.review",
            "target": "new",
            "view_mode": "form",
            "view_type": "form",
            "context": {"default_approval_step_id": self.id},
        }


# ┌─────────────────────────────────────────────────────────┐
# │               🔗 SYMBOL DEPENDENCIES                   │
# └─────────────────────────────────────────────────────────┘

"""
=================================================================
📋 PHÂN TÍCH PHỤ THUỘC CÁC SYMBOL TRONG APPROVAL STEP MODEL
=================================================================

🎯 **Core Model Symbols**:
- ApprovalStep: Main model class kế thừa từ mail.thread và mail.activity.mixin
- _name: Định danh model trong Odoo registry
- _description: Mô tả model cho UI và documentation

📋 **Field Dependencies**:
- approval_id: Many2one link đến vnfield.approval (parent approval)
- root_of_approval_id: Computed field reference đến approval root
- requester_id: Many2one đến res.users (người yêu cầu approval)
- approver_id: Many2one đến res.users (người có quyền approve step)
- next_step_ids: Many2many relationship tạo workflow graph
- prev_step_ids: Inverse của next_step_ids cho navigation

🔄 **Status Workflow Dependencies**:
- status: Selection field với states (waiting → in-progress → approved/rejected)
- come_at: Datetime mark khi step become active
- approval_at: Datetime mark khi step được approve/reject
- can_user_approve: Computed field dựa trên current user và approver_id

⏱️ **Time Tracking Dependencies**:
- approval_step_period: Float hours cho deadline calculation
- duration_hours: Computed duration từ come_at đến approval_at
- is_overdue: Computed field check deadline với current time

🔐 **Permission System Dependencies**:
- vnfield.group_contractor_admin: Security group cho admin permissions
- res.users model: User management và partner relationships
- partner_id field: Mail notifications through partner system

🔔 **Notification Dependencies**:
- mail.thread: Message posting và tracking capabilities
- mail.activity.mixin: Activity management cho reminders
- message_post(): Method gửi notifications đến users

🔄 **Workflow Action Dependencies**:
- action_approve(): Status transition và parent approval notification
- action_reject(): Rejection handling và workflow termination
- _handle_step_approved(): Callback từ approval model
- _handle_step_rejected(): Rejection cascade trong parent approval

🔗 **Validation Dependencies**:
- _check_next_step(): Circular dependency detection trong workflow graph
- _check_approval_consistency(): Consistency check giữa approval references
- _check_circular_dependency_with_step(): Recursive traversal algorithm

📊 **UI Dependencies**:
- vnfield.approval.review: Wizard model cho approval actions
- approval_step_form_view: XML view reference cho form display
- JavaScript AJAX: Client-side workflow interactions

=================================================================
"""
