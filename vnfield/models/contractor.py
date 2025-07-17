from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


# ═══════════════════════════════════════════════════════════
# ═                🏢 CONTRACTOR BASE MODEL                  ═
# ═══════════════════════════════════════════════════════════

class Contractor(models.Model):
    _name = "vnfield.contractor"
    _description = "VN Field Contractor"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ─────────────── 🏷️ BASIC INFORMATION ───────────────
    name = fields.Char(string="Name", required=True, tracking=True)
    phone = fields.Char(string="Phone", tracking=True)
    email = fields.Char(string="Email", tracking=True)
    address = fields.Char(string="Address", tracking=True)
    active = fields.Boolean(default=True, tracking=True)

    # ─────────────── 🏢 CONTRACTOR STATUS & LEADERSHIP ───────────────
    is_default_contractor = fields.Boolean(
        string="Is Default Contractor",
        default=False,
        help="Contractor đại diện cho toàn bộ ứng dụng nhà thầu"
    )
    
    # 👑 Leader relationship
    leader_id = fields.Many2one(
        'res.users',
        string="Contractor Leader",
        help="User who leads this contractor organization"
    )

    # ─────────────── ️ CONTRACTOR PROFILE ───────────────
    specialization = fields.Char(
        string="Specialization",
        help="Primary area of expertise"
    )
    
    rating = fields.Float(
        string="Rating", 
        digits=(3,1),
        help="Contractor performance rating"
    )
    
    last_activity = fields.Datetime(
        string="Last Activity",
        help="Last recorded activity timestamp"
    )

    # ─────────────── 🔗 RELATIONSHIPS ───────────────
    user_ids = fields.One2many(
        "res.users", 
        "contractor_id", 
        string="Users",
        help="Users who belong to this contractor"
    )
    
    project_ids = fields.Many2many(
        "vnfield.project",
        "contractor_project_rel",
        "contractor_id",
        "project_id",
        string="Projects",
    )
    
    # ─────────────── 📊 COMPUTED FIELDS ───────────────
    user_count = fields.Integer(
        string='User Count',
        compute='_compute_user_count',
        store=True,
        help='Number of users belonging to this contractor'
    )
    
    has_leader = fields.Boolean(
        string='Has Leader',
        compute='_compute_has_leader',
        store=True,
        help='Whether this contractor has a designated leader'
    )
    
    # ─────────────── 📊 PERFORMANCE METRICS ───────────────
    completed_projects = fields.Integer(
        string='Completed Projects',
        default=0,
        help='Number of successfully completed projects'
    )
    
    active_projects = fields.Integer(
        string='Active Projects',
        default=0,
        help='Number of currently active projects'
    )
    
    total_earnings = fields.Monetary(
        string='Total Earnings',
        currency_field='currency_id',
        default=0.0,
        help='Total earnings from all projects'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        help='Currency for earnings calculation'
    )
    
    average_completion_time = fields.Float(
        string='Avg Completion Time (days)',
        default=0.0,
        help='Average project completion time in days'
    )
    
    client_satisfaction = fields.Float(
        string='Client Satisfaction (%)',
        default=0.0,
        help='Average client satisfaction percentage'
    )
    
    created_date = fields.Datetime(
        string='Created Date',
        default=fields.Datetime.now,
        readonly=True,
        help='Date when contractor was created'
    )

    # ═══════════════════════════════════════════════════════════
    # ═                📊 CONTRACTOR COMMON METHODS             ═
    # ═══════════════════════════════════════════════════════════

    @api.depends('user_ids')
    def _compute_user_count(self):
        """📊 Compute user count statistics"""
        for contractor in self:
            contractor.user_count = len(contractor.user_ids)

    @api.depends('leader_id')
    def _compute_has_leader(self):
        """👑 Compute whether contractor has a leader"""
        for contractor in self:
            contractor.has_leader = bool(contractor.leader_id)

    def update_rating(self, new_rating):
        """⭐ Update contractor rating with validation"""
        if 0 <= new_rating <= 5:
            self.rating = new_rating
        else:
            raise ValueError("Rating must be between 0 and 5")

    def update_last_activity(self):
        """🕒 Update last activity timestamp"""
        self.last_activity = fields.Datetime.now()

    def is_active_contractor(self):
        """✅ Check if contractor is active and available"""
        return self.active and bool(self.name)

    @api.model
    def get_contractors_by_type(self, contractor_type):
        """🔍 Get contractors filtered by type"""
        return self.search([
            ('contractor_type', '=', contractor_type),
            ('active', '=', True)
        ])

    @api.model
    def get_contractors_by_specialization(self, specialization):
        """🎯 Get contractors by specialization"""
        return self.search([
            ('specialization', 'ilike', specialization),
            ('active', '=', True)
        ])

    # ═══════════════════════════════════════════════════════════
    # ═              🔐 CONTRACTOR MANAGEMENT METHODS          ═
    # ═══════════════════════════════════════════════════════════

    def action_create_default_contractor(self):
        """� Make this contractor the default one"""
        self.ensure_one()
        
        # Remove default status from other contractors
        other_defaults = self.search([
            ('is_default_contractor', '=', True),
            ('id', '!=', self.id)
        ])
        other_defaults.write({'is_default_contractor': False})
        
        # Set this as default
        self.is_default_contractor = True
        
        # 📝 TODO(assistant): Log default contractor change
        self.message_post(
            body=f"Contractor set as default by {self.env.user.name}",
            message_type='notification'
        )
        
        return True

    def action_assign_contractor_leader(self):
        """👑 Open wizard to assign contractor leader"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assign Contractor Leader',
            'res_model': 'res.users',
            'view_mode': 'tree,form',
            'domain': [('contractor_id', '=', self.id)],
            'context': {
                'default_contractor_id': self.id,
                'contractor_assignment_mode': True,
            },
            'target': 'new',
        }

    def action_view_users(self):
        """👥 View all users of this contractor"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Users - {self.name}',
            'res_model': 'res.users',
            'view_mode': 'tree,form',
            'domain': [('contractor_id', '=', self.id)],
            'context': {'default_contractor_id': self.id},
        }

    def action_view_leader(self):
        """👑 View the leader of this contractor"""
        self.ensure_one()
        
        if not self.leader_id:
            raise UserError("Contractor này chưa có lãnh đạo được chỉ định.")
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Leader - {self.name}',
            'res_model': 'res.users',
            'view_mode': 'form',
            'res_id': self.leader_id.id,
            'context': {'default_contractor_id': self.id},
        }

    def action_view_projects(self):
        """🔗 View all projects associated with this contractor"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Projects - {self.name}',
            'res_model': 'vnfield.project',
            'view_mode': 'tree,form',
            'domain': [('contractor_ids', 'in', self.id)],
        }

    @api.constrains('is_default_contractor')
    def _check_single_default_contractor(self):
        """✅ Ensure only one default contractor exists"""
        for contractor in self:
            if contractor.is_default_contractor:
                other_defaults = self.search([
                    ('is_default_contractor', '=', True),
                    ('id', '!=', contractor.id)
                ])
                if other_defaults:
                    raise ValidationError("Chỉ có thể có một contractor mặc định duy nhất trong hệ thống.")

    @api.model_create_multi
    def create(self, vals_list):
        """📝 Override create to handle default contractor"""
        contractors = super().create(vals_list)
        
        for contractor in contractors:
            # If no default contractor exists, make the first one default
            if not self.search([('is_default_contractor', '=', True)]):
                contractor.is_default_contractor = True
        
        return contractors

    @api.model
    def create_default_contractor(self):
        """🏠 Create default contractor if none exists"""
        existing_default = self.search([('is_default_contractor', '=', True)], limit=1)
        
        if not existing_default:
            default_contractor = self.create({
                'name': 'Default Internal Contractor',
                'contractor_type': 'internal',
                'is_default_contractor': True,
                'specialization': 'General Construction Management',
                'email': 'admin@vnfield.com',
                'phone': '+84-123-456-789'
            })
            return default_contractor
        
        return existing_default
