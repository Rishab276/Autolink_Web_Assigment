import flet as ft
import flet_map as fm
import asyncio

from shared import api, nav, PRIMARY, BG, APP_STATE

# -----------------------------
# CONFIG
# -----------------------------
DEFAULT_ZOOM = 12
TILE_URL = "https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}"

FALLBACK_LAT = -20.3185
FALLBACK_LNG = 57.5260


# -----------------------------
# HELPERS
# -----------------------------
def format_price(price):
    try:
        val = float(price)
        if val <= 0:
            return "0"
        if val >= 500_000:
            res = val / 1_000_000
            return f"{res:.2f}".rstrip("0").rstrip(".") + "M"
        if val >= 1_000:
            res = val / 1_000
            if res >= 100:
                return f"{int(res)}k"
            return f"{res:.2g}".rstrip("0").rstrip(".") + "k"
        return f"{int(val)}"
    except Exception:
        return "?"


# -----------------------------
# MAIN SCREEN
# -----------------------------
def nearby_screen(page: ft.Page, go_to, geo=None):
    """
    geo = ftg.Geolocator added via page.add() in main.py (mobile only).
    geo = None on web.
    """

    user_location = {"lat": FALLBACK_LAT, "lng": FALLBACK_LNG}
    state = {"vehicles": []}

    location_status = ft.Text(
        "📍 Tap button to get your location",
        size=12,
        color=ft.Colors.GREY,
    )

    map_container = ft.Container(
        expand=True,
        alignment=ft.Alignment(0, 0),
        content=ft.ProgressRing(color=PRIMARY),
    )

    # -----------------------------
    # MARKERS
    # -----------------------------
    def on_marker_click(vehicle):
        APP_STATE["sv"] = vehicle
        go_to("detail")

    def build_markers():
        markers = []
        for v in state["vehicles"]:
            gps = v.get("gps_coor")
            if not gps:
                continue
            try:
                lat, lng = gps.split(",")
                lat = float(lat.strip())
                lng = float(lng.strip())
                color = ft.Colors.BLUE if v.get("is_rental") else ft.Colors.RED
                price_label = format_price(v.get("price", 0))
                markers.append(
                    fm.Marker(
                        coordinates=fm.MapLatitudeLongitude(lat, lng),
                        content=ft.Container(
                            content=ft.Text(price_label, color="white", size=10, weight="bold"),
                            bgcolor=color,
                            padding=ft.Padding(5, 2, 5, 2),
                            border_radius=8,
                            border=ft.Border.all(1.5, "white"),
                            ink=True,
                            on_click=lambda e, veh=v: on_marker_click(veh),
                        ),
                    )
                )
            except Exception as ex:
                print(f"Marker error: {ex}")
                continue

        # User location marker
        markers.append(
            fm.Marker(
                coordinates=fm.MapLatitudeLongitude(
                    user_location["lat"], user_location["lng"]
                ),
                content=ft.Icon(ft.Icons.MY_LOCATION, color=ft.Colors.BLACK, size=30),
            )
        )
        return markers

    # -----------------------------
    # RENDER MAP
    # -----------------------------
    def render_map():
        map_container.content = fm.Map(
            expand=True,
            initial_center=fm.MapLatitudeLongitude(
                user_location["lat"], user_location["lng"]
            ),
            initial_zoom=DEFAULT_ZOOM,
            layers=[
                fm.TileLayer(url_template=TILE_URL),
                fm.MarkerLayer(markers=build_markers()),
            ],
        )
        map_container.alignment = None
        page.update()

    # -----------------------------
    # FETCH VEHICLES
    # -----------------------------
    def fetch_data():
        try:
            print("Fetching vehicles...")
            vehicles = api.vehicles()
            print(f"Loaded: {len(vehicles)}")
            state["vehicles"] = vehicles
            render_map()
        except Exception as e:
            print(f"Fetch error: {e}")
            map_container.content = ft.Text("Failed to load vehicles", color="red")
            page.update()

    # -----------------------------
    # GEOLOCATION
    # Matches official example exactly:
    #   await geo.request_permission(timeout=60)
    #   await geo.get_current_position()
    #   geo.on_position_change = handler
    # -----------------------------
    def handle_position_change(e):
        """Live tracking — fires when device moves."""
        user_location["lat"] = e.position.latitude
        user_location["lng"] = e.position.longitude
        location_status.value = f"📍 {e.position.latitude:.5f}, {e.position.longitude:.5f}"
        if state["vehicles"]:
            render_map()
        else:
            page.update()

    async def get_location(e):
        """Called when user taps 'Use My Location'."""
        if not geo:
            location_status.value = "⚠️ Location only works on mobile app"
            page.update()
            return

        # Attach live tracking handler
        geo.on_position_change = handle_position_change
        geo.on_error = lambda err: print(f"Geo error: {err.data}")

        # Step 1: request permission — timeout=60 matches official example
        location_status.value = "Requesting permission..."
        page.update()

        import flet_geolocator as ftg
        p = await geo.request_permission()
        print(f"Permission: {p}")

        if p not in (
            ftg.GeolocatorPermissionStatus.ALWAYS,
            ftg.GeolocatorPermissionStatus.WHILE_IN_USE,
        ):
            location_status.value = "⚠️ Permission denied — check phone settings"
            page.update()
            return

        # Step 2: get current position
        location_status.value = "Getting location..."
        page.update()

        pos = await geo.get_current_position()
        print(f"Position: {pos.latitude}, {pos.longitude}")

        user_location["lat"] = pos.latitude
        user_location["lng"] = pos.longitude
        location_status.value = f"📍 {pos.latitude:.5f}, {pos.longitude:.5f}"

        if state["vehicles"]:
            render_map()
        else:
            page.update()

    # -----------------------------
    # REFRESH
    # -----------------------------
    def on_refresh(e):
        map_container.content = ft.ProgressRing(color=PRIMARY)
        map_container.alignment = ft.Alignment(0, 0)
        page.update()
        fetch_data()

    # -----------------------------
    # LAYOUT
    # -----------------------------
    ui = ft.Column(
        expand=True,
        spacing=10,
        controls=[
            ft.Text("Explore Nearby", size=22, weight=ft.FontWeight.BOLD),

            # Legend
            ft.Row([
                ft.Container(width=12, height=12, bgcolor=ft.Colors.BLUE, border_radius=3),
                ft.Text("Rentals", size=13),
                ft.Container(width=10),
                ft.Container(width=12, height=12, bgcolor=ft.Colors.RED, border_radius=3),
                ft.Text("For Sale", size=13),
            ]),

            # Location button + status row
            ft.Row(
                [
                    ft.Button(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.MY_LOCATION, color="white", size=16),
                                ft.Text("Use My Location", color="white", size=13),
                            ],
                            tight=True,
                            spacing=6,
                        ),
                        style=ft.ButtonStyle(
                            bgcolor=PRIMARY,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.Padding(12, 8, 12, 8),
                        ),
                        on_click=get_location,  # ← async handler directly, no lambda
                        visible=not page.web,   # hide on web, only works on mobile
                    ),
                    location_status,
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),

            map_container,
        ],
    )

    fetch_data()

    return ft.View(
        route="/nearby",
        bgcolor=BG,
        navigation_bar=nav("nearby", go_to),
        appbar=ft.AppBar(
            bgcolor=PRIMARY,
            title=ft.Text("Vehicle Finder", color="white"),
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color="white",
                on_click=lambda _: go_to("home"),
            ),
            actions=[
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    icon_color="white",
                    on_click=on_refresh,
                )
            ],
        ),
        controls=[
            ft.Container(content=ui, padding=16, expand=True),
        ],
    )