from odoo import models, fields, api


class CpfEventTheme(models.Model):
    _name = 'cpf.event.theme'
    _description = 'Event Theme'

    name = fields.Char(required=True)
    css_class = fields.Char(required=True)
    preview_color = fields.Char(default='#000000')
    is_listing_theme = fields.Boolean(string='Use for Events Page')

    @api.model
    def get_active_listing_theme_class(self):
        theme = self.sudo().search([('is_listing_theme', '=', True)], limit=1)
        return theme.css_class if theme else 'theme-louvre'

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record.is_listing_theme:
            self.search([
                ('id', '!=', record.id),
                ('is_listing_theme', '=', True)
            ]).write({'is_listing_theme': False})
        return record

    def write(self, vals):
        res = super().write(vals)
        if vals.get('is_listing_theme'):
            for record in self:
                self.search([
                    ('id', '!=', record.id),
                    ('is_listing_theme', '=', True)
                ]).write({'is_listing_theme': False})
        return res
