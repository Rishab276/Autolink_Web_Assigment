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
    msg  = ft.Text("", size=13, text_align=ft.TextAlign.CENTER)
    spin = ft.ProgressRing(visible=False, color=PRIMARY, width=30, height=30)
    entries_col = ft.Column(spacing=20)

    def label(text):
        return ft.Text(text, size=12, color=TEXT_LIGHT, weight=ft.FontWeight.W_600)

    def make_entry(index):
        """Build one full vehicle form block and return (container, get_data_fn, remove_fn)."""
        make_f    = field("Make *")
        model_f   = field("Model *")
        year_f    = field("Year *",        keyboard=ft.KeyboardType.NUMBER)
        mile_f    = field("Mileage (km) *", keyboard=ft.KeyboardType.NUMBER)
        price_f   = field("Price (Rs) *",  keyboard=ft.KeyboardType.NUMBER)
        contact_f = field("Contact Number", keyboard=ft.KeyboardType.PHONE,
                          icon=ft.Icons.PHONE_OUTLINED)
        gps_f     = field("GPS Coordinates")
        desc_f    = ft.TextField(
            label="Description",
            multiline=True, min_lines=3,
            border_color=PRIMARY, focused_border_color=ACCENT,
        )

        trans_ref = {"val": "Manual"}
        fuel_ref  = {"val": "Petrol"}
        type_ref  = {"val": "Car"}

        trans_row = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8)
        fuel_row  = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8)
        type_row  = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8)

        def chip_row(options, ref, row_ctrl):
            def build():
                row_ctrl.controls.clear()
                for val in options:
                    active = ref["val"] == val
                    def click(e, v=val, r=ref, b=build):
                        r["val"] = v; b(); page.update()
                    row_ctrl.controls.append(ft.Container(
                        content=ft.Text(val, size=12, weight=ft.FontWeight.W_500,
                                        color="white" if active else TEXT_DARK),
                        bgcolor=PRIMARY if active else CARD_BG,
                        border=ft.border.all(1.5, PRIMARY if active else "#d1d5db"),
                        border_radius=99,
                        padding=ft.padding.symmetric(horizontal=14, vertical=7),
                        on_click=click, ink=True,
                    ))
                page.update()
            build()

        chip_row(["Manual", "Automatic", "CVT", "Other"],          trans_ref, trans_row)
        chip_row(["Petrol", "Diesel", "Hybrid", "Electric", "Other"], fuel_ref, fuel_row)
        chip_row(["Car", "SUV", "Motorbike", "Truck", "Van", "Bus"],  type_ref, type_row)

        # Wrapper ref so we can remove this block from entries_col
        wrapper_ref = {"ctrl": None}

        def remove(e):
            if len(entries_col.controls) > 1:
                entries_col.controls.remove(wrapper_ref["ctrl"])
                page.update()

        header = ft.Row(
            controls=[
                ft.Text(f"Vehicle {index}", size=15,
                        weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.IconButton(
                    icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                    icon_color=ERROR, tooltip="Remove this entry",
                    on_click=remove,
                    visible=(index > 1),   # hide remove on first card
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        block = ft.Container(
            bgcolor=CARD_BG,
            border_radius=16,
            padding=ft.padding.all(16),
            shadow=ft.BoxShadow(blur_radius=8, color="#12000000", offset=ft.Offset(0, 2)),
            content=ft.Column(spacing=12, controls=[
                header,
                ft.Divider(height=1, color="#e5e7eb"),
                ft.Row([make_f, model_f],   spacing=10),
                ft.Row([year_f, mile_f],    spacing=10),
                price_f,
                label("VEHICLE TYPE"),  type_row,
                label("TRANSMISSION"), trans_row,
                label("FUEL TYPE"),    fuel_row,
                desc_f,
                contact_f,
                gps_f,
            ]),
        )
        wrapper_ref["ctrl"] = block

        def get_data():
            return {
                "make":            make_f.value,
                "model":           model_f.value,
                "year":            year_f.value,
                "mileage":         mile_f.value,
                "price":           price_f.value,
                "transmission":    trans_ref["val"],
                "fuel_type":       fuel_ref["val"],
                "type_of_vehicle": type_ref["val"],
                "desc":            desc_f.value,
                "contact":         contact_f.value,
                "gps_coor":        gps_f.value,
            }

        def is_valid():
            return all([make_f.value, model_f.value,
                        year_f.value, mile_f.value, price_f.value])

        return block, get_data, is_valid

    # ── State tracking ────────────────────────────────────────────────
    form_registry = []   # list of (block, get_data, is_valid)

    def add_entry(e=None):
        idx = len(form_registry) + 1
        block, get_data, is_valid = make_entry(idx)
        form_registry.append((block, get_data, is_valid))
        entries_col.controls.append(block)
        page.update()

    # Add the first entry immediately
    add_entry()

    # ── Submit all ────────────────────────────────────────────────────
    def do_upload_all(e):
        msg.value = ""
        # Validate all entries
        for i, (_, _, is_valid) in enumerate(form_registry):
            if not is_valid():
                msg.color = ERROR
                msg.value = f"Vehicle {i+1}: please fill in all required (*) fields."
                page.update()
                return

        spin.visible = True
        page.update()

        def call():
            successes = 0
            errors    = []
            for i, (_, get_data, _) in enumerate(form_registry):
                try:
                    r = requests.post(
                        f"{BASE_URL}/vehicles/upload/",
                        json=get_data(),
                        headers=api.h(),
                        timeout=10,
                    )
                    if r.status_code == 201:
                        successes += 1
                    else:
                        data = r.json()
                        errors.append(f"Vehicle {i+1}: {data.get('error', 'failed')}")
                except Exception as ex:
                    errors.append(f"Vehicle {i+1}: connection error — {ex}")

            spin.visible = False
            if errors:
                msg.color = ERROR
                msg.value = "\n".join(errors)
            else:
                msg.color = SUCCESS
                msg.value = f"✅ {successes} vehicle(s) uploaded successfully!"
                # Clear all entries and reset to a single blank form
                form_registry.clear()
                entries_col.controls.clear()
                add_entry()
            page.update()

        threading.Thread(target=call).start()

    # ── "Add Another" button ──────────────────────────────────────────
    add_btn = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, color=PRIMARY, size=18),
            ft.Text("Add Another Vehicle", color=PRIMARY, size=13,
                    weight=ft.FontWeight.W_600),
        ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
        on_click=add_entry,
        padding=ft.padding.symmetric(vertical=14),
        border=ft.border.all(1.5, PRIMARY),
        border_radius=12,
        ink=True,
    )

    return ft.View(
        route="/upload_vehicle", bgcolor=BG, scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(
            title=ft.Text("List Vehicles", color="white"),
            bgcolor=PRIMARY,
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK, icon_color="white",
                on_click=lambda e: go_to("my_vehicles"),
            ),
        ),
        controls=[
            ft.Container(
                padding=ft.padding.all(20),
                content=ft.Column(spacing=16, controls=[
                    ft.Text("Vehicle Details", size=18,
                            weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                    entries_col,
                    add_btn,
                    ft.Container(height=4),
                    msg,
                    ft.Row([spin], alignment=ft.MainAxisAlignment.CENTER),
                    big_btn("Upload All Vehicles", do_upload_all),
                    ft.Container(height=20),
                ]),
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
