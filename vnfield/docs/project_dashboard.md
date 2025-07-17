# 📊 Project Dashboard Documentation

## Tổng Quan Dashboard

Project Dashboard là một interface tập trung cho việc quản lý project theo kiểu project-centric. Khi user chọn một project cụ thể, dashboard sẽ filter và hiển thị chỉ những data liên quan đến project đó.

## 🎯 Dashboard Features

### Left Sidebar - Project Selection

- **Chức năng**: Danh sách tất cả projects với quick selection
- **Hiển thị**:
  - Project name và code
  - Status badge với color coding
  - Progress percentage
- **Interaction**: Click để switch giữa các projects
- **Active State**: Highlight project đang được chọn

### Main Content Area

- **Project Header**: Tên, mô tả, status của project được chọn
- **Key Metrics Cards**: Progress %, Task count, Member count, Approval count
- **Content Sections**: 4 main sections với project-specific data

## 📋 Dashboard Sections

### 1. 👥 Team Members Section

- **Hiển thị**: Danh sách members của project được chọn
- **Thông tin**: Avatar, name, email
- **Actions**: "Manage Team" button → redirect to project form
- **Empty State**: "No team members assigned"

### 2. 🏢 Contractors Section

- **Hiển thị**: Project owner + subcontractors của project được chọn
- **Thông tin**: Company icon, name, contractor type
- **Actions**: "Manage Contractors" button → redirect to project form
- **Empty State**: "No contractors assigned"

### 3. 📋 Recent Tasks Section

- **Hiển thị**: 5 tasks gần nhất của project được chọn
- **Thông tin**: Task name, assignee, status badge, progress %
- **Actions**: "View All Tasks" button → redirect to task kanban view
- **Empty State**: "No tasks found"

### 4. ✅ Recent Approvals Section

- **Hiển thị**: 5 approvals gần nhất của project được chọn
- **Thông tin**: Approval name, status badge, creation date
- **Actions**: "View All Approvals" button → redirect to approval view
- **Empty State**: "No approvals found"

## 🔗 Navigation và Integration

### Menu Structure

```
Projects (Top Level Menu)
├── Dashboard (Default - opens /projects/dashboard)
└── Manage Projects (Traditional views - kanban/list/form)
```

### URL Structure

- **Dashboard Base**: `/projects/dashboard`
- **Project Selection**: `/projects/dashboard?project_id=123`

### Integration Links

- **"Edit Project"**: Redirect to project form view
- **"New Project"**: Redirect to project creation form
- **Section Action Buttons**: Redirect to relevant detail views

## 🎨 UI Design và Styling

### CSS Framework

- **Bootstrap**: Grid system và components
- **Custom CSS**: Project-specific styling
- **Responsive**: Adapts to different screen sizes

### Color Scheme

- **Primary**: #007bff (Blue)
- **Success**: Green badges for completed status
- **Warning**: Yellow badges for on-hold status
- **Danger**: Red badges for canceled/overdue
- **Info**: Blue badges for in-progress status

### Visual Elements

- **Metric Cards**: Elevated cards với shadows
- **Status Badges**: Color-coded status indicators
- **Icons**: Font Awesome icons cho visual context
- **Progress Bars**: Visual progress representation

## 🔧 Technical Implementation

### Controller Logic

```python
@http.route('/projects/dashboard', type='http', auth='user', website=True)
def project_dashboard(self, project_id=None, **kwargs):
    # Get all projects user has access to
    # Get selected project (first if none selected)
    # Load project-specific data (members, contractors, tasks, approvals)
    # Render template với dashboard data
```

### Template Structure

```xml
<template id="project_dashboard_template">
    <div class="container-fluid">
        <div class="row">
            <div class="col-3 project-sidebar">
                <!-- Project selection sidebar -->
            </div>
            <div class="col-9 dashboard-main">
                <!-- Main dashboard content -->
            </div>
        </div>
    </div>
</template>
```

### Data Flow

1. **Controller**: Load projects và selected project data
2. **Template**: Render với project-specific filtering
3. **JavaScript**: Handle project selection clicks
4. **Backend**: Filter data theo selected project

## 📱 Responsive Design

### Desktop (≥992px)

- **Sidebar**: 3 columns width
- **Main Content**: 9 columns width
- **Grid**: 2x2 metric cards

### Tablet (768px-991px)

- **Sidebar**: Collapsible menu
- **Main Content**: Full width
- **Grid**: 2x2 metric cards

### Mobile (≤767px)

- **Sidebar**: Hidden by default, toggle menu
- **Main Content**: Full width
- **Grid**: 1x4 stacked cards

## 🔄 Project-Centric Filtering Logic

### Selection Process

1. User clicks project trong sidebar
2. URL updates với `project_id` parameter
3. Controller reloads page với selected project data
4. Dashboard shows filtered data cho selected project only

### Data Filtering

```python
# Controller logic
if selected_project:
    dashboard_data.update({
        'members': selected_project.member_ids,
        'contractors': selected_project.get_all_contractors(),
        'tasks': selected_project.task_ids,
        'approvals': selected_project.approval_ids
    })
```

## 🚀 Performance Considerations

### Data Loading

- **Lazy Loading**: Chỉ load data cho selected project
- **Caching**: Browser caching cho static assets
- **Minimal Queries**: Efficient ORM queries

### User Experience

- **Fast Navigation**: Quick project switching
- **Visual Feedback**: Loading states và transitions
- **Error Handling**: Graceful fallbacks

## 📊 Empty States

### No Projects

- **Message**: "No Projects Found"
- **Action**: "Create Project" button
- **Icon**: Large folder icon

### No Selected Project

- **Message**: Instruction to select a project
- **Visual**: Placeholder content

### No Data in Sections

- **Customized Messages**: Per section empty states
- **Action Buttons**: Direct links to add data

---

_Document Version: 1.0_  
_Last Updated: July 17, 2025_  
_Author: GitHub Copilot Assistant_
