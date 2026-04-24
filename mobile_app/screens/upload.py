''' 
use of geolocation
   instead of user has to input the location 
   manually, this a click on the icon, the location is loaded.

use of camera sensor
 user does not need to select photo and just
 a click from the phone camera and photo is taken

'''

import flet as ft
import flet_camera as fc
import requests
import threading
import os

from shared import (
    LOCAL_IMAGES, api, APP_STATE, big_btn, field, nav,
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
                    v_id=v.get("id")
                    if v_id in LOCAL_IMAGES:
                        img_src = LOCAL_IMAGES[v_id]
                    else:

                        images = v.get("images", [])
                        img_src = f"{BASE_URL}{images[0]['image']}" if images else None
                    if images:
      
                        raw_path = images[0].get("image")
                        if raw_path:
                            if raw_path.startswith("http"):
                                img_url = raw_path
                            else:
              
                                img_url = f"{BASE_URL}{raw_path}"

                 
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
                            ft.Container(
                                content=(
                                    ft.Image(
                                        src=img_src, 
                                        fit=ft.BoxFit.COVER
                                    ) if img_src else ft.Icon(
                                        ft.Icons.DIRECTIONS_CAR, 
                                        color="#c7d2fe", 
                                        size=28
                                    )
                                ),
                                width=80, height=80, 
                                bgcolor="#eef2ff",
                                border_radius=12, 
                                
                                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                            ),
                        
                          
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
        geo = page.data.get("geo")

        async def get_real_location(e):
            if not geo:
                msg.value = "Geolocator not available on this platform."
                msg.color = ERROR
                page.update()
                return

            # Visual feedback
            gps_f.hint_text = "Accessing GPS..."
            gps_f.update()

            try:
                # Check permissions first
                p = await geo.get_permission_status()
                if p != "granted":
                    p = await geo.request_permission()
                
                if p == "granted":
                    # Get the current position from hardware sensor
                    pos = await geo.get_current_position()
                    if pos:
                        gps_f.value = f"{pos.latitude}, {pos.longitude}"
                        msg.value = "GPS Location set successfully!"
                        msg.color = SUCCESS
                    else:
                        msg.value = "Could not retrieve GPS coordinates."
                        msg.color = ERROR
                else:
                    msg.value = "Location permission denied."
                    msg.color = ERROR

            except Exception as ex:
                msg.value = f"GPS Error: {ex}"
                msg.color = ERROR
            
            gps_f.hint_text = None
            page.update()
        gps_row = ft.Row([
            ft.Container(content=gps_f, expand=True), # Let the field take most space
            ft.IconButton(
                icon=ft.Icons.MY_LOCATION,
                icon_color=PRIMARY,
                tooltip="Get location ",
                on_click=get_real_location,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    bgcolor="#f0f2f5"
                )
            )
        ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)
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
        wrapper_ref = {"ctrl": None}

        def remove(e):
            if len(entries_col.controls) > 1:
               
                entries_col.controls.remove(wrapper_ref["ctrl"])
                
             
                for item in form_registry:
                    if item[0] == wrapper_ref["ctrl"]:  # Match by the UI block reference
                        form_registry.remove(item)
                        break
                        
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

        photo_path_ref = {"path": None}
        cam = fc.Camera(expand=True, preview_enabled=True)
        cam_container = ft.Container(
            content=cam, 
            height=250, 
            visible=False, 
            border_radius=10, 
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )
        img_preview = ft.Image(
            src="",
            width=80, height=80, 
            border_radius=8, 
            visible=False, 
            fit=ft.BoxFit.COVER
        )
        async def toggle_camera(e):
            if cam_container.visible:
                # Capture Photo
                try:
                    path = await cam.take_picture()
                    photo_path_ref["path"] = path
                    img_preview.src = path
                    img_preview.visible = True
                    cam_container.visible = False
                    cam_btn.text = "Retake Photo"
                    cam_btn.icon = ft.Icons.REPLAY
                    page.update()
                except Exception as err:
                    print(f"Error taking picture: {err}")
            else:
                # Open Viewfinder
                cam_container.visible = True
                page.update()  # <-- Must update page first so the camera is actually "on screen"
                
                try:
                   
                    cameras = await cam.get_available_cameras()
                    if not cameras:
                        print("No cameras found on this device!")
                        return
                    await cam.initialize(
                        description=cameras[0],
                        resolution_preset=fc.ResolutionPreset.HIGH
                    )
                    cam_btn.text = "Snap Photo!"
                    cam_btn.icon = ft.Icons.CAMERA
                    page.update()
                except Exception as err:
                    print(f"Failed to initialize camera: {err}")
        cam_btn = ft.ElevatedButton("Add Photo", icon=ft.Icons.CAMERA_ALT, on_click=toggle_camera)
        photo_row = ft.Row([cam_btn, img_preview], alignment=ft.MainAxisAlignment.START)
        block = ft.Container(
            bgcolor=CARD_BG,
            border_radius=16,
            padding=ft.padding.all(16),
            shadow=ft.BoxShadow(blur_radius=8, color="#12000000", offset=ft.Offset(0, 2)),
            content=ft.Column(spacing=12, controls=[
                header,
                ft.Divider(height=1, color="#e5e7eb"),
                label("VEHICLE PHOTO"),
                photo_row,
                cam_container,
                ft.Divider(height=1, color="#e5e7eb"),
                ft.Row([make_f, model_f],   spacing=10),
                ft.Row([year_f, mile_f],    spacing=10),
                price_f,
                label("VEHICLE TYPE"),  type_row,
                label("TRANSMISSION"), trans_row,
                label("FUEL TYPE"),    fuel_row,
                desc_f,
                contact_f,
                gps_row,
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
                "photo_path":      photo_path_ref["path"] 
            }

        def is_valid():
            def has_text(val):
                return val is not None and str(val).strip() != ""
            
            return all([
                has_text(make_f.value), 
                has_text(model_f.value),
                has_text(year_f.value), 
                has_text(mile_f.value), 
                has_text(price_f.value)
            ])

        return block, get_data, is_valid
    form_registry = []   # list of (block, get_data, is_valid)

    def add_entry(e=None):
        idx = len(form_registry) + 1
        block, get_data, is_valid = make_entry(idx)
        form_registry.append((block, get_data, is_valid))
        entries_col.controls.append(block)
        page.update()
    add_entry()

    def do_upload_all(e):
        msg.value = ""
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
            req_headers = api.h().copy()
            if "Content-Type" in req_headers and "json" in req_headers["Content-Type"]:
                del req_headers["Content-Type"]
            
            for i, (_, get_data, _) in enumerate(form_registry):
                data = get_data()
                photo_path = data.pop("photo_path", None)
                upload_files = {}
                try:
                    
                    if photo_path and os.path.exists(photo_path):
                        f=open(photo_path,"rb")
                        upload_files = {"image": f}

                    r = requests.post(
                        f"{BASE_URL}/vehicles/upload/",
                        data=data,          
                        files=upload_files,
                        headers=req_headers,
                        timeout=20,        
                    )
                    
                    if r.status_code == 201:
                        successes += 1
                        new_vehicle = r.json()
   
                    if photo_path:
                        LOCAL_IMAGES[new_vehicle["id"]] = photo_path
                    else:
                        
                       errors.append(f"Vehicle {i+1}: Server returned {r.status_code}")
                        
                except Exception as ex:
                    errors.append(f"Vehicle {i+1}: connection error — {ex}")
                
                finally:
                    # Cleanup the open file safely
                    if upload_files and "image" in upload_files:
                        upload_files["image"].close()

            spin.visible = False
            if errors:
                msg.color = ERROR
                msg.value = "\n".join(errors)
            else:
                msg.color = SUCCESS
                msg.value = f"✅ {successes} vehicle(s) uploaded successfully!"
                form_registry.clear()
                entries_col.controls.clear()
                add_entry()
            page.update()

        threading.Thread(target=call).start()


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

