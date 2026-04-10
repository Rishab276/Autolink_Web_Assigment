# screens/saved.py
# ─────────────────────────────────────────────────────────────
# SAVED VEHICLES SCREEN
# Owner: Salwan Cassam Maighun (2412258)
#
# GEOLOCATION FEATURE: Sort Saved Vehicles by Distance
#   A "Sort by distance" button requests the device's current GPS
#   coordinates via flet-geolocator, then calls the REST API
#   endpoint GET /api/saved/?sort_by_distance=true&lat=X&lng=Y
#   which returns the user's saved vehicles ordered by proximity.
#   If a vehicle has no GPS coordinates stored, it is shown last.
#
# REQUIRES: pip install flet-geolocator==0.83.1
# ─────────────────────────────────────────────────────────────

import flet as ft
import threading
import math
from shared import api, APP_STATE, nav, v_card, section
from shared import PRIMARY, ACCENT, BG, TEXT_LIGHT, SUCCESS, ERROR, TEXT_DARK

# flet-geolocator is a separate package — import carefully
try:
    from flet_geolocator import (
        Geolocator,
        GeolocatorPositionAccuracy,
        GeolocatorPermissionStatus,
    )
    GEO_AVAILABLE = True
except ImportError:
    GEO_AVAILABLE = False


# ── local haversine (used client-side for distance labels) ────
def _haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def saved_screen(page: ft.Page, go_to):
    col    = ft.Column(spacing=12)
    status = ft.Text("", color=TEXT_LIGHT, text_align=ft.TextAlign.CENTER)
    spin   = ft.ProgressRing(visible=True, color=PRIMARY, width=30, height=30)

    # geo state
    geo_ref        = [None]    # holds Geolocator instance
    user_lat       = [None]
    user_lng       = [None]
    sort_active    = [False]   # True when distance sort is on

    # ── sort-toggle button (we keep a ref to update its label) ─
    sort_btn_text = ft.Text("📍 Sort by Distance", size=13, color="white")
    sort_btn = ft.Container(
        content=sort_btn_text,
        bgcolor=PRIMARY,
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
        ink=True,
        on_click=lambda e: _toggle_sort(),
        visible=GEO_AVAILABLE,
    )
    geo_status = ft.Text("", size=12, color=TEXT_LIGHT, italic=True)

    # ── geolocator setup ──────────────────────────────────────
    def _setup_geo():
        """Append Geolocator to page.overlay once."""
        if not GEO_AVAILABLE or geo_ref[0] is not None:
            return
        g = Geolocator()
        page.overlay.append(g)
        page.update()
        geo_ref[0] = g

    def _toggle_sort():
        if sort_active[0]:
            # turn off sort
            sort_active[0] = False
            sort_btn_text.value = "📍 Sort by Distance"
            sort_btn.bgcolor = PRIMARY
            geo_status.value = ""
            page.update()
            _load_vehicles()          # reload in default order
        else:
            # request location then sort
            geo_status.value = "Getting your location…"
            page.update()
            threading.Thread(target=_fetch_location_then_sort).start()

    def _fetch_location_then_sort():
        _setup_geo()
        g = geo_ref[0]
        if g is None:
            geo_status.value = "Geolocation not available."
            page.update()
            return
        try:
            # request permission first
            import asyncio

            async def _get_pos():
                perm = await g.request_permission(timeout=30)
                if perm not in (
                    GeolocatorPermissionStatus.ALWAYS,
                    GeolocatorPermissionStatus.WHILE_IN_USE,
                ):
                    return None
                pos = await g.get_current_position(
                    accuracy=GeolocatorPositionAccuracy.BEST
                )
                return pos

            loop = asyncio.new_event_loop()
            pos  = loop.run_until_complete(_get_pos())
            loop.close()

            if pos is None:
                geo_status.value = "Location permission denied."
                page.update()
                return

            user_lat[0] = pos.latitude
            user_lng[0] = pos.longitude
            sort_active[0] = True
            sort_btn_text.value = "✕ Clear Distance Sort"
            sort_btn.bgcolor = ACCENT
            geo_status.value = f"📍 ({pos.latitude:.4f}, {pos.longitude:.4f})"
            page.update()
            _load_vehicles(lat=pos.latitude, lng=pos.longitude)

        except Exception as ex:
            geo_status.value = f"Location error: {ex}"
            page.update()

    # ── vehicle loader ────────────────────────────────────────
    def _load_vehicles(lat=None, lng=None):
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

                # Call the API — pass lat/lng if we have them
                items = api.saved_sorted(lat=lat, lng=lng) if (lat and lng) else api.saved()
                spin.visible = False

                if not items:
                    status.value = "You haven't saved any vehicles yet."
                    page.update()
                    return

                for item in items:
                    v        = item["vehicle"]
                    distance = item.get("distance_km")  # present when sorted by API

                    # fallback: compute distance client-side from gps_coor
                    if distance is None and lat and lng:
                        gps = v.get("gps_coor", "")
                        if gps:
                            try:
                                parts    = gps.split(",")
                                v_lat    = float(parts[0].strip())
                                v_lng    = float(parts[1].strip())
                                distance = _haversine(lat, lng, v_lat, v_lng)
                            except (ValueError, IndexError):
                                pass

                    # distance badge shown below the card when sort is active
                    dist_badge = ft.Container()
                    if distance is not None:
                        dist_badge = ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.LOCATION_ON, size=14, color=PRIMARY),
                                    ft.Text(
                                        f"{distance:.1f} km away",
                                        size=12, color=PRIMARY,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ],
                                spacing=2,
                            ),
                            padding=ft.padding.only(left=12, bottom=8),
                        )

                    def tap_fn(veh):
                        def tap(e):
                            APP_STATE["sv"] = veh
                            go_to("detail")
                        return tap

                    def unsave_fn(veh):
                        def do(e):
                            def run():
                                api.toggle_save(veh["id"])
                                _load_vehicles(lat=user_lat[0], lng=user_lng[0])
                            threading.Thread(target=run).start()
                        return do

                    col.controls.append(
                        ft.Column([
                            v_card(v, on_tap=tap_fn(v), on_save=unsave_fn(v), saved=True),
                            dist_badge,
                        ], spacing=0)
                    )

                page.update()

            except Exception as ex:
                spin.visible = False
                status.value = f"Error: {ex}"
                page.update()

        threading.Thread(target=fetch).start()

    _load_vehicles()   # initial load (no sort)

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
                    # header row: title + sort button
                    ft.Row(
                        [
                            section("Your Saved Vehicles"),
                            sort_btn,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    geo_status,
                    ft.Row([spin], alignment=ft.MainAxisAlignment.CENTER),
                    status,
                    col,
                ])
            )
        ]
    )