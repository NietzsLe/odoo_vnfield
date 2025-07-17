# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════
# ═             👥 USER CONTRACTOR DASHBOARD CONTROLLER       ═
# ═         Unified view for User-Contractor Management      ═
# ═══════════════════════════════════════════════════════════

"""
=================================================================
🎯 CHỨC NĂNG: USER-CONTRACTOR UNIFIED DASHBOARD CONTROLLER
=================================================================
- Cung cấp interface tích hợp giữa user và contractor management
- Sidebar contractor selector với filtering động
- Real-time user list update dựa trên contractor selection
- RESTful API endpoints cho AJAX calls
=================================================================
"""

import json
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError


# ┌─────────────────────────────────────────────────────────┐
# │              🎮 DASHBOARD CONTROLLER CLASS              │
# └─────────────────────────────────────────────────────────┘

class UserContractorDashboard(http.Controller):
    """
    ==========================================================
    👥 USER-CONTRACTOR DASHBOARD CONTROLLER
    ==========================================================
    
    🎯 **Mục đích**: 
    - Tạo unified dashboard cho user và contractor management
    - Hỗ trợ filtering user theo contractor selection
    - Cung cấp real-time data updates
    
    📋 **Tính năng chính**:
    - Dashboard route với contractor sidebar
    - API endpoints cho filtering data
    - User list updates dựa trên contractor selection
    - Responsive design với Bootstrap
    
    🔐 **Bảo mật**:
    - Kiểm tra user login và permissions
    - Group-based access control
    - Data filtering theo user rights
    ==========================================================
    """

    # ┌───────────────────────────────────────────────────────┐
    # │              📊 MAIN DASHBOARD ROUTE                 │
    # └───────────────────────────────────────────────────────┘

    @http.route('/user-contractor/dashboard', type='http', auth='user', website=True)
    def user_contractor_dashboard(self, contractor_id=None, **kwargs):
        """
        🏠 Main dashboard route with contractor sidebar và user filtering
        
        Args:
            contractor_id (int, optional): ID của contractor được chọn
            **kwargs: Additional parameters
            
        Returns:
            Rendered template with dashboard data
        """
        # 🔐 Kiểm tra quyền truy cập
        if not request.env.user.has_group('vnfield.group_contractor_user'):
            return request.render('http_routing.404')
        
        try:
            # 📊 Lấy dữ liệu contractors cho sidebar
            contractors = self._get_contractors_data()
            
            # 🎯 Xác định contractor hiện tại
            current_contractor = None
            users = []
            
            if contractor_id:
                contractor_id = int(contractor_id)
                current_contractor = request.env['vnfield.contractor'].browse(contractor_id)
                if current_contractor.exists():
                    users = self._get_users_by_contractor(contractor_id)
            else:
                # 🏠 Mặc định chọn contractor đầu tiên nếu có
                if contractors:
                    current_contractor = contractors[0]
                    users = self._get_users_by_contractor(current_contractor.id)
            
            # 📈 Chuẩn bị context cho template
            dashboard_data = {
                'contractors': contractors,
                'current_contractor': current_contractor,
                'users': users,
                'user_count': len(users) if users else 0,
                'contractor_count': len(contractors),
                'page_title': '👥 User & Contractor Dashboard',
            }
            
            return request.render('vnfield.user_contractor_dashboard_template', dashboard_data)
            
        except Exception as e:
            # 🚨 Error handling
            request.env['ir.logging'].create({
                'name': 'User-Contractor Dashboard Error',
                'type': 'server',
                'level': 'ERROR',
                'message': f'Dashboard error: {str(e)}',
                'path': '/user-contractor/dashboard',
                'func': 'user_contractor_dashboard',
            })
            return request.render('http_routing.404')

    # ┌───────────────────────────────────────────────────────┐
    # │               🔄 AJAX API ENDPOINTS                   │
    # └───────────────────────────────────────────────────────┘

    @http.route('/user-contractor/api/users/<int:contractor_id>', 
                type='json', auth='user', methods=['GET'])
    def get_users_by_contractor_api(self, contractor_id, **kwargs):
        """
        📡 API endpoint để lấy users theo contractor_id (AJAX call)
        
        Args:
            contractor_id (int): ID của contractor
            
        Returns:
            JSON response với user data
        """
        try:
            # 🔐 Kiểm tra quyền truy cập
            if not request.env.user.has_group('vnfield.group_contractor_user'):
                return {'error': 'Access denied', 'code': 403}
            
            # 👥 Lấy users data
            users = self._get_users_by_contractor(contractor_id)
            contractor = request.env['vnfield.contractor'].browse(contractor_id)
            
            # 📊 Format data cho JSON response
            users_data = []
            for user in users:
                users_data.append({
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'phone': user.phone or '',
                    'phone_work': user.phone_work or '',
                    'specialization': user.specialization or '',
                    'is_leader_of_contractor': user.is_leader_of_contractor,
                    'active': user.active,
                    'login_date': user.login_date.strftime('%Y-%m-%d %H:%M:%S') if user.login_date else '',
                })
            
            return {
                'success': True,
                'data': {
                    'users': users_data,
                    'contractor': {
                        'id': contractor.id,
                        'name': contractor.name,
                        'user_count': len(users_data),
                    },
                    'user_count': len(users_data),
                }
            }
            
        except Exception as e:
            return {'error': f'Failed to fetch users: {str(e)}', 'code': 500}

    @http.route('/user-contractor/api/contractors', 
                type='json', auth='user', methods=['GET'])
    def get_contractors_api(self, **kwargs):
        """
        📡 API endpoint để lấy danh sách contractors
        
        Returns:
            JSON response với contractor data
        """
        try:
            # 🔐 Kiểm tra quyền truy cập
            if not request.env.user.has_group('vnfield.group_contractor_user'):
                return {'error': 'Access denied', 'code': 403}
            
            contractors = self._get_contractors_data()
            
            # 📊 Format data cho JSON
            contractors_data = []
            for contractor in contractors:
                contractors_data.append({
                    'id': contractor.id,
                    'name': contractor.name,
                    'user_count': contractor.user_count,
                    'has_leader': contractor.has_leader,
                    'active': contractor.active,
                })
            
            return {
                'success': True,
                'data': {
                    'contractors': contractors_data,
                    'contractor_count': len(contractors_data),
                }
            }
            
        except Exception as e:
            return {'error': f'Failed to fetch contractors: {str(e)}', 'code': 500}

    # ┌───────────────────────────────────────────────────────┐
    # │                🛠️ HELPER METHODS                     │
    # └───────────────────────────────────────────────────────┘

    def _get_contractors_data(self):
        """
        📊 Lấy danh sách contractors với proper access rights
        
        Returns:
            Recordset of contractors với access rights
        """
        # 🔍 Domain filtering dựa trên user permissions
        domain = [('active', '=', True)]
        
        # 👑 Nếu không phải admin, chỉ hiển thị contractor của user
        current_user = request.env.user
        if not current_user.has_group('vnfield.group_contractor_admin'):
            if current_user.contractor_id:
                domain.append(('id', '=', current_user.contractor_id.id))
            else:
                domain.append(('id', '=', False))  # 🚫 Không có contractor nào
        
        return request.env['vnfield.contractor'].search(domain, order='name asc')

    def _get_users_by_contractor(self, contractor_id):
        """
        👥 Lấy users thuộc về contractor cụ thể
        
        Args:
            contractor_id (int): ID của contractor
            
        Returns:
            Recordset of users filtered by contractor
        """
        # 🔍 Domain cho user filtering
        domain = [
            ('contractor_id', '=', contractor_id),
            ('share', '=', False),  # 👥 Chỉ internal users
            ('active', '=', True),
        ]
        
        return request.env['res.users'].search(domain, order='name asc')


# ┌─────────────────────────────────────────────────────────┐
# │               📊 SYMBOL DEPENDENCIES                   │
# └─────────────────────────────────────────────────────────┘

"""
=================================================================
🔗 SYMBOL DEPENDENCIES ANALYSIS
=================================================================

📋 **Phụ thuộc vào các symbol khác:**

1. **Odoo Framework Dependencies:**
   - `http.Controller`: Base controller class từ Odoo framework
   - `http.route`: Decorator cho URL routing và endpoint definition  
   - `request`: Global request object cho HTTP request handling
   - `request.env`: Environment context cho database access
   - `AccessError`: Exception class cho access control violations

2. **VNField Models:**
   - `vnfield.contractor`: Contractor model với fields: name, user_count, has_leader, active
   - `res.users`: Extended user model với fields: contractor_id, specialization, is_leader_of_contractor, phone_work
   - `vnfield.group_contractor_user`: Security group cho basic contractor access
   - `vnfield.group_contractor_admin`: Security group cho contractor administration

3. **Template Dependencies:**
   - `vnfield.user_contractor_dashboard_template`: QWeb template sẽ được tạo
   - `http_routing.404`: Standard Odoo 404 error template

4. **Python Standard Library:**
   - `json`: Module cho JSON serialization/deserialization
   - `int()`: Built-in function cho integer conversion

📈 **Được sử dụng bởi:**

1. **URL Routes:**
   - `/user-contractor/dashboard`: Main dashboard interface
   - `/user-contractor/api/users/<int:contractor_id>`: AJAX API cho user filtering
   - `/user-contractor/api/contractors`: AJAX API cho contractor list

2. **Frontend JavaScript:**
   - AJAX calls từ dashboard template sẽ gọi API endpoints
   - Contractor selection events sẽ trigger user list updates
   - Real-time filtering và UI updates

3. **Security System:**
   - Group-based access control integration
   - User permission validation cho data access
   - Error handling và logging system

🔄 **Tương tác với ecosystem:**
- Controller tích hợp với existing user-contractor management system
- API endpoints hỗ trợ dynamic frontend functionality  
- Security integration với VNField permission system
- Template rendering với Odoo QWeb system
=================================================================
"""
