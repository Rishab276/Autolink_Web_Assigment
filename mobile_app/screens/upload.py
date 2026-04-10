import flet as ft
import requests
import threading
from shared import (
    api, APP_STATE, big_btn, field, nav,
    PRIMARY, ACCENT, BG, CARD_BG, TEXT_DARK, TEXT_LIGHT,
    SUCCESS, ERROR, CENTER, BASE_URL
)



def my_vehicles_screen(page, go_to):
    col    = ft.Column(spacing=12)
    status = ft.Text("", color=TEXT_LIGHT, text_align=ft.TextAlign.CENTER, size=14)
    spin   = ft.ProgressRing(visible=True, color=PRIMARY, width=30, height=30)

    def load():
        spin.visible = True; col.controls.clear(); page.update()
        def fetch():
            try:
                r = requests.get(f"{BASE_URL}/my-vehicles/", headers=api.h(), timeout=10)
                vehicles = r.json()
                spin.visible = False

                if not vehicles:
                    status.value = "You haven't listed any vehicles yet."
                    page.update()
                    return

                for v in vehicles:
                    images  = v.get("images", [])
                    img_url = images[0]["image"] if images else None

                    # Status badge
                    if v['is_sold']:
                        badge_text = "Sold"
                        badge_color = TEXT_LIGHT
                    elif v['is_rented']:
                        badge_text = "Rented"
                        badge_color = TEXT_LIGHT
                    else:
                        badge_text = "Active"
                        badge_color = SUCCESS

                    status_badge = ft.Container(
                        content=ft.Text(badge_text, size=10, color="white",
                                        weight=ft.FontWeight.W_600),
                        bgcolor=badge_color,
                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        border_radius=99,
                    )

                    def make_edit(veh):
                        def do(e):
                            APP_STATE["edit_vehicle"] = veh
                            go_to("edit_vehicle")
                        return do

                    def make_delete(veh):
                        def do(e):
                            def run():
                                try:
                                    requests.delete(
                                        f"{BASE_URL}/vehicles/{veh['id']}/delete/",
                                        headers=api.h(), timeout=10
                                    )
                                    load()
                                except:
                                    pass
                            threading.Thread(target=run).start()
                        return do

                    card = ft.Container(
                        content=ft.Row([
                            # Thumbnail
                            ft.Container(
                                content=ft.Image(src=img_url, fit=ft.BoxFit.COVER) if img_url
                                        else ft.Icon(ft.Icons.DIRECTIONS_CAR,
                                                     color="#c7d2fe", size=28),
                                width=80, height=80, bgcolor="#eef2ff",
                                border_radius=12, alignment=CENTER,
                                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                            ),
                            # Info
                            ft.Column([
                                ft.Row([
                                    ft.Text(f"{v['make']} {v['model']}", size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=TEXT_DARK, expand=True),
                                    status_badge,
                                ]),
                                ft.Text(
                                    f"{v['year']}  ·  {v['type_of_vehicle']}  ·  {v['fuel_type']}",
                                    size=12, color=TEXT_LIGHT,
                                ),
                                ft.Text(
                                    f"Rs {int(v['price']):,}",
                                    size=15, weight=ft.FontWeight.BOLD, color=ACCENT,
                                ),
                                ft.Row([
                                    ft.Container(
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.EDIT, color=PRIMARY, size=14),
                                            ft.Text("Edit", color=PRIMARY, size=12),
                                        ], spacing=4),
                                        on_click=make_edit(v),
                                        padding=ft.padding.symmetric(horizontal=10, vertical=6),
                                        border=ft.border.all(1, PRIMARY),
                                        border_radius=8, ink=True,
                                    ),
                                    ft.Container(
                                        content=ft.Row([
                                            ft.Icon(ft.Icons.DELETE_OUTLINE, color=ERROR, size=14),
                                            ft.Text("Delete", color=ERROR, size=12),
                                        ], spacing=4),
                                        on_click=make_delete(v),
                                        padding=ft.padding.symmetric(horizontal=10, vertical=6),
                                        border=ft.border.all(1, ERROR),
                                        border_radius=8, ink=True,
                                    ),
                                ], spacing=8),
                            ], spacing=4, expand=True),
                        ], spacing=12),
                        bgcolor=CARD_BG, border_radius=14,
                        padding=ft.padding.all(14),
                        shadow=ft.BoxShadow(
                            blur_radius=8, color="#12000000", offset=ft.Offset(0, 2)
                        ),
                    )
                    col.controls.append(card)
                page.update()

            except Exception as ex:
                spin.visible = False
                status.value = f"Error: {ex}"
                page.update()

        threading.Thread(target=fetch).start()

    load()

    return ft.View(
        route="/my_vehicles", bgcolor=BG, scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(
            title=ft.Text("My Listings", color="white"),
            bgcolor=PRIMARY,
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK, icon_color="white",
                on_click=lambda e: go_to("profile"),
            ),
            actions=[
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ADD, color="white", size=18),
                        ft.Text("Add New", color="white", size=13,
                                weight=ft.FontWeight.W_600),
                    ], spacing=4),
                    bgcolor=ACCENT, border_radius=10,
                    padding=ft.padding.symmetric(horizontal=14, vertical=8),
                    margin=ft.margin.only(right=12),
                    on_click=lambda e: go_to("upload_vehicle"),
                    ink=True,
                )
            ],
        ),
        controls=[
            ft.Container(
                padding=ft.padding.all(16),
                content=ft.Column(spacing=12, controls=[
                    ft.Row([spin], alignment=ft.MainAxisAlignment.CENTER),
                    status, col,
                    ft.Container(height=20),
                ]),
            )
        ]
    )


def upload_vehicle_screen(page, go_to):
    import os

    msg = ft.Text("", size=13, text_align=ft.TextAlign.CENTER)
    spin = ft.ProgressRing(visible=False, color=PRIMARY, width=30, height=30)

    # ---------------- FIELDS ----------------
    make_f = field("Make *")
    model_f = field("Model *")
    year_f = field("Year *", keyboard=ft.KeyboardType.NUMBER)
    mile_f = field("Mileage (km) *", keyboard=ft.KeyboardType.NUMBER)
    price_f = field("Price (Rs) *", keyboard=ft.KeyboardType.NUMBER)
    contact_f = field("Contact Number", keyboard=ft.KeyboardType.PHONE)
    gps_f = field("GPS Coordinates")

    desc_f = ft.TextField(
        label="Description",
        multiline=True,
        min_lines=3,
        border_color=PRIMARY,
        focused_border_color=ACCENT,
    )

    transmission = {"val": "Manual"}
    fuel_type = {"val": "Petrol"}
    vehicle_type = {"val": "Car"}

    selected_images = []

    # ---------------- IMAGE PICKER ----------------
    preview_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=10)

    picker = ft.FilePicker()
    page.overlay.append(picker)
    page.update()

    def on_pick(e):
        if e.files:
            selected_images.clear()
            selected_images.extend(e.files)

            preview_row.controls.clear()

            for file in selected_images:
                preview_row.controls.append(
                    ft.Stack([
                        ft.Image(
                            src=file.path,
                            width=90,
                            height=90,
                            fit=ft.BoxFit.COVER,
                            border_radius=10,
                        )
                    ])
                )

            page.update()

    picker.on_result = on_pick

    # ---------------- CHIPS ----------------
    def chip_selector(options, ref):
        row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8)

        def rebuild():
            row.controls.clear()
            for opt in options:
                active = ref["val"] == opt

                def click(e, v=opt):
                    ref["val"] = v
                    rebuild()
                    page.update()

                row.controls.append(
                    ft.Container(
                        content=ft.Text(
                            opt,
                            color="white" if active else TEXT_DARK,
                            size=12
                        ),
                        bgcolor=PRIMARY if active else CARD_BG,
                        border=ft.border.all(
                            1.5,
                            PRIMARY if active else "#d1d5db"
                        ),
                        border_radius=99,
                        padding=ft.padding.symmetric(
                            horizontal=14,
                            vertical=7
                        ),
                        on_click=click,
                        ink=True,
                    )
                )

        rebuild()
        return row

    type_row = chip_selector(
        ["Car", "SUV", "Motorbike", "Truck", "Van", "Bus"],
        vehicle_type
    )

    trans_row = chip_selector(
        ["Manual", "Automatic", "CVT", "Other"],
        transmission
    )

    fuel_row = chip_selector(
        ["Petrol", "Diesel", "Hybrid", "Electric", "Other"],
        fuel_type
    )

    # ---------------- UPLOAD ----------------
    def upload_vehicle(e):
        if not all([
            make_f.value,
            model_f.value,
            year_f.value,
            mile_f.value,
            price_f.value
        ]):
            msg.value = "Please fill all required fields."
            msg.color = ERROR
            page.update()
            return

        if not selected_images:
            msg.value = "Please add at least one vehicle image."
            msg.color = ERROR
            page.update()
            return

        spin.visible = True
        msg.value = ""
        page.update()

        def run():
            try:
                data = {
                    "make": make_f.value,
                    "model": model_f.value,
                    "year": year_f.value,
                    "mileage": mile_f.value,
                    "price": price_f.value,
                    "transmission": transmission["val"],
                    "fuel_type": fuel_type["val"],
                    "type_of_vehicle": vehicle_type["val"],
                    "desc": desc_f.value,
                    "contact": contact_f.value,
                    "gps_coor": gps_f.value,
                }

                files = []

                for img in selected_images:
                    files.append(
                        (
                            "images",
                            (
                                os.path.basename(img.path),
                                open(img.path, "rb"),
                                "image/jpeg"
                            )
                        )
                    )

                headers = api.h()
                headers.pop("Content-Type", None)

                r = requests.post(
                    f"{BASE_URL}/vehicles/upload/",
                    data=data,
                    files=files,
                    headers=headers,
                    timeout=30,
                )

                spin.visible = False

                if r.status_code == 201:
                    msg.value = "✅ Vehicle uploaded successfully!"
                    msg.color = SUCCESS

                    for f in [
                        make_f, model_f, year_f, mile_f,
                        price_f, contact_f, gps_f
                    ]:
                        f.value = ""

                    desc_f.value = ""
                    selected_images.clear()
                    preview_row.controls.clear()

                else:
                    msg.value = f"Upload failed: {r.text}"
                    msg.color = ERROR

            except Exception as ex:
                spin.visible = False
                msg.value = f"Error: {ex}"
                msg.color = ERROR

            page.update()

        threading.Thread(target=run).start()

    return ft.View(
        route="/upload_vehicle",
        bgcolor=BG,
        scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(
            title=ft.Text("Upload Vehicle", color="white"),
            bgcolor=PRIMARY,
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color="white",
                on_click=lambda e: go_to("my_vehicles"),
            ),
        ),
        controls=[
            ft.Container(
                padding=20,
                content=ft.Column([
                    make_f,
                    model_f,
                    ft.Row([year_f, mile_f]),
                    price_f,

                    ft.Text("Vehicle Type"),
                    type_row,

                    ft.Text("Transmission"),
                    trans_row,

                    ft.Text("Fuel Type"),
                    fuel_row,

                    desc_f,
                    contact_f,
                    gps_f,

                    ft.Divider(),

                    ft.Text("Vehicle Images", weight=ft.FontWeight.BOLD),

                    ft.Row([
                        ft.ElevatedButton(
                            "Choose Images",
                            icon=ft.Icons.IMAGE,
                            on_click=lambda e: picker.pick_files(
                                allow_multiple=True,
                                allowed_extensions=["jpg", "jpeg", "png"]
                            )
                        ),
                    ]),

                    preview_row,

                    msg,
                    spin,

                    big_btn("Upload Vehicle", upload_vehicle),
                    ft.Container(height=20),
                ])
            )
        ]
    )

def edit_vehicle_screen(page, go_to):
    v = APP_STATE.get("edit_vehicle")
    if not v:
        go_to("my_vehicles")
        return ft.View(route="/edit_vehicle")

    make_f    = field("Make");    make_f.value    = v.get("make", "")
    model_f   = field("Model");   model_f.value   = v.get("model", "")
    year_f    = field("Year",     keyboard=ft.KeyboardType.NUMBER)
    year_f.value = str(v.get("year", ""))
    mile_f    = field("Mileage",  keyboard=ft.KeyboardType.NUMBER)
    mile_f.value = str(v.get("mileage", ""))
    price_f   = field("Price (Rs)", keyboard=ft.KeyboardType.NUMBER)
    price_f.value = str(int(float(v.get("price", 0))))
    contact_f = field("Contact", keyboard=ft.KeyboardType.PHONE,
                      icon=ft.Icons.PHONE_OUTLINED)
    contact_f.value = v.get("contact", "")
    gps_f     = field("GPS Coordinates"); gps_f.value = v.get("gps_coor", "")
    desc_f    = ft.TextField(
        label="Description",
        multiline=True, min_lines=3,
        border_color=PRIMARY, focused_border_color=ACCENT,
        value=v.get("desc", ""),
    )

    msg  = ft.Text("", size=13, text_align=ft.TextAlign.CENTER)
    spin = ft.ProgressRing(visible=False, color=PRIMARY, width=30, height=30)

    def save(e):
        msg.value = ""; spin.visible = True; page.update()
        def call():
            try:
                r = requests.patch(
                    f"{BASE_URL}/vehicles/{v['id']}/update/",
                    json={
                        "make":     make_f.value,
                        "model":    model_f.value,
                        "year":     year_f.value,
                        "mileage":  mile_f.value,
                        "price":    price_f.value,
                        "desc":     desc_f.value,
                        "contact":  contact_f.value,
                        "gps_coor": gps_f.value,
                    },
                    headers=api.h(),
                    timeout=10,
                )
                if r.status_code == 200:
                    msg.color = SUCCESS
                    msg.value = "✅ Vehicle updated successfully!"
                else:
                    msg.color = ERROR
                    msg.value = "Update failed. Try again."
            except Exception as ex:
                msg.color = ERROR
                msg.value = f"Connection error: {ex}"
            finally:
                spin.visible = False; page.update()
        threading.Thread(target=call).start()

    return ft.View(
        route="/edit_vehicle", bgcolor=BG, scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(
            title=ft.Text("Edit Vehicle", color="white"),
            bgcolor=PRIMARY,
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK, icon_color="white",
                on_click=lambda e: go_to("my_vehicles"),
            ),
        ),
        controls=[
            ft.Container(
                padding=ft.padding.all(20),
                content=ft.Column(spacing=14, controls=[
                    ft.Text(
                        f"Editing: {v.get('make','')} {v.get('model','')}",
                        size=16, weight=ft.FontWeight.BOLD, color=TEXT_DARK,
                    ),
                    ft.Row([make_f, model_f], spacing=10),
                    ft.Row([year_f, mile_f], spacing=10),
                    price_f, desc_f, contact_f, gps_f,
                    msg, spin,
                    big_btn("Save Changes", save),
                    ft.Container(height=20),
                ]),
            )
        ]
    )
