# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════
# ═                 📋 VNFIELD APPROVAL MODEL                ═
# ═           Enhanced Approval Workflow System              ═
# ═══════════════════════════════════════════════════════════

"""
=================================================================
🎯 CHỨC NĂNG: APPROVAL WORKFLOW MANAGEMENT
=================================================================
- Quản lý quy trình phê duyệt với sequential step processing
- Hỗ trợ requester và approver role-based permissions
- Sequential workflow với strict ordering và rejection logic
- Permission system dựa trên status và user roles
=================================================================
"""

from odoo import api, fields, models, http
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


# ┌─────────────────────────────────────────────────────────┐
# │                📋 APPROVAL MODEL CLASS                 │
# └─────────────────────────────────────────────────────────┘

class Approval(models.Model):
    """
    ==========================================================
    📋 VNFIELD APPROVAL MODEL
    ==========================================================
    
    🎯 **Mục đích**: 
    - Quản lý yêu cầu phê duyệt với workflow tuần tự
    - Hỗ trợ requester và multi-step approval process
    - Permission control dựa trên status và user roles
    
    📋 **Workflow States**:
    - draft: Bản nháp, chưa gửi yêu cầu
    - in-progress: Đang trong quá trình phê duyệt
    - approved: Đã được phê duyệt hoàn toàn
    - rejected: Bị từ chối (bất kỳ step nào reject)
    
    🔐 **Permission Logic**:
    - Requester: Chỉ edit khi status = draft
    - Approvers: Chỉ approve/reject step được assign
    - Admin: Full access mọi lúc
    ==========================================================
    """
    _name = "vnfield.approval"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "VN Field Approval"
    _order = "request_at desc, id desc"

    # ┌───────────────────────────────────────────────────────┐
    # │                🗂️ BASIC FIELDS                       │
    # └───────────────────────────────────────────────────────┘

    name = fields.Char(
        required=True,
        string="Approval Subject",
        tracking=True,
        help="Brief description of what needs approval"
    )
    code = fields.Char(
        string="Approval Code",
        readonly=True,
        copy=False,
        help="Unique auto-generated code for the approval"
    )
    description = fields.Text(
        string="Detailed Description",
        help="Full description of the approval request"
    )
    
    # ┌───────────────────────────────────────────────────────┐
    # │              📊 STATUS & WORKFLOW FIELDS             │
    # └───────────────────────────────────────────────────────┘
    
    status = fields.Selection(
        selection=[
            ("draft", "📝 Draft"),
            ("in-progress", "🔄 In Progress"),
            ("approved", "✅ Approved"),
            ("rejected", "❌ Rejected"),
        ],
        default="draft",
        readonly=True,
        tracking=True,
        string="Status",
        help="Current status of the approval workflow"
    )
    
    priority = fields.Selection(
        selection=[
            ("high", "🔴 High"), 
            ("medium", "🟡 Medium"), 
            ("low", "🟢 Low")
        ],
        default="medium",
        tracking=True,
        string="Priority",
        help="Priority level of this approval request"
    )
    
    # ┌───────────────────────────────────────────────────────┐
    # │               👥 USER RELATIONSHIP FIELDS            │
    # └───────────────────────────────────────────────────────┘
    
    requester_id = fields.Many2one(
        comodel_name="res.users",
        string="👤 Requester",
        required=True,
        default=lambda self: self.env.user,
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True,
        help="User who submitted this approval request"
    )
    
    # ┌───────────────────────────────────────────────────────┐
    # │               📅 DATETIME FIELDS                     │
    # └───────────────────────────────────────────────────────┘
    
    request_at = fields.Datetime(
        string="📅 Requested At",
        readonly=True,
        tracking=True,
        help="When the approval request was submitted"
    )
    
    approved_at = fields.Datetime(
        string="✅ Approved At",
        readonly=True,
        tracking=True,
        help="When the approval was fully approved"
    )
    
    rejected_at = fields.Datetime(
        string="❌ Rejected At", 
        readonly=True,
        tracking=True,
        help="When the approval was rejected"
    )
    
    approval_period = fields.Float(
        string="⏱️ Approval Period (Hours)",
        required=True, 
        default=24.0,
        help="Expected time for approval completion"
    )
    
    # ┌───────────────────────────────────────────────────────┐
    # │              🔗 RELATIONSHIP FIELDS                  │
    # └───────────────────────────────────────────────────────┘
    
    approval_step_ids = fields.One2many(
        comodel_name="vnfield.approval.step", 
        inverse_name="approval_id",
        string="📋 Approval Steps",
        help="All steps in this approval workflow"
    )
    
    root_step_ids = fields.One2many(
        comodel_name="vnfield.approval.step", 
        inverse_name="root_of_approval_id",
        string="🌱 Root Steps",
        help="Starting steps of the approval workflow"
    )
    
    project_id = fields.Many2one(
        comodel_name="vnfield.project",
        string="🏗️ Related Project",
        help="Project this approval is related to"
    )
    
    processing_step_ids = fields.Many2many(
        comodel_name="vnfield.approval.step",
        relation="approval_processing_step_rel",
        column1="approval_id",
        column2="step_id",
        readonly=True,
        store=True,
        string="🔄 Processing Steps",
        help="Steps currently being processed"
    )
    
    # ┌───────────────────────────────────────────────────────┐
    # │               📊 COMPUTED FIELDS                     │
    # └───────────────────────────────────────────────────────┘
    
    current_approver_ids = fields.Many2many(
        comodel_name="res.users",
        compute="_compute_current_approvers",
        string="👥 Current Approvers",
        help="Users who need to approve current steps"
    )
    
    is_current_user_approver = fields.Boolean(
        compute="_compute_is_current_user_approver",
        string="🎯 Can Current User Approve",
        help="Whether current user can approve any current step"
    )
    
    can_user_edit = fields.Boolean(
        compute="_compute_can_user_edit",
        string="✏️ Can Edit",
        help="Whether current user can edit this approval"
    )
    
    progress_percentage = fields.Float(
        compute="_compute_progress",
        string="📊 Progress %",
        help="Percentage of completed steps"
    )
    
    total_steps = fields.Integer(
        compute="_compute_step_counts",
        string="📝 Total Steps"
    )
    
    completed_steps = fields.Integer(
        compute="_compute_step_counts", 
        string="✅ Completed Steps"
    )

    # ┌───────────────────────────────────────────────────────┐
    # │               📊 COMPUTED METHODS                    │
    # └───────────────────────────────────────────────────────┘

    @api.depends('processing_step_ids', 'processing_step_ids.approver_id')
    def _compute_current_approvers(self):
        """🎯 Tính toán danh sách approvers hiện tại"""
        for record in self:
            if record.status == 'in-progress' and record.processing_step_ids:
                # Lấy approvers của các steps đang processing
                approvers = record.processing_step_ids.mapped('approver_id')
                record.current_approver_ids = [(6, 0, approvers.ids)]
            else:
                record.current_approver_ids = [(5, 0, 0)]

    @api.depends('current_approver_ids')
    def _compute_is_current_user_approver(self):
        """🎯 Kiểm tra user hiện tại có phải approver không"""
        for record in self:
            record.is_current_user_approver = self.env.user in record.current_approver_ids

    @api.depends('status', 'requester_id')
    def _compute_can_user_edit(self):
        """✏️ Kiểm tra quyền edit của user hiện tại"""
        for record in self:
            current_user = self.env.user
            
            # Admin luôn có quyền edit
            if current_user.has_group('vnfield.group_contractor_admin'):
                record.can_user_edit = True
            # Requester chỉ edit được khi status = draft
            elif current_user == record.requester_id and record.status == 'draft':
                record.can_user_edit = True
            else:
                record.can_user_edit = False

    @api.depends('approval_step_ids', 'approval_step_ids.status')
    def _compute_progress(self):
        """📊 Tính toán tiến độ hoàn thành"""
        for record in self:
            if record.approval_step_ids:
                completed = len(record.approval_step_ids.filtered(lambda s: s.status == 'approved'))
                total = len(record.approval_step_ids)
                record.progress_percentage = (completed / total) * 100 if total > 0 else 0
            else:
                record.progress_percentage = 0

    @api.depends('approval_step_ids', 'approval_step_ids.status')
    def _compute_step_counts(self):
        """📝 Đếm số lượng steps"""
        for record in self:
            record.total_steps = len(record.approval_step_ids)
            record.completed_steps = len(record.approval_step_ids.filtered(lambda s: s.status == 'approved'))

    # ┌───────────────────────────────────────────────────────┐
    # │              🔄 RECORD LIFECYCLE METHODS             │
    # └───────────────────────────────────────────────────────┘

    @api.model_create_multi
    def create(self, vals_list):
        """🆕 Create approval with auto-generated code"""
        for vals in vals_list:
            # Auto-generate code if not provided
            if not vals.get('code'):
                vals['code'] = self.env['ir.sequence'].next_by_code('vnfield.approval') or '/'
            
            # Set default status if not provided
            if not vals.get('status'):
                vals['status'] = 'draft'
                
            # Set default priority if not provided  
            if not vals.get('priority'):
                vals['priority'] = 'medium'
                
        records = super().create(vals_list)
        
        # 📧 Send notification for new approval
        for record in records:
            record.message_post(
                body=f"🆕 New approval request created by {record.requester_id.name}",
                subject=f"New Approval: {record.name}"
            )
        
        return records

    @api.constrains('approval_step_ids')
    def _check_sequential_steps(self):
        """🔗 Kiểm tra tính hợp lệ của sequential workflow"""
        for record in self:
            if record.approval_step_ids:
                # Kiểm tra có ít nhất 1 root step
                root_steps = record.approval_step_ids.filtered(lambda s: not s.prev_step_ids)
                if not root_steps:
                    raise ValidationError("Approval must have at least one root step (step without predecessors)")
                
                # Kiểm tra không có circular dependencies
                for step in record.approval_step_ids:
                    step._check_circular_dependency()

    # ┌───────────────────────────────────────────────────────┐
    # │               🎯 WORKFLOW ACTION METHODS              │
    # └───────────────────────────────────────────────────────┘

    def action_submit_request(self):
        """📤 Submit approval request - chuyển từ draft sang in-progress"""
        self.ensure_one()
        
        # Validation checks
        if self.status != 'draft':
            raise UserError("Only draft approvals can be submitted")
            
        if not self.approval_step_ids:
            raise UserError("Cannot submit approval without approval steps")
        
        if not self.root_step_ids:
            raise UserError("Approval must have at least one root step")
        
        # Update approval status
        self.write({
            'status': 'in-progress',
            'request_at': fields.Datetime.now(),
        })
        
        # Activate root steps
        root_steps = self.root_step_ids.filtered(lambda s: s.status == 'waiting')
        root_steps.write({
            'status': 'in-progress',
            'come_at': fields.Datetime.now(),
        })
        
        # Update processing steps
        self.processing_step_ids = [(6, 0, root_steps.ids)]
        
        # 📧 Notify approvers
        for step in root_steps:
            if step.approver_id:
                step.message_post(
                    body=f"📋 New approval step awaiting your review: {step.name}",
                    partner_ids=[step.approver_id.partner_id.id]
                )
        
        # 📧 Notify requester
        self.message_post(
            body=f"✅ Approval request submitted successfully. Root steps activated.",
            partner_ids=[self.requester_id.partner_id.id]
        )
        
        return True

    def action_cancel_request(self):
        """❌ Cancel approval request"""
        self.ensure_one()
        
        if self.status not in ('draft', 'in-progress'):
            raise UserError("Cannot cancel approved or rejected approvals")
        
        # Reset all steps to waiting
        self.approval_step_ids.write({
            'status': 'waiting',
            'come_at': False,
            'approval_at': False,
        })
        
        # Reset approval to draft
        self.write({
            'status': 'draft',
            'request_at': False,
            'processing_step_ids': [(5, 0, 0)],
        })
        
        # 📧 Notify
        self.message_post(
            body="❌ Approval request has been cancelled",
            partner_ids=[self.requester_id.partner_id.id]
        )
        
        return True

    def _handle_step_approved(self, approved_step):
        """✅ Xử lý khi một step được approved"""
        self.ensure_one()
        
        # Kiểm tra next steps
        next_steps = approved_step.next_step_ids.filtered(lambda s: s.status == 'waiting')
        
        if next_steps:
            # Activate next steps
            next_steps.write({
                'status': 'in-progress', 
                'come_at': fields.Datetime.now(),
            })
            
            # Update processing steps
            current_processing = self.processing_step_ids - approved_step
            self.processing_step_ids = [(6, 0, (current_processing + next_steps).ids)]
            
            # 📧 Notify next approvers
            for step in next_steps:
                if step.approver_id:
                    step.message_post(
                        body=f"📋 New approval step awaiting your review: {step.name}",
                        partner_ids=[step.approver_id.partner_id.id]
                    )
        else:
            # Remove from processing steps
            self.processing_step_ids = [(3, approved_step.id)]
            
            # Check if all steps are completed
            if all(step.status == 'approved' for step in self.approval_step_ids):
                self.write({
                    'status': 'approved',
                    'approved_at': fields.Datetime.now(),
                })
                
                # 📧 Notify completion
                self.message_post(
                    body="🎉 All approval steps completed! Approval is now fully approved.",
                    partner_ids=[self.requester_id.partner_id.id]
                )

    def _handle_step_rejected(self, rejected_step):
        """❌ Xử lý khi một step bị rejected"""
        self.ensure_one()
        
        # Reject entire approval
        self.write({
            'status': 'rejected',
            'rejected_at': fields.Datetime.now(),
            'processing_step_ids': [(5, 0, 0)],
        })
        
        # Cancel all other in-progress steps
        in_progress_steps = self.approval_step_ids.filtered(lambda s: s.status == 'in-progress')
        in_progress_steps.write({
            'status': 'waiting',
            'come_at': False,
        })
        
        # 📧 Notify rejection
        self.message_post(
            body=f"❌ Approval rejected at step: {rejected_step.name}. Reason: {rejected_step.comment or 'No reason provided'}",
            partner_ids=[self.requester_id.partner_id.id]
        )

    # ┌───────────────────────────────────────────────────────┐
    # │               🎯 ACTION METHODS                       │
    # └───────────────────────────────────────────────────────┘

    def action_view_steps(self):
        """📋 View approval steps"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Approval Steps - {self.name}',
            'res_model': 'vnfield.approval.step',
            'view_mode': 'tree,form',
            'domain': [('approval_id', '=', self.id)],
            'context': {'default_approval_id': self.id, 'default_root_of_approval_id': self.id},
        }

    def action_view_current_steps(self):
        """🔄 View current processing steps"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Current Steps - {self.name}',
            'res_model': 'vnfield.approval.step',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.processing_step_ids.ids)],
        }
