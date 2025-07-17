from odoo import api, fields, models, exceptions
from odoo.tools.float_utils import float_compare


# ═══════════════════════════════════════════════════════════
# ═                🏗️ PROJECT MODEL                         ═
# ═══════════════════════════════════════════════════════════

class Project(models.Model):
    _name = "vnfield.project"
    _description = "VN Field Project Management"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, create_date desc"

    # ─────────────── 🏷️ BASIC PROJECT INFORMATION ───────────────
    name = fields.Char(
        string="Project Name", 
        required=True,
        tracking=True
    )
    
    description = fields.Html(
        string="Project Description",
        help="Detailed description of the project scope and objectives"
    )
    
    code = fields.Char(
        string="Project Code",
        help="Unique identifier code for the project"
    )

    # ─────────────── ⚡ PROJECT STATUS & PRIORITY ───────────────
    status = fields.Selection([
        ("draft", "Draft"),
        ("planning", "Planning"),
        ("in-progress", "In Progress"),
        ("on-hold", "On Hold"),
        ("review", "Under Review"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ], string="Status", default="draft", tracking=True)

    priority = fields.Selection([
        ("0", "Low"),
        ("1", "Normal"),
        ("2", "High"),
        ("3", "Critical")
    ], string="Priority", default="1")

    # ─────────────── 📅 PROJECT TIMELINE ───────────────
    start_date = fields.Date(
        string="Start Date",
        tracking=True
    )
    
    end_date = fields.Date(
        string="End Date",
        tracking=True
    )
    
    deadline = fields.Date(
        string="Deadline",
        help="Final deadline for project completion"
    )

    # ─────────────── 💰 PROJECT FINANCIALS ───────────────
    budget = fields.Monetary(
        string="Project Budget",
        currency_field="currency_id"
    )
    
    actual_cost = fields.Monetary(
        string="Actual Cost",
        currency_field="currency_id",
        compute="_compute_actual_cost",
        store=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        default=lambda self: self.env.company.currency_id
    )

    # ─────────────── 📊 PROJECT PROGRESS ───────────────
    progress = fields.Float(
        string="Progress (%)",
        compute="_compute_progress",
        store=True,
        help="Overall project completion percentage"
    )

    # ─────────────── 👥 PROJECT TEAM STRUCTURE ───────────────
    manager_id = fields.Many2one(
        'res.users',
        string="Project Manager",
        required=True,
        tracking=True,
        help="User responsible for managing this project"
    )

    member_ids = fields.Many2many(
        'res.users',
        'project_member_rel',
        'project_id',
        'user_id',
        string="Project Members",
        help="Team members working on this project"
    )

    # ─────────────── 🏢 CONTRACTOR RELATIONSHIPS ───────────────
    project_owner_id = fields.Many2one(
        'vnfield.contractor',
        string="Project Owner",
        required=True,
        tracking=True,
        help="Main contractor who owns this project"
    )

    subcontractor_ids = fields.Many2many(
        'vnfield.contractor',
        'project_subcontractor_rel',
        'project_id',
        'contractor_id',
        string="Subcontractors",
        help="Additional contractors participating in the project"
    )

    # ─────────────── 🔗 PROJECT RELATIONSHIPS ───────────────
    task_ids = fields.One2many(
        'vnfield.task',
        'project_id',
        string="Project Tasks"
    )

    approval_ids = fields.One2many(
        'vnfield.approval',
        'project_id',
        string="Project Approvals"
    )

    # ─────────────── 📈 COMPUTED FIELDS ───────────────
    task_count = fields.Integer(
        string="Tasks Count",
        compute="_compute_task_count"
    )

    approval_count = fields.Integer(
        string="Approvals Count", 
        compute="_compute_approval_count"
    )

    member_count = fields.Integer(
        string="Members Count",
        compute="_compute_member_count"
    )

    # ═══════════════════════════════════════════════════════════
    # ═                📊 COMPUTED METHODS                      ═
    # ═══════════════════════════════════════════════════════════

    @api.depends('task_ids.progress')
    def _compute_progress(self):
        """💡 Calculate overall project progress based on tasks"""
        for project in self:
            if project.task_ids:
                total_progress = sum(project.task_ids.mapped('progress'))
                project.progress = total_progress / len(project.task_ids)
            else:
                project.progress = 0.0

    @api.depends('task_ids')
    def _compute_actual_cost(self):
        """💰 Calculate actual cost from tasks"""
        for project in self:
            # This would be implemented based on task cost tracking
            project.actual_cost = 0.0

    def _compute_task_count(self):
        """📋 Count total tasks"""
        for project in self:
            project.task_count = len(project.task_ids)

    def _compute_approval_count(self):
        """✅ Count total approvals"""
        for project in self:
            project.approval_count = len(project.approval_ids)

    def _compute_member_count(self):
        """👥 Count team members"""
        for project in self:
            project.member_count = len(project.member_ids)

    # ═══════════════════════════════════════════════════════════
    # ═                🔒 VALIDATION METHODS                    ═
    # ═══════════════════════════════════════════════════════════

    @api.constrains('status')
    def _check_status_transition(self):
        """🔒 Validate status transitions when status is changed directly"""
        for project in self:
            if project._origin and project._origin.status != project.status:
                # Skip validation for new records
                if not project._origin.id:
                    continue
                    
                try:
                    # Use a temporary instance to validate transition
                    temp_project = project._origin
                    temp_project._validate_status_transition(project.status)
                except exceptions.UserError:
                    # Re-raise with context about direct status change
                    raise exceptions.UserError(
                        f"❌ Không thể thay đổi trạng thái trực tiếp từ '{project._origin.status}' sang '{project.status}'. "
                        f"Vui lòng sử dụng các nút action tương ứng!"
                    )

    @api.constrains('start_date', 'end_date', 'deadline')
    def _check_project_dates(self):
        """📅 Validate project date logic"""
        for project in self:
            if project.start_date and project.end_date:
                if project.start_date > project.end_date:
                    raise exceptions.UserError("❌ Ngày bắt đầu không thể sau ngày kết thúc!")
            
            if project.start_date and project.deadline:
                if project.start_date > project.deadline:
                    raise exceptions.UserError("❌ Ngày bắt đầu không thể sau deadline!")
            
            if project.end_date and project.deadline:
                if project.end_date > project.deadline:
                    raise exceptions.UserError("❌ Ngày kết thúc không thể sau deadline!")

    @api.constrains('progress')
    def _check_progress_range(self):
        """📊 Validate progress percentage"""
        for project in self:
            if project.progress < 0 or project.progress > 100:
                raise exceptions.UserError("❌ Progress phải trong khoảng 0-100%!")

    @api.constrains('budget', 'actual_cost')
    def _check_budget_values(self):
        """💰 Validate budget and cost values"""
        for project in self:
            if project.budget < 0:
                raise exceptions.UserError("❌ Budget không thể âm!")
            
            if project.actual_cost < 0:
                raise exceptions.UserError("❌ Actual cost không thể âm!")

    # ═══════════════════════════════════════════════════════════
    # ═                🎯 ACTION METHODS                        ═
    # ═══════════════════════════════════════════════════════════

    def _validate_status_transition(self, new_status):
        """🔒 Validate if status transition is allowed"""
        # Define allowed transitions
        allowed_transitions = {
            'draft': ['planning', 'canceled'],
            'planning': ['in-progress', 'on-hold', 'canceled'],
            'in-progress': ['review', 'completed', 'on-hold', 'canceled'],
            'on-hold': ['in-progress', 'planning', 'canceled'],
            'review': ['completed', 'in-progress'],
            'completed': [],  # Final state - no transitions allowed
            'canceled': []    # Final state - no transitions allowed
        }
        
        current_status = self.status
        if new_status not in allowed_transitions.get(current_status, []):
            raise exceptions.UserError(
                f"❌ Không thể chuyển từ trạng thái '{current_status}' sang '{new_status}'. "
                f"Các trạng thái được phép: {', '.join(allowed_transitions.get(current_status, []))}"
            )

    def action_start_project(self):
        """▶️ Start the project"""
        # 🔍 Validate transition
        self._validate_status_transition('in-progress')
        
        # ✅ Additional business validations
        if not self.manager_id:
            raise exceptions.UserError("❌ Phải có Project Manager mới có thể bắt đầu dự án!")
        
        if not self.project_owner_id:
            raise exceptions.UserError("❌ Phải có Project Owner mới có thể bắt đầu dự án!")
        
        # 📝 TODO(assistant): Kiểm tra thêm các điều kiện khác như budget, timeline
        
        self.write({
            'status': 'in-progress',
            'start_date': fields.Date.today()
        })
        
        # 📧 Send notification
        self.message_post(
            body=f"🚀 Dự án đã được bắt đầu bởi {self.env.user.name}",
            subject="Dự án đã bắt đầu"
        )

    def action_complete_project(self):
        """✅ Complete the project"""
        # 🔍 Validate transition
        self._validate_status_transition('completed')
        
        # ✅ Additional business validations
        incomplete_tasks = self.task_ids.filtered(lambda t: t.status != 'completed')
        if incomplete_tasks:
            raise exceptions.UserError(
                f"❌ Không thể hoàn thành dự án khi còn {len(incomplete_tasks)} task chưa hoàn thành!"
            )
        
        pending_approvals = self.approval_ids.filtered(lambda a: a.status == 'pending')
        if pending_approvals:
            raise exceptions.UserError(
                f"❌ Không thể hoàn thành dự án khi còn {len(pending_approvals)} approval đang chờ xử lý!"
            )
        
        self.write({
            'status': 'completed',
            'end_date': fields.Date.today(),
            'progress': 100.0
        })
        
        # 📧 Send notification
        self.message_post(
            body=f"🎉 Dự án đã được hoàn thành bởi {self.env.user.name}",
            subject="Dự án đã hoàn thành"
        )

    def action_cancel_project(self):
        """❌ Cancel the project"""
        # 🔍 Validate transition  
        self._validate_status_transition('canceled')
        
        # ⚠️ Warning for active tasks
        active_tasks = self.task_ids.filtered(lambda t: t.status == 'in-progress')
        if active_tasks:
            # 💡 NOTE(assistant): Có thể thêm wizard để xác nhận hủy khi có task đang chạy
            self.message_post(
                body=f"⚠️ Cảnh báo: Có {len(active_tasks)} task đang thực hiện sẽ bị ảnh hưởng",
                subject="Cảnh báo hủy dự án"
            )
        
        self.write({'status': 'canceled'})
        
        # 📧 Send notification
        self.message_post(
            body=f"❌ Dự án đã bị hủy bởi {self.env.user.name}",
            subject="Dự án đã bị hủy"
        )

    def action_put_on_hold(self):
        """⏸️ Put project on hold"""
        # 🔍 Validate transition
        self._validate_status_transition('on-hold')
        
        self.write({'status': 'on-hold'})
        
        # 📧 Send notification
        self.message_post(
            body=f"⏸️ Dự án đã được tạm dừng bởi {self.env.user.name}",
            subject="Dự án tạm dừng"
        )

    def action_move_to_planning(self):
        """📋 Move project to planning phase"""
        # 🔍 Validate transition
        self._validate_status_transition('planning')
        
        # ✅ Basic validations for planning
        if not self.name or not self.description:
            raise exceptions.UserError("❌ Phải có tên và mô tả dự án trước khi chuyển sang lập kế hoạch!")
        
        self.write({'status': 'planning'})
        
        # 📧 Send notification
        self.message_post(
            body=f"📋 Dự án đã chuyển sang giai đoạn lập kế hoạch bởi {self.env.user.name}",
            subject="Chuyển sang lập kế hoạch"
        )

    def action_move_to_review(self):
        """🔍 Move project to review phase"""
        # 🔍 Validate transition
        self._validate_status_transition('review')
        
        # ✅ Validation: All tasks should be completed before review
        incomplete_tasks = self.task_ids.filtered(lambda t: t.status != 'completed')
        if incomplete_tasks:
            raise exceptions.UserError(
                f"❌ Không thể chuyển sang đánh giá khi còn {len(incomplete_tasks)} task chưa hoàn thành!"
            )
        
        self.write({'status': 'review'})
        
        # 📧 Send notification
        self.message_post(
            body=f"🔍 Dự án đã chuyển sang giai đoạn đánh giá bởi {self.env.user.name}",
            subject="Chuyển sang đánh giá"
        )

    def action_resume_project(self):
        """▶️ Resume project from on-hold"""
        if self.status != 'on-hold':
            raise exceptions.UserError("❌ Chỉ có thể tiếp tục dự án đang tạm dừng!")
        
        # Resume to previous logical state (usually in-progress)
        self.write({'status': 'in-progress'})
        
        # 📧 Send notification
        self.message_post(
            body=f"▶️ Dự án đã được tiếp tục bởi {self.env.user.name}",
            subject="Dự án được tiếp tục"
        )

    # ═══════════════════════════════════════════════════════════
    # ═                🔗 UTILITY METHODS                       ═
    # ═══════════════════════════════════════════════════════════

    def get_all_contractors(self):
        """🏢 Get all contractors (owner + subcontractors)"""
        contractors = self.env['vnfield.contractor']
        if self.project_owner_id:
            contractors |= self.project_owner_id
        contractors |= self.subcontractor_ids
        return contractors

    # ═══════════════════════════════════════════════════════════
    # ═                🔄 RECORD LIFECYCLE METHODS              ═
    # ═══════════════════════════════════════════════════════════

    @api.model_create_multi
    def create(self, vals_list):
        """🆕 Create project with auto-generated code"""
        for vals in vals_list:
            if not vals.get('code'):
                vals['code'] = self.env['ir.sequence'].next_by_code('vnfield.project') or '/'
        return super().create(vals_list)

    def is_overdue(self):
        """🚨 Check if project is overdue"""
        if self.deadline:
            return fields.Date.today() > self.deadline and self.status not in ['completed', 'canceled']
        return False
