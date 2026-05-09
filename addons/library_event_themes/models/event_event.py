from odoo import fields, models


class EventEvent(models.Model):
    _inherit = 'event.event'

    library_theme_id = fields.Many2one(
        'library.event.theme',
        string='Library Theme',
        domain=[('active', '=', True)],
        help='Website visual style used for this event.',
    )

    def action_cycle_library_theme(self):
        themes = self.env['library.event.theme'].search([('active', '=', True)])
        if not themes:
            return True

        theme_ids = themes.ids
        for event in self:
            if event.library_theme_id and event.library_theme_id.id in theme_ids:
                current_index = theme_ids.index(event.library_theme_id.id)
                next_theme = themes[(current_index + 1) % len(themes)]
            else:
                next_theme = themes[0]
            event.library_theme_id = next_theme
        return True
