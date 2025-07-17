# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════
# ═             📋 VNFIELD APPROVAL REVIEW WIZARD            ═
# ═           Approval Step Review and Decision              ═
# ═══════════════════════════════════════════════════════════

"""
=================================================================
🎯 CHỨC NĂNG: APPROVAL REVIEW WIZARD
=================================================================
- Wizard để approve/reject các approval steps
- Input comment và decision từ approver
- Validate permissions và execute workflow actions
=================================================================
"""

from odoo import api, fields, models
from odoo.exceptions import UserError


# ┌─────────────────────────────────────────────────────────┐
# │              📋 APPROVAL REVIEW WIZARD CLASS           │
# └─────────────────────────────────────────────────────────┘

class ApprovalReview(models.TransientModel):
    """
    ==========================================================
    📋 VNFIELD APPROVAL REVIEW WIZARD
    ==========================================================
    
    🎯 **Mục đích**: 
    - Wizard cho approver để review và đưa ra quyết định
    - Input comment và approval decision
    - Execute approve/reject actions với proper validation
    
    📋 **Review Actions**:
    - approve: Phê duyệt step và chuyển workflow tiếp
    - reject: Từ chối step và terminate approval
    
    🔐 **Permission Logic**:
    - Chỉ assigned approver mới có quyền review
    - Admin có thể override decisions
    - Validate step status trước khi action
    ==========================================================
    """
    
    _name = 'vnfield.approval.review'
    _description = 'Approval Step Review Wizard'

    # ┌───────────────────────────────────────────────────────┐
    # │                    📋 FIELD DEFINITIONS               │
    # └───────────────────────────────────────────────────────┘

    approval_step_id = fields.Many2one(
        'vnfield.approval.step',
        string='Approval Step',
        required=True,
        readonly=True,
        help="Step being reviewed"
    )

    approval_id = fields.Many2one(
        'vnfield.approval',
        string='Approval',
        related='approval_step_id.approval_id',
        readonly=True,
        help="Parent approval of the step"
    )

    step_name = fields.Char(
        string='Step Name',
        related='approval_step_id.name',
        readonly=True
    )

    requester_id = fields.Many2one(
        'res.users',
        string='Requester',
        related='approval_step_id.requester_id',
        readonly=True
    )

    approver_id = fields.Many2one(
        'res.users',
        string='Approver',
        related='approval_step_id.approver_id',
        readonly=True
    )

    current_status = fields.Selection(
        string='Current Status',
        related='approval_step_id.status',
        readonly=True
    )

    decision = fields.Selection([
        ('approve', '✅ Approve'),
        ('reject', '❌ Reject')
    ], string='Decision', required=True, default='approve')

    comment = fields.Text(
        string='Comment',
        help="Add your comment about this decision"
    )

    rejection_reason = fields.Text(
        string='Rejection Reason',
        help="Required reason when rejecting the step"
    )

    # ┌───────────────────────────────────────────────────────┐
    # │               🔄 RECORD LIFECYCLE METHODS             │
    # └───────────────────────────────────────────────────────┘

    @api.model
    def default_get(self, fields_list):
        """🆕 Set default values từ context"""
        res = super().default_get(fields_list)
        
        # Get approval_step_id từ context
        approval_step_id = self.env.context.get('default_approval_step_id')
        if approval_step_id:
            step = self.env['vnfield.approval.step'].browse(approval_step_id)
            res.update({
                'approval_step_id': approval_step_id,
                'comment': f"Reviewed by {self.env.user.name}",
            })
        
        return res

    # ┌───────────────────────────────────────────────────────┐
    # │               🔧 VALIDATION METHODS                   │
    # └───────────────────────────────────────────────────────┘

    def _validate_permission(self):
        """🔐 Validate user permission để review step"""
        self.ensure_one()
        
        if not self.approval_step_id.can_user_approve:
            raise UserError(
                "You don't have permission to review this approval step!"
            )
        
        if self.current_status != 'in-progress':
            raise UserError(
                f"Cannot review step in '{self.current_status}' status. "
                "Only 'in-progress' steps can be reviewed."
            )

    def _validate_decision_data(self):
        """📝 Validate required data cho decision"""
        self.ensure_one()
        
        if self.decision == 'reject' and not self.rejection_reason:
            raise UserError(
                "Rejection reason is required when rejecting a step!"
            )

    # ┌───────────────────────────────────────────────────────┐
    # │               🎯 ACTION METHODS                       │
    # └───────────────────────────────────────────────────────┘

    def action_submit_review(self):
        """📝 Submit review decision"""
        self.ensure_one()
        
        # Validate permissions và data
        self._validate_permission()
        self._validate_decision_data()
        
        # Prepare comment
        final_comment = self.comment or ''
        if self.decision == 'reject' and self.rejection_reason:
            final_comment = f"{final_comment}\n\nRejection Reason: {self.rejection_reason}"
        
        # Update step comment
        if final_comment:
            self.approval_step_id.comment = final_comment
        
        # Execute decision
        if self.decision == 'approve':
            self.approval_step_id.action_approve()
            message = f"✅ Step '{self.step_name}' has been approved"
        else:
            self.approval_step_id.action_reject()
            message = f"❌ Step '{self.step_name}' has been rejected"
        
        # Return success notification
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Review Submitted',
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_cancel(self):
        """❌ Cancel review wizard"""
        return {'type': 'ir.actions.act_window_close'}


# ┌─────────────────────────────────────────────────────────┐
# │               🔗 SYMBOL DEPENDENCIES                   │
# └─────────────────────────────────────────────────────────┘

"""
=================================================================
📋 PHÂN TÍCH PHỤ THUỘC CÁC SYMBOL TRONG APPROVAL REVIEW WIZARD
=================================================================

🎯 **Core Wizard Symbols**:
- ApprovalReview: TransientModel class cho temporary wizard data
- _name: Wizard model identifier trong Odoo registry
- _description: Wizard description cho UI display

📋 **Field Dependencies**:
- approval_step_id: Many2one link đến vnfield.approval.step (target step)
- approval_id: Related field từ step đến parent approval
- requester_id/approver_id: Related fields đến res.users
- decision: Selection field cho approve/reject choices
- comment/rejection_reason: Text fields cho user input

🔄 **Workflow Dependencies**:
- approval_step_id.can_user_approve: Permission check từ step model
- approval_step_id.action_approve(): Workflow action method
- approval_step_id.action_reject(): Rejection workflow method
- current_status validation: Check step status before review

🔐 **Permission System Dependencies**:
- self.env.user: Current user context cho permission checks
- vnfield.group_contractor_admin: Admin group cho override permissions
- UserError exceptions: Validation error handling

📊 **UI Dependencies**:
- default_get(): Context-based default value setting
- ir.actions.client: Notification action type
- display_notification: Client action cho user feedback
- ir.actions.act_window_close: Wizard close action

🔔 **Validation Dependencies**:
- _validate_permission(): Permission validation method
- _validate_decision_data(): Input data validation
- TransientModel: Temporary data storage cho wizard workflow

=================================================================
"""
