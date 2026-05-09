# Library Event Themes

Reusable Odoo addon for assigning library-inspired website event themes to individual events.

The module is independent from any museum or CPF theme addon. It does not import from, depend on, or modify `cpf_event_themes`.

## Features

- Adds a `library.event.theme` configuration model.
- Adds `library_theme_id` to events.
- Adds a backend button to cycle an event through available library themes.
- Applies the selected theme class to website event detail pages.
- Applies selected event theme classes to event listing cards when the listing template exposes event records.
- Ships two default themes:
  - Library of Congress Style (`o_library_theme_loc`)
  - British Library Style (`o_library_theme_bl`)

## Design Scope

The included frontend styles are original designs inspired by public library event sites. They do not copy logos, trademarks, exact HTML, images, or proprietary assets.

CSS is scoped under:

- `.o_library_event_theme.o_library_theme_loc`
- `.o_library_event_theme.o_library_theme_bl`

## Upgrade

From this repository, restart Odoo and upgrade the module with:

```bash
docker compose restart odoo
docker compose exec odoo odoo -d <database_name> -u library_event_themes --stop-after-init
docker compose restart odoo
```

Replace `<database_name>` with the database that has the module installed.
