from odoo import api, models


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    @api.model
    def _get_recruitment_sender(self):
        """Return the SMTP login address of the first active outgoing server."""
        server = self.sudo().search(
            [("active", "=", True)],
            order="sequence, id",
            limit=1,
        )
        return server.smtp_user or False