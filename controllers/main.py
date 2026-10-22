
import base64
import logging
import re

from odoo import http
from odoo.http import request
from werkzeug.utils import secure_filename


_logger = logging.getLogger(__name__)

MAX_RESUME_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}


class RecruitmentWebsite(http.Controller):

    def _get_open_job(self, job_id):
        return request.env["recruitment.job"].sudo().search([
            ("id", "=", job_id),
            ("state", "=", "open"),
        ], limit=1)

    @http.route(
        "/careers",
        type="http",
        auth="public",
        website=True,
        methods=["GET"],
    )
    def careers(self, **kwargs):
        jobs = request.env["recruitment.job"].sudo().search(
            [("state", "=", "open")],
            order="announcement_date desc, id desc",
        )

        return request.render(
            "recruitment_management.website_recruitment_jobs",
            {"jobs": jobs},
        )

    @http.route(
        "/careers/job/<int:job_id>",
        type="http",
        auth="public",
        website=True,
        methods=["GET"],
    )
    def career_details(self, job_id, **kwargs):
        job = request.env["recruitment.job"].sudo().search([
            ("id", "=", job_id),
            ("state", "=", "open"),
        ], limit=1)

        if not job:
            return request.not_found()

        return request.render(
            "recruitment_management.careers_job_detail",
            {
                "job": job,
                "error": kwargs.get("error"),
            },
        )

    @http.route(
        "/careers/apply",
        type="http",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def apply(self, **post):
        try:
            job_id = int(post.get("job_id", "0"))
        except (TypeError, ValueError):
            return request.not_found()

        job = request.env["recruitment.job"].sudo().search([
            ("id", "=", job_id),
            ("state", "=", "open"),
        ], limit=1)

        if not job:
            return request.not_found()

        # Honeypot for basic spam protection.
        if post.get("website"):
            return request.redirect("/careers")

        candidate_name = (post.get("candidate_name") or "").strip()
        email = (post.get("email") or "").strip()
        phone = (post.get("phone") or "").strip()
        location = (post.get("location") or "").strip()
        note = (post.get("note") or "").strip()
        gender = post.get("gender") or False

        if (
            not candidate_name
            or len(candidate_name) > 200
            or not email
            or len(email) > 254
            or len(phone) > 50
            or len(location) > 200
            or len(note) > 10000
            or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email)
            or gender not in ("male", "female", False)
        ):
            return request.redirect(
                f"/careers/job/{job.id}?error=invalid"
            )

        uploaded_file = request.httprequest.files.get("resume")

        if not uploaded_file or not uploaded_file.filename:
            return request.redirect(
                f"/careers/job/{job.id}?error=resume"
            )

        filename = secure_filename(uploaded_file.filename)

        if not filename:
            return request.redirect(
                f"/careers/job/{job.id}?error=resume"
            )

        extension = "." + filename.rsplit(".", 1)[-1].lower() \
            if "." in filename else ""

        if extension not in ALLOWED_EXTENSIONS:
            return request.redirect(
                f"/careers/job/{job.id}?error=resume"
            )

        content = uploaded_file.stream.read(MAX_RESUME_SIZE + 1)

        if not content or len(content) > MAX_RESUME_SIZE:
            return request.redirect(
                f"/careers/job/{job.id}?error=resume"
            )

        try:
            application = request.env["recruitment.application"].sudo().create({
                "name": candidate_name,
                "job_id": job.id,
                "email": email,
                "phone": phone,
                "location": location,
                "gender": gender,
                "note": note,
                "resume": base64.b64encode(content),
                "resume_filename": filename,
            })
        except Exception:
            _logger.exception("Could not create job application")
            return request.redirect(
                f"/careers/job/{job.id}?error=server"
            )

        try:
            application._send_confirmation_email()
        except Exception:
            _logger.exception(
                "Could not send confirmation email to %s", email
            )

        return request.redirect("/careers/thank-you")

        return request.redirect("/careers/thank-you")

    @http.route(
        "/careers/thank-you",
        type="http",
        auth="public",
        website=True,
        methods=["GET"],
    )
    def application_thank_you(self, **kwargs):
        return request.render(
            "recruitment_management.careers_thank_you",
            {},
        )
