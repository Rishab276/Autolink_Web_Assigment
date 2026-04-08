# screens/saved.py
# ─────────────────────────────────────────────────────────────
# SAVED VEHICLES SCREEN
# Owner: Salwan Cassam Maighun (2412258)
# ─────────────────────────────────────────────────────────────

import flet as ft
import threading
from shared import api, APP_STATE, nav, v_card, section
from shared import PRIMARY, BG, TEXT_LIGHT


def saved_screen(page, go_to):
    col    = ft.Column(spacing=12)
    status = ft.Text("", color=TEXT_LIGHT, text_align=ft.TextAlign.CENTER)
    spin   = ft.ProgressRing(visible=True, color=PRIMARY, width=30, height=30)

    def load():
        spin.visible = True
        col.controls.clear()
        page.update()

        def fetch():
            try:
                if not api.token:
                    spin.visible = False
                    status.value = "Please login to view saved vehicles."
                    page.update()
                    return

                items = api.saved()
                spin.visible = False

                if not items:
                    status.value = "You haven't saved any vehicles yet."
                    page.update()
                    return

                for item in items:
                    v = item["vehicle"]

                    def tap_fn(veh):
                        def tap(e):
                            APP_STATE["sv"] = veh
                            go_to("detail")
                        return tap

                    def unsave_fn(veh):
                        def do(e):
                            def run():
                                api.toggle_save(veh["id"])
                                load()
                            threading.Thread(target=run).start()
                        return do

                    col.controls.append(
                        v_card(v, on_tap=tap_fn(v), on_save=unsave_fn(v), saved=True)
                    )
                page.update()

            except Exception as ex:
                spin.visible = False
                status.value = f"Error: {ex}"
                page.update()

        threading.Thread(target=fetch).start()

    load()

    return ft.View(
        route="/saved", bgcolor=BG, scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(
            title=ft.Text("Saved Vehicles", color="white"),
            bgcolor=PRIMARY,
        ),
        navigation_bar=nav("saved", go_to),
        controls=[
            ft.Container(
                padding=ft.padding.all(16),
                content=ft.Column(spacing=12, controls=[
                    section("Your Saved Vehicles"),
                    ft.Row([spin], alignment=ft.MainAxisAlignment.CENTER),
                    status,
                    col,
                ])
            )
        ]
    )
