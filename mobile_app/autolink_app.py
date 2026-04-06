# autolink_app.py
# AutoLink Mobile App — written specifically for Flet 0.84.0

import flet as ft
import requests
import threading

BASE_URL = "http://127.0.0.1:8000/api"

# Colors
PRIMARY    = "#1a237e"
ACCENT     = "#ff6f00"
BG         = "#f5f5f5"
CARD_BG    = "#ffffff"
TEXT_DARK  = "#212121"
TEXT_LIGHT = "#757575"
SUCCESS    = "#388e3c"
ERROR      = "#c62828"

# Alignment helper (flet 0.84 uses ft.alignment.Alignment(x,y))
CENTER = ft.alignment.Alignment(0, 0)


# ── API ──────────────────────────────────────────────────────
class API:
    def __init__(self):
        self.token = None

    def h(self):
        return {"Authorization": f"Token {self.token}"} if self.token else {}

    def login(self, email, pwd):
        r = requests.post(f"{BASE_URL}/login/", json={"email": email, "password": pwd}, timeout=10)
        return r.status_code, r.json()

    def register(self, data):
        r = requests.post(f"{BASE_URL}/register/", json=data, timeout=10)
        return r.status_code, r.json()

    def logout(self):
        try: requests.post(f"{BASE_URL}/logout/", headers=self.h(), timeout=10)
        except: pass
        self.token = None

    def profile(self):
        return requests.get(f"{BASE_URL}/profile/", headers=self.h(), timeout=10).json()

    def vehicles(self, search="", vtype=""):
        p = {}
        if search: p["search"] = search
        if vtype:  p["type"]   = vtype
        return requests.get(f"{BASE_URL}/vehicles/", params=p, timeout=10).json()

    def nearby(self, lat, lng, radius=20):
        return requests.get(f"{BASE_URL}/vehicles/nearby/", params={"lat": lat, "lng": lng, "radius": radius}, timeout=10).json()

    def saved(self):
        return requests.get(f"{BASE_URL}/saved/", headers=self.h(), timeout=10).json()

    def toggle_save(self, vid):
        return requests.post(f"{BASE_URL}/saved/toggle/{vid}/", headers=self.h(), timeout=10).json()

    def reviews(self):
        return requests.get(f"{BASE_URL}/reviews/", timeout=10).json()

    def submit_review(self, data):
        r = requests.post(f"{BASE_URL}/reviews/submit/", json=data, timeout=10)
        return r.status_code, r.json()

api = API()


# ── HELPERS ──────────────────────────────────────────────────
def big_btn(label, on_click, bg=None, fg="white", width=300):
    bg = bg or PRIMARY
    return ft.Container(
        content=ft.Text(label, color=fg, size=15, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.W_500),
        bgcolor=bg, border_radius=8, width=width,
        padding=ft.padding.symmetric(horizontal=20, vertical=14),
        alignment=CENTER, on_click=on_click, ink=True,
    )

def link_btn(label, on_click, color=None):
    color = color or PRIMARY
    return ft.TextButton(
        content=ft.Text(label, color=color, size=13),
        on_click=on_click,
    )

def field(label, password=False, keyboard=None, icon=None):
    return ft.TextField(
        label=label,
        password=password,
        can_reveal_password=password,
        keyboard_type=keyboard,
        prefix_icon=icon,
        border_color=PRIMARY,
        focused_border_color=ACCENT,
    )

def spinner():
    return ft.ProgressRing(color=PRIMARY, width=30, height=30)

def section(text):
    return ft.Text(text, size=20, weight=ft.FontWeight.BOLD, color=PRIMARY)


# ── NAVIGATION BAR ───────────────────────────────────────────
ROUTES = ["home", "nearby", "saved", "reviews", "profile"]

def nav(selected, go_to):
    return ft.NavigationBar(
        selected_index=ROUTES.index(selected),
        bgcolor=CARD_BG,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME,        label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.LOCATION_ON, label="Nearby"),
            ft.NavigationBarDestination(icon=ft.Icons.BOOKMARK,    label="Saved"),
            ft.NavigationBarDestination(icon=ft.Icons.STAR,        label="Reviews"),
            ft.NavigationBarDestination(icon=ft.Icons.PERSON,      label="Profile"),
        ],
        on_change=lambda e: go_to(ROUTES[e.control.selected_index]),
    )


# ── VEHICLE CARD ─────────────────────────────────────────────
def v_card(v, on_tap, on_save=None, saved=False):
    images = v.get("images", [])
    img_url = images[0]["image"] if images else None

    img_box = ft.Container(
        content=ft.Image(src=img_url, fit=ft.BoxFit.COVER) if img_url
                else ft.Icon(ft.Icons.DIRECTIONS_CAR, size=50, color=TEXT_LIGHT),
        height=160, bgcolor="#e0e0e0",
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        alignment=CENTER,
    )

    save_btn = ft.Container(
        content=ft.Icon(
            ft.Icons.BOOKMARK if saved else ft.Icons.BOOKMARK_BORDER,
            color=ACCENT if saved else TEXT_LIGHT, size=22,
        ),
        on_click=on_save, padding=4,
    ) if on_save else ft.Container()

    badge = ft.Container(
        content=ft.Text("For Rent" if v['is_rental'] else "For Sale", size=11, color="white"),
        bgcolor=PRIMARY if v['is_rental'] else SUCCESS,
        padding=ft.padding.symmetric(horizontal=8, vertical=3),
        border_radius=10,
    )

    info = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text(f"{v['make']} {v['model']}", size=15, weight=ft.FontWeight.BOLD, color=TEXT_DARK, expand=True),
                save_btn,
            ]),
            ft.Text(f"{v['year']}  •  {v['type_of_vehicle']}  •  {v['fuel_type']}", size=12, color=TEXT_LIGHT),
            ft.Text(
                f"Rs {int(v['price']):,}{'  /month' if v['is_rental'] else ''}",
                size=17, weight=ft.FontWeight.BOLD, color=ACCENT,
            ),
            badge,
        ], spacing=5),
        padding=ft.padding.all(12),
    )

    return ft.GestureDetector(
        content=ft.Card(content=ft.Column([img_box, info], spacing=0), elevation=3),
        on_tap=on_tap,
    )


# ── LOGIN ────────────────────────────────────────────────────
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
                    api.token = data["token"]
                    page.session.set("name", data.get("name",""))
                    go_to("home")
                else:
                    msg.value = data.get("error", "Login failed.")
            except Exception as ex:
                msg.value = f"Cannot connect. Is Django running?\n{ex}"
            finally:
                spin.visible = False; page.update()
        threading.Thread(target=call).start()

    return ft.View(route="/login", bgcolor=BG, scroll=ft.ScrollMode.AUTO, controls=[
        ft.Container(padding=ft.padding.symmetric(horizontal=30, vertical=20), content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8, controls=[
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
        ))
    ])


# ── REGISTER ─────────────────────────────────────────────────
def register_screen(page, go_to):
    fname = field("First Name")
    lname = field("Last Name")
    email = field("Email", keyboard=ft.KeyboardType.EMAIL)
    pwd   = field("Password", password=True)
    pwd2  = field("Confirm Password", password=True)
    addr  = field("Address")
    phone = field("Contact Number", keyboard=ft.KeyboardType.PHONE)
    lic   = field("Driver License (Sellers/Renters only)")
    utype = ft.Dropdown(label="I want to...", border_color=PRIMARY, value="buyer", options=[
        ft.dropdown.Option("buyer",  "Buy vehicles"),
        ft.dropdown.Option("seller", "Sell vehicles"),
        ft.dropdown.Option("renter", "Rent out vehicles"),
    ])
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
                    "first_name": fname.value, "last_name": lname.value,
                    "email": email.value, "password": pwd.value,
                    "user_type": utype.value, "address": addr.value,
                    "contact_number": phone.value, "driver_license": lic.value or "",
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

    return ft.View(route="/register", bgcolor=BG, scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(title=ft.Text("Create Account", color="white"), bgcolor=PRIMARY,
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda e: go_to("login"))),
        controls=[ft.Container(padding=ft.padding.symmetric(horizontal=24, vertical=16), content=ft.Column(
            spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.Text("Join AutoLink", size=22, weight=ft.FontWeight.BOLD, color=PRIMARY),
                ft.Text("Create your free account", size=13, color=TEXT_LIGHT),
                ft.Row([fname, lname], spacing=10),
                email, utype, pwd, pwd2, addr, phone, lic,
                msg, spin,
                big_btn("Create Account", do_register),
                link_btn("Already have an account? Login", lambda e: go_to("login")),
            ]
        ))]
    )


# ── HOME ─────────────────────────────────────────────────────
def home_screen(page, go_to):
    search_f = ft.TextField(hint_text="Search make, model...", prefix_icon=ft.Icons.SEARCH,
                            border_radius=30, border_color=PRIMARY, expand=True)
    type_f   = ft.Dropdown(hint_text="All Types", width=130, border_color=PRIMARY, value="", options=[
        ft.dropdown.Option("", "All Types"), ft.dropdown.Option("Car", "Cars"),
        ft.dropdown.Option("Motorbike", "Motorbikes"), ft.dropdown.Option("Truck", "Trucks"),
        ft.dropdown.Option("Bus", "Buses"), ft.dropdown.Option("Van", "Vans"),
        ft.dropdown.Option("SUV", "SUVs"),
    ])
    col    = ft.Column(spacing=12)
    status = ft.Text("", color=TEXT_LIGHT, text_align=ft.TextAlign.CENTER)
    spin   = ft.ProgressRing(visible=True, color=PRIMARY, width=30, height=30)
    saved_ids: set = set()

    def load(e=None):
        spin.visible = True; col.controls.clear(); status.value = ""; page.update()
        def fetch():
            nonlocal saved_ids
            try:
                if api.token:
                    try: saved_ids = {s["vehicle"]["id"] for s in api.saved()}
                    except: saved_ids = set()
                vehicles = api.vehicles(search=search_f.value, vtype=type_f.value or "")
                spin.visible = False
                if not vehicles:
                    status.value = "No vehicles found."; page.update(); return
                for v in vehicles:
                    def tap_fn(veh): return lambda e: (page.session.set("sv", veh), go_to("detail"))
                    def save_fn(veh):
                        def do(e):
                            if not api.token: go_to("login"); return
                            def run(): 
                                r = api.toggle_save(veh["id"])
                                if r.get("saved"): saved_ids.add(veh["id"])
                                else: saved_ids.discard(veh["id"])
                                load()
                            threading.Thread(target=run).start()
                        return do
                    col.controls.append(v_card(v, on_tap=tap_fn(v), on_save=save_fn(v), saved=(v["id"] in saved_ids)))
                page.update()
            except Exception as ex:
                spin.visible = False; status.value = f"Error: {ex}"; page.update()
        threading.Thread(target=fetch).start()

    load()

    def do_logout(e):
        threading.Thread(target=api.logout).start(); go_to("login")

    actions = [ft.IconButton(icon=ft.Icons.LOGOUT, icon_color="white", on_click=do_logout)] if api.token \
              else [ft.TextButton(content=ft.Text("Login", color="white"), on_click=lambda e: go_to("login"))]

    return ft.View(route="/home", bgcolor=BG, scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(bgcolor=PRIMARY, actions=actions,
            title=ft.Row([ft.Icon(ft.Icons.DIRECTIONS_CAR, color="white"), ft.Text("AutoLink", color="white", weight=ft.FontWeight.BOLD)])),
        navigation_bar=nav("home", go_to),
        controls=[ft.Container(padding=ft.padding.all(16), content=ft.Column(spacing=10, controls=[
            ft.Row([search_f, type_f], spacing=8),
            big_btn("Search", load, bg=ACCENT),
            section("Available Vehicles"),
            ft.Row([spin], alignment=ft.MainAxisAlignment.CENTER),
            status, col,
        ]))]
    )


# ── DETAIL ───────────────────────────────────────────────────
def detail_screen(page, go_to):
    vehicle = page.session.get("sv")
    if not vehicle: go_to("home"); return ft.View(route="/detail")

    saved_ids: set = set()
    if api.token:
        try: saved_ids = {s["vehicle"]["id"] for s in api.saved()}
        except: pass

    is_saved = vehicle["id"] in saved_ids
    save_txt  = ft.Text("Unsave" if is_saved else "Save", color="white", size=14)
    save_box  = ft.Container(
        content=ft.Row([ft.Icon(ft.Icons.BOOKMARK, color="white", size=16), save_txt], spacing=6),
        bgcolor=ACCENT if is_saved else PRIMARY, border_radius=8,
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
        alignment=CENTER, ink=True, expand=True,
    )

    def toggle(e):
        if not api.token: go_to("login"); return
        def run():
            r = api.toggle_save(vehicle["id"])
            s = r.get("saved", False)
            save_txt.value = "Unsave" if s else "Save"
            save_box.bgcolor = ACCENT if s else PRIMARY
            page.update()
        threading.Thread(target=run).start()
    save_box.on_click = toggle

    def irow(icon, lbl, val):
        return ft.Row([
            ft.Icon(icon, size=18, color=PRIMARY),
            ft.Text(f"{lbl}:", weight=ft.FontWeight.BOLD, size=13, width=110),
            ft.Text(str(val), size=13, color=TEXT_LIGHT, expand=True),
        ])

    images = vehicle.get("images", [])
    imgs = [ft.Container(content=ft.Image(src=i["image"], fit=ft.BoxFit.COVER), height=240) for i in images] or \
           [ft.Container(content=ft.Icon(ft.Icons.DIRECTIONS_CAR, size=80, color=TEXT_LIGHT), height=240, bgcolor="#e0e0e0", alignment=CENTER)]

    wa = ft.Container(
        content=ft.Row([ft.Icon(ft.Icons.CHAT, color="white", size=16), ft.Text("WhatsApp", color="white", size=14)], spacing=6),
        bgcolor="#25D366", border_radius=8,
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
        alignment=CENTER, ink=True, expand=True,
        on_click=lambda e: page.launch_url(f"https://wa.me/{vehicle.get('contact','')}"),
    ) if vehicle.get("contact") else ft.Container()

    return ft.View(route="/detail", bgcolor=BG, scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(bgcolor=PRIMARY,
            title=ft.Text(f"{vehicle['make']} {vehicle['model']}", color="white"),
            leading=ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda e: go_to("home"))),
        controls=[ft.Column(spacing=0, controls=[
            ft.ListView(controls=imgs, height=240),
            ft.Container(padding=ft.padding.all(20), content=ft.Column(spacing=12, controls=[
                ft.Row([
                    ft.Column(expand=True, controls=[
                        ft.Text(f"{vehicle['make']} {vehicle['model']} {vehicle['year']}", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Rs {int(vehicle['price']):,}{'  /month' if vehicle['is_rental'] else ''}", size=18, color=ACCENT, weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Container(
                        content=ft.Text("For Rent" if vehicle['is_rental'] else "For Sale", color="white", size=12),
                        bgcolor=PRIMARY if vehicle['is_rental'] else SUCCESS,
                        padding=ft.padding.symmetric(horizontal=10, vertical=5), border_radius=20,
                    ),
                ]),
                ft.Divider(),
                section("Specifications"),
                irow(ft.Icons.SPEED,             "Mileage",      f"{vehicle['mileage']:,} km"),
                irow(ft.Icons.SETTINGS,          "Transmission", vehicle['transmission']),
                irow(ft.Icons.LOCAL_GAS_STATION, "Fuel Type",    vehicle['fuel_type']),
                irow(ft.Icons.CATEGORY,          "Type",         vehicle['type_of_vehicle']),
                irow(ft.Icons.PERSON,            "Listed by",    vehicle.get('uploader_name','N/A')),
                ft.Divider(),
                section("Description"),
                ft.Text(vehicle.get('desc') or "No description provided.", size=14, color=TEXT_LIGHT),
                ft.Divider(),
                ft.Row([save_box, wa], spacing=10),
                ft.Text(f"📍 GPS: {vehicle.get('gps_coor','N/A')}", size=12, color=TEXT_LIGHT),
                ft.Container(height=20),
            ])),
        ])]
    )


# ── NEARBY ───────────────────────────────────────────────────
def nearby_screen(page, go_to):
    col    = ft.Column(spacing=12)
    status = ft.Text("Tap the button to find vehicles near you.", color=TEXT_LIGHT, text_align=ft.TextAlign.CENTER)
    spin   = ft.ProgressRing(visible=False, color=PRIMARY, width=30, height=30)
    r_lbl  = ft.Text("Search radius: 20 km", color=TEXT_DARK)
    slider = ft.Slider(min=5, max=50, value=20, divisions=9, active_color=PRIMARY,
                       label="{value} km", on_change=lambda e: (setattr(r_lbl, 'value', f"Search radius: {int(slider.value)} km"), page.update()))

    def find(e):
        spin.visible = True; status.value = "Getting your GPS location..."; col.controls.clear(); page.update()
        try:
            gl = ft.Geolocator(location_settings=ft.GeolocatorSettings(accuracy=ft.GeolocatorPositionAccuracy.HIGH))
            page.overlay.append(gl); page.update()
            def on_pos(pos):
                lat, lng = pos.latitude, pos.longitude
                status.value = f"📍 {lat:.4f}, {lng:.4f} — Searching..."; page.update()
                def fetch():
                    try:
                        data     = api.nearby(lat, lng, int(slider.value))
                        vehicles = data.get("vehicles", [])
                        count    = data.get("count", 0)
                        spin.visible = False
                        status.value = f"Found {count} vehicle(s) near you:" if count else f"No vehicles within {int(slider.value)} km."
                        for v in vehicles:
                            def tap_fn(veh): return lambda e2: (page.session.set("sv", veh), go_to("detail"))
                            col.controls.append(v_card(v, on_tap=tap_fn(v)))
                        try: page.overlay.remove(gl)
                        except: pass
                        page.update()
                    except Exception as ex:
                        spin.visible = False; status.value = f"Error: {ex}"; page.update()
                threading.Thread(target=fetch).start()
            gl.get_current_position(on_pos)
        except Exception as ex:
            spin.visible = False; status.value = f"GPS error: {ex}"; page.update()

    return ft.View(route="/nearby", bgcolor=BG, scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(title=ft.Text("Vehicles Near Me", color="white"), bgcolor=PRIMARY),
        navigation_bar=nav("nearby", go_to),
        controls=[ft.Container(padding=ft.padding.all(20), content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10, controls=[
                ft.Icon(ft.Icons.LOCATION_ON, size=60, color=ACCENT),
                ft.Text("Find Vehicles Near You", size=22, weight=ft.FontWeight.BOLD, color=PRIMARY, text_align=ft.TextAlign.CENTER),
                ft.Text("Uses your phone's GPS to find nearby listings.", size=13, color=TEXT_LIGHT, text_align=ft.TextAlign.CENTER),
                r_lbl, slider,
                big_btn("📍 Find Nearby Vehicles", find, bg=ACCENT, width=280),
                ft.Row([spin], alignment=ft.MainAxisAlignment.CENTER),
                status, col,
            ]
        ))]
    )


# ── SAVED ────────────────────────────────────────────────────
def saved_screen(page, go_to):
    col    = ft.Column(spacing=12)
    status = ft.Text("", color=TEXT_LIGHT, text_align=ft.TextAlign.CENTER)
    spin   = ft.ProgressRing(visible=True, color=PRIMARY, width=30, height=30)

    def load():
        spin.visible = True; col.controls.clear(); page.update()
        def fetch():
            try:
                if not api.token:
                    spin.visible = False; status.value = "Please login to view saved vehicles."; page.update(); return
                items = api.saved(); spin.visible = False
                if not items:
                    status.value = "You haven't saved any vehicles yet."; page.update(); return
                for item in items:
                    v = item["vehicle"]
                    def tap_fn(veh): return lambda e: (page.session.set("sv", veh), go_to("detail"))
                    def unsave_fn(veh):
                        def do(e):
                            def run(): api.toggle_save(veh["id"]); load()
                            threading.Thread(target=run).start()
                        return do
                    col.controls.append(v_card(v, on_tap=tap_fn(v), on_save=unsave_fn(v), saved=True))
                page.update()
            except Exception as ex:
                spin.visible = False; status.value = f"Error: {ex}"; page.update()
        threading.Thread(target=fetch).start()
    load()

    return ft.View(route="/saved", bgcolor=BG, scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(title=ft.Text("Saved Vehicles", color="white"), bgcolor=PRIMARY),
        navigation_bar=nav("saved", go_to),
        controls=[ft.Container(padding=ft.padding.all(16), content=ft.Column(spacing=12, controls=[
            section("Your Saved Vehicles"),
            ft.Row([spin], alignment=ft.MainAxisAlignment.CENTER),
            status, col,
        ]))]
    )


# ── REVIEWS ──────────────────────────────────────────────────
def reviews_screen(page, go_to):
    rev_col  = ft.Column(spacing=10)
    status   = ft.Text("", color=TEXT_LIGHT)
    spin     = ft.ProgressRing(visible=True, color=PRIMARY, width=30, height=30)
    title_f  = field("Review Title")
    body_f   = ft.TextField(label="Your Review", multiline=True, min_lines=3, border_color=PRIMARY)
    author_f = field("Your Name")
    email_f  = field("Email", keyboard=ft.KeyboardType.EMAIL)
    rating_f = ft.Dropdown(label="Rating", border_color=PRIMARY, value="5",
                           options=[ft.dropdown.Option(str(i), "⭐"*i) for i in range(1,6)])
    sub_msg  = ft.Text("", text_align=ft.TextAlign.CENTER)
    sub_spin = ft.ProgressRing(visible=False, color=PRIMARY, width=30, height=30)

    def load_reviews():
        def fetch():
            try:
                reviews = api.reviews(); spin.visible = False
                if not reviews: status.value = "No reviews yet. Be the first!"
                for r in reviews:
                    rev_col.controls.append(ft.Card(elevation=2, content=ft.Container(
                        padding=ft.padding.all(14),
                        content=ft.Column(spacing=5, controls=[
                            ft.Row([ft.Text(r["title"], weight=ft.FontWeight.BOLD, size=15, expand=True), ft.Text("⭐"*r["rating"], size=13)]),
                            ft.Text(r["review_text"], size=13, color=TEXT_LIGHT),
                            ft.Text(f"— {r['author_name']}", size=12, color=ACCENT, italic=True),
                        ])
                    )))
                page.update()
            except Exception as ex:
                spin.visible = False; status.value = f"Error: {ex}"; page.update()
        threading.Thread(target=fetch).start()
    load_reviews()

    def do_submit(e):
        sub_msg.value = ""
        if not all([title_f.value, body_f.value, author_f.value, email_f.value]):
            sub_msg.color = ERROR; sub_msg.value = "Please fill in all fields."; page.update(); return
        sub_spin.visible = True; page.update()
        def post():
            try:
                code, data = api.submit_review({"title": title_f.value, "review_text": body_f.value, "rating": int(rating_f.value), "author_name": author_f.value, "email": email_f.value})
                if code == 201:
                    sub_msg.color = SUCCESS; sub_msg.value = "✅ Submitted! Awaiting approval."
                    title_f.value = body_f.value = author_f.value = email_f.value = ""
                else:
                    sub_msg.color = ERROR; sub_msg.value = str(data)
            except Exception as ex:
                sub_msg.color = ERROR; sub_msg.value = f"Error: {ex}"
            finally:
                sub_spin.visible = False; page.update()
        threading.Thread(target=post).start()

    return ft.View(route="/reviews", bgcolor=BG, scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(title=ft.Text("Reviews", color="white"), bgcolor=PRIMARY),
        navigation_bar=nav("reviews", go_to),
        controls=[ft.Container(padding=ft.padding.all(16), content=ft.Column(spacing=12, controls=[
            section("Write a Review"),
            ft.Card(elevation=3, content=ft.Container(padding=ft.padding.all(16), content=ft.Column(
                spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[title_f, rating_f, body_f, author_f, email_f, sub_msg, sub_spin, big_btn("Submit Review", do_submit, width=250)],
            ))),
            section("What People Say"),
            ft.Row([spin], alignment=ft.MainAxisAlignment.CENTER),
            status, rev_col,
        ]))]
    )


# ── PROFILE ──────────────────────────────────────────────────
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
                    ]; page.update(); return
                p = api.profile(); spin.visible = False

                def tile(icon, lbl, val):
                    return ft.ListTile(
                        leading=ft.Icon(icon, color=PRIMARY),
                        title=ft.Text(lbl, size=12, color=TEXT_LIGHT),
                        subtitle=ft.Text(str(val or "N/A"), size=15, color=TEXT_DARK),
                    )

                col.controls += [
                    ft.Container(height=10),
                    ft.CircleAvatar(
                        content=ft.Text((p.get("first_name") or "U")[0].upper(), size=36, color="white"),
                        bgcolor=PRIMARY, radius=45,
                    ),
                    ft.Text(f"{p.get('first_name','')} {p.get('last_name','')}", size=22, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                    ft.Container(
                        content=ft.Text(p.get("user_type","").capitalize(), color="white", size=13),
                        bgcolor=ACCENT, padding=ft.padding.symmetric(horizontal=12, vertical=4), border_radius=20,
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
                    big_btn("Logout", lambda e: do_logout(), bg=ERROR, width=200),
                ]
                page.update()
            except Exception as ex:
                spin.visible = False; col.controls.append(ft.Text(f"Error: {ex}", color=ERROR)); page.update()
        threading.Thread(target=fetch).start()

    def do_logout():
        threading.Thread(target=api.logout).start(); go_to("login")

    load()

    return ft.View(route="/profile", bgcolor=BG, scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(title=ft.Text("My Profile", color="white"), bgcolor=PRIMARY),
        navigation_bar=nav("profile", go_to),
        controls=[ft.Container(padding=ft.padding.all(16), content=ft.Column(spacing=10, controls=[
            ft.Row([spin], alignment=ft.MainAxisAlignment.CENTER), col,
        ]))]
    )


# ── MAIN ─────────────────────────────────────────────────────
def main(page: ft.Page):
    page.title        = "AutoLink"
    page.theme_mode   = ft.ThemeMode.LIGHT
    page.bgcolor      = BG
    page.window_width  = 400
    page.window_height = 800
    page.padding      = 0

    screens = {
        "login":    login_screen,
        "register": register_screen,
        "home":     home_screen,
        "detail":   detail_screen,
        "nearby":   nearby_screen,
        "saved":    saved_screen,
        "reviews":  reviews_screen,
        "profile":  profile_screen,
    }

    def go_to(route):
        page.views.clear()
        if route in screens:
            page.views.append(screens[route](page, go_to))
        page.update()

    go_to("login")


ft.app(target=main)
