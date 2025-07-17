# 🏢 Contractor Management Documentation

## 📋 **Tổng quan**

Hệ thống quản lý nhà thầu (Contractor Management) trong VNField cung cấp khả năng quản lý thông tin, profile, và mối quan hệ của các contractor tham gia vào các dự án. Hệ thống hỗ trợ tracking performance, specialization và integration với user management.

---

## 🎯 **Mục tiêu**

### **📊 Business Goals**

- ✅ **Centralized Management**: Quản lý tập trung thông tin contractor
- ✅ **Performance Tracking**: Theo dõi rating và hoạt động của contractor
- ✅ **Specialization Management**: Quản lý chuyên môn và lĩnh vực
- ✅ **User Integration**: Liên kết contractor với user accounts
- ✅ **Project Relationships**: Quản lý contractor participation trong projects

### **🔧 Technical Goals**

- ✅ **Flexible Data Model**: Cấu trúc dữ liệu linh hoạt và mở rộng được
- ✅ **API Integration**: Hỗ trợ integration với external systems
- ✅ **Performance Optimization**: Query optimization cho large datasets
- ✅ **Data Integrity**: Đảm bảo tính nhất quán của dữ liệu

---

## 🏗️ **Data Model Architecture**

### **📊 Core Entity: vnfield.contractor**

```python
class Contractor(models.Model):
    _name = "vnfield.contractor"
    _description = "VN Field Contractor"
```

### **🔧 Field Categories**

#### **1. 🏷️ Basic Information**

```python
# ─────────────── 🏷️ BASIC INFORMATION ───────────────
name = fields.Char(string="Name", required=True)
phone = fields.Char(string="Phone")
email = fields.Char(string="Email")
address = fields.Char(string="Address")
active = fields.Boolean(default=True)
```

**Purpose**: Thông tin cơ bản để identify và contact contractor

#### **2. 🎯 Contractor Profile**

```python
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
```

**Purpose**: Tracking performance, specialization và activity patterns

#### **3. 🔗 Relationships**

```python
# ─────────────── 🔗 RELATIONSHIPS ───────────────
user_ids = fields.One2many("res.users", "contractor_ids", string="Users")
project_ids = fields.Many2many(
    "vnfield.project",
    "contractor_project_rel",
    "contractor_id",
    "project_id",
    string="Projects",
)
```

**Purpose**: Liên kết với users và projects để quản lý relationships

---

## 💻 **Implementation Details**

### **🔧 Core Methods**

#### **1. Rating Management**

```python
def update_rating(self, new_rating):
    """
    ⭐ Update contractor rating with validation
    """
    if 0 <= new_rating <= 5:
        self.rating = new_rating
    else:
        raise ValueError("Rating must be between 0 and 5")
```

**Features**:

- ✅ Validation: Rating từ 0-5
- ✅ Error Handling: Raise exception cho invalid values
- ✅ Business Logic: Encapsulated rating logic

#### **2. Activity Tracking**

```python
def update_last_activity(self):
    """
    🕒 Update last activity timestamp
    """
    self.last_activity = fields.Datetime.now()
```

**Features**:

- ✅ Automatic Timestamp: Set current datetime
- ✅ Activity Monitoring: Track contractor engagement
- ✅ Simple API: Easy to call from other methods

#### **3. Status Check**

```python
def is_active_contractor(self):
    """
    ✅ Check if contractor is active and available
    """
    return self.active and bool(self.name)
```

**Features**:

- ✅ Business Logic: Combine active status và name validation
- ✅ Boolean Return: Easy integration với business logic
- ✅ Defensive Programming: Handle edge cases

### **🔍 Search & Filter Methods**

#### **1. Search by Type**

```python
@api.model
def get_contractors_by_type(self, contractor_type):
    """
    🔍 Get contractors filtered by type
    """
    return self.search([
        ('contractor_type', '=', contractor_type),
        ('active', '=', True)
    ])
```

#### **2. Search by Specialization**

```python
@api.model
def get_contractors_by_specialization(self, specialization):
    """
    🎯 Get contractors by specialization
    """
    return self.search([
        ('specialization', 'ilike', specialization),
        ('active', '=', True)
    ])
```

**Features**:

- ✅ **Model-level Methods**: Accessible từ any context
- ✅ **Flexible Search**: Support partial matching với ilike
- ✅ **Active Filter**: Chỉ return active contractors
- ✅ **Reusable**: Can be called từ other methods hoặc external APIs

---

## 🎨 **UI Integration**

### **📱 Form View Features**

#### **1. Contact Information Section**

```xml
<group name="contact_info" string="Contact Information">
    <field name="name"/>
    <field name="phone"/>
    <field name="email" widget="email"/>
    <field name="address"/>
</group>
```

#### **2. Professional Profile Section**

```xml
<group name="profile" string="Professional Profile">
    <field name="specialization"/>
    <field name="rating" widget="priority"/>
    <field name="last_activity" readonly="1"/>
    <field name="active"/>
</group>
```

#### **3. Relationships Section**

```xml
<notebook>
    <page string="Users" name="users">
        <field name="user_ids"/>
    </page>
    <page string="Projects" name="projects">
        <field name="project_ids"/>
    </page>
</notebook>
```

### **📋 List View Features**

#### **Basic Information Display**

```xml
<tree string="Contractors">
    <field name="name"/>
    <field name="specialization"/>
    <field name="rating" widget="priority"/>
    <field name="phone"/>
    <field name="email"/>
    <field name="active"/>
</tree>
```

### **🔍 Search View Features**

#### **Search Filters**

```xml
<search string="Contractor Search">
    <field name="name"/>
    <field name="specialization"/>
    <field name="email"/>

    <filter name="active" string="Active" domain="[('active','=',True)]"/>
    <filter name="rated" string="Rated" domain="[('rating','>',0)]"/>

    <group expand="0" string="Group By">
        <filter string="Specialization" name="specialization" context="{'group_by':'specialization'}"/>
        <filter string="Rating" name="rating" context="{'group_by':'rating'}"/>
    </group>
</search>
```

---

## 🔗 **Integration Patterns**

### **👥 User Management Integration**

#### **1. User-Contractor Relationship**

```python
# res.users extension
contractor_ids = fields.Many2many(
    'vnfield.contractor',
    'user_contractor_rel',
    'user_id',
    'contractor_id',
    string='Associated Contractors'
)
```

#### **2. Context-based Access**

```python
def get_user_contractors(self, user_id):
    """Get contractors associated with specific user"""
    user = self.env['res.users'].browse(user_id)
    return user.contractor_ids
```

### **🏗️ Project Integration**

#### **1. Project-Contractor Relationship**

```python
# Many2many relationship với projects
project_ids = fields.Many2many(
    "vnfield.project",
    "contractor_project_rel",
    "contractor_id",
    "project_id",
    string="Projects"
)
```

#### **2. Project Assignment Methods**

```python
def assign_to_project(self, project_id):
    """Assign contractor to project"""
    project = self.env['vnfield.project'].browse(project_id)
    project.contractor_ids = [(4, self.id)]
    self.update_last_activity()
```

### **📋 Task Integration**

#### **1. Task Assignment Logic**

```python
def get_available_contractors(self, specialization=None):
    """Get contractors available for task assignment"""
    domain = [('active', '=', True)]
    if specialization:
        domain.append(('specialization', 'ilike', specialization))
    return self.search(domain)
```

---

## 📊 **Performance Features**

### **⭐ Rating System**

#### **1. Rating Scale**

- **5.0**: Excellent performance
- **4.0**: Good performance
- **3.0**: Average performance
- **2.0**: Below average
- **1.0**: Poor performance
- **0.0**: No rating yet

#### **2. Rating Updates**

```python
def calculate_average_rating(self):
    """Calculate average rating from project feedback"""
    # Implementation sẽ tính average từ project ratings
    pass

def update_rating_from_project(self, project_rating):
    """Update rating based on project completion"""
    # Weighted average với existing rating
    pass
```

### **📈 Activity Tracking**

#### **1. Activity Patterns**

```python
def get_activity_summary(self, days=30):
    """Get contractor activity trong N days"""
    # Return summary of:
    # - Projects worked on
    # - Tasks completed
    # - Average response time
    pass
```

#### **2. Performance Metrics**

```python
def get_performance_metrics(self):
    """Get comprehensive performance data"""
    return {
        'rating': self.rating,
        'projects_count': len(self.project_ids),
        'active_status': self.active,
        'last_activity': self.last_activity,
        'specialization': self.specialization
    }
```

---

## 🔒 **Security Integration**

### **🛡️ Access Control**

#### **1. Record Rules**

```xml
<!-- Users can only see contractors in their projects -->
<record id="rule_contractor_user_projects" model="ir.rule">
    <field name="name">User Project Contractors</field>
    <field name="model_id" ref="model_vnfield_contractor"/>
    <field name="groups" eval="[(4, ref('group_vnfield_user'))]"/>
    <field name="domain_force">[
        ('project_ids.member_ids', 'in', user.id)
    ]</field>
</record>
```

#### **2. Field-level Security**

```python
# Sensitive fields có thể restrict
rating = fields.Float(
    string="Rating",
    groups="vnfield.group_vnfield_manager,vnfield.group_vnfield_admin"
)
```

### **🔐 Data Privacy**

#### **1. Personal Information Protection**

- Email và phone chỉ visible cho authorized users
- Address information restricted theo business need
- Rating information chỉ manager+ mới xem được

#### **2. Audit Trail**

```python
_inherit = ["mail.thread", "mail.activity.mixin"]

# Track important changes
name = fields.Char(tracking=True)
rating = fields.Float(tracking=True)
specialization = fields.Char(tracking=True)
```

---

## 🧪 **Testing Strategy**

### **✅ Unit Tests**

#### **1. Basic CRUD Operations**

```python
def test_contractor_creation(self):
    contractor = self.env['vnfield.contractor'].create({
        'name': 'Test Contractor',
        'email': 'test@contractor.com',
        'specialization': 'Construction'
    })
    self.assertTrue(contractor.active)
    self.assertEqual(contractor.name, 'Test Contractor')
```

#### **2. Rating Validation**

```python
def test_rating_validation(self):
    contractor = self.create_test_contractor()

    # Valid rating
    contractor.update_rating(4.5)
    self.assertEqual(contractor.rating, 4.5)

    # Invalid rating
    with self.assertRaises(ValueError):
        contractor.update_rating(6.0)
```

#### **3. Search Methods**

```python
def test_search_by_specialization(self):
    # Create test contractors
    contractor1 = self.create_contractor('Construction')
    contractor2 = self.create_contractor('Electrical')

    # Search
    results = self.env['vnfield.contractor'].get_contractors_by_specialization('Construction')
    self.assertIn(contractor1, results)
    self.assertNotIn(contractor2, results)
```

### **🔧 Integration Tests**

#### **1. User-Contractor Relationship**

```python
def test_user_contractor_assignment(self):
    user = self.create_test_user()
    contractor = self.create_test_contractor()

    # Assign
    user.contractor_ids = [(4, contractor.id)]

    # Verify
    self.assertIn(contractor, user.contractor_ids)
    self.assertIn(user, contractor.user_ids)
```

---

## 🔮 **Future Enhancements**

### **🚀 Planned Features**

#### **1. Advanced Performance Analytics**

- [ ] **Performance Dashboard**: Visual metrics và trends
- [ ] **Predictive Analytics**: Forecast contractor performance
- [ ] **Benchmark Comparison**: So sánh với industry standards
- [ ] **Automated Rating**: AI-powered rating based on project outcomes

#### **2. Enhanced Integration**

- [ ] **External System Sync**: Sync với HR systems
- [ ] **Mobile App**: Contractor self-service portal
- [ ] **API Gateway**: RESTful APIs cho external integration
- [ ] **Real-time Notifications**: Push notifications cho status changes

#### **3. Advanced Features**

- [ ] **Skills Matrix**: Chi tiết technical skills tracking
- [ ] **Certification Management**: Track certificates và licenses
- [ ] **Document Management**: Store contractor documents
- [ ] **Financial Integration**: Payment và billing integration

### **📊 Analytics & Reporting**

- [ ] **Performance Reports**: Comprehensive contractor reports
- [ ] **Utilization Analysis**: Contractor workload analysis
- [ ] **Cost Analysis**: ROI analysis per contractor
- [ ] **Trend Analysis**: Historical performance trends

---

## 📚 **Best Practices**

### **🔧 Development Guidelines**

#### **1. Data Modeling**

- ✅ Use descriptive field names
- ✅ Add helpful help text
- ✅ Implement proper constraints
- ✅ Consider future extensibility

#### **2. Method Design**

- ✅ Single responsibility principle
- ✅ Proper error handling
- ✅ Clear documentation
- ✅ Return meaningful data structures

#### **3. Security**

- ✅ Implement proper access controls
- ✅ Validate all inputs
- ✅ Audit sensitive changes
- ✅ Protect personal information

### **📊 Business Usage**

#### **1. Contractor Onboarding**

1. Create contractor record with basic info
2. Assign relevant users
3. Set specialization và initial rating
4. Add to appropriate projects

#### **2. Performance Management**

1. Regular rating updates based on project feedback
2. Track activity patterns
3. Monitor specialization utilization
4. Review và update profiles periodically

---

## 📚 **References**

- [Odoo Many2many Relationships](https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html#many2many)
- [Model Methods Best Practices](https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html#model-methods)
- [Field Types Documentation](https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html#fields)

---
