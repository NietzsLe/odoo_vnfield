# 🏗️ Project Model Documentation

## Tổng Quan Model

`vnfield.project` là core model cho việc quản lý dự án trong VNField system. Model này tích hợp đầy đủ workflow management, team collaboration, financial tracking và external integration.

## 📊 Model Structure

### Inheritance

```python
_name = "vnfield.project"
_description = "VN Field Project Management"
_inherit = ["mail.thread", "mail.activity.mixin"]
_order = "priority desc, create_date desc"
```

## 📋 Field Groups

### 🏷️ Basic Project Information

```python
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
```

### ⚡ Status & Priority

```python
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
```

### 📅 Timeline Fields

```python
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
```

### 💰 Financial Fields

```python
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
```

### 👥 Team Structure

```python
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
```

### 🏢 Contractor Relationships

```python
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
```

### 🔗 Project Relationships

```python
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
```

### 📈 Computed Fields

```python
progress = fields.Float(
    string="Progress (%)",
    compute="_compute_progress",
    store=True,
    help="Overall project completion percentage"
)

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
```

### 🌐 External Integration

```python
external_id = fields.Char(
    string="External ID",
    help="ID for mapping with external systems"
)

external_mapping_data = fields.Text(
    string="External Mapping Data",
    help="JSON data for external system mapping"
)
```

## 🔧 Computed Methods

### Progress Calculation

```python
@api.depends('task_ids.progress')
def _compute_progress(self):
    """💡 Calculate overall project progress based on tasks"""
    for project in self:
        if project.task_ids:
            total_progress = sum(project.task_ids.mapped('progress'))
            project.progress = total_progress / len(project.task_ids)
        else:
            project.progress = 0.0
```

### Cost Calculation

```python
@api.depends('task_ids')
def _compute_actual_cost(self):
    """💰 Calculate actual cost from tasks"""
    for project in self:
        # TODO: Implement based on task cost tracking
        project.actual_cost = 0.0
```

### Count Methods

```python
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
```

## 🔒 Validation Constraints

### Status Transition Validation

```python
@api.constrains('status')
def _check_status_transition(self):
    """🔒 Validate status transitions when status is changed directly"""
    # Prevents direct status field changes
    # Forces users to use action buttons
```

### Date Logic Validation

```python
@api.constrains('start_date', 'end_date', 'deadline')
def _check_project_dates(self):
    """📅 Validate project date logic"""
    # start_date ≤ end_date ≤ deadline
```

### Range Validations

```python
@api.constrains('progress')
def _check_progress_range(self):
    """📊 Validate progress percentage"""
    # 0% ≤ progress ≤ 100%

@api.constrains('budget', 'actual_cost')
def _check_budget_values(self):
    """💰 Validate budget and cost values"""
    # budget ≥ 0, actual_cost ≥ 0
```

## 🎯 Action Methods

### Workflow Actions

```python
def action_move_to_planning(self):
    """📋 Move project to planning phase"""
    # Validates name và description required
    # Transition: draft → planning

def action_start_project(self):
    """▶️ Start the project"""
    # Validates manager_id và project_owner_id required
    # Transition: draft/planning → in-progress
    # Auto-set start_date

def action_move_to_review(self):
    """🔍 Move project to review phase"""
    # Validates all tasks completed
    # Transition: in-progress → review

def action_complete_project(self):
    """✅ Complete the project"""
    # Validates all tasks completed + no pending approvals
    # Transition: in-progress/review → completed
    # Auto-set end_date, progress = 100%

def action_put_on_hold(self):
    """⏸️ Put project on hold"""
    # Transition: in-progress/planning → on-hold

def action_resume_project(self):
    """▶️ Resume project from on-hold"""
    # Transition: on-hold → in-progress

def action_cancel_project(self):
    """❌ Cancel the project"""
    # Warning về active tasks
    # Transition: any → canceled
```

## 🔗 Utility Methods

### Contractor Management

```python
def get_all_contractors(self):
    """🏢 Get all contractors (owner + subcontractors)"""
    contractors = self.env['vnfield.contractor']
    if self.project_owner_id:
        contractors |= self.project_owner_id
    contractors |= self.subcontractor_ids
    return contractors
```

### Status Checking

```python
def is_overdue(self):
    """🚨 Check if project is overdue"""
    if self.deadline:
        return fields.Date.today() > self.deadline and self.status not in ['completed', 'canceled']
    return False
```

### Data Export

```python
def to_dict(self, include_private=False):
    """📋 Convert project to dictionary for external systems"""
    # Returns project data as dictionary
    # Supports private data inclusion for internal use
```

## 📧 Notification System

Mỗi action method đều có automatic notification:

```python
self.message_post(
    body=f"🚀 Dự án đã được bắt đầu bởi {self.env.user.name}",
    subject="Dự án đã bắt đầu"
)
```

## 🔄 Business Rules

### Data Integrity

- **Delete Permission**: Chỉ có thể delete khi status = 'draft'
- **Required Fields**: manager_id, project_owner_id required khi start project
- **Task Dependencies**: Không thể complete project khi có incomplete tasks
- **Approval Dependencies**: Không thể complete khi có pending approvals

### Auto-calculations

- **Progress**: Tự động tính từ task progress
- **Dates**: Auto-set start_date khi start, end_date khi complete
- **Counts**: Auto-count tasks, approvals, members

### Tracking

- **Status Changes**: Tracked trong chatter
- **Important Fields**: name, manager_id, project_owner_id tracked
- **Audit Trail**: Full history của mọi thay đổi

---

_Document Version: 1.0_  
_Last Updated: July 17, 2025_  
_Author: GitHub Copilot Assistant_
