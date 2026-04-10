# screens/profile.py
# ─────────────────────────────────────────────────────────────
# PROFILE SCREEN
# Owner: Salwan Maighun (2412258)
#
# SENSOR FEATURE: Shake-to-Logout
#   Uses ft.Accelerometer (raw sensor, includes gravity ~9.8 m/s²).
#   When the user shakes the phone hard enough (magnitude > SHAKE_THRESHOLD),
#   a confirmation dialog pops up asking them to confirm logout.
#   A cooldown (SHAKE_COOLDOWN_S) prevents repeated triggers.
# ─────────────────────────────────────────────────────────────

import flet as ft
import threading
import time
import math
from shared import api, big_btn, nav
from shared import PRIMARY, ACCENT, BG, TEXT_DARK, TEXT_LIGHT, ERROR

# ── SHAKE DETECTION CONSTANTS ────────────────────────────────
# The accelerometer includes gravity (~9.8 m/s²), so at rest the
# magnitude is ~9.8.  A hard shake easily exceeds 25 m/s².
SHAKE_THRESHOLD = 25.0   # m/s² — tune up if too sensitive
SHAKE_COOLDOWN_S = 2.0   # seconds between shake triggers


def profile_screen(page: ft.Page, go_to):
    col  = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    spin = ft.ProgressRing(visible=True, color=PRIMARY, width=30, height=30)

    # ── shake state (shared across threads) ──────────────────
    last_shake_time = [0.0]       # list so inner functions can mutate it
    dialog_open     = [False]
    accel_service   = [None]      # hold reference so it isn't garbage-collected

    # ── logout helpers ────────────────────────────────────────
    def _do_logout():
        if accel_service[0]:
            accel_service[0].enabled = False   # stop sensor
        threading.Thread(target=api.logout).start()
        go_to("login")

    def _close_dialog(confirmed):
        dialog_open[0] = False
        page.close(page.dialog)
        if confirmed:
            _do_logout()

    def _show_shake_dialog():
        dialog_open[0] = True
        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Shake detected 👋", weight=ft.FontWeight.BOLD),
            content=ft.Text("Did you want to log out?"),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda e: _close_dialog(False),
                    style=ft.ButtonStyle(color=TEXT_LIGHT),
                ),
                ft.ElevatedButton(
                    "Yes, log out",
                    on_click=lambda e: _close_dialog(True),
                    bgcolor=ERROR,
                    color="white",
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(page.dialog)

    # ── accelerometer reading handler ─────────────────────────
    def on_accel_reading(e: ft.AccelerometerReadingEvent):
        # magnitude of the acceleration vector
        magnitude = math.sqrt(e.x ** 2 + e.y ** 2 + e.z ** 2)

        if magnitude > SHAKE_THRESHOLD:
            now = time.time()
            if (now - last_shake_time[0]) > SHAKE_COOLDOWN_S and not dialog_open[0]:
                last_shake_time[0] = now
                page.run_task(_async_show_dialog)   # must update UI from main loop

    async def _async_show_dialog():
        _show_shake_dialog()
        page.update()

    # ── start accelerometer ───────────────────────────────────
    def _start_accelerometer():
        acc = ft.Accelerometer(
            interval=ft.Duration(milliseconds=100),
            on_reading=on_accel_reading,
        )
        page.services.append(acc)
        accel_service[0] = acc

    # ── profile data loader ───────────────────────────────────
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
                    ft.Container(height=4),

                    # ── shake hint banner ─────────────────────
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.VIBRATION, color=ACCENT, size=18),
                                ft.Text(
                                    "Shake your phone to log out",
                                    size=13, color=TEXT_LIGHT,
                                    italic=True,
                                ),
                            ],
                            spacing=6,
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=8),
                        bgcolor="#fff3e0",
                        border_radius=8,
                        margin=ft.margin.symmetric(horizontal=16),
                    ),

                    ft.Container(height=6),
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
                    big_btn("Logout", lambda e: _do_logout(), bg=ERROR, width=200),
                ]
                page.update()

                # start accelerometer only after profile is shown
                _start_accelerometer()
                page.update()

            except Exception as ex:
                spin.visible = False
                col.controls.append(ft.Text(f"Error: {ex}", color=ERROR))
                page.update()

        threading.Thread(target=fetch).start()

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