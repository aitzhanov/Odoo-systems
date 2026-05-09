from odoo import api, fields, models


class LibraryEventTheme(models.Model):
    _name = 'library.event.theme'
    _description = 'Library Event Theme'
    _order = 'sequence, name, id'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    css_class = fields.Char(required=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    use_for_events_page = fields.Boolean(string='Use for Events Page')
    event_count = fields.Integer(
        string='Events',
        compute='_compute_event_count',
    )

    _code_uniq = models.Constraint(
        'unique(code)',
        'The library event theme code must be unique.',
    )

    def _compute_event_count(self):
        grouped = self.env['event.event']._read_group(
            [('library_theme_id', 'in', self.ids)],
            ['library_theme_id'],
            ['__count'],
        )
        counts = {theme.id: count for theme, count in grouped}
        for theme in self:
            theme.event_count = counts.get(theme.id, 0)

    def _disable_other_events_page_themes(self):
        for theme in self:
            self.search([
                ('id', '!=', theme.id),
                ('use_for_events_page', '=', True),
            ]).write({'use_for_events_page': False})

    def _clear_museum_theme_integration(self, events):
        if 'theme_id' in events._fields:
            events.write({'theme_id': False})

        if 'cpf.event.theme' not in self.env.registry:
            return

        CpfTheme = self.env['cpf.event.theme'].sudo()
        if 'is_listing_theme' in CpfTheme._fields:
            CpfTheme.search([('is_listing_theme', '=', True)]).write({
                'is_listing_theme': False,
            })

    @api.model
    def get_active_events_page_theme(self):
        return self.sudo().search([
            ('use_for_events_page', '=', True),
            ('active', '=', True),
        ], limit=1)

    @api.model
    def get_active_events_page_theme_class(self):
        theme = self.get_active_events_page_theme()
        return theme.css_class if theme else ''

    def action_apply_to_all_events(self):
        events = self.env['event.event'].search([])
        for theme in self:
            theme.search([
                ('id', '!=', theme.id),
                ('use_for_events_page', '=', True),
            ]).write({'use_for_events_page': False})
            theme.use_for_events_page = True
            events.write({'library_theme_id': theme.id})
            theme._clear_museum_theme_integration(events)
        return True

    def action_clear_from_all_events(self):
        for theme in self:
            self.env['event.event'].search([
                ('library_theme_id', '=', theme.id),
            ]).write({'library_theme_id': False})
            if theme.use_for_events_page:
                theme.use_for_events_page = False
        return True

    def action_view_events(self):
        self.ensure_one()
        action = self.env.ref('event.action_event_view').read()[0]
        action['domain'] = [('library_theme_id', '=', self.id)]
        action['context'] = {
            'default_library_theme_id': self.id,
            'search_default_upcoming': 1,
        }
        action['name'] = 'Events Using %s' % self.name
        return action

    def write(self, vals):
        result = super().write(vals)
        if vals.get('use_for_events_page'):
            self._disable_other_events_page_themes()
        return result

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record.use_for_events_page:
            record._disable_other_events_page_themes()
        return record
