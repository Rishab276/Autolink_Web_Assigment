# screens/detail.py
# ─────────────────────────────────────────────────────────────
# VEHICLE DETAIL SCREEN
# Owner: Rishab Raghoonundun (2412024)
# ─────────────────────────────────────────────────────────────

import flet as ft
import threading
from shared import api, APP_STATE, section
from shared import PRIMARY, ACCENT, BG, TEXT_DARK, TEXT_LIGHT, SUCCESS, ERROR, CENTER


def detail_screen(page, go_to):
    vehicle = APP_STATE.get("sv")
    if not vehicle:
        go_to("home")
        return ft.View(route="/detail")

    saved_ids = set()
    if api.token:
        try: saved_ids = {s["vehicle"]["id"] for s in api.saved()}
        except: pass

    is_saved  = vehicle["id"] in saved_ids
    save_txt  = ft.Text("Unsave" if is_saved else "Save", color="white", size=14)
    save_icon = ft.Icon(ft.Icons.BOOKMARK, color="white", size=16)
    save_box  = ft.Container(
        content=ft.Row([save_icon, save_txt], spacing=6),
        bgcolor=ACCENT if is_saved else PRIMARY, border_radius=8,
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
        alignment=CENTER, ink=True, expand=True,
    )

    def toggle(e):
        if not api.token: go_to("login"); return
        def run():
            r = api.toggle_save(vehicle["id"])
            s = r.get("saved", False)
            save_txt.value  = "Unsave" if s else "Save"
            save_box.bgcolor = ACCENT if s else PRIMARY
            page.update()
        threading.Thread(target=run).start()

    save_box.on_click = toggle

    def irow(icon, lbl, val):
        return ft.Row([
            ft.Icon(icon, size=18, color=PRIMARY),
            ft.Text(f"{lbl}:", weight=ft.FontWeight.BOLD, size=13, width=110),
            ft.Text(str(val), size=13, color=TEXT_LIGHT, expand=True),
        ])

    images = vehicle.get("images", [])
    imgs = [
        ft.Container(content=ft.Image(src=i["image"], fit=ft.BoxFit.COVER), height=240)
        for i in images
    ] or [
        ft.Container(
            content=ft.Icon(ft.Icons.DIRECTIONS_CAR, size=80, color=TEXT_LIGHT),
            height=240, bgcolor="#e0e0e0", alignment=CENTER,
        )
    ]

    wa = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.CHAT, color="white", size=16),
            ft.Text("WhatsApp", color="white", size=14),
        ], spacing=6),
        bgcolor="#25D366", border_radius=8,
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
        alignment=CENTER, ink=True, expand=True,
        on_click=lambda e: page.launch_url(f"https://wa.me/{vehicle.get('contact','')}"),
    ) if vehicle.get("contact") else ft.Container()

    return ft.View(
        route="/detail", bgcolor=BG, scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(
            bgcolor=PRIMARY,
            title=ft.Text(f"{vehicle['make']} {vehicle['model']}", color="white"),
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK, icon_color="white",
                on_click=lambda e: go_to("home"),
            )
        ),
        controls=[
            ft.Column(spacing=0, controls=[
                ft.ListView(controls=imgs, height=240),
                ft.Container(
                    padding=ft.padding.all(20),
                    content=ft.Column(spacing=12, controls=[
                        ft.Row([
                            ft.Column(expand=True, controls=[
                                ft.Text(
                                    f"{vehicle['make']} {vehicle['model']} {vehicle['year']}",
                                    size=20, weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    f"Rs {int(vehicle['price']):,}{'  /month' if vehicle['is_rental'] else ''}",
                                    size=18, color=ACCENT, weight=ft.FontWeight.BOLD,
                                ),
                            ]),
                            ft.Container(
                                content=ft.Text(
                                    "For Rent" if vehicle['is_rental'] else "For Sale",
                                    color="white", size=12,
                                ),
                                bgcolor=PRIMARY if vehicle['is_rental'] else SUCCESS,
                                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                border_radius=20,
                            ),
                        ]),
                        ft.Divider(),
                        section("Specifications"),
                        irow(ft.Icons.SPEED,             "Mileage",      f"{vehicle['mileage']:,} km"),
                        irow(ft.Icons.SETTINGS,          "Transmission", vehicle['transmission']),
                        irow(ft.Icons.LOCAL_GAS_STATION, "Fuel Type",    vehicle['fuel_type']),
                        irow(ft.Icons.CATEGORY,          "Type",         vehicle['type_of_vehicle']),
                        irow(ft.Icons.PERSON,            "Listed by",    vehicle.get('uploader_name', 'N/A')),
                        ft.Divider(),
                        section("Description"),
                        ft.Text(vehicle.get('desc') or "No description provided.", size=14, color=TEXT_LIGHT),
                        ft.Divider(),
                        ft.Row([save_box, wa], spacing=10),
                        ft.Text(f"📍 GPS: {vehicle.get('gps_coor', 'N/A')}", size=12, color=TEXT_LIGHT),
                        ft.Container(height=20),
                    ])
                ),
            ])
        ]
    )
