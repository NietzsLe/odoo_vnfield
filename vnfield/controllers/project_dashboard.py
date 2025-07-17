# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class ProjectDashboard(http.Controller):
    
    @http.route('/projects/dashboard', type='http', auth='user', website=True)
    def project_dashboard(self, project_id=None, **kwargs):
        """🏗️ Project Dashboard with sidebar project selection"""
        
        # Get all projects user has access to
        projects = request.env['vnfield.project'].search([])
        
        # Get selected project (first project if none selected)
        selected_project = None
        if project_id:
            selected_project = request.env['vnfield.project'].browse(int(project_id))
        elif projects:
            selected_project = projects[0]
        
        # Prepare dashboard data
        dashboard_data = {
            'projects': projects,
            'selected_project': selected_project,
            'members': [],
            'contractors': [],
            'tasks': [],
            'approvals': []
        }
        
        # Load data for selected project
        if selected_project:
            dashboard_data.update({
                'members': selected_project.member_ids,
                'contractors': selected_project.get_all_contractors(),
                'tasks': selected_project.task_ids,
                'approvals': selected_project.approval_ids
            })
        
        return request.render('vnfield.project_dashboard_template', dashboard_data)
