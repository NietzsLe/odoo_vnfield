# 🔄 Auto-Generation System Documentation

## 📋 **Tổng quan**

Hệ thống tự động sinh mã (Auto-Generation System) trong VNField cho phép tự động tạo mã unique cho các models chính: **Task**, **Project**, và **Approval**. Hệ thống này đảm bảo tính duy nhất, truy vết được và ngăn chặn việc chỉnh sửa mã thủ công.

---

## 🎯 **Mục tiêu**

### **Business Goals**

- ✅ **Tính duy nhất**: Mỗi record có mã unique không trùng lặp
- ✅ **Truy vết**: Dễ dàng tìm kiếm và theo dõi records
- ✅ **Tự động hóa**: Giảm lỗi human error trong việc tạo mã
- ✅ **Standardization**: Thống nhất format mã trong toàn hệ thống

### **Technical Goals**

- ✅ **Performance**: Tạo mã nhanh chóng không ảnh hưởng performance
- ✅ **Scalability**: Hỗ trợ hàng triệu records
- ✅ **Security**: Readonly field, không thể chỉnh sửa
- ✅ **Integration**: Tích hợp liền mạch với Odoo sequence system

---

## 🏗️ **Kiến trúc kỹ thuật**

### **🔧 Core Components**

#### **1. Odoo Sequence System**

```python
# Sử dụng ir.sequence của Odoo
self.env['ir.sequence'].next_by_code('vnfield.task')
```

#### **2. Model Integration**

```python
@api.model_create_multi
def create(self, vals_list):
    """🆕 Auto-generate code during creation"""
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('model.code') or '/'
    return super().create(vals_list)
```

#### **3. Field Definition**

```python
code = fields.Char(
    string="Code",
    readonly=True,    # Không thể chỉnh sửa
    copy=False,       # Không copy khi duplicate
    help="Unique auto-generated code"
)
```

---

## 📊 **Implementation Details**

### **🏷️ Code Formats**

| Model        | Prefix | Format    | Example              |
| ------------ | ------ | --------- | -------------------- |
| **Task**     | TSK-   | TSK-00001 | TSK-00001, TSK-00002 |
| **Project**  | PRJ-   | PRJ-00001 | PRJ-00001, PRJ-00002 |
| **Approval** | APV-   | APV-00001 | APV-00001, APV-00002 |

### **🔧 Sequence Configuration**

#### **Task Sequence**

```xml
<record id="seq_vnfield_task" model="ir.sequence">
    <field name="name">VNField Task Sequence</field>
    <field name="code">vnfield.task</field>
    <field name="prefix">TSK-</field>
    <field name="padding">5</field>
    <field name="number_next">1</field>
    <field name="number_increment">1</field>
</record>
```

#### **Project Sequence**

```xml
<record id="seq_vnfield_project" model="ir.sequence">
    <field name="name">VNField Project Sequence</field>
    <field name="code">vnfield.project</field>
    <field name="prefix">PRJ-</field>
    <field name="padding">5</field>
    <field name="number_next">1</field>
    <field name="number_increment">1</field>
</record>
```

#### **Approval Sequence**

```xml
<record id="seq_vnfield_approval" model="ir.sequence">
    <field name="name">VNField Approval Sequence</field>
    <field name="code">vnfield.approval</field>
    <field name="prefix">APV-</field>
    <field name="padding">5</field>
    <field name="number_next">1</field>
    <field name="number_increment">1</field>
</record>
```

---

## 💻 **Code Implementation**

### **📋 Task Model Enhancement**

**File**: `models/task.py`

```python
# ═══════════════════════════════════════════════════════════
# ═                📋 ENHANCED TASK MODEL                   ═
# ═══════════════════════════════════════════════════════════

class Task(models.Model):
    _name = "vnfield.task"
    _description = "VN Field Task Management"

    # ─────────────── 🏷️ BASIC TASK INFORMATION ───────────────
    name = fields.Char(string="Task Name", required=True, tracking=True)

    code = fields.Char(
        string="Task Code",
        readonly=True,
        copy=False,
        help="Unique auto-generated code for the task"
    )

    # ═══════════════════════════════════════════════════════════
    # ═                🔄 RECORD LIFECYCLE METHODS              ═
    # ═══════════════════════════════════════════════════════════

    @api.model_create_multi
    def create(self, vals_list):
        """🆕 Create task with auto-generated code"""
        for vals in vals_list:
            if not vals.get('code'):
                vals['code'] = self.env['ir.sequence'].next_by_code('vnfield.task') or '/'
        return super().create(vals_list)
```

### **🏗️ Project Model Enhancement**

**File**: `models/project.py`

```python
@api.model_create_multi
def create(self, vals_list):
    """🆕 Create project with auto-generated code"""
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('vnfield.project') or '/'
    return super().create(vals_list)
```

### **✅ Approval Model Enhancement**

**File**: `models/approval.py`

```python
# ─────────────── 🏷️ BASIC APPROVAL INFORMATION ───────────────
code = fields.Char(
    string="Approval Code",
    readonly=True,
    copy=False,
    help="Unique auto-generated code for the approval"
)

@api.model_create_multi
def create(self, vals_list):
    """🆕 Create approval with auto-generated code"""
    for vals in vals_list:
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('vnfield.approval') or '/'
    return super().create(vals_list)
```

---

## 🎨 **UI Integration**

### **📱 Form Views**

Code field được hiển thị ở vị trí prominent trong form view:

```xml
<field name="code" placeholder="Auto-generated upon save"/>
```

### **📋 List Views**

Code field xuất hiện trong list view để dễ dàng identify:

```xml
<field name="code"/>
```

### **🔍 Search Views**

Code field có thể tìm kiếm:

```xml
<field name="code" string="Code" filter_domain="[('code','ilike',self)]"/>
```

---

## 🔒 **Security Features**

### **🛡️ Field Protection**

```python
readonly=True    # User không thể edit
copy=False       # Không copy khi duplicate record
```

### **🔐 Validation**

- Code chỉ được tạo một lần khi create
- Không thể modify sau khi đã tạo
- Fallback to '/' nếu sequence không hoạt động

---

## 📈 **Performance Considerations**

### **⚡ Optimization**

- **Bulk Creation**: Sử dụng `@api.model_create_multi` cho performance tốt
- **Database Level**: Sequence được handle ở database level
- **Caching**: Odoo tự động cache sequence values
- **Atomic Operations**: Sequence generation là atomic

### **📊 Scalability**

- **Padding**: 5 digits hỗ trợ đến 99,999 records
- **Extensible**: Có thể tăng padding khi cần
- **Multiple Companies**: Sequence independent theo company

---

## 🧪 **Testing**

### **✅ Test Cases**

#### **1. Basic Creation Test**

```python
def test_task_auto_generation(self):
    task = self.env['vnfield.task'].create({'name': 'Test Task'})
    self.assertTrue(task.code.startswith('TSK-'))
    self.assertEqual(len(task.code), 9)  # TSK-00001
```

#### **2. Bulk Creation Test**

```python
def test_bulk_creation(self):
    tasks = self.env['vnfield.task'].create([
        {'name': 'Task 1'},
        {'name': 'Task 2'},
        {'name': 'Task 3'}
    ])
    codes = tasks.mapped('code')
    self.assertEqual(len(set(codes)), 3)  # All unique
```

#### **3. Readonly Test**

```python
def test_code_readonly(self):
    task = self.env['vnfield.task'].create({'name': 'Test Task'})
    original_code = task.code
    with self.assertRaises(ValidationError):
        task.write({'code': 'CUSTOM-001'})
```

---

## 🐛 **Troubleshooting**

### **❓ Common Issues**

#### **Problem**: Code hiển thị '/'

**Solution**: Kiểm tra sequence definition trong data/sequences.xml

#### **Problem**: Code bị trùng lặp

**Solution**: Restart Odoo server để reload sequence cache

#### **Problem**: User có thể edit code

**Solution**: Kiểm tra readonly=True trong field definition

### **🔧 Debug Commands**

```python
# Check sequence current value
sequence = self.env['ir.sequence'].search([('code', '=', 'vnfield.task')])
print(f"Current number: {sequence.number_next}")

# Reset sequence
sequence.write({'number_next': 1})

# Generate next code manually
next_code = self.env['ir.sequence'].next_by_code('vnfield.task')
print(f"Next code: {next_code}")
```

---

## 🔮 **Future Enhancements**

### **🚀 Planned Features**

- [ ] **Custom Prefixes**: Cho phép user config prefix theo company
- [ ] **Reset Sequence**: Admin có thể reset sequence về 1
- [ ] **Audit Trail**: Log tất cả code generation events
- [ ] **Barcode Integration**: Generate barcode từ code
- [ ] **QR Code**: Generate QR code cho mobile scanning

### **📊 Analytics**

- [ ] **Usage Statistics**: Thống kê số lượng codes generated
- [ ] **Performance Metrics**: Monitor sequence generation time
- [ ] **Gap Analysis**: Detect missing sequences

---

## 📚 **References**

- [Odoo Sequence Documentation](https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html#sequences)
- [Model Create Multi Decorator](https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html#odoo.api.model_create_multi)
- [Field Attributes](https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html#field-attributes)

---
