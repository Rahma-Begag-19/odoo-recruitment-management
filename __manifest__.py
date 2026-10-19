
{
    "name": "Recruitment Management",
    "version": "19.0.1.0.0",
    "summary": "Manage jobs, applications, and interviews",
    "description": """
Recruitment Management
======================

A recruitment management solution for Odoo 19.

Features:
- Create and manage job announcements.
- Define job requirements, experience, salary, and work mode.
- Manage candidates and their applications.
- Track recruitment progress for each application.
- Schedule interviews and manage interview details.
- Prepare for a public job portal where applicants can
  browse job offers and apply without creating accounts.
    """,
    "category": "Human Resources/Recruitment",
    "license": "LGPL-3",
    "depends": [
        "base",
        "hr",
        "mail",
        "web",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/recruitment_sequence.xml",
        "views/recruitment_job_views.xml",
        "views/job_seeker_views.xml",
        "views/recruitment_application_views.xml",
        "views/recruitment_interview_views.xml",
        "views/recruitment_menus.xml",
    ],
    "installable": True,
    "application": True,
}
