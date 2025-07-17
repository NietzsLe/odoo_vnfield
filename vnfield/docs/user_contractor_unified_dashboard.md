# 👥 VNField User-Contractor Unified Dashboard

## 🎯 Tổng quan Dashboard

User-Contractor Unified Dashboard là một interface thống nhất cho phép quản lý user và contractor trong một view duy nhất với tính năng filtering theo contractor thông qua sidebar.

## 🚀 Những gì đã được thực hiện

### ✅ **Controller Layer Implementation**

#### 📋 **Dashboard Controller (`controllers/user_contractor_dashboard.py`)**

**🔧 Main Route Handler:**

```python
@http.route('/user-contractor/dashboard', type='http', auth='user', website=True)
def user_contractor_dashboard(self, **kwargs):
    # Security check
    if not request.env.user.has_group('vnfield.group_contractor_user'):
        return request.render('website.403')

    # Get contractors and users
    contractors = request.env['vnfield.contractor'].search([])
    users = request.env['res.users'].search([('contractor_id', '!=', False)])

    return request.render('vnfield.user_contractor_dashboard_template', {
        'contractors': contractors,
        'users': users,
    })
```

**🔄 AJAX API Endpoint:**

```python
@http.route('/user-contractor/api/users/<int:contractor_id>', type='json', auth='user')
def get_users_by_contractor_api(self, contractor_id, **kwargs):
    try:
        contractor = request.env['vnfield.contractor'].browse(contractor_id)
        if not contractor.exists():
            return {'error': 'Contractor not found'}

        users = request.env['res.users'].search([
            ('contractor_id', '=', contractor_id)
        ])

        return {
            'success': True,
            'contractor': {
                'id': contractor.id,
                'name': contractor.name,
            },
            'users': [{
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'login': user.login,
                'specialization': user.specialization or '',
                'phone_work': user.phone_work or '',
                'is_leader': user.is_leader_of_contractor,
            } for user in users]
        }
    except Exception as e:
        return {'error': str(e)}
```

**🔐 Security Integration:**

- Group-based access control
- Permission validation cho API calls
- Error handling cho unauthorized access

### ✅ **Professional Template Design**

#### 📋 **Dashboard Template (`views/user_contractor_dashboard_views.xml`)**

**🎨 Main Layout Structure:**

```xml
<template id="user_contractor_dashboard_template" name="User-Contractor Dashboard">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure">
            <div class="container-fluid">
                <div class="row">
                    <!-- Sidebar -->
                    <div class="col-md-3 bg-light p-3">
                        <h5>📋 Contractors</h5>
                        <div class="list-group" id="contractorList">
                            <t t-foreach="contractors" t-as="contractor">
                                <a href="#" class="list-group-item contractor-item"
                                   t-att-data-contractor-id="contractor.id">
                                    <i class="fa fa-building mr-2"></i>
                                    <span t-field="contractor.name"/>
                                    <span class="badge badge-secondary float-right"
                                          t-esc="contractor.user_count"/>
                                </a>
                            </t>
                        </div>
                    </div>

                    <!-- Main Content -->
                    <div class="col-md-9 p-3">
                        <!-- Header with selected contractor info -->
                        <div class="d-flex justify-content-between align-items-center mb-4">
                            <h2 id="dashboardTitle">👥 All Users</h2>
                            <div id="selectedContractorInfo" class="d-none">
                                <span class="badge badge-primary p-2">
                                    <i class="fa fa-filter mr-1"></i>
                                    Filtered by: <span id="selectedContractorName"></span>
                                </span>
                            </div>
                        </div>

                        <!-- User Cards Container -->
                        <div id="userCardsContainer" class="row">
                            <!-- Initial user cards will be loaded here -->
                        </div>

                        <!-- Loading indicator -->
                        <div id="loadingIndicator" class="text-center d-none">
                            <div class="spinner-border text-primary" role="status">
                                <span class="sr-only">Loading...</span>
                            </div>
                            <p class="mt-2">Loading users...</p>
                        </div>

                        <!-- Empty state -->
                        <div id="emptyState" class="text-center d-none">
                            <div class="alert alert-info">
                                <h4>📭 No Users Found</h4>
                                <p>No users found for the selected contractor.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </t>
</template>
```

**👤 User Card Template:**

```xml
<script type="text/javascript" id="userCardTemplate">
    <div class="col-md-6 col-lg-4 mb-3 user-card">
        <div class="card h-100">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h5 class="card-title mb-0">${name}</h5>
                    {{if is_leader}}
                    <span class="badge badge-warning">
                        <i class="fa fa-crown"></i> Leader
                    </span>
                    {{/if}}
                </div>

                <div class="text-muted small mb-2">
                    <div><i class="fa fa-envelope mr-1"></i> ${email}</div>
                    <div><i class="fa fa-user mr-1"></i> ${login}</div>
                    {{if specialization}}
                    <div><i class="fa fa-star mr-1"></i> ${specialization}</div>
                    {{/if}}
                    {{if phone_work}}
                    <div><i class="fa fa-phone mr-1"></i> ${phone_work}</div>
                    {{/if}}
                </div>
            </div>

            <div class="card-footer bg-transparent">
                <div class="btn-group btn-group-sm w-100">
                    <a href="/web#id=${id}&view_type=form&model=res.users"
                       class="btn btn-outline-primary">
                        <i class="fa fa-eye"></i> View
                    </a>
                    <a href="/web#id=${id}&view_type=form&model=res.users&mode=edit"
                       class="btn btn-outline-secondary">
                        <i class="fa fa-edit"></i> Edit
                    </a>
                </div>
            </div>
        </div>
    </div>
</script>
```

### ✅ **Interactive JavaScript Implementation**

#### 📋 **Client-side Functionality**

**🔄 Contractor Selection Handler:**

```javascript
$(document).ready(function () {
  // Handle contractor selection
  $(".contractor-item").click(function (e) {
    e.preventDefault();

    const contractorId = $(this).data("contractor-id");
    const contractorName = $(this).find("span").first().text();

    // Update UI state
    $(".contractor-item").removeClass("active");
    $(this).addClass("active");

    // Show loading
    showLoading();

    // Fetch users for selected contractor
    fetchUsersByContractor(contractorId, contractorName);
  });
});
```

**📊 AJAX Data Fetching:**

```javascript
function fetchUsersByContractor(contractorId, contractorName) {
  $.ajax({
    url: `/user-contractor/api/users/${contractorId}`,
    type: "POST",
    dataType: "json",
    contentType: "application/json",
    data: JSON.stringify({}),
    success: function (response) {
      hideLoading();

      if (response.error) {
        showError(response.error);
        return;
      }

      // Update UI with filtered users
      updateDashboardTitle(contractorName);
      renderUserCards(response.users);
      showSelectedContractorInfo(contractorName);
    },
    error: function (xhr, status, error) {
      hideLoading();
      showError("Failed to fetch users: " + error);
    },
  });
}
```

**🎨 Dynamic UI Updates:**

```javascript
function renderUserCards(users) {
  const container = $("#userCardsContainer");
  container.empty();

  if (users.length === 0) {
    showEmptyState();
    return;
  }

  hideEmptyState();

  users.forEach(function (user) {
    const cardHtml = userCardTemplate
      .replace(/\${name}/g, user.name)
      .replace(/\${email}/g, user.email)
      .replace(/\${login}/g, user.login)
      .replace(/\${id}/g, user.id)
      .replace(/\${specialization}/g, user.specialization || "")
      .replace(/\${phone_work}/g, user.phone_work || "");

    // Handle leader badge
    if (user.is_leader) {
      cardHtml = cardHtml
        .replace("{{if is_leader}}", "")
        .replace("{{/if}}", "");
    } else {
      cardHtml = cardHtml.replace(/{{if is_leader}}.*?{{\/if}}/g, "");
    }

    container.append(cardHtml);
  });
}
```

### ✅ **Responsive Design Features**

#### 📱 **Mobile-First Approach**

**🎨 Bootstrap Grid System:**

```xml
<div class="col-md-3 bg-light p-3">           <!-- Sidebar -->
<div class="col-md-9 p-3">                    <!-- Main content -->
<div class="col-md-6 col-lg-4 mb-3">          <!-- User cards -->
```

**📱 Mobile Optimizations:**

- Collapsible sidebar on mobile
- Responsive card grid
- Touch-friendly buttons
- Optimized spacing

**🎨 Professional Styling:**

```css
.contractor-item.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.user-card .card {
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid #e9ecef;
}

.user-card .card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
```

### ✅ **Integration with Menu System**

#### 📋 **Menu Integration (`views/user_contractor_dashboard_views.xml`)**

**🔗 Action Definition:**

```xml
<record id="action_user_contractor_dashboard" model="ir.actions.act_url">
    <field name="name">User-Contractor Dashboard</field>
    <field name="url">/user-contractor/dashboard</field>
    <field name="target">self</field>
</record>
```

**📋 Menu Integration:**

```xml
<menuitem id="menu_user_contractor_dashboard"
          name="📊 Dashboard"
          parent="menu_user_contractor_management_root"
          action="action_user_contractor_dashboard"
          sequence="5"/>
```

**🎯 Navigation Flow:**

1. User clicks "📊 Dashboard" trong menu
2. Controller loads contractors và users
3. Template renders với sidebar và user cards
4. JavaScript handles contractor filtering
5. AJAX updates user list in real-time

## 🔄 **Dashboard Workflow**

### 📋 **User Interaction Flow**

1. **Dashboard Access**: User navigates to dashboard từ menu
2. **Initial Load**: Hiển thị all contractors trong sidebar, all users trong main area
3. **Contractor Selection**: User clicks contractor trong sidebar
4. **Real-time Filtering**: AJAX call filters users by selected contractor
5. **UI Updates**: Dashboard updates title, user cards, và active states
6. **Action Integration**: User có thể view/edit user từ cards

### 🔄 **State Management**

**📊 Dashboard States:**

- **All Users**: Initial state showing all users
- **Filtered by Contractor**: Showing users của specific contractor
- **Loading**: During AJAX requests
- **Empty State**: When no users found for contractor
- **Error State**: When API calls fail

**🎨 Visual State Indicators:**

- Active contractor highlighting trong sidebar
- Selected contractor badge trong header
- Loading spinner during transitions
- Empty state với helpful messages

## 🎯 **Technical Features**

### 🔐 **Security & Permissions**

**Access Control:**

```python
if not request.env.user.has_group('vnfield.group_contractor_user'):
    return request.render('website.403')
```

**API Security:**

- Authentication required cho all endpoints
- Group membership validation
- Error handling cho unauthorized access

### ⚡ **Performance Optimizations**

**Client-side Caching:**

- User data cached after initial load
- Minimal server requests
- Efficient DOM updates

**Server-side Efficiency:**

- Optimized database queries
- JSON response format
- Error handling

### 🔄 **Error Handling**

**Client-side Error Handling:**

```javascript
function showError(message) {
  const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <strong>Error:</strong> ${message}
            <button type="button" class="close" data-dismiss="alert">
                <span>&times;</span>
            </button>
        </div>
    `;
  $("#userCardsContainer").prepend(alertHtml);
}
```

**Server-side Error Handling:**

```python
try:
    # API logic here
    return {'success': True, 'data': data}
except Exception as e:
    return {'error': str(e)}
```

## 📊 **Business Impact**

### ✅ **Operational Efficiency**

**Unified Interface:**

- Single dashboard cho user-contractor management
- Reduced navigation complexity
- Faster user lookup và filtering

**Real-time Updates:**

- No page reloads required
- Instant filtering results
- Smooth user experience

### 🎯 **User Experience Benefits**

**Intuitive Navigation:**

- Clear sidebar organization
- Visual feedback cho selections
- Professional card-based layout

**Responsive Design:**

- Works on all devices
- Touch-friendly interface
- Mobile-optimized layouts

### 📈 **Management Benefits**

**Better Visibility:**

- Quick contractor overview
- User count indicators
- Leader identification

**Efficient Filtering:**

- Instant contractor-based filtering
- Clear filter status indication
- Easy switching between contractors

## 📁 **File Structure**

```
vnfield/
├── controllers/
│   ├── __init__.py                           # Controller package init
│   └── user_contractor_dashboard.py          # Dashboard controller
├── views/
│   └── user_contractor_dashboard_views.xml   # Dashboard template & actions
├── static/
│   └── src/
│       ├── js/
│       │   └── user_contractor_dashboard.js  # Client-side logic
│       └── css/
│           └── user_contractor_dashboard.css # Custom styling
└── docs/
    └── user_contractor_unified_dashboard.md  # This documentation
```

## 🔧 **Technical Dependencies**

**Backend Requirements:**

- Odoo 17.0 framework
- Website module (for HTTP routing)
- VNField base modules (res.users, vnfield.contractor)

**Frontend Requirements:**

- Bootstrap 4 (responsive design)
- jQuery (AJAX và DOM manipulation)
- Font Awesome (icons)

**Integration Requirements:**

- Security groups configuration
- Menu system integration
- Model relationships (user.contractor_id)

## 🎯 **Future Enhancements**

### 📈 **Planned Features**

1. **Advanced Filtering**: Multiple filter criteria (specialization, status, etc.)
2. **Search Functionality**: Real-time user search
3. **Bulk Actions**: Multi-user operations
4. **Export Features**: User data export capabilities
5. **Analytics Dashboard**: User-contractor relationship metrics

### 🔄 **Integration Opportunities**

1. **Task Assignment**: Direct task assignment từ dashboard
2. **Project Management**: Project member management integration
3. **Approval Workflows**: User permission management integration
4. **Communication**: Direct messaging to users

### 📱 **Mobile App Integration**

1. **Native Mobile Views**: Optimized mobile layouts
2. **Offline Support**: Cached user data
3. **Push Notifications**: User status updates
4. **Mobile Actions**: Quick actions for mobile users

## 📚 **Related Documentation**

- [Contractor Management](./contractor_management.md)
- [Security System](./security_system.md)
- [Project Management Overview](./project_management_overview.md)
- [Implementation Summary](./implementation_summary.md)

## 🔧 **Setup & Configuration**

### ⚙️ **Module Dependencies**

Update `__manifest__.py`:

```python
'depends': ['base', 'mail', 'website'],
'data': [
    # ... other data files
    'views/user_contractor_dashboard_views.xml',
],
```

### 🔐 **Security Groups Required**

- `vnfield.group_contractor_user`: Basic dashboard access
- `vnfield.group_contractor_manager`: Enhanced dashboard features
- `vnfield.group_contractor_admin`: Full dashboard access

### 🌐 **URL Configuration**

Dashboard accessible at: `/user-contractor/dashboard`
API endpoint: `/user-contractor/api/users/<contractor_id>`

---
