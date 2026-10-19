
from odoo import models, fields


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
        string="Applications Count",
        compute="_compute_application_count",
    )

    def _compute_application_count(self):
        for job in self:
            job.application_count = len(job.application_ids)


class RecruitmentExperience(models.Model):
    _name = "recruitment.experience"
    _description = "Professional Experience"

    name = fields.Char(
        string="Experience",
        required=True,
    )
