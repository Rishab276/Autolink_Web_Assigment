# screens/nearby.py
# ─────────────────────────────────────────────────────────────
# NEARBY (GPS) SCREEN
# Owner: Rishab Raghoonundun (2412024)
# ─────────────────────────────────────────────────────────────

import flet as ft
import threading
from shared import api, APP_STATE, big_btn, nav, v_card
from shared import PRIMARY, ACCENT, BG, TEXT_DARK, TEXT_LIGHT, CENTER


def nearby_screen(page, go_to):
    col    = ft.Column(spacing=12)
    status = ft.Text(
        "Tap the button to find vehicles near you.",
        color=TEXT_LIGHT, text_align=ft.TextAlign.CENTER,
    )
    spin   = ft.ProgressRing(visible=False, color=PRIMARY, width=30, height=30)
    r_lbl  = ft.Text("Search radius: 20 km", color=TEXT_DARK)
    slider = ft.Slider(
        min=5, max=50, value=20, divisions=9,
        active_color=PRIMARY, label="{value} km",
    )

    def on_slide(e):
        r_lbl.value = f"Search radius: {int(slider.value)} km"
        page.update()

    slider.on_change = on_slide

    def find(e):
        spin.visible = True
        status.value = "Getting your GPS location..."
        col.controls.clear()
        page.update()

        try:
            gl = ft.Geolocator(
                location_settings=ft.GeolocatorSettings(
                    accuracy=ft.GeolocatorPositionAccuracy.HIGH
                )
            )
            page.overlay.append(gl)
            page.update()

            def on_pos(pos):
                lat, lng = pos.latitude, pos.longitude
                status.value = f"📍 {lat:.4f}, {lng:.4f} — Searching..."
                page.update()

                def fetch():
                    try:
                        data     = api.nearby(lat, lng, int(slider.value))
                        vehicles = data.get("vehicles", [])
                        count    = data.get("count", 0)
                        spin.visible = False
                        status.value = (
                            f"Found {count} vehicle(s) near you:"
                            if count else
                            f"No vehicles within {int(slider.value)} km."
                        )
                        for v in vehicles:
                            def tap_fn(veh):
                                def tap(e2):
                                    APP_STATE["sv"] = veh
                                    go_to("detail")
                                return tap
                            col.controls.append(v_card(v, on_tap=tap_fn(v)))
                        try: page.overlay.remove(gl)
                        except: pass
                        page.update()
                    except Exception as ex:
                        spin.visible = False
                        status.value = f"Error: {ex}"
                        page.update()

                threading.Thread(target=fetch).start()

            gl.get_current_position(on_pos)

        except Exception as ex:
            spin.visible = False
            status.value = f"GPS error: {ex}"
            page.update()

    return ft.View(
        route="/nearby", bgcolor=BG, scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(
            title=ft.Text("Vehicles Near Me", color="white"),
            bgcolor=PRIMARY,
        ),
        navigation_bar=nav("nearby", go_to),
        controls=[
            ft.Container(
                padding=ft.padding.all(20),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        ft.Icon(ft.Icons.LOCATION_ON, size=60, color=ACCENT),
                        ft.Text(
                            "Find Vehicles Near You",
                            size=22, weight=ft.FontWeight.BOLD,
                            color=PRIMARY, text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "Uses your phone's GPS to find nearby listings.",
                            size=13, color=TEXT_LIGHT,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        r_lbl,
                        slider,
                        big_btn("📍 Find Nearby Vehicles", find, bg=ACCENT, width=280),
                        ft.Row([spin], alignment=ft.MainAxisAlignment.CENTER),
                        status,
                        col,
                    ]
                )
            )
        ]
    )
