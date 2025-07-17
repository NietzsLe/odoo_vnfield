# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


# ═══════════════════════════════════════════════════════════
# ═              🔐 USER PERMISSION ASSIGNMENT WIZARD       ═
# ═══════════════════════════════════════════════════════════

class UserPermissionWizard(models.TransientModel):
    _name = 'vnfield.user.permission.wizard'
    _description = 'User Permission Assignment Wizard'

    # ─────────────── 👥 USER SELECTION ───────────────
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        help='User to assign permissions to'
    )
    
    # ─────────────── 🔐 PERMISSION SELECTION ───────────────
    permission_level = fields.Selection([
        ('user', 'Basic User'),
        ('manager', 'Manager'),
        ('leader', 'Contractor Leader'),
    ], string='Permission Level', required=True, default='user')
    
    # ─────────────── 📋 ADDITIONAL GROUPS ───────────────
    additional_groups = fields.Many2many(
        'res.groups',
        string='Additional Groups',
        help='Additional groups to assign to the user'
    )
    
    # ─────────────── 💬 REASON ───────────────
    reason = fields.Text(
        string='Reason',
        help='Reason for permission assignment'
    )

    @api.model
    def default_get(self, fields_list):
        """📝 Set default values from context"""
        res = super().default_get(fields_list)
        
        if self.env.context.get('active_model') == 'res.users':
            res['user_id'] = self.env.context.get('active_id')
        
        return res

    def action_assign_permissions(self):
        """🔐 Assign permissions to selected user"""
        self.ensure_one()
        
        # Check if current user can manage permissions
        if not self._can_manage_permissions():
            raise UserError("Chỉ có lãnh đạo contractor mới được quyền gán quyền cho user khác.")
        
        # Check if target user belongs to same contractor
        current_user = self.env.user
        if (current_user.contractor_id and 
            self.user_id.contractor_id != current_user.contractor_id):
            raise UserError("Bạn chỉ có thể gán quyền cho user trong cùng contractor.")
        
        # Assign basic group based on permission level
        groups_to_add = []
        
        if self.permission_level == 'user':
            group = self.env.ref('vnfield.group_contractor_user', raise_if_not_found=False)
            if group:
                groups_to_add.append(group.id)
        
        elif self.permission_level == 'manager':
            group = self.env.ref('vnfield.group_contractor_manager', raise_if_not_found=False)
            if group:
                groups_to_add.append(group.id)
        
        elif self.permission_level == 'leader':
            group = self.env.ref('vnfield.group_contractor_leader', raise_if_not_found=False)
            if group:
                groups_to_add.append(group.id)
            # Also set as contractor leader by updating contractor.leader_id
            if self.user_id.contractor_id:
                self.user_id.contractor_id.leader_id = self.user_id.id
        
        # Add additional groups
        groups_to_add.extend(self.additional_groups.ids)
        
        # Apply groups
        for group_id in groups_to_add:
            self.user_id.groups_id = [(4, group_id)]
        
        # 📝 Log permission assignment
        reason_text = f" (Reason: {self.reason})" if self.reason else ""
        self.user_id.message_post(
            body=f"Permission level '{self.permission_level}' assigned by {self.env.user.name}{reason_text}",
            message_type='notification'
        )
        
        return {'type': 'ir.actions.act_window_close'}

    def _can_manage_permissions(self):
        """🔍 Check if current user can manage permissions"""
        current_user = self.env.user
        
        # System admin can always manage
        if current_user.has_group('base.group_system'):
            return True
        
        # Contractor admin can manage
        if current_user.has_group('vnfield.group_contractor_admin'):
            return True
        
        # Contractor leader can manage users in same contractor
        if (current_user.contractor_id and 
            current_user.contractor_id.leader_id.id == current_user.id):
            return True
        
        return False
