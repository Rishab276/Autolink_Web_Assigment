# main.py
# ─────────────────────────────────────────────────────────────
# AUTOLINK MOBILE APP — Entry Point
# Run this file to start the app: python main.py
#
# Folder structure:
#   main.py              ← start here (do not modify)
#   shared.py            ← API, theme, shared components (Salwan)
#   screens/
#     login.py           ← Login & Register  (Vigneshwar 2411725)
#     home.py            ← Home screen       (Keshni    2412390)
#     detail.py          ← Vehicle detail    (Rishab    2412024)
#     nearby.py          ← GPS nearby        (Rishab    2412024)
#     saved.py           ← Saved vehicles    (Salwan    2412258)
#     reviews.py         ← Reviews           (Humaa     2412290)
#     profile.py         ← Profile           (Salwan    2412258)
# ─────────────────────────────────────────────────────────────

import flet as ft
from shared import BG

from screens.login   import login_screen, register_screen
from screens.home    import home_screen
from screens.detail  import detail_screen
from screens.nearby  import nearby_screen
from screens.saved   import saved_screen
from screens.reviews import report_vehicle_screen, reviews_screen, report_screen_for_review
from screens.profile import profile_screen
from screens.upload import upload_vehicle_screen, my_vehicles_screen, edit_vehicle_screen

SCREENS = {
    "login":    login_screen,
    "register": register_screen,
    "home":     home_screen,
    "detail":   detail_screen,
    "nearby":   nearby_screen,
    "saved":    saved_screen,
    "reviews":  reviews_screen,
    "profile":  profile_screen,
    "report_review":  report_screen_for_review,
    "report_vehicle": report_vehicle_screen,
    "upload_vehicle":upload_vehicle_screen,
    "my_vehicles":my_vehicles_screen,
    "edit_vehicle":edit_vehicle_screen,
}


def main(page: ft.Page):
    page.title         = "AutoLink"
    page.theme_mode    = ft.ThemeMode.LIGHT
    page.bgcolor       = BG
    page.window_width  = 400
    page.window_height = 800
    page.padding       = 0

    def go_to(route):
        page.views.clear()
        if route in SCREENS:
            page.views.append(SCREENS[route](page, go_to))
        page.update()

    go_to("login")


ft.app(target=main, assets_dir="assets")
