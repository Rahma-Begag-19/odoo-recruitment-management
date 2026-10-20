
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

    # Dashboard Part

    @api.model
    def get_dashboard_stats(self):
        """Called by the dashboard to get pipeline + job stats."""
        application_groups = self.read_group(
            [("state", "in", ["draft", "interview", "hired", "closed"])],
            ["state"],
            ["state"],
        )
        stage_counts = {g["state"]: g["state_count"] for g in application_groups}

        job_groups = self.env["recruitment.job"].read_group(
            [("state", "in", ["open", "closed"])],
            ["state"],
            ["state"],
        )
        job_counts = {g["state"]: g["state_count"] for g in job_groups}

        return {
            "stages": [
                {"key": "draft", "label": "New Applications",
                 "count": stage_counts.get("draft", 0),
                 "color": "#0d6efd"},
                {"key": "interview", "label": "In Interview",
                 "count": stage_counts.get("interview", 0),
                 "color": "#fd7e14"},
                {"key": "hired", "label": "Hired",
                 "count": stage_counts.get("hired", 0),
                 "color": "#198754"},
                {"key": "closed", "label": "Closed",
                 "count": stage_counts.get("closed", 0),
                 "color": "#6c757d"},
            ],
            "total_applications": sum(stage_counts.values()),
            "open_jobs": job_counts.get("open", 0),
            "closed_jobs": job_counts.get("closed", 0),
        }


    @api.model
    def get_applications_over_time(self):
        """Monthly application counts for the dashboard chart."""
        groups = self.read_group(
            [("application_date", "!=", False)],
            ["application_date"],
            ["application_date:month"],
            orderby="application_date",
        )
        return {
            "labels": [g["application_date:month"] for g in groups],
            "counts": [g["application_date_count"] for g in groups],
        }