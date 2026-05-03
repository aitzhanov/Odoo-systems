/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, onMounted } from "@odoo/owl";

const THEME_MAP = {
    "theme-louvre":    "louvre",
    "theme-hermitage": "louvre",
};

class CpfBackendTheme extends Component {
    static template = "cpf_event_themes.BackendThemeIndicator";

    setup() {
        // orm гарантированно доступен в systray, rpc — нет
        this.orm = useService("orm");

        onWillStart(async () => {
            try {
                const cssClass = await this.orm.call(
                    "cpf.event.theme",
                    "get_active_listing_theme_class",
                    []
                );
                const theme = THEME_MAP[cssClass] || "default";
                sessionStorage.setItem("cpf_backend_theme", theme);
                this._apply(theme);
            } catch (_) {
                const cached = sessionStorage.getItem("cpf_backend_theme");
                if (cached) this._apply(cached);
            }
        });
    }

    _apply(theme) {
        if (theme === "default") {
            document.body.removeAttribute("data-cpf-theme");
        } else {
            document.body.setAttribute("data-cpf-theme", theme);
        }
    }
}

registry.category("systray").add("cpf_backend_theme", {
    Component: CpfBackendTheme,
}, { sequence: 99 });