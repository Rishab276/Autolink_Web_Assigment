# screens/login.py
# ─────────────────────────────────────────────────────────────
# LOGIN & REGISTER SCREENS
# Owner: Vigneshwar Bhewa (2411725)
# ─────────────────────────────────────────────────────────────

import flet as ft
import threading
from shared import api, APP_STATE, big_btn, link_btn, field
from shared import PRIMARY, ACCENT, BG, TEXT_LIGHT, SUCCESS, ERROR, CENTER


def login_screen(page, go_to):
    email_f = field("Email",    keyboard=ft.KeyboardType.EMAIL, icon=ft.Icons.EMAIL)
    pass_f  = field("Password", password=True,                  icon=ft.Icons.LOCK)
    msg     = ft.Text("", color=ERROR, text_align=ft.TextAlign.CENTER)
    spin    = ft.ProgressRing(visible=False, color=PRIMARY, width=30, height=30)

    def do_login(e):
        msg.value = ""
        if not email_f.value or not pass_f.value:
            msg.value = "Please fill in all fields."; page.update(); return
        spin.visible = True; page.update()

        def call():
            try:
                code, data = api.login(email_f.value, pass_f.value)
                if code == 200:
                    api.token     = data["token"]
                    api.user_name = data.get("name", "")
                    api.user_type = data.get("user_type", "")
                    go_to("home")
                else:
                    msg.value = data.get("error", "Login failed.")
            except Exception as ex:
                msg.value = f"Cannot connect. Is Django running?\n{ex}"
            finally:
                spin.visible = False; page.update()

        threading.Thread(target=call).start()

    return ft.View(route="/login", bgcolor=BG, scroll=ft.ScrollMode.AUTO, controls=[
        ft.Container(
            padding=ft.padding.symmetric(horizontal=30, vertical=20),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8,
                controls=[
                    ft.Container(height=60),
                    ft.Icon(ft.Icons.DIRECTIONS_CAR, size=80, color=PRIMARY),
                    ft.Text("AutoLink", size=36, weight=ft.FontWeight.BOLD, color=PRIMARY),
                    ft.Text("Your Vehicle Marketplace", size=14, color=TEXT_LIGHT),
                    ft.Container(height=20),
                    email_f, pass_f,
                    msg, spin,
                    big_btn("Login", do_login),
                    link_btn("Don't have an account? Register", lambda e: go_to("register")),
                ]
            )
        )
    ])


def register_screen(page, go_to):
    fname = field("First Name")
    lname = field("Last Name")
    email = field("Email",           keyboard=ft.KeyboardType.EMAIL)
    pwd   = field("Password",        password=True)
    pwd2  = field("Confirm Password", password=True)
    addr  = field("Address")
    phone = field("Contact Number",  keyboard=ft.KeyboardType.PHONE)
    lic   = field("Driver License (Sellers/Renters only)")

    utype = ft.Dropdown(
        label="I want to...", border_color=PRIMARY, value="buyer",
        options=[
            ft.dropdown.Option("buyer",  "Buy vehicles"),
            ft.dropdown.Option("seller", "Sell vehicles"),
            ft.dropdown.Option("renter", "Rent out vehicles"),
        ]
    )
    msg  = ft.Text("", text_align=ft.TextAlign.CENTER)
    spin = ft.ProgressRing(visible=False, color=PRIMARY, width=30, height=30)

    def do_register(e):
        msg.color = ERROR; msg.value = ""
        if pwd.value != pwd2.value:
            msg.value = "Passwords do not match."; page.update(); return
        if not all([fname.value, lname.value, email.value, pwd.value, addr.value, phone.value]):
            msg.value = "Please fill in all required fields."; page.update(); return

        spin.visible = True; page.update()

        def call():
            try:
                code, data = api.register({
                    "first_name":    fname.value,
                    "last_name":     lname.value,
                    "email":         email.value,
                    "password":      pwd.value,
                    "user_type":     utype.value,
                    "address":       addr.value,
                    "contact_number": phone.value,
                    "driver_license": lic.value or "",
                })
                if code == 201:
                    api.token = data["token"]
                    msg.color = SUCCESS; msg.value = "Account created!"; page.update()
                    import time; time.sleep(1); go_to("home")
                else:
                    first = next(iter(data.values()))
                    msg.value = first[0] if isinstance(first, list) else str(first)
            except Exception as ex:
                msg.value = f"Error: {ex}"
            finally:
                spin.visible = False; page.update()

        threading.Thread(target=call).start()

    return ft.View(
        route="/register", bgcolor=BG, scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(
            title=ft.Text("Create Account", color="white"), bgcolor=PRIMARY,
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK, icon_color="white",
                on_click=lambda e: go_to("login")
            )
        ),
        controls=[
            ft.Container(
                padding=ft.padding.symmetric(horizontal=24, vertical=16),
                content=ft.Column(
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Join AutoLink", size=22, weight=ft.FontWeight.BOLD, color=PRIMARY),
                        ft.Text("Create your free account", size=13, color=TEXT_LIGHT),
                        fname,
                        lname,
                        email, 
                        utype, 
                        pwd, 
                        pwd2, 
                        addr, 
                        phone, 
                        lic,
                        msg, 
                        spin,
                        big_btn("Create Account", do_register),
                        link_btn("Already have an account? Login", lambda e: go_to("login")),
                    ]
                )
            )
        ]
    )
