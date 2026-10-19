from odoo import http
from odoo.http import request


class RecruitmentWebsite(http.Controller):

    @http.route('/careers', type='http', auth='public', website=True)
    def careers(self, **kwargs):
        jobs = request.env["recruitment.job"].sudo().search(
            [("state", "=", "open")],
            order="announcement_date desc",
        )

        return request.render(
            "recruitment_management.website_recruitment_jobs",
            {
                "jobs": jobs,
            },
        )