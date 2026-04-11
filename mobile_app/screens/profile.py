# screens/profile.py
# ─────────────────────────────────────────────────────────────
# PROFILE SCREEN
# Owner: Salwan Maighun (2412258)
#
# SENSOR FEATURES:
#   1. ft.Battery — queries device battery level + charging
#      state on load. Shows a coloured banner:
#        🔴 < 20% not charging → critical warning
#        🟠 < 50% not charging → low warning
#        🟢 charging or > 50%  → all good
#
#   2. flet_camera (fc.Camera) — front camera selfie for
#      profile picture. User taps "Change Photo", camera
#      opens, they snap a selfie, it shows as their avatar.
#      "Delete Photo" reverts to initials avatar.
#      Camera is a hardware sensor unique to mobile devices.
# ─────────────────────────────────────────────────────────────

import flet as ft
import flet_camera as fc
import threading
from shared import api, big_btn, nav
from shared import PRIMARY, ACCENT, BG, TEXT_DARK, TEXT_LIGHT, ERROR, SUCCESS


def profile_screen(page: ft.Page, go_to):
    col  = ft.Column(spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    spin = ft.ProgressRing(visible=True, color=PRIMARY, width=30, height=30)

    # ── profile photo state ───────────────────────────────────
    photo_path   = [None]   # holds captured image path
    user_initial = ["U"]    # fallback initial letter

    # ── avatar display (switches between photo and initials) ──
    avatar_image = ft.Image(
        src="", fit=ft.BoxFit.COVER,
        width=90, height=90,
        visible=False,
    )
    avatar_initials = ft.CircleAvatar(
        content=ft.Text("U", size=36, color="white"),
        bgcolor=PRIMARY, radius=45,
        visible=True,
    )
    avatar_stack = ft.Stack(
        [
            ft.Container(
                content=avatar_initials,
                width=90, height=90,
                border_radius=45,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            ),
            ft.Container(
                content=avatar_image,
                width=90, height=90,
                border_radius=45,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            ),
        ],
        width=90, height=90,
    )

    def _show_photo(path):
        photo_path[0]           = path
        avatar_image.src        = path
        avatar_image.visible    = True
        avatar_initials.visible = False
        page.update()

    def _clear_photo():
        photo_path[0]           = None
        avatar_image.src        = ""
        avatar_image.visible    = False
        avatar_initials.visible = True
        cam_container.visible   = False
        cam_btn.text            = "Change Photo"
        cam_btn.icon            = ft.Icons.CAMERA_ALT
        page.update()

    # ── camera ────────────────────────────────────────────────
    cam = fc.Camera(expand=True, preview_enabled=True)
    cam_container = ft.Container(
        content=cam,
        height=280,
        visible=False,
        border_radius=12,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        margin=ft.margin.symmetric(horizontal=0),
    )

    async def _toggle_camera(e):
        if cam_container.visible:
            # snap photo
            try:
                path = await cam.take_picture()
                _show_photo(path)
                cam_container.visible = False
                cam_btn.text = "Retake Photo"
                cam_btn.icon = ft.Icons.REPLAY
                page.update()
            except Exception as err:
                page.snack_bar = ft.SnackBar(ft.Text(f"Camera error: {err}"))
                page.snack_bar.open = True
                page.update()
        else:
            # open camera
            cam_container.visible = True
            page.update()
            try:
                # 1. Fetch the list of physical cameras
                cameras = await cam.get_available_cameras()
                if not cameras:
                    page.snack_bar = ft.SnackBar(ft.Text("No camera found."))
                    page.snack_bar.open = True
                    page.update()
                    return

                # 2. Filter specifically for the FRONT lens
                # We use the fc.CameraLensDirection.FRONT enum for accuracy
                front = next(
                    (c for c in cameras if c.lens_direction == fc.CameraLensDirection.FRONT),
                    cameras[0] # Fallback to first camera if front isn't detected
                )

                # 3. Initialize the camera using the 'front' description
                await cam.initialize(
                    description=front,
                    resolution_preset=fc.ResolutionPreset.MEDIUM,
                )
                
                cam_btn.text = "Snap Selfie!"
                cam_btn.icon = ft.Icons.CAMERA
                page.update()

            except Exception as err:
                page.snack_bar = ft.SnackBar(ft.Text(f"Camera init error: {err}"))
                page.snack_bar.open = True
                cam_container.visible = False
                page.update()
                
    cam_btn = ft.ElevatedButton(
        "Change Photo",
        icon=ft.Icons.CAMERA_ALT,
        on_click=_toggle_camera,
        color="white",
        bgcolor=PRIMARY,
    )
    delete_btn = ft.TextButton(
        "Delete Photo",
        icon=ft.Icons.DELETE_OUTLINE,
        style=ft.ButtonStyle(color=ERROR),
        on_click=lambda e: _clear_photo(),
        visible=False,
    )

    # ── battery banner ────────────────────────────────────────
    battery_text = ft.Text(
        "", size=13, italic=True, no_wrap=False,
    )
    battery_banner = ft.Container(
        visible=False,
        border_radius=8,
        padding=ft.padding.symmetric(horizontal=14, vertical=10),
        content=battery_text,
    )

    async def _check_battery():
        try:
            bat         = ft.Battery()
            level       = await bat.get_battery_level()
            state       = await bat.get_battery_state()
            is_charging = "charging" in str(state).lower()

            if is_charging or level >= 50:
                battery_banner.bgcolor  = "#e8f5e9"
                battery_text.value      = f"🟢 Battery: {level}% {'(charging)' if is_charging else '— all good!'}"
                battery_text.color      = "#2e7d32"
            elif level >= 20:
                battery_banner.bgcolor  = "#fff3e0"
                battery_text.value      = f"🟠 Battery low: {level}% — consider charging soon."
                battery_text.color      = "#e65100"
            else:
                battery_banner.bgcolor  = "#ffebee"
                battery_text.value      = f"🔴 Battery critical: {level}% — plug in now!"
                battery_text.color      = ERROR

            battery_banner.visible = True
        except Exception:
            pass
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

                # set initial letter
                initial = (p.get("first_name") or "U")[0].upper()
                user_initial[0] = initial
                avatar_initials.content = ft.Text(initial, size=36, color="white")

                def tile(icon, lbl, val):
                    return ft.ListTile(
                        leading=ft.Icon(icon, color=PRIMARY),
                        title=ft.Text(lbl, size=12, color=TEXT_LIGHT),
                        subtitle=ft.Text(str(val or "N/A"), size=15, color=TEXT_DARK),
                    )

                col.controls += [
                    ft.Container(height=10),

                    # avatar
                    avatar_stack,

                    # camera controls
                    ft.Row(
                        [cam_btn, delete_btn],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                    ),

                    # camera viewfinder
                    cam_container,

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

                    # battery banner
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

                # show delete button only when photo exists
                def _watch_photo():
                    import time
                    while True:
                        time.sleep(0.5)
                        delete_btn.visible = photo_path[0] is not None
                        page.update()
                threading.Thread(target=_watch_photo, daemon=True).start()

                # check battery
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