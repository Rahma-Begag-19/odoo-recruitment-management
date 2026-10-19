
from odoo import fields, models


class RecruitmentInterview(models.Model):
    _name = "recruitment.interview"
    _description = "Recruitment Interview"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "interview_date desc, id desc"

    name = fields.Char(
        string="Interview Title",
        required=True,
        tracking=True,
    )

    application_id = fields.Many2one(
        "recruitment.application",
        string="Job Application",
        required=True,
        ondelete="cascade",
        tracking=True,
    )

    job_id = fields.Many2one(
        "recruitment.job",
        string="Job Offer",
        related="application_id.job_id",
        store=True,
        readonly=True,
    )

    interview_date = fields.Datetime(
        string="Interview Date",
        required=True,
        tracking=True,
    )

    interviewer_id = fields.Many2one(
        "res.users",
        string="Interviewer",
        required=True,
        tracking=True,
        ondelete="restrict",
    )

    interview_type = fields.Selection(
        [
            ("phone", "Phone"),
            ("online", "Online"),
            ("onsite", "On-site"),
        ],
        string="Interview Type",
        default="onsite",
        required=True,
    )

    location = fields.Char(string="Location or Meeting Link")
    feedback = fields.Text(string="Feedback")

    result = fields.Selection(
        [
            ("pending", "Pending"),
            ("passed", "Passed"),
            ("failed", "Failed"),
            ("cancelled", "Cancelled"),
        ],
        string="Result",
        default="pending",
        required=True,
        tracking=True,
    )

    def action_open_application(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Job Application",
            "res_model": "recruitment.application",
            "view_mode": "form",
            "res_id": self.application_id.id,
            "target": "current",
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
