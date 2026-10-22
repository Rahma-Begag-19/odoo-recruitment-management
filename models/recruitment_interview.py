import logging

from odoo import api, fields, models
from odoo.tools import html_escape


_logger = logging.getLogger(__name__)


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

    def _get_invitation_body(self):
        """Build the HTML body of the interview invitation."""
        self.ensure_one()
        application = self.application_id

        interview_dt = ""
        if self.interview_date:
            local_dt = fields.Datetime.context_timestamp(self, self.interview_date)
            interview_dt = local_dt.strftime("%A, %d %B %Y at %H:%M")

        type_label = dict(self._fields["interview_type"].selection).get(
            self.interview_type, ""
        )

        return (
            '<div style="font-family: Arial, sans-serif; max-width: 600px; '
            'margin: auto; color: #333;">'
            '<h2 style="color: #0d6efd;">Interview Invitation</h2>'
            "<p>Dear %(name)s,</p>"
            "<p>Thank you for your application for the position of "
            "<strong>%(job)s</strong>.</p>"
            "<p>We are pleased to invite you to an interview. "
            "Please find the details below:</p>"
            '<div style="background-color: #f5f7fa; padding: 16px; '
            'border-radius: 8px;">'
            "<p><strong>Position:</strong> %(job)s</p>"
            "<p><strong>Date and time:</strong> %(date)s</p>"
            "<p><strong>Interview type:</strong> %(type)s</p>"
            "<p><strong>Location / Meeting link:</strong> %(location)s</p>"
            "</div>"
            "<p>Please confirm your availability by replying to this email. "
            "We look forward to meeting you.</p>"
            "<p>Best regards,<br/>The Recruitment Team</p>"
            "</div>"
        ) % {
            "name": html_escape(application.name or ""),
            "job": html_escape(self.job_id.name or ""),
            "date": html_escape(interview_dt),
            "type": html_escape(type_label),
            "location": html_escape(self.location or "To be confirmed"),
        }

    @api.model_create_multi
    def create(self, vals_list):
        interviews = super().create(vals_list)

        # Use the SMTP account of the outgoing mail server as the sender.
        sender = self.env["ir.mail_server"]._get_recruitment_sender()

        for interview in interviews:
            application = interview.application_id

            # Update the linked application status.
            application.write({"state": "interview"})

            _logger.info(
                "Interview %s created for application %s. Applicant email: %s",
                interview.id,
                application.id,
                application.email,
            )

            if not application.email:
                _logger.warning(
                    "Interview invitation skipped: application %s has no email.",
                    application.id,
                )
                continue

            try:
                mail_values = {
                    "subject": "Interview Invitation - %s"
                               % (interview.job_id.name or ""),
                    "body_html": interview._get_invitation_body(),
                    "email_from": sender,
                    "email_to": application.email,
                    "auto_delete": False,
                }
                mail = self.env["mail.mail"].sudo().create(mail_values)
                mail.send(raise_exception=True)

                _logger.info(
                    "Interview invitation sent: interview %s, to %s, "
                    "from %s, mail ID %s",
                    interview.id,
                    application.email,
                    sender,
                    mail.id,
                )

            except Exception:
                _logger.exception(
                    "Failed to send interview invitation for interview %s "
                    "to %s",
                    interview.id,
                    application.email,
                )

        return interviews

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