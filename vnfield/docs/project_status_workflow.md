# 🔄 Project Status Workflow Documentation

## Tổng Quan Workflow

VNField Project Management System sử dụng một workflow 7-state để quản lý vòng đời của project từ khởi tạo đến hoàn thành.

## 📋 Các Trạng Thái (Status States)

### 1. 📝 Draft (Bản nháp)

- **Ý nghĩa**: Project mới tạo, chưa chính thức bắt đầu
- **Đặc điểm**:
  - Thông tin cơ bản đã nhập nhưng chưa đầy đủ
  - Chưa assign team members hoặc contractors
  - Có thể chỉnh sửa tự do mà không ảnh hưởng đến workflow
- **Hành động có thể**: Edit, Delete, Move to Planning
- **Business Rules**: Chỉ có thể delete project khi ở trạng thái này

### 2. 📋 Planning (Lập kế hoạch)

- **Ý nghĩa**: Project đang trong giai đoạn lập kế hoạch chi tiết
- **Đặc điểm**:
  - Đã xác định scope, timeline, budget
  - Đang assign team members và contractors
  - Tạo các tasks và approval workflows
  - Chuẩn bị tài nguyên cần thiết
- **Validations**: Phải có tên và mô tả project
- **Hành động có thể**: Start Project, Put on Hold, Cancel

### 3. ⚡ In Progress (Đang thực hiện)

- **Ý nghĩa**: Project đang được thực hiện tích cực
- **Đặc điểm**:
  - Team đang làm việc trên các tasks
  - Track progress hàng ngày
  - Regular status updates và meetings
  - Quản lý resources và timeline
- **Validations**: Phải có Manager và Project Owner
- **Hành động có thể**: Move to Review, Complete, Put on Hold

### 4. ⏸️ On Hold (Tạm dừng)

- **Ý nghĩa**: Project tạm dừng vì lý do bất khả kháng
- **Lý do thường gặp**:
  - Thiếu ngân sách hoặc resources
  - Chờ approval từ client
  - Vấn đề kỹ thuật cần giải quyết
  - Thay đổi requirements
- **Hành động có thể**: Resume (back to In Progress), Cancel

### 5. 🔍 Under Review (Đang đánh giá)

- **Ý nghĩa**: Project đã hoàn thành và đang được đánh giá
- **Đặc điểm**:
  - Tất cả tasks đã completed
  - Đang chờ final approval từ client/stakeholders
  - Quality check và testing
  - Documentation review
- **Validations**: Tất cả tasks phải completed
- **Hành động có thể**: Complete, Back to In Progress (nếu cần sửa)

### 6. ✅ Completed (Hoàn thành)

- **Ý nghĩa**: Project đã hoàn thành thành công
- **Đặc điểm**:
  - Đã delivery cho client
  - Final approval đã có
  - All documentation completed
  - Project closure activities done
- **Validations**:
  - Tất cả tasks phải completed
  - Không có pending approvals
- **Hành động có thể**: Archive, Clone for new project
- **Final State**: Không thể chuyển sang trạng thái khác

### 7. ❌ Canceled (Đã hủy)

- **Ý nghĩa**: Project bị hủy bỏ trước khi hoàn thành
- **Lý do thường gặp**:
  - Client hủy contract
  - Không khả thi về mặt kỹ thuật/tài chính
  - Thay đổi chiến lược business
  - Force majeure events
- **Warning**: Cảnh báo về active tasks sẽ bị ảnh hưởng
- **Final State**: Không thể chuyển sang trạng thái khác

## 🔄 Transition Matrix (Ma trận chuyển trạng thái)

```
FROM State      →   TO States (Allowed)
─────────────────────────────────────────
draft           →   [planning, canceled]
planning        →   [in-progress, on-hold, canceled]
in-progress     →   [review, completed, on-hold, canceled]
on-hold         →   [in-progress, planning, canceled]
review          →   [completed, in-progress]
completed       →   [] (Final state)
canceled        →   [] (Final state)
```

## 🎯 Action Methods và Validations

### action_move_to_planning()

```python
# Transition: draft → planning
# Validations:
- Phải có tên và mô tả project
```

### action_start_project()

```python
# Transition: draft/planning → in-progress
# Validations:
- Phải có manager_id (Project Manager)
- Phải có project_owner_id (Project Owner)
# Auto-actions:
- Set start_date = today()
```

### action_move_to_review()

```python
# Transition: in-progress → review
# Validations:
- Tất cả tasks phải có status = 'completed'
```

### action_complete_project()

```python
# Transition: in-progress/review → completed
# Validations:
- Tất cả tasks phải có status = 'completed'
- Không có approval nào có status = 'pending'
# Auto-actions:
- Set end_date = today()
- Set progress = 100.0
```

### action_put_on_hold()

```python
# Transition: in-progress/planning → on-hold
# No specific validations
```

### action_resume_project()

```python
# Transition: on-hold → in-progress
# No specific validations
```

### action_cancel_project()

```python
# Transition: Any → canceled
# Warnings:
- Cảnh báo về số lượng active tasks sẽ bị ảnh hưởng
```

## 🔒 Validation Constraints

### Status Transition Validation

```python
@api.constrains('status')
def _check_status_transition(self):
    # Prevents direct status field changes
    # Forces users to use action buttons
```

### Field Validations

```python
@api.constrains('start_date', 'end_date', 'deadline')
def _check_project_dates(self):
    # start_date ≤ end_date ≤ deadline

@api.constrains('progress')
def _check_progress_range(self):
    # 0% ≤ progress ≤ 100%

@api.constrains('budget', 'actual_cost')
def _check_budget_values(self):
    # budget ≥ 0, actual_cost ≥ 0
```

## 📧 Notification System

Mỗi status change đều có automatic notification:

```python
self.message_post(
    body=f"🚀 Dự án đã được bắt đầu bởi {self.env.user.name}",
    subject="Dự án đã bắt đầu"
)
```

## 🎨 UI Implementation

### Form View Buttons

- Status-specific buttons với conditional visibility
- Workflow guidance cho users
- Visual status bar với all states

### Kanban View Actions

- Quick action buttons per status
- Status-based card styling
- Progress visualization

## 🔧 Technical Implementation

### Error Handling

- Vietnamese error messages for better UX
- Specific validation messages
- Business rule enforcement

### Audit Trail

- Full tracking via message_post()
- Chatter integration
- Status change history

---

_Document Version: 1.0_  
_Last Updated: July 17, 2025_  
_Author: GitHub Copilot Assistant_
