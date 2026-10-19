
{
    "name": "Recruitment Management",
    "version": "19.0.1.0.0",
    "summary": "Manage job openings, candidates, applications, and interviews",
    "author":"Rahma BEGAG",
    "description": """
        Recruitment Management for Odoo 19.

        Manage job announcements, candidate information,
        job applications, and interview scheduling.

        Designed to support a public job portal where
        candidates can apply without creating an account.
    """,
    "category": "Human Resources/Recruitment",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "hr",
        "website",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/recruitment_job_views.xml",
        "views/recruitment_application_views.xml",
        "views/recruitment_interview_views.xml",
        "views/recruitment_job_menus.xml",
        "views/recruitment_templates.xml",
    ],
    "images": ['static/description/icon.png'],
    "installable": True,
    "application": True,
}
