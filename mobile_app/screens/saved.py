# screens/saved.py
# ─────────────────────────────────────────────────────────────
# SAVED VEHICLES SCREEN
# Owner: Salwan Cassam Maighun (2412258)
#
# FEATURE 1: Live Weather at Vehicle Location
#   Each card shows a natural-language weather sentence using:
#     - Nominatim (OpenStreetMap) for reverse geocoding
#     - Open-Meteo for current weather
#
# FEATURE 2: Sort by My Location
#   A button gets the user's approximate location via IP
#   geolocation (ipapi.co — free, no key, pure requests.get)
#   then sorts saved vehicles by distance (nearest first)
#   and shows a distance badge on each card.
# ─────────────────────────────────────────────────────────────

import flet as ft
import threading
import requests
import math
from shared import api, APP_STATE, nav, section
from shared import PRIMARY, ACCENT, BG, TEXT_LIGHT, TEXT_DARK, SUCCESS, ERROR
from flet_geolocator import Geolocator


# ── helpers ───────────────────────────────────────────────────
def _haversine(lat1, lon1, lat2, lon2):
    R    = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a    = (math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _get_my_location():
    """Approximate user location via IP geolocation. Returns (lat, lng, city) or None."""
    try:
        r = requests.get("https://ipapi.co/json/", timeout=6)
        r.raise_for_status()
        data = r.json()
        return float(data["latitude"]), float(data["longitude"]), data.get("city", "your location")
    except Exception:
        return None, None, None


def _weather_desc(code):
    if code == 0:                return "clear skies ☀️"
    elif code in (1, 2):         return "partly cloudy 🌤️"
    elif code == 3:              return "overcast ☁️"
    elif code in range(45, 50):  return "foggy 🌫️"
    elif code in range(51, 58):  return "drizzling 🌦️"
    elif code in range(61, 68):  return "raining 🌧️"
    elif code in range(71, 78):  return "snowing ❄️"
    elif code in range(80, 83):  return "rain showers 🌦️"
    elif code in range(95, 100): return "thunderstorming ⛈️"
    return "mixed conditions 🌡️"


def _maybe_visit(code):
    if code == 0:                return "great day to visit!"
    elif code in (1, 2):         return "not a bad day to visit."
    elif code == 3:              return "maybe bring a jacket."
    elif code in range(45, 50):  return "drive carefully if you visit."
    elif code in range(51, 68):  return "maybe visit tomorrow."
    elif code in range(71, 78):  return "best to wait for better weather."
    elif code in range(80, 83):  return "maybe visit tomorrow."
    elif code in range(95, 100): return "best to wait for better weather."
    return "check before visiting."


def _get_city(lat, lng):
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lng, "format": "json"},
            headers={"User-Agent": "AutoLink-MobileApp/1.0"},
            timeout=6,
        )
        r.raise_for_status()
        addr = r.json().get("address", {})
        return (
            addr.get("city") or addr.get("town") or addr.get("village")
            or addr.get("suburb") or addr.get("county") or "this area"
        )
    except Exception:
        return None


def _get_weather(lat, lng):
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude":      lat,
                "longitude":     lng,
                "current":       "temperature_2m,weather_code",
                "forecast_days": 1,
            },
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()
        return (
            data["current"]["temperature_2m"],
            data["current_units"]["temperature_2m"],
            data["current"]["weather_code"],
        )
    except Exception:
        return None, None, None


def saved_screen(page: ft.Page, go_to):
    col    = ft.Column(spacing=12)
    status = ft.Text("", color=TEXT_LIGHT, text_align=ft.TextAlign.CENTER)
    spin   = ft.ProgressRing(visible=True, color=PRIMARY, width=30, height=30)

    saved_items  = [None]
    sort_active  = [False]
    user_coords  = [None]   # (lat, lng, city)

    # ── sort button ───────────────────────────────────────────
    sort_label = ft.Text("📍 Sort by My Location", size=13, color="white")
    sort_spin  = ft.ProgressRing(
        visible=False, color="white", width=14, height=14, stroke_width=2,
    )
    sort_btn = ft.Container(
        content=ft.Row([sort_spin, sort_label], spacing=6,
                       alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=PRIMARY,
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
        ink=True,
        on_click=lambda e: threading.Thread(target=_toggle_sort).start(),
    )
    location_status = ft.Text("", size=11, color=TEXT_LIGHT, italic=True)

    def _toggle_sort():
        if sort_active[0]:
            # clear sort
            sort_active[0]      = False
            sort_label.value    = "📍 Sort by My Location"
            sort_btn.bgcolor    = PRIMARY
            location_status.value = ""
            page.update()
            _render_cards(saved_items[0], user_lat=None, user_lng=None)
            return

        # show spinner
        sort_spin.visible   = True
        sort_label.value    = "Getting location…"
        sort_btn.bgcolor    = "#455a64"
        location_status.value = ""
        page.update()

        lat, lng, city = _get_my_location()

        if lat is None:
            sort_spin.visible  = False
            sort_label.value   = "📍 Sort by My Location"
            sort_btn.bgcolor   = PRIMARY
            location_status.value = "Could not get location. Check internet."
            page.update()
            return

        user_coords[0]        = (lat, lng, city)
        sort_active[0]        = True
        sort_spin.visible     = False
        sort_label.value      = "✕ Clear Sort"
        sort_btn.bgcolor      = ACCENT
        location_status.value = f"📍 Sorting from: {city}"
        page.update()

        _render_cards(saved_items[0], user_lat=lat, user_lng=lng)

    # ── build one card ────────────────────────────────────────
    def _build_card(v, on_tap, on_unsave, distance_km=None):
        images  = v.get("images", [])
        img_url = images[0]["image"] if images else None

        weather_text = ft.Text(
            "Fetching location weather…",
            size=12, color=TEXT_LIGHT, italic=True, no_wrap=False,
        )
        weather_container = ft.Container(
            content=weather_text,
            bgcolor="#f0f4ff",
            border_radius=6,
            padding=ft.padding.symmetric(horizontal=10, vertical=6),
            margin=ft.margin.only(top=4),
        )

        # distance badge — only shown when sort is active
        dist_badge = ft.Container(
            visible=distance_km is not None,
            content=ft.Row([
                ft.Icon(ft.Icons.NEAR_ME, size=13, color="white"),
                ft.Text(
                    f"{distance_km:.1f} km away" if distance_km is not None else "",
                    size=12, color="white", weight=ft.FontWeight.W_500,
                ),
            ], spacing=4),
            bgcolor=ACCENT,
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=10, vertical=3),
            margin=ft.margin.only(bottom=2),
        )

        img_box = ft.Container(
            content=ft.Image(src=img_url, fit=ft.BoxFit.COVER) if img_url
                    else ft.Icon(ft.Icons.DIRECTIONS_CAR, size=50, color=TEXT_LIGHT),
            height=160, bgcolor="#e0e0e0",
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            alignment=ft.alignment.Alignment(0, 0),
        )

        badge = ft.Container(
            content=ft.Text(
                "For Rent" if v["is_rental"] else "For Sale",
                size=11, color="white",
            ),
            bgcolor=PRIMARY if v["is_rental"] else SUCCESS,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
            border_radius=10,
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
                ft.Row([badge, dist_badge], spacing=6),
                weather_container,
            ], spacing=5),
            padding=ft.padding.all(12),
        )

        card = ft.GestureDetector(
            on_tap=on_tap,
            content=ft.Card(
                elevation=3,
                content=ft.Column([img_box, info], spacing=0),
            ),
        )

        # fetch weather in background
        def _load_weather(gps):
            if not gps:
                weather_text.value        = "Location not set for this listing."
                weather_text.italic       = True
                weather_container.bgcolor = "#f5f5f5"
                page.update()
                return
            try:
                parts = gps.split(",")
                lat   = float(parts[0].strip())
                lng   = float(parts[1].strip())
            except (ValueError, IndexError):
                weather_text.value = "Invalid coordinates."
                page.update()
                return

            city             = _get_city(lat, lng) or "this area"
            temp, unit, code = _get_weather(lat, lng)

            if temp is not None:
                vtype    = v.get("type_of_vehicle", "vehicle").lower()
                sentence = (
                    f"This {vtype} is listed in {city}, "
                    f"currently {temp}{unit} and {_weather_desc(code)} "
                    f"— {_maybe_visit(code)}"
                )
                weather_text.value        = sentence
                weather_text.italic       = False
                weather_text.color        = TEXT_DARK
                weather_container.bgcolor = "#fff3e0" if code >= 61 else "#f0f4ff"
            else:
                weather_text.value        = f"Weather unavailable for {city}."
                weather_text.italic       = True
                weather_container.bgcolor = "#f5f5f5"

            page.update()

        threading.Thread(
            target=_load_weather, args=(v.get("gps_coor", ""),)
        ).start()

        return card

    # ── render cards (with optional distance sort) ────────────
    def _render_cards(items, user_lat=None, user_lng=None):
        col.controls.clear()

        # compute distances if we have user location
        annotated = []
        for item in items:
            v   = item["vehicle"]
            gps = v.get("gps_coor", "")
            dist = None
            if user_lat is not None and gps:
                try:
                    parts = gps.split(",")
                    v_lat = float(parts[0].strip())
                    v_lng = float(parts[1].strip())
                    dist  = _haversine(user_lat, user_lng, v_lat, v_lng)
                except (ValueError, IndexError):
                    pass
            annotated.append((dist, v))

        # sort: vehicles with distance first (nearest), no-GPS last
        if user_lat is not None:
            with_dist    = [(d, v) for d, v in annotated if d is not None]
            without_dist = [(d, v) for d, v in annotated if d is None]
            with_dist.sort(key=lambda x: x[0])
            annotated = with_dist + without_dist

        for dist, v in annotated:
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

            col.controls.append(
                _build_card(v, tap_fn(v), unsave_fn(v), distance_km=dist)
            )

        page.update()

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
                _render_cards(items)

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
                    ft.Row(
                        [section("Your Saved Vehicles"), sort_btn],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    location_status,
                    ft.Row([spin], alignment=ft.MainAxisAlignment.CENTER),
                    status,
                    col,
                ])
            )
        ]
    )