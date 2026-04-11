# screens/saved.py
# ─────────────────────────────────────────────────────────────
# SAVED VEHICLES SCREEN
# Owner: Salwan Cassam Maighun (2412258)
#
# FEATURE: Live Weather at Vehicle Location
#
#   Each saved vehicle card shows a natural-language sentence:
#   "This car is listed in Curepipe, currently 22°C and
#    raining — maybe visit tomorrow."
#
#   Two free REST APIs are called per vehicle (in background):
#     1. Nominatim (OpenStreetMap) — reverse geocode lat/lng
#        to get the city name. Free, no API key.
#     2. Open-Meteo — current temperature + weather code.
#        Free, no API key.
#
#   Vehicles with no gps_coor show a friendly fallback.
# ─────────────────────────────────────────────────────────────

import flet as ft
import threading
import requests
from shared import api, APP_STATE, nav, section
from shared import PRIMARY, ACCENT, BG, TEXT_LIGHT, TEXT_DARK, SUCCESS


# ── WMO weather code → human description ─────────────────────
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
            addr.get("city")
            or addr.get("town")
            or addr.get("village")
            or addr.get("suburb")
            or addr.get("county")
            or "this area"
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

    # ── build one vehicle card ────────────────────────────────
    def _build_card(v, on_tap, on_unsave):
        images  = v.get("images", [])
        img_url = images[0]["image"] if images else None

        # weather text — wraps freely, no Row wrapper
        weather_text = ft.Text(
            "Fetching location weather…",
            size=12,
            color=TEXT_LIGHT,
            italic=True,
            no_wrap=False,
        )
        weather_container = ft.Container(
            content=weather_text,
            bgcolor="#f0f4ff",
            border_radius=6,
            padding=ft.padding.symmetric(horizontal=10, vertical=6),
            margin=ft.margin.only(top=4),
        )

        img_box = ft.Container(
            content=ft.Image(src=img_url, fit=ft.BoxFit.COVER) if img_url
                    else ft.Icon(ft.Icons.DIRECTIONS_CAR, size=50, color=TEXT_LIGHT),
            height=160,
            bgcolor="#e0e0e0",
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
                badge,
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

        # ── background thread: reverse geocode + weather ──────
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
                vehicle_type = v.get("type_of_vehicle", "vehicle").lower()
                sentence = (
                    f"This {vehicle_type} is listed in {city}, "
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

    # ── load saved vehicles ───────────────────────────────────
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

                    col.controls.append(_build_card(v, tap_fn(v), unsave_fn(v)))

                page.update()

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
                    ft.Row([spin], alignment=ft.MainAxisAlignment.CENTER),
                    status,
                    col,
                ])
            )
        ]
    )