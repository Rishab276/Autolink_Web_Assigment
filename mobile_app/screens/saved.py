# screens/saved.py
# ─────────────────────────────────────────────────────────────
# SAVED VEHICLES SCREEN
# Owner: Salwan Cassam Maighun (2412258)
#
# SENSOR FEATURE: Battery-Aware Power Saving Mode (ft.Battery)
#
#   When the screen loads, ft.Battery queries the device battery
#   level and charging state. If battery is below 20% AND the
#   phone is not charging, Power Saving Mode activates:
#     - Vehicle images are hidden to reduce network/CPU load
#     - A banner explains why with an override option
#   If battery >= 20% OR the phone is charging, full cards with
#   images are shown as normal.
# ─────────────────────────────────────────────────────────────

import flet as ft
import threading
from shared import api, APP_STATE, nav, section
from shared import PRIMARY, ACCENT, BG, TEXT_LIGHT, TEXT_DARK, SUCCESS, ERROR

# threshold for testing — set to 20 before submission
BATTERY_THRESHOLD = 95


def saved_screen(page: ft.Page, go_to):
    col    = ft.Column(spacing=12)
    status = ft.Text("", color=TEXT_LIGHT, text_align=ft.TextAlign.CENTER)
    spin   = ft.ProgressRing(visible=True, color=PRIMARY, width=30, height=30)

    power_saving = [False]
    saved_items  = [None]

    # ── power saving banner ───────────────────────────────────
    banner_text = ft.Text("", size=13, color="white", expand=True)
    power_banner = ft.Container(
        visible=False,
        bgcolor=ERROR,
        border_radius=8,
        padding=ft.padding.symmetric(horizontal=14, vertical=10),
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.BATTERY_ALERT, color="white", size=18),
                banner_text,
            ], spacing=8),
            ft.TextButton(
                "Show images anyway",
                style=ft.ButtonStyle(color="white"),
                on_click=lambda e: _disable_power_saving(),
            ),
        ], spacing=4),
    )

    def _disable_power_saving():
        power_saving[0]      = False
        power_banner.visible = False
        page.update()
        if saved_items[0]:
            _render_cards(saved_items[0])

    # ── lite card (no image) ──────────────────────────────────
    def _lite_card(v, on_tap, on_unsave):
        return ft.GestureDetector(
            on_tap=on_tap,
            content=ft.Card(
                elevation=2,
                content=ft.Container(
                    padding=ft.padding.all(14),
                    content=ft.Column([
                        ft.Row([
                            ft.Text(
                                f"{v['make']} {v['model']}",
                                size=15, weight=ft.FontWeight.BOLD,
                                color=TEXT_DARK, expand=True,
                            ),
                            ft.Container(
                                content=ft.Icon(ft.Icons.BOOKMARK, color=ACCENT, size=20),
                                on_click=on_unsave, padding=4,
                            ),
                        ]),
                        ft.Text(
                            f"{v['year']}  •  {v['type_of_vehicle']}  •  {v['fuel_type']}",
                            size=12, color=TEXT_LIGHT,
                        ),
                        ft.Text(
                            f"Rs {int(v['price']):,}{'  /month' if v['is_rental'] else ''}",
                            size=16, weight=ft.FontWeight.BOLD, color=ACCENT,
                        ),
                        ft.Container(
                            content=ft.Text(
                                "For Rent" if v["is_rental"] else "For Sale",
                                size=11, color="white",
                            ),
                            bgcolor=PRIMARY if v["is_rental"] else SUCCESS,
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            border_radius=10,
                        ),
                        ft.Row([
                            ft.Icon(ft.Icons.BATTERY_ALERT, size=12, color=TEXT_LIGHT),
                            ft.Text(
                                "Image hidden — Power Saving Mode",
                                size=11, color=TEXT_LIGHT, italic=True,
                            ),
                        ], spacing=4),
                    ], spacing=6),
                ),
            ),
        )

    # ── full card (with image) ────────────────────────────────
    def _full_card(v, on_tap, on_unsave):
        images  = v.get("images", [])
        img_url = images[0]["image"] if images else None

        img_box = ft.Container(
            content=ft.Image(src=img_url, fit=ft.BoxFit.COVER) if img_url
                    else ft.Icon(ft.Icons.DIRECTIONS_CAR, size=50, color=TEXT_LIGHT),
            height=160, bgcolor="#e0e0e0",
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            alignment=ft.alignment.Alignment(0, 0),
        )
        info = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(
                        f"{v['make']} {v['model']}",
                        size=15, weight=ft.FontWeight.BOLD,
                        color=TEXT_DARK, expand=True,
                    ),
                    ft.Container(
                        content=ft.Icon(ft.Icons.BOOKMARK, color=ACCENT, size=22),
                        on_click=on_unsave, padding=4,
                    ),
                ]),
                ft.Text(
                    f"{v['year']}  •  {v['type_of_vehicle']}  •  {v['fuel_type']}",
                    size=12, color=TEXT_LIGHT,
                ),
                ft.Text(
                    f"Rs {int(v['price']):,}{'  /month' if v['is_rental'] else ''}",
                    size=17, weight=ft.FontWeight.BOLD, color=ACCENT,
                ),
                ft.Container(
                    content=ft.Text(
                        "For Rent" if v["is_rental"] else "For Sale",
                        size=11, color="white",
                    ),
                    bgcolor=PRIMARY if v["is_rental"] else SUCCESS,
                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                    border_radius=10,
                ),
            ], spacing=5),
            padding=ft.padding.all(12),
        )
        return ft.GestureDetector(
            on_tap=on_tap,
            content=ft.Card(
                elevation=3,
                content=ft.Column([img_box, info], spacing=0),
            ),
        )

    # ── render cards based on power_saving state ──────────────
    def _render_cards(items):
        col.controls.clear()
        for item in items:
            v = item["vehicle"]

            def tap_fn(veh):
                def _tap(e):
                    APP_STATE["sv"] = veh
                    go_to("detail")
                return _tap

            def unsave_fn(veh):
                def _do(e):
                    def _run():
                        api.toggle_save(veh["id"])
                        _load()
                    threading.Thread(target=_run).start()
                return _do

            if power_saving[0]:
                col.controls.append(_lite_card(v, tap_fn(v), unsave_fn(v)))
            else:
                col.controls.append(_full_card(v, tap_fn(v), unsave_fn(v)))

        page.update()

    # ── battery check runs in its own thread (no async) ───────
    def _check_battery(items):
        try:
            import asyncio
            loop = asyncio.new_event_loop()

            async def _query():
                bat   = ft.Battery()
                level = await bat.get_battery_level()
                state = await bat.get_battery_state()
                return level, state

            level, state = loop.run_until_complete(_query())
            loop.close()

            is_charging = "charging" in str(state).lower()

            if level >= BATTERY_THRESHOLD or is_charging:
                power_saving[0]      = False
                power_banner.visible = False
            else:
                power_saving[0]   = True
                banner_text.value = (
                    f"⚡ Power Saving Mode — battery at {level}%. "
                    "Images hidden to save battery."
                )
                power_banner.visible = True

        except Exception as ex:
            # battery check failed — just show full cards
            power_saving[0] = False
            power_banner.visible = False

        page.update()
        _render_cards(items)

    # ── main loader ───────────────────────────────────────────
    def _load():
        spin.visible = True
        col.controls.clear()
        status.value = ""
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
                page.update()

                if not items:
                    status.value = "You haven't saved any vehicles yet."
                    page.update()
                    return

                saved_items[0] = items

                # run battery check in thread, then render
                threading.Thread(target=_check_battery, args=(items,)).start()

            except Exception as ex:
                spin.visible = False
                status.value = f"Error: {ex}"
                page.update()

        threading.Thread(target=fetch).start()

    _load()

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
                    power_banner,
                    ft.Row([spin], alignment=ft.MainAxisAlignment.CENTER),
                    status,
                    col,
                ])
            )
        ]
    )