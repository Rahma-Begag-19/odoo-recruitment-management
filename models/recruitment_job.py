
from odoo import models, fields, api


class RecruitmentJob(models.Model):
    _name = "recruitment.job"
    _description = "Recruitment Job"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "announcement_date desc, id desc"

    name = fields.Char(
        string="Job Title",
        required=True,
        tracking=True,
    )
    announcement_date = fields.Date(
        string="Announcement Date",
        default=fields.Date.context_today,
        required=True,
    )
    expiration_date = fields.Date(
        string="Expiration Date",
        required=True,
    )
    place = fields.Char(
        string="Place",
        required=True,
    )
    description = fields.Html(
        string="Job Description",
    )
    experience = fields.Many2many(
        "recruitment.experience",
        string="Required Experience",
    )
    work_mode = fields.Selection(
        [
            ("onsite", "On-site"),
            ("hybrid", "Hybrid"),
            ("remote", "Remote"),
        ],
        string="Work Mode",
        default="onsite",
        required=True,
    )
    salary = fields.Float(
        string="Salary",
    )
    state = fields.Selection(
        [
            ("open", "Open"),
            ("closed", "Closed"),
        ],
        string="Status",
        default="open",
        required=True,
        tracking=True,
    )
    number_of_positions = fields.Integer(
        string="Number of Positions",
        default=1,
        required=True,
    )
    level = fields.Selection(
        [
            ("entry", "Entry Level"),
            ("junior", "Junior"),
            ("mid", "Mid-Level"),
            ("senior", "Senior"),
            ("lead", "Lead"),
        ],
        string="Experience Level",
        required=True,
        default="entry",
    )
    department_id = fields.Many2one(
        "hr.department",
        string="Department",
        ondelete="set null",
    )

    application_ids = fields.One2many(
        "recruitment.application",
        "job_id",
        string="Applications",
    )

    application_count = fields.Integer(
        string="Application Count",
        compute="_compute_application_count",
    )


    # Detailed job content
    responsibilities = fields.Html(
        string="Responsibilities",
        help="Describe the main duties and responsibilities of this position.",
    )

    requirements = fields.Html(
        string="Required Qualifications",
        help="Describe the essential qualifications, skills, and experience.",
    )

    nice_to_have = fields.Html(
        string="Preferred Qualifications",
        help="Describe additional skills or qualifications that are an advantage.",
    )

    benefits = fields.Html(
        string="Benefits",
        help="Describe the benefits and advantages offered for this position.",
    )

    # Optional company information for the job detail page
    company_intro = fields.Html(
        string="About the Company",
        help="Provide information about the company or team hiring for this position.",
    )

    # Image displayed on the website job card or detail page
    image_1920 = fields.Image(
        string="Job Image",
        max_width=1920,
        max_height=1920,
    )

    # Website publication controls
    website_published = fields.Boolean(
        string="Published on Website",
        default=True,
        tracking=True,
        help="Enable this option to display the job on the public careers website.",
    )

    website_sequence = fields.Integer(
        string="Website Sequence",
        default=10,
        help="Lower values appear first on the careers page.",
    )

    # Employment arrangement
    employment_type = fields.Selection(
        [
            ("full_time", "Full-time"),
            ("part_time", "Part-time"),
            ("contract", "Contract"),
            ("internship", "Internship"),
            ("temporary", "Temporary"),
        ],
        string="Employment Type",
        default="full_time",
        required=True,
        tracking=True,
    )



    @api.depends("application_ids")
    def _compute_application_count(self):
        for job in self:
            job.application_count = len(job.application_ids)

    def action_view_applications(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Job Applications",
            "res_model": "recruitment.application",
            "view_mode": "list,form",
            "domain": [("job_id", "=", self.id)],
            "context": {
                "default_job_id": self.id,
            },
        }


class RecruitmentExperience(models.Model):
    _name = "recruitment.experience"
    _description = "Professional Experience"

    name = fields.Char(
        string="Experience",
        required=True,
    )
