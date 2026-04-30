from odoo import models, fields

class Event(models.Model):
    _inherit = 'event.event'

    theme_id = fields.Many2one('cpf.event.theme', string='Стиль оформления')
