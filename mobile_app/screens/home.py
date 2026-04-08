# screens/home.py
# ─────────────────────────────────────────────────────────────
# HOME SCREEN
# Owner: Keshni Nunkoo (2412390)
# ─────────────────────────────────────────────────────────────

import flet as ft
import threading
from shared import api, APP_STATE, big_btn, nav, v_card, section
from shared import PRIMARY, ACCENT, BG, CARD_BG, TEXT_DARK, TEXT_LIGHT, CENTER


def home_screen(page, go_to):
    search_f = ft.TextField(
        hint_text="Search make, model...",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=30, border_color=PRIMARY, expand=True,
    )
    type_f = ft.Dropdown(
        hint_text="All Types", width=130, border_color=PRIMARY, value="",
        options=[
            ft.dropdown.Option("",         "All Types"),
            ft.dropdown.Option("Car",      "Cars"),
            ft.dropdown.Option("Motorbike","Motorbikes"),
            ft.dropdown.Option("Truck",    "Trucks"),
            ft.dropdown.Option("Bus",      "Buses"),
            ft.dropdown.Option("Van",      "Vans"),
            ft.dropdown.Option("SUV",      "SUVs"),
        ]
    )

    col       = ft.Column(spacing=12)
    status    = ft.Text("", color=TEXT_LIGHT, text_align=ft.TextAlign.CENTER)
    spin      = ft.ProgressRing(visible=True, color=PRIMARY, width=30, height=30)
    saved_ids = set()

    def load(e=None):
        spin.visible = True; col.controls.clear(); status.value = ""; page.update()

        def fetch():
            nonlocal saved_ids
            try:
                if api.token:
                    try: saved_ids = {s["vehicle"]["id"] for s in api.saved()}
                    except: saved_ids = set()

                vehicles = api.vehicles(search=search_f.value, vtype=type_f.value or "")
                spin.visible = False

                if not vehicles:
                    status.value = "No vehicles found."; page.update(); return

                for v in vehicles:
                    def tap_fn(veh):
                        def tap(e):
                            APP_STATE["sv"] = veh
                            go_to("detail")
                        return tap

                    def save_fn(veh):
                        def do(e):
                            if not api.token: go_to("login"); return
                            def run():
                                r = api.toggle_save(veh["id"])
                                if r.get("saved"): saved_ids.add(veh["id"])
                                else: saved_ids.discard(veh["id"])
                                load()
                            threading.Thread(target=run).start()
                        return do

                    col.controls.append(
                        v_card(v, on_tap=tap_fn(v), on_save=save_fn(v), saved=(v["id"] in saved_ids))
                    )
                page.update()

            except Exception as ex:
                spin.visible = False
                status.value = f"Connection error. Is Django running?"
                page.update()

        threading.Thread(target=fetch).start()

    load()

    def do_logout(e):
        threading.Thread(target=api.logout).start()
        go_to("login")

    actions = [
        ft.IconButton(icon=ft.Icons.LOGOUT, icon_color="white", on_click=do_logout)
    ] if api.token else [
        ft.TextButton(content=ft.Text("Login", color="white"), on_click=lambda e: go_to("login"))
    ]

    return ft.View(
        route="/home", bgcolor=BG, scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(
            bgcolor=PRIMARY, actions=actions,
            title=ft.Row([
                ft.Icon(ft.Icons.DIRECTIONS_CAR, color="white"),
                ft.Text("AutoLink", color="white", weight=ft.FontWeight.BOLD),
            ])
        ),
        navigation_bar=nav("home", go_to),
        controls=[
            ft.Container(
                padding=ft.padding.all(16),
                content=ft.Column(spacing=10, controls=[
                    ft.Row([search_f, type_f], spacing=8),
                    big_btn("Search", load, bg=ACCENT),
                    section("Available Vehicles"),
                    ft.Row([spin], alignment=ft.MainAxisAlignment.CENTER),
                    status,
                    col,
                ])
            )
        ]
    )
