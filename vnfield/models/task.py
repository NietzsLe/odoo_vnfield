from odoo import api, fields, models, _, exceptions
from odoo.tools.float_utils import float_compare


# ═══════════════════════════════════════════════════════════
# ═                📋 ENHANCED TASK MODEL                   ═
# ═══════════════════════════════════════════════════════════

class Task(models.Model):
    _name = "vnfield.task"
    _description = "VN Field Task Management"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, create_date desc"

    # ─────────────── 🏷️ BASIC TASK INFORMATION ───────────────
    name = fields.Char(
        string="Task Name", 
        required=True,
        tracking=True
    )
    
    code = fields.Char(
        string="Task Code",
        readonly=True,
        copy=False,
        help="Unique auto-generated code for the task"
    )
    
    description = fields.Html(
        string="Task Description",
        help="Detailed description of the task requirements and objectives"
    )
    
    # ─────────────── ⚡ TASK STATUS & PRIORITY ───────────────
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

    # ─────────────── 👥 TASK ROLES & RESPONSIBILITIES ───────────────
    assignee_id = fields.Many2one(
        'res.users',
        string="Assignee",
        required=True,
        tracking=True,
        help="User responsible for executing this task"
    )
    
    assigner_id = fields.Many2one(
        'res.users',
        string="Assigner",
        required=True,
        tracking=True,
        help="User who assigned this task"
    )
    
    verifier_id = fields.Many2one(
        'res.users',
        string="Verifier",
        required=True,
        tracking=True,
        help="User responsible for reviewing and verifying task completion"
    )

    # ─────────────── 🏢 CONTRACTOR RELATIONSHIPS ───────────────
    assignee_contractor_id = fields.Many2one(
        'vnfield.contractor',
        string="Assignee Contractor",
        compute="_compute_user_contractors",
        store=True,
        help="Contractor associated with the assignee"
    )
    
    assigner_contractor_id = fields.Many2one(
        'vnfield.contractor',
        string="Assigner Contractor",
        compute="_compute_user_contractors",
        store=True,
        help="Contractor associated with the assigner"
    )
    
    verifier_contractor_id = fields.Many2one(
        'vnfield.contractor',
        string="Verifier Contractor",
        compute="_compute_user_contractors",
        store=True,
        help="Contractor associated with the verifier"
    )
    
    related_contractor_ids = fields.Many2many(
        'vnfield.contractor',
        'task_contractor_rel',
        'task_id',
        'contractor_id',
        string="Related Contractors",
        compute="_compute_related_contractors",
        store=True,
        help="All contractors involved in this task"
    )

    # ─────────────── ✅ APPROVAL WORKFLOW ───────────────
    approval_id = fields.Many2one(
        'vnfield.approval',
        string="Approval",
        help="Optional approval required for task completion from review status"
    )
    
    requires_approval = fields.Boolean(
        string="Requires Approval",
        default=False,
        help="Whether this task requires approval to move from review to completed"
    )

    requires_approval = fields.Boolean(
        string="Requires Approval",
        default=False,
        help="Whether this task requires approval to move from review to completed"
    )

    # ─────────────── 📅 TASK TIMELINE ───────────────
    start_date = fields.Datetime(
        string="Start Date",
        tracking=True
    )
    
    completion_date = fields.Datetime(
        string="Completion Date",
        tracking=True
    )
    
    deadline = fields.Datetime(
        string="Deadline",
        help="Final deadline for task completion"
    )

    # ─────────────── 📊 TASK PROGRESS & EFFORT ───────────────
    progress = fields.Float(
        string="Progress (%)",
        default=0.0,
        help="Task completion progress percentage"
    )
    
    estimated_hours = fields.Float(
        string="Estimated Hours",
        help="Estimated time to complete the task"
    )
    
    actual_hours = fields.Float(
        string="Actual Hours",
        help="Actual time spent on the task"
    )

    # ─────────────── 🔗 PROJECT & TASK RELATIONSHIPS ───────────────
    project_id = fields.Many2one(
        'vnfield.project',
        string="Project",
        help="Project this task belongs to"
    )
    
    parent_task_id = fields.Many2one(
        'vnfield.task',
        string="Parent Task",
        help="Parent task if this is a subtask"
    )
    
    child_task_ids = fields.One2many(
        'vnfield.task',
        'parent_task_id',
        string="Subtasks"
    )

    # ═══════════════════════════════════════════════════════════
    # ═                📊 COMPUTED METHODS                      ═
    # ═══════════════════════════════════════════════════════════

    @api.depends('assignee_id', 'assigner_id', 'verifier_id')
    def _compute_user_contractors(self):
        """🏢 Compute contractor relationships for each user role"""
        for task in self:
            # Find contractors for each user
            task.assignee_contractor_id = self._get_user_contractor(task.assignee_id)
            task.assigner_contractor_id = self._get_user_contractor(task.assigner_id)
            task.verifier_contractor_id = self._get_user_contractor(task.verifier_id)

    @api.depends('assignee_contractor_id', 'assigner_contractor_id', 'verifier_contractor_id')
    def _compute_related_contractors(self):
        """🔗 Compute all contractors related to this task"""
        for task in self:
            contractors = self.env['vnfield.contractor']
            if task.assignee_contractor_id:
                contractors |= task.assignee_contractor_id
            if task.assigner_contractor_id:
                contractors |= task.assigner_contractor_id
            if task.verifier_contractor_id:
                contractors |= task.verifier_contractor_id
            task.related_contractor_ids = contractors

    def _get_user_contractor(self, user):
        """🔍 Get contractor associated with a user"""
        if not user:
            return False
        
        # Search for contractor where user is associated
        # This could be through various relationships depending on your data model
        contractor = self.env['vnfield.contractor'].search([
            '|', '|',
            ('manager_user_id', '=', user.id),  # If contractor has manager_user_id field
            ('user_id', '=', user.id),          # If contractor has user_id field
            ('member_ids', 'in', user.id)       # If contractor has member_ids field
        ], limit=1)
        
        return contractor if contractor else False

    # ═══════════════════════════════════════════════════════════
    # ═                🔒 VALIDATION METHODS                    ═
    # ═══════════════════════════════════════════════════════════

    @api.constrains('status')
    def _check_status_transition(self):
        """🔒 Validate status transitions when status is changed directly"""
        for task in self:
            if task._origin and task._origin.status != task.status:
                # Skip validation for new records
                if not task._origin.id:
                    continue
                    
                try:
                    # Use a temporary instance to validate transition
                    temp_task = task._origin
                    temp_task._validate_status_transition(task.status)
                except exceptions.UserError:
                    # Re-raise with context about direct status change
                    raise exceptions.UserError(
                        f"❌ Không thể thay đổi trạng thái trực tiếp từ '{task._origin.status}' sang '{task.status}'. "
                        f"Vui lòng sử dụng các nút action tương ứng!"
                    )

    @api.constrains('progress')
    def _check_progress_range(self):
        """📊 Validate progress percentage"""
        for task in self:
            if task.progress < 0 or task.progress > 100:
                raise exceptions.UserError("❌ Progress phải trong khoảng 0-100%!")

    @api.constrains('estimated_hours', 'actual_hours')
    def _check_hours_values(self):
        """⏰ Validate hour values"""
        for task in self:
            if task.estimated_hours < 0:
                raise exceptions.UserError("❌ Estimated hours không thể âm!")
            
            if task.actual_hours < 0:
                raise exceptions.UserError("❌ Actual hours không thể âm!")

    @api.constrains('start_date', 'completion_date', 'deadline')
    def _check_task_dates(self):
        """📅 Validate task date logic"""
        for task in self:
            if task.start_date and task.completion_date:
                if task.start_date > task.completion_date:
                    raise exceptions.UserError("❌ Ngày bắt đầu không thể sau ngày hoàn thành!")
            
            if task.start_date and task.deadline:
                if task.start_date > task.deadline:
                    raise exceptions.UserError("❌ Ngày bắt đầu không thể sau deadline!")
            
            if task.completion_date and task.deadline:
                if task.completion_date > task.deadline:
                    raise exceptions.UserError("❌ Ngày hoàn thành không thể sau deadline!")

    # ═══════════════════════════════════════════════════════════
    # ═                🎯 ACTION METHODS                        ═
    # ═══════════════════════════════════════════════════════════

    def _validate_status_transition(self, new_status):
        """🔒 Validate if status transition is allowed"""
        # Define allowed transitions (similar to project)
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

    def action_start_task(self):
        """▶️ Start the task"""
        # 🔍 Validate transition
        self._validate_status_transition('in-progress')
        
        # ✅ Additional business validations
        if not self.assignee_id:
            raise exceptions.UserError("❌ Phải có Assignee mới có thể bắt đầu task!")
        
        self.write({
            'status': 'in-progress',
            'start_date': fields.Datetime.now()
        })
        
        # 📧 Send notification
        self.message_post(
            body=f"🚀 Task đã được bắt đầu bởi {self.env.user.name}",
            subject="Task đã bắt đầu"
        )

    def action_move_to_review(self):
        """🔍 Move task to review phase"""
        # 🔍 Validate transition
        self._validate_status_transition('review')
        
        # ✅ Check if verifier is set
        if not self.verifier_id:
            raise exceptions.UserError("❌ Phải có Verifier mới có thể chuyển task sang review!")
        
        self.write({'status': 'review'})
        
        # 📧 Send notification to verifier
        self.message_post(
            body=f"🔍 Task đã chuyển sang review, chờ {self.verifier_id.name} xác nhận",
            subject="Task chờ review"
        )

    def action_complete_task(self):
        """✅ Complete the task"""
        # 🔍 Validate transition
        self._validate_status_transition('completed')
        
        # ✅ Check permissions - only verifier can complete from review
        if self.status == 'review':
            if self.env.user != self.verifier_id:
                raise exceptions.UserError("❌ Chỉ Verifier mới có thể hoàn thành task từ trạng thái review!")
            
            # Check if approval is required and exists
            if self.requires_approval and not self.approval_id:
                raise exceptions.UserError("❌ Task này yêu cầu approval để hoàn thành!")
            
            # If approval exists, check its status
            if self.approval_id and self.approval_id.status != 'approved':
                raise exceptions.UserError("❌ Approval chưa được phê duyệt!")
        
        self.write({
            'status': 'completed',
            'completion_date': fields.Datetime.now(),
            'progress': 100.0
        })
        
        # 📧 Send notification
        self.message_post(
            body=f"🎉 Task đã được hoàn thành bởi {self.env.user.name}",
            subject="Task đã hoàn thành"
        )

    def action_assign_approval(self):
        """🎯 Assign approval to task (only verifier can do this)"""
        if self.env.user != self.verifier_id:
            raise exceptions.UserError("❌ Chỉ Verifier mới có thể gán approval cho task!")
        
        # Create approval if doesn't exist
        if not self.approval_id:
            approval = self.env['vnfield.approval'].create({
                'name': f"Approval for {self.name}",
                'task_id': self.id,
                'status': 'pending',
                'approver_id': self.verifier_id.id,
            })
            self.approval_id = approval.id
            self.requires_approval = True
            
            # 📧 Send notification
            self.message_post(
                body=f"✅ Approval đã được gán cho task bởi {self.env.user.name}",
                subject="Approval được gán"
            )
        else:
            raise exceptions.UserError("❌ Task này đã có approval!")

    def action_cancel_task(self):
        """❌ Cancel the task"""
        # 🔍 Validate transition
        self._validate_status_transition('canceled')
        
        self.write({'status': 'canceled'})
        
        # 📧 Send notification
        self.message_post(
            body=f"❌ Task đã bị hủy bởi {self.env.user.name}",
            subject="Task đã bị hủy"
        )

    def action_put_on_hold(self):
        """⏸️ Put task on hold"""
        # 🔍 Validate transition
        self._validate_status_transition('on-hold')
        
        self.write({'status': 'on-hold'})
        
        # 📧 Send notification
        self.message_post(
            body=f"⏸️ Task đã được tạm dừng bởi {self.env.user.name}",
            subject="Task tạm dừng"
        )

    def action_resume_task(self):
        """▶️ Resume task from on-hold"""
        if self.status != 'on-hold':
            raise exceptions.UserError("❌ Chỉ có thể tiếp tục task đang tạm dừng!")
        
        # Resume to previous logical state (usually in-progress)
        self.write({'status': 'in-progress'})
        
        # 📧 Send notification
        self.message_post(
            body=f"▶️ Task đã được tiếp tục bởi {self.env.user.name}",
            subject="Task được tiếp tục"
        )

    # ═══════════════════════════════════════════════════════════
    # ═                � RECORD LIFECYCLE METHODS              ═
    # ═══════════════════════════════════════════════════════════

    @api.model_create_multi
    def create(self, vals_list):
        """🆕 Create task with auto-generated code"""
        for vals in vals_list:
            if not vals.get('code'):
                vals['code'] = self.env['ir.sequence'].next_by_code('vnfield.task') or '/'
        return super().create(vals_list)

    # ═══════════════════════════════════════════════════════════
    # ═                �🔗 UTILITY METHODS                       ═
    # ═══════════════════════════════════════════════════════════

    def is_overdue(self):
        """🚨 Check if task is overdue"""
        if self.deadline:
            return fields.Datetime.now() > self.deadline and self.status not in ['completed', 'canceled']
        return False

    def get_hours_efficiency(self):
        """📊 Calculate task efficiency (estimated vs actual hours)"""
        if self.estimated_hours and self.actual_hours:
            return (self.estimated_hours / self.actual_hours) * 100
        return 0.0
