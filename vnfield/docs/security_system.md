# 🔐 Security System Documentation

## 📋 **Tổng quan**

Hệ thống bảo mật VNField được thiết kế theo mô hình **Role-Based Access Control (RBAC)** với **4 tầng phân quyền** rõ ràng. Hệ thống đảm bảo tính bảo mật dữ liệu, phân tách trách nhiệm và kiểm soát truy cập theo vai trò.

---

## 🎯 **Mục tiêu bảo mật**

### **🛡️ Security Objectives**

- ✅ **Data Isolation**: User chỉ truy cập dữ liệu thuộc quyền hạn
- ✅ **Role Separation**: Phân tách rõ ràng trách nhiệm theo vai trò
- ✅ **Principle of Least Privilege**: Cấp quyền tối thiểu cần thiết
- ✅ **Audit Trail**: Theo dõi tất cả hoạt động quan trọng
- ✅ **Scalable Permissions**: Dễ dàng mở rộng quyền hạn

### **📊 Business Requirements**

- ✅ **User Management**: Quản lý user theo contractor và role
- ✅ **Project Security**: Bảo mật dữ liệu project theo team
- ✅ **Task Assignment**: Chỉ assignee/manager mới thao tác task
- ✅ **Approval Workflow**: Controlled approval process

---

## 🏗️ **Kiến trúc 4 tầng**

### **🔄 Role Hierarchy**

```
👑 VNField Administrator (Admin)
├── 🏃‍♂️ VNField Manager (Manager)
├── 🔍 VNField Verifier (Verifier)
└── 👤 VNField User (User)
```

### **📊 Permission Matrix**

| Resource          | User    | Manager         | Verifier    | Admin       |
| ----------------- | ------- | --------------- | ----------- | ----------- |
| **Task**          | R/W Own | R/W/C/D Project | R/W All     | R/W/C/D All |
| **Project**       | R Own   | R/W/C/D Own     | R All       | R/W/C/D All |
| **Approval**      | R Own   | R/W Project     | R/W/C/D All | R/W/C/D All |
| **Contractor**    | R Own   | R Project       | R All       | R/W/C/D All |
| **Configuration** | -       | -               | -           | R/W/C/D All |

**Legend**: R=Read, W=Write, C=Create, D=Delete

---

## 👥 **Chi tiết từng Role**

### **👤 VNField User** (Người dùng cơ bản)

#### **🎯 Mục đích**

Nhân viên thực hiện công việc hàng ngày, làm việc với task được assign.

#### **🔑 Quyền hạn**

```xml
<record id="group_vnfield_user" model="res.groups">
    <field name="name">VNField User</field>
    <field name="comment">Basic users who can view and work on assigned tasks</field>
    <field name="category_id" ref="base.module_category_services"/>
</record>
```

#### **📋 Có thể làm**

- ✅ Xem task được assign cho mình
- ✅ Cập nhật progress và status của task
- ✅ Xem project mà mình là member
- ✅ View approval liên quan đến task của mình
- ✅ Cập nhật thông tin cá nhân

#### **❌ Không thể làm**

- ❌ Tạo/xóa task hoặc project
- ❌ Assign task cho người khác
- ❌ Xem task không liên quan
- ❌ Truy cập configuration

---

### **🏃‍♂️ VNField Manager** (Quản lý dự án)

#### **🎯 Mục đích**

Quản lý dự án, tạo và assign task, theo dõi tiến độ team.

#### **🔑 Quyền hạn**

```xml
<record id="group_vnfield_manager" model="res.groups">
    <field name="name">VNField Manager</field>
    <field name="comment">Project managers who can create and manage projects and tasks</field>
    <field name="implied_ids" eval="[(4, ref('group_vnfield_user'))]"/>
</record>
```

#### **📋 Có thể làm**

- ✅ **Kế thừa tất cả quyền của User**
- ✅ Tạo và quản lý project
- ✅ Tạo, assign và delete task trong project
- ✅ Quản lý team members
- ✅ View reports về project progress
- ✅ Approve/reject task completion

#### **🔒 Giới hạn**

- 🔒 Chỉ quản lý project mà mình là manager
- 🔒 Không xem được project của manager khác
- 🔒 Không access được system configuration

---

### **🔍 VNField Verifier** (Người xác minh)

#### **🎯 Mục đích**

Xử lý approval workflow, verify task completion, quality control.

#### **🔑 Quyền hạn**

```xml
<record id="group_vnfield_verifier" model="res.groups">
    <field name="name">VNField Verifier</field>
    <field name="comment">Users who can verify task completion and handle approvals</field>
    <field name="implied_ids" eval="[(4, ref('group_vnfield_user'))]"/>
</record>
```

#### **📋 Có thể làm**

- ✅ **Kế thừa tất cả quyền của User**
- ✅ Xem tất cả approval cần verify
- ✅ Approve/reject approval requests
- ✅ Verify task completion quality
- ✅ Access approval workflow configuration
- ✅ Generate verification reports

#### **🎯 Đặc quyền**

- 🎯 Xem cross-project approval để đảm bảo quality
- 🎯 Override task status khi cần thiết
- 🎯 Access verification tools và checklists

---

### **👑 VNField Administrator** (Quản trị viên)

#### **🎯 Mục đích**

Toàn quyền hệ thống, cấu hình, user management, system maintenance.

#### **🔑 Quyền hạn**

```xml
<record id="group_vnfield_admin" model="res.groups">
    <field name="name">VNField Administrator</field>
    <field name="comment">System administrators with full access</field>
    <field name="implied_ids" eval="[(4, ref('group_vnfield_manager')), (4, ref('group_vnfield_verifier'))]"/>
</record>
```

#### **📋 Có thể làm**

- ✅ **Kế thừa tất cả quyền của Manager và Verifier**
- ✅ User management và role assignment
- ✅ System configuration và settings
- ✅ Database maintenance và backup
- ✅ Security policy configuration
- ✅ System monitoring và analytics
- ✅ Access all data across system

#### **🚨 Trách nhiệm đặc biệt**

- 🚨 Đảm bảo data backup và recovery
- 🚨 Monitor system security và performance
- 🚨 Handle security incidents
- 🚨 System updates và maintenance

---

## 🔒 **Model Access Rights**

### **📋 Task Model Access**

#### **User Level**

```xml
<record id="access_vnfield_task_user" model="ir.model.access">
    <field name="name">vnfield.task.user</field>
    <field name="model_id" ref="model_vnfield_task"/>
    <field name="group_id" ref="group_vnfield_user"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

#### **Manager Level**

```xml
<record id="access_vnfield_task_manager" model="ir.model.access">
    <field name="name">vnfield.task.manager</field>
    <field name="model_id" ref="model_vnfield_task"/>
    <field name="group_id" ref="group_vnfield_manager"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>
```

### **🏗️ Project Model Access**

#### **User Level**

```xml
<record id="access_vnfield_project_user" model="ir.model.access">
    <field name="name">vnfield.project.user</field>
    <field name="model_id" ref="model_vnfield_project"/>
    <field name="group_id" ref="group_vnfield_user"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="False"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

---

## 🛡️ **Record Rules (Data Isolation)**

### **🔒 Task Record Rules**

#### **User Own Tasks**

```xml
<record id="rule_task_user_own" model="ir.rule">
    <field name="name">User Own Tasks</field>
    <field name="model_id" ref="model_vnfield_task"/>
    <field name="groups" eval="[(4, ref('group_vnfield_user'))]"/>
    <field name="domain_force">[
        '|',
        ('assignee_id', '=', user.id),
        ('project_id.member_ids', 'in', user.id)
    ]</field>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>
```

#### **Manager Project Tasks**

```xml
<record id="rule_task_manager_projects" model="ir.rule">
    <field name="name">Manager Project Tasks</field>
    <field name="model_id" ref="model_vnfield_task"/>
    <field name="groups" eval="[(4, ref('group_vnfield_manager'))]"/>
    <field name="domain_force">[
        '|',
        ('project_id.manager_id', '=', user.id),
        ('assigner_id', '=', user.id)
    ]</field>
</record>
```

### **🏗️ Project Record Rules**

#### **User Project Membership**

```xml
<record id="rule_project_user_member" model="ir.rule">
    <field name="name">User Project Membership</field>
    <field name="model_id" ref="model_vnfield_project"/>
    <field name="groups" eval="[(4, ref('group_vnfield_user'))]"/>
    <field name="domain_force">[
        ('member_ids', 'in', user.id)
    ]</field>
</record>
```

#### **Manager Own Projects**

```xml
<record id="rule_project_manager_own" model="ir.rule">
    <field name="name">Manager Own Projects</field>
    <field name="model_id" ref="model_vnfield_project"/>
    <field name="groups" eval="[(4, ref('group_vnfield_manager'))]"/>
    <field name="domain_force">[
        '|',
        ('manager_id', '=', user.id),
        ('project_owner_id.user_ids', 'in', user.id)
    ]</field>
</record>
```

---

## 🔧 **Security Implementation**

### **📁 File Structure**

```
security/
└── security.xml              # Complete security configuration
    ├── User Groups           # 4-tier role definitions
    ├── Model Access Rights   # CRUD permissions per model
    └── Record Rules          # Data isolation rules
```

### **🔐 Key Security Features**

#### **1. Group Inheritance**

```xml
<!-- Manager inherits User permissions -->
<field name="implied_ids" eval="[(4, ref('group_vnfield_user'))]"/>

<!-- Admin inherits both Manager and Verifier -->
<field name="implied_ids" eval="[(4, ref('group_vnfield_manager')), (4, ref('group_vnfield_verifier'))]"/>
```

#### **2. Domain Filtering**

```python
# Users chỉ thấy task của mình hoặc project mình tham gia
domain_force = [
    '|',
    ('assignee_id', '=', user.id),
    ('project_id.member_ids', 'in', user.id)
]
```

#### **3. Permission Granularity**

```xml
<!-- Specific CRUD permissions per role -->
<field name="perm_read" eval="True"/>
<field name="perm_write" eval="True"/>
<field name="perm_create" eval="False"/>
<field name="perm_unlink" eval="False"/>
```

---

## 🧪 **Security Testing**

### **✅ Test Scenarios**

#### **1. User Access Test**

```python
def test_user_access_own_tasks(self):
    # User chỉ thấy task được assign
    user_tasks = self.env['vnfield.task'].with_user(self.test_user).search([])
    assigned_tasks = self.env['vnfield.task'].search([('assignee_id', '=', self.test_user.id)])
    self.assertEqual(user_tasks, assigned_tasks)
```

#### **2. Manager Project Test**

```python
def test_manager_project_access(self):
    # Manager chỉ thấy project mình quản lý
    manager_projects = self.env['vnfield.project'].with_user(self.test_manager).search([])
    own_projects = self.env['vnfield.project'].search([('manager_id', '=', self.test_manager.id)])
    self.assertEqual(manager_projects, own_projects)
```

#### **3. Permission Violation Test**

```python
def test_user_cannot_create_project(self):
    # User không thể tạo project
    with self.assertRaises(AccessError):
        self.env['vnfield.project'].with_user(self.test_user).create({
            'name': 'Unauthorized Project'
        })
```

---

## 🚨 **Security Best Practices**

### **🔒 Implementation Guidelines**

#### **1. Principle of Least Privilege**

- Cấp quyền tối thiểu cần thiết cho từng role
- Review quyền hạn định kỳ
- Remove unused permissions

#### **2. Data Encryption**

- Sensitive fields được hash/encrypt
- Password policies enforced
- Session management secure

#### **3. Audit Trail**

```python
# Mail tracking for important changes
_inherit = ["mail.thread", "mail.activity.mixin"]

# Track critical fields
field = fields.Char(tracking=True)
```

#### **4. Input Validation**

```python
@api.constrains('field_name')
def _check_field_validation(self):
    # Validate input để prevent injection
    for record in self:
        if not self._validate_input(record.field_name):
            raise ValidationError("Invalid input")
```

---

## 🔧 **Troubleshooting**

### **❓ Common Security Issues**

#### **Problem**: User có thể xem data không thuộc quyền

**Solution**: Kiểm tra record rules và domain_force

#### **Problem**: Manager không tạo được task

**Solution**: Kiểm tra model access rights cho group_vnfield_manager

#### **Problem**: Record rules conflict

**Solution**: Sử dụng proper OR/AND logic trong domain_force

### **🔍 Debug Commands**

```python
# Check user groups
user = self.env.user
print(f"User groups: {user.groups_id.mapped('name')}")

# Check model access
access = self.env['ir.model.access'].search([('model_id.model', '=', 'vnfield.task')])
print(f"Task access: {access.mapped('name')}")

# Check record rules
rules = self.env['ir.rule'].search([('model_id.model', '=', 'vnfield.task')])
print(f"Task rules: {rules.mapped('name')}")
```

---

## 🔮 **Security Roadmap**

### **🚀 Planned Enhancements**

- [ ] **Two-Factor Authentication**: Implement 2FA for Admin role
- [ ] **Session Management**: Advanced session timeout và monitoring
- [ ] **IP Whitelisting**: Restrict access by IP ranges
- [ ] **API Security**: OAuth2/JWT for API endpoints
- [ ] **Data Encryption**: Encrypt sensitive fields at rest

### **📊 Security Monitoring**

- [ ] **Failed Login Attempts**: Monitor và alert
- [ ] **Permission Changes**: Audit trail cho role changes
- [ ] **Data Access Logs**: Log tất cả data access attempts
- [ ] **Security Dashboard**: Real-time security metrics

---

## 📚 **References**

- [Odoo Security Documentation](https://www.odoo.com/documentation/17.0/developer/reference/backend/security.html)
- [Access Rights Management](https://www.odoo.com/documentation/17.0/developer/reference/backend/security.html#access-rights)
- [Record Rules](https://www.odoo.com/documentation/17.0/developer/reference/backend/security.html#record-rules)

---

**📝 Document Version**: 1.0  
**📅 Last Updated**: July 17, 2025  
**👤 Author**: GitHub Copilot  
**🎯 Project**: VNField Security System
