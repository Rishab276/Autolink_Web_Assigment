# screens/profile.py
# ─────────────────────────────────────────────────────────────
# PROFILE SCREEN
# Owner: Salwan Maighun (2412258)
#
# SENSOR FEATURE: Battery-Aware Profile (ft.Battery)
#   When the profile loads, the app queries the device's battery
#   level and charging state using ft.Battery — a Flet system
#   sensor service. A contextual banner is shown:
#     🔴 < 20% and not charging → urgent warning
#     🟡 20–50% and not charging → caution notice
#     🟢 charging or > 50%      → all good / hidden
#   The user can tap "Refresh" to re-query the battery live.
#   This is mobile-specific: a web browser cannot expose raw
#   battery hardware the same way a native Android app can.
# ─────────────────────────────────────────────────────────────

import flet as ft
import threading
from shared import api, big_btn, nav
from shared import PRIMARY, ACCENT, BG, TEXT_DARK, TEXT_LIGHT, ERROR, SUCCESS


def profile_screen(page: ft.Page, go_to):
    col  = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    spin = ft.ProgressRing(visible=True, color=PRIMARY, width=30, height=30)

    # ── battery banner controls (built once, updated in place) ─
    battery_icon  = ft.Icon(ft.Icons.BATTERY_UNKNOWN, size=20)
    battery_text  = ft.Text("Checking battery…", size=13, italic=True)
    refresh_btn   = ft.IconButton(
        icon=ft.Icons.REFRESH,
        icon_size=18,
        tooltip="Refresh battery",
        on_click=lambda e: page.run_task(_check_battery),
    )
    battery_row   = ft.Row(
        [battery_icon, battery_text, refresh_btn],
        spacing=6,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    battery_banner = ft.Container(
        content=battery_row,
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
        border_radius=8,
        margin=ft.margin.symmetric(horizontal=0),
        bgcolor="#e3f2fd",   # default blue — overwritten below
        visible=False,       # hidden until battery data arrives
    )

    # ── battery check (async — uses ft.Battery query, not stream) ─
    async def _check_battery():
        try:
            battery_banner.visible = False
            battery_text.value = "Checking battery…"
            page.update()

            bat   = ft.Battery()
            level = await bat.get_battery_level()        # 0–100
            state = await bat.get_battery_state()        # BatteryState enum
            is_charging = str(state).lower() in ("batterystate.charging", "charging")

            # pick colour, icon and message based on level + charging
            if is_charging:
                bg      = "#e8f5e9"   # green tint
                icon    = ft.Icons.BATTERY_CHARGING_FULL
                icon_c  = SUCCESS
                message = f"Charging — {level}% 🔌  Good to go!"
            elif level < 20:
                bg      = "#ffebee"   # red tint
                icon    = ft.Icons.BATTERY_ALERT
                icon_c  = ERROR
                message = f"Battery critical: {level}% 🔴  Plug in before browsing listings!"
            elif level < 50:
                bg      = "#fff8e1"   # amber tint
                icon    = ft.Icons.BATTERY_2_BAR
                icon_c  = "#f57c00"
                message = f"Battery low: {level}% 🟡  Consider charging soon."
            else:
                bg      = "#e8f5e9"   # green tint
                icon    = ft.Icons.BATTERY_FULL
                icon_c  = SUCCESS
                message = f"Battery: {level}% 🟢"

            battery_icon.name  = icon
            battery_icon.color = icon_c
            battery_text.value = message
            battery_banner.bgcolor  = bg
            battery_banner.visible  = True
            page.update()

        except Exception as ex:
            battery_text.value      = f"Battery unavailable: {ex}"
            battery_banner.bgcolor  = "#f5f5f5"
            battery_banner.visible  = True
            page.update()

    # ── logout ────────────────────────────────────────────────
    def do_logout():
        threading.Thread(target=api.logout).start()
        go_to("login")

    # ── profile loader ────────────────────────────────────────
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
                        content=ft.Text(
                            p.get("user_type", "").capitalize(),
                            color="white", size=13,
                        ),
                        bgcolor=ACCENT,
                        padding=ft.padding.symmetric(horizontal=12, vertical=4),
                        border_radius=20,
                    ),
                    ft.Container(height=4),

                    # ── battery banner ────────────────────────
                    battery_banner,

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
                ]

                if p.get("user_type") in ["seller", "renter"]:
                    col.controls.append(
                        big_btn("🚗  My Listings", lambda e: go_to("my_vehicles"), width=280)
                    )
                    col.controls.append(ft.Container(height=8))

                col.controls += [
                    big_btn("Logout", lambda e: do_logout(), bg=ERROR, width=200),
                    ft.Container(height=20),
                ]

                page.update()

                # trigger battery check after profile renders
                page.run_task(_check_battery)

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