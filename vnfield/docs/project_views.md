# 🎨 Project Views Documentation

## Tổng Quan Views

VNField Project Management System cung cấp 4 main views cho project management: List, Form, Kanban và Dashboard. Mỗi view được thiết kế cho mục đích sử dụng cụ thể với UI/UX tối ưu.

## 📋 List View (Tree View)

### Tính Năng Chính

- **Status Decorations**: Color coding theo trạng thái project
- **Optional Columns**: Flexible column visibility
- **Progressive Disclosure**: Core info hiển thị, details optional

### Field Layout

```xml
<!-- 🏷️ Basic Information -->
<field name="name" string="Project Name"/>
<field name="code" string="Code" optional="show"/>
<field name="manager_id" string="Manager" widget="many2one_avatar_user"/>
<field name="project_owner_id" string="Owner"/>

<!-- ⚡ Status & Priority -->
<field name="status" string="Status" widget="badge"/>
<field name="priority" string="Priority" widget="priority"/>

<!-- 📅 Timeline -->
<field name="start_date" string="Start Date" optional="show"/>
<field name="deadline" string="Deadline" optional="show"/>

<!-- 📊 Progress & Metrics -->
<field name="progress" string="Progress" widget="progressbar" optional="show"/>
<field name="task_count" string="Tasks" optional="show"/>
<field name="member_count" string="Members" optional="hide"/>
```

### Status Decorations

```xml
<tree decoration-success="status=='completed'"
      decoration-info="status=='in-progress'"
      decoration-warning="status=='on-hold'"
      decoration-danger="status=='canceled'">
```

## 📝 Form View

### Header Section

- **Workflow Buttons**: Status-specific action buttons
- **Status Bar**: Visual workflow progression
- **Conditional Visibility**: Buttons appear based on current status

### Button Layout

```xml
<!-- Planning Phase -->
<button name="action_move_to_planning" type="object"
        string="Start Planning" class="btn-info"
        invisible="status != 'draft'"/>

<!-- Execution Phase -->
<button name="action_start_project" type="object"
        string="Start Project" class="btn-primary"
        invisible="status not in ['draft', 'planning']"/>

<!-- Review Phase -->
<button name="action_move_to_review" type="object"
        string="Move to Review" class="btn-info"
        invisible="status != 'in-progress'"/>
```

### Content Sections

#### 🏷️ Project Title

- **Large Title**: H1 styling cho project name
- **Subtitle**: H3 styling cho project code
- **Placeholders**: Helpful placeholder text

#### 🎯 Key Metrics Cards

```xml
<div class="row mt16 o_settings_container">
    <div class="col-12 col-lg-6 o_setting_box">
        <div class="o_field_widget o_stat_info">
            <span class="o_stat_value">
                <field name="progress" widget="percentage"/>
            </span>
            <span class="o_stat_text">Progress</span>
        </div>
    </div>
</div>
```

#### 📋 Information Groups

- **Project Information**: Priority, Manager, Owner
- **Timeline & Deadlines**: Start, End, Deadline dates
- **Financial Information**: Budget, Actual cost với currency

#### 📑 Tabbed Sections

1. **👥 Team**: Members và contractors management
2. **📋 Tasks**: Inline task editing với tree view
3. **✅ Approvals**: Approval list với status
4. **🌐 Integration**: External ID và mapping data

### Chatter Integration

```xml
<div class="oe_chatter">
    <field name="message_follower_ids" options="{'post_refresh':True}"/>
    <field name="activity_ids"/>
    <field name="message_ids"/>
</div>
```

## 🎯 Kanban View

### Grouping Strategy

- **Default Grouping**: By status cho workflow visualization
- **Quick Create**: Disabled để force proper data entry

### Card Design

- **Header**: Project name, code, priority badge
- **Progress Bar**: Visual progress indicator
- **Team Info**: Manager và owner information
- **Timeline**: Deadline với overdue detection
- **Budget**: Financial information display
- **Team Size**: Member count indicator

### Status-Specific Actions

```xml
<!-- Draft Status -->
<a name="action_move_to_planning" type="object"
   t-if="record.status.raw_value == 'draft'"
   class="btn btn-info btn-sm">
    <i class="fa fa-edit"/> Plan
</a>

<!-- Planning Status -->
<a name="action_start_project" type="object"
   t-if="record.status.raw_value == 'planning'"
   class="btn btn-primary btn-sm">
    <i class="fa fa-play"/> Start
</a>
```

### Visual Indicators

- **Overdue Badge**: Red badge khi past deadline
- **Status Colors**: Color-coded status representation
- **Progress Visualization**: Progress bar trong card

## 🔍 Search View

### Search Fields

```xml
<field name="name" string="Project Name"/>
<field name="code" string="Project Code"/>
<field name="manager_id" string="Manager"/>
<field name="project_owner_id" string="Owner"/>
```

### Quick Filters

```xml
<filter string="My Projects" name="my_projects"
        domain="[('manager_id', '=', uid)]"/>
<filter string="In Progress" name="in_progress"
        domain="[('status', '=', 'in-progress')]"/>
<filter string="Completed" name="completed"
        domain="[('status', '=', 'completed')]"/>
<filter string="Overdue" name="overdue"
        domain="[('deadline', '<', context_today()), ('status', 'not in', ['completed', 'canceled'])]"/>
<filter string="High Priority" name="high_priority"
        domain="[('priority', 'in', ['2', '3'])]"/>
```

### Group By Options

```xml
<filter string="Status" name="group_status" context="{'group_by': 'status'}"/>
<filter string="Manager" name="group_manager" context="{'group_by': 'manager_id'}"/>
<filter string="Owner" name="group_owner" context="{'group_by': 'project_owner_id'}"/>
<filter string="Priority" name="group_priority" context="{'group_by': 'priority'}"/>
<filter string="Start Date" name="group_start_date" context="{'group_by': 'start_date'}"/>
```

## 📊 Dashboard View

### Layout Structure

- **Left Sidebar**: Project selection (25% width)
- **Main Content**: Project details (75% width)
- **Responsive**: Adapts to screen size

### Project Sidebar

```xml
<div class="col-3 project-sidebar">
    <h5><i class="fa fa-folder-open"></i> Projects</h5>
    <!-- Project list với status badges -->
    <!-- Active state highlighting -->
    <!-- New project button -->
</div>
```

### Content Sections

- **Project Header**: Name, description, status
- **Key Metrics**: Progress, tasks, members, approvals
- **Team Members**: Avatar display với management links
- **Contractors**: Company info với type details
- **Recent Tasks**: Latest 5 tasks với status
- **Recent Approvals**: Latest 5 approvals với dates

## 🎨 Styling và Visual Design

### Color Scheme

```css
.project-sidebar {
  background: #f8f9fa;
  border-right: 1px solid #dee2e6;
}

.project-item.active {
  background-color: #007bff;
  color: white;
}

.metric-card {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
```

### Widget Usage

- **Priority**: `widget="priority"` cho star rating
- **Progress**: `widget="progressbar"` cho visual progress
- **Status**: `widget="badge"` cho colored status
- **Avatar**: `widget="many2one_avatar_user"` cho user photos
- **Monetary**: `widget="monetary"` cho currency formatting

### Icons

- **Font Awesome**: Consistent icon usage throughout
- **Contextual Icons**: Icons match section content
- **Action Icons**: Clear visual cues cho buttons

## 📱 Responsive Considerations

### Mobile Adaptations

- **Sidebar**: Collapsible trên mobile
- **Cards**: Stack vertically
- **Buttons**: Touch-friendly sizing

### Tablet Adaptations

- **Grid Layout**: 2-column layout cho metrics
- **Navigation**: Touch-optimized interactions

## 🔧 Technical Implementation

### View Inheritance

- **Standard Odoo**: Uses standard Odoo view architecture
- **Custom Widgets**: Leverages built-in widgets
- **Extensions**: Custom CSS và JavaScript khi cần

### Performance

- **Lazy Loading**: Dashboard chỉ load selected project data
- **Efficient Queries**: Optimized database queries
- **Caching**: Browser caching cho static assets

### Accessibility

- **ARIA Labels**: Screen reader support
- **Keyboard Navigation**: Full keyboard accessibility
- **Color Contrast**: Meets accessibility standards

---
