
from odoo import api, fields, models


class RecruitmentApplication(models.Model):
    _name = "recruitment.application"
    _description = "Job Application"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "application_date desc, id desc"

    name = fields.Char(
        string="Candidate Name",
        required=True,
        tracking=True,
    )

    job_id = fields.Many2one(
        "recruitment.job",
        string="Job Offer",
        required=True,
        ondelete="cascade",
        tracking=True,
    )

    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")

    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
        ],
        string="Gender",
    )

    location = fields.Char(string="Location")
    note = fields.Text(string="Notes")

    resume = fields.Binary(
        string="Resume",
        attachment=True,
    )
    resume_filename = fields.Char(string="Resume Filename")

    application_date = fields.Datetime(
        string="Application Date",
        default=fields.Datetime.now,
        readonly=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("interview", "Interview"),
            ("hired", "Hired"),
            ("closed", "Closed"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )

    interview_ids = fields.One2many(
        "recruitment.interview",
        "application_id",
        string="Interviews",
    )

    interview_count = fields.Integer(
        string="Interview Count",
        compute="_compute_interview_count",
    )

    @api.depends("interview_ids")
    def _compute_interview_count(self):
        for application in self:
            application.interview_count = len(application.interview_ids)

    def action_view_interviews(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Interviews",
            "res_model": "recruitment.interview",
            "view_mode": "list,form",
            "domain": [("application_id", "=", self.id)],
            "context": {
                "default_application_id": self.id,
            },
        }

    def action_open_job(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Job Offer",
            "res_model": "recruitment.job",
            "view_mode": "form",
            "res_id": self.job_id.id,
            "target": "current",
        }
