# screens/profile.py
# ─────────────────────────────────────────────────────────────
# PROFILE SCREEN
# Owner: Vigneshwar Bhewa (2411725)
# ─────────────────────────────────────────────────────────────

import flet as ft
import threading
from shared import api, big_btn, nav
from shared import PRIMARY, ACCENT, BG, TEXT_DARK, TEXT_LIGHT, ERROR


def profile_screen(page, go_to):
    col  = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    spin = ft.ProgressRing(visible=True, color=PRIMARY, width=30, height=30)

    def load():
        def fetch():
            try:
                if not api.token:
                    spin.visible = False
                    col.controls += [
                        ft.Icon(ft.Icons.PERSON_OUTLINE, size=60, color=TEXT_LIGHT),
                        ft.Text("You are not logged in.", size=16, color=TEXT_LIGHT),
                        big_btn("Login", lambda e: go_to("login"), width=200),
                    ]
                    page.update()
                    return

                p = api.profile()
                spin.visible = False

                def tile(icon, lbl, val):
                    return ft.ListTile(
                        leading=ft.Icon(icon, color=PRIMARY),
                        title=ft.Text(lbl, size=12, color=TEXT_LIGHT),
                        subtitle=ft.Text(str(val or "N/A"), size=15, color=TEXT_DARK),
                    )

                col.controls += [
                    ft.Container(height=10),
                    ft.CircleAvatar(
                        content=ft.Text(
                            (p.get("first_name") or "U")[0].upper(),
                            size=36, color="white",
                        ),
                        bgcolor=PRIMARY, radius=45,
                    ),
                    ft.Text(
                        f"{p.get('first_name','')} {p.get('last_name','')}",
                        size=22, weight=ft.FontWeight.BOLD, color=TEXT_DARK,
                    ),
                    ft.Container(
                        content=ft.Text(p.get("user_type","").capitalize(), color="white", size=13),
                        bgcolor=ACCENT,
                        padding=ft.padding.symmetric(horizontal=12, vertical=4),
                        border_radius=20,
                    ),
                    ft.Container(height=10),
                    ft.Card(elevation=3, content=ft.Column(spacing=0, controls=[
                        tile(ft.Icons.EMAIL,       "Email",          p.get("email")),
                        ft.Divider(height=1),
                        tile(ft.Icons.PHONE,       "Contact",        p.get("contact_number")),
                        ft.Divider(height=1),
                        tile(ft.Icons.HOME,        "Address",        p.get("address")),
                        ft.Divider(height=1),
                        tile(ft.Icons.CREDIT_CARD, "Driver License", p.get("driver_license")),
                    ])),
                    ft.Container(height=10),
                    
                ]

                if p.get("user_type") in ["seller", "renter"]:
                    col.controls.append(
                        big_btn(
                            "🚗  My Listings",
                            lambda e: go_to("my_vehicles"),
                            width=280,
                        )
                    )
                    col.controls.append(ft.Container(height=8))

                col.controls += [
                    big_btn("Logout", lambda e: do_logout(), bg=ERROR, width=200),
                    ft.Container(height=20),
                ]

                page.update()

            except Exception as ex:
                spin.visible = False
                col.controls.append(ft.Text(f"Error: {ex}", color=ERROR))
                page.update()

        threading.Thread(target=fetch).start()

    def do_logout():
        threading.Thread(target=api.logout).start()
        go_to("login")

    load()

    return ft.View(
        route="/profile", bgcolor=BG, scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(title=ft.Text("My Profile", color="white"), bgcolor=PRIMARY),
        navigation_bar=nav("profile", go_to),
        controls=[
            ft.Container(
                padding=ft.padding.all(16),
                content=ft.Column(spacing=10, controls=[
                    ft.Row([spin], alignment=ft.MainAxisAlignment.CENTER),
                    col,
                ])
            )
        ]
    )
