from odoo import models, fields, api
from odoo.exceptions import UserError

class LandingPage(models.Model):
    _name= 'landing_page.landing_page'
    _description = 'Landing Page User Roles'

    name = fields.Char(required=True)
    content = fields.Text()
    state = fields.Selection([('draft', 'Draft'), ('in_review', 'In Review'), ('published', 'Published'), ('rejected', 'Rejected')], default='draft')

    submitted_by = fields.Many2one('res.users', readonly=True)
    reviewer_id = fields.Many2one('res.users', string="Reviewed by", readonly=True)

    history = fields.Text(string="Change History")

    def action_submit(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError("Chỉ draft mới được gửi duyệt.")
            rec.state = 'in_review'
            rec.submitted_by = self.env.user
            rec.history = (rec.history or '') + f"\nSubmitted by {self.env.user.name}"

    def action_approve(self):
        for rec in self:
            if not self.env.user.has_group('user_roles.group_reviewer'):
                raise UserError("Không có quyền duyệt.")
            rec.state = 'published'
            rec.reviewer_id = self.env.user
            rec.history = (rec.history or '') + f"\nApproved by {self.env.user.name}"

    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'
            rec.reviewer_id = self.env.user
            rec.history = (rec.history or '') + f"\nRejected by {self.env.user.name}"


    @api.model
    def create(self, vals):
        if 'submitted_by' not in vals:
            vals['submitted_by'] = self.env.uid
        return super().create(vals)

