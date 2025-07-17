# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Saneen K (<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    "name": "VN Field",
    "version": "17.0.1.0.1",
    "category": "Approval",
    "author": "Nhan Le",
    "depends": ["base", "mail", "website"],
    "data": [
        "data/sequences.xml",
        "data/default_contractor.xml",
        "security/security.xml",
        "views/project_views.xml",
        "views/project_dashboard_views.xml",
        "views/approval_views.xml",
        "views/task_views.xml",
        "views/approval_step_views.xml",
        "wizards/approval_step_wizards.xml",
        "wizards/user_permission_wizard.xml",
        "views/approval_review_views.xml",
        "views/user_management_views.xml",
        "views/contractor_management_views.xml",
        "views/user_contractor_dashboard_views.xml",
        "views/menu.xml",
        "data/task_type.xml",
        "data/ir_cron.xml",
    ],
    # "post_init_hook": "start_kafka_consumers",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "application": True,
}
