from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


# ═══════════════════════════════════════════════════════════
# ═                👥 USER CONTRACTOR INTEGRATION           ═
# ═══════════════════════════════════════════════════════════

class ResUsers(models.Model):
    _inherit = "res.users"

    # ─────────────── 🏢 CONTRACTOR RELATIONSHIP ───────────────
    contractor_id = fields.Many2one(
        "vnfield.contractor",
        string="Contractor",
        help="Contractor this user belongs to"
    )
    
    # ─────────────── 📊 USER PROFILE ENHANCEMENTS ───────────────
    specialization = fields.Char(
        string="User Specialization",
        help="Primary area of expertise for this user"
    )
    
    phone_work = fields.Char(string="Work Phone")
    
    # ─────────────── 👑 CONTRACTOR LEADERSHIP ───────────────
    # 💡 NOTE(assistant): Leadership được quản lý thông qua contractor.leader_id relationship
    
    is_leader_of_contractor = fields.Boolean(
        string="Is Leader of Contractor",
        compute="_compute_is_leader_of_contractor",
        store=False,
        help="Computed field showing if user is leader of their contractor"
    )
    
    @api.depends('contractor_id', 'contractor_id.leader_id')
    def _compute_is_leader_of_contractor(self):
        """👑 Compute if user is leader of their contractor"""
        for user in self:
            user.is_leader_of_contractor = (
                user.contractor_id and 
                user.contractor_id.leader_id.id == user.id
            )
    
    def is_contractor_leader(self):
        """👑 Check if user is leader of their contractor"""
        if not self.contractor_id:
            return False
        return self.contractor_id.leader_id.id == self.id
    
    # ═══════════════════════════════════════════════════════════
    # ═                 UTILITY METHODS                       ═
    # ═══════════════════════════════════════════════════════════
    
    def get_user_projects(self):
        """📋 Get all projects where user is involved"""
        if self.contractor_id:
            return self.env['vnfield.project'].search([
                ('contractor_ids', 'in', self.contractor_id.id)
            ])
        return self.env['vnfield.project'].browse()
    
    def get_user_tasks(self):
        """📋 Get all tasks assigned to or related to user"""
        return self.env['vnfield.task'].search([
            '|', '|', '|',
            ('assignee_id', '=', self.id),
            ('assigner_id', '=', self.id),
            ('verifier_id', '=', self.id),
            ('project_id.member_ids', 'in', self.id)
        ])
    
    def is_contractor_user(self):
        """✅ Check if user is a contractor user"""
        return bool(self.contractor_id)
    
    @api.model
    def get_contractor_users(self, contractor_id):
        """👥 Get all users belonging to a contractor"""
        return self.search([('contractor_id', '=', contractor_id)])

    # ═══════════════════════════════════════════════════════════
    # ═              🔐 PERMISSION MANAGEMENT METHODS          ═
    # ═══════════════════════════════════════════════════════════

    def action_assign_manager_permissions(self):
        """👔 Assign manager permissions"""
        self.ensure_one()
        
        # Check if current user is contractor leader or admin
        if not self._can_manage_permissions():
            raise UserError("Chỉ có lãnh đạo contractor mới được quyền gán quyền manager cho user khác.")
        
        # Get manager group
        manager_group = self.env.ref('vnfield.group_contractor_manager', raise_if_not_found=False)
        if manager_group:
            self.groups_id = [(4, manager_group.id)]
        
        # 📝 TODO(assistant): Log manager assignment activity
        self.message_post(
            body=f"Manager permissions assigned by {self.env.user.name}",
            message_type='notification'
        )
        
        return True

    def action_remove_permissions(self):
        """🚫 Remove user permissions"""
        self.ensure_one()
        
        # Check if current user is contractor leader or admin
        if not self._can_manage_permissions():
            raise UserError("Chỉ có lãnh đạo contractor mới được quyền thu hồi quyền của user khác.")
        
        # Remove contractor-specific groups
        contractor_groups = self.env['res.groups'].search([
            ('name', 'like', 'VNField')
        ])
        
        for group in contractor_groups:
            if group.id in self.groups_id.ids:
                self.groups_id = [(3, group.id)]
        
        # 📝 TODO(assistant): Log permission removal activity
        self.message_post(
            body=f"Permissions removed by {self.env.user.name}",
            message_type='notification'
        )
        
        return True

    def action_remove_leader_status(self):
        """👑 Remove leader status from user"""
        self.ensure_one()
        
        # Check if current user can manage permissions
        if not self._can_manage_permissions():
            raise UserError("Chỉ có lãnh đạo contractor mới được quyền thu hồi vai trò lãnh đạo.")
        
        # Remove leader status
        self.is_contractor_leader = False
        
        # Remove leader group
        leader_group = self.env.ref('vnfield.group_contractor_leader', raise_if_not_found=False)
        if leader_group and leader_group.id in self.groups_id.ids:
            self.groups_id = [(3, leader_group.id)]
        
        # 📝 TODO(assistant): Log leader removal activity
        self.message_post(
            body=f"Leader status removed by {self.env.user.name}",
            message_type='notification'
        )
        
        return True

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

    # ═══════════════════════════════════════════════════════════
    # ═                    ACTION METHODS                       ═
    # ═══════════════════════════════════════════════════════════
    
    def action_set_as_contractor_leader(self):
        """👑 Set this user as contractor leader"""
        self.ensure_one()
        
        if not self.contractor_id:
            raise UserError("User phải thuộc về một contractor để có thể làm lãnh đạo.")
        
        # Set this user as leader of their contractor
        self.contractor_id.leader_id = self.id
        
        # Assign leader group
        leader_group = self.env.ref('vnfield.group_contractor_leader', raise_if_not_found=False)
        if leader_group:
            self.groups_id = [(4, leader_group.id)]
        
        # 📝 Log leadership assignment
        self.message_post(
            body=f"Được chỉ định làm lãnh đạo contractor {self.contractor_id.name}",
            message_type='notification'
        )
        
        return True
    
    def action_remove_contractor_leadership(self):
        """� Remove contractor leadership from this user"""
        self.ensure_one()
        
        if not self.contractor_id or self.contractor_id.leader_id.id != self.id:
            raise UserError("User không phải là lãnh đạo contractor.")
        
        # Remove leadership
        self.contractor_id.leader_id = False
        
        # Remove leader group
        leader_group = self.env.ref('vnfield.group_contractor_leader', raise_if_not_found=False)
        if leader_group and leader_group.id in self.groups_id.ids:
            self.groups_id = [(3, leader_group.id)]
        
        # 📝 Log leadership removal
        self.message_post(
            body=f"Đã bị gỡ bỏ vai trò lãnh đạo contractor {self.contractor_id.name}",
            message_type='notification'
        )
        
        return True
