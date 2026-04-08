# AutoLink Mobile App

## How to run
```
python main.py
```
Make sure Django is running in another terminal first.

## Folder structure
```
mobile_app/
├── main.py              ← Entry point. Run this. DO NOT MODIFY.
├── shared.py            ← API, theme colours, shared components. Ask Salwan before changing.
├── README.md            ← This file
└── screens/
    ├── __init__.py      ← Leave empty
    ├── login.py         ← Vigneshwar (2411725) — Login & Register
    ├── home.py          ← Keshni    (2412390) — Home screen
    ├── detail.py        ← Rishab    (2412024) — Vehicle detail
    ├── nearby.py        ← Rishab    (2412024) — GPS nearby
    ├── saved.py         ← Salwan    (2412258) — Saved vehicles
    ├── reviews.py       ← Humaa     (2412290) — Reviews
    └── profile.py       ← Vigneshwar (2411725) — Profile
```

## Rules for the team
1. Only edit YOUR file(s). Do not touch other people's files.
2. Do not modify `main.py` or `shared.py` without telling everyone.
3. To navigate to another screen, use: `go_to("screen_name")`
4. To pass data between screens, use: `APP_STATE["key"] = value` (imported from shared)
5. To read data from another screen: `APP_STATE.get("key")`
6. To use the API: `api.vehicles()`, `api.login()` etc. (imported from shared)
7. Push to your own branch on GitHub, then merge.

## Available routes
| Route        | Screen            | Owner       |
|-------------|-------------------|-------------|
| `"login"`   | Login page        | Vigneshwar  |
| `"register"`| Register page     | Vigneshwar  |
| `"home"`    | Browse vehicles   | Keshni      |
| `"detail"`  | Vehicle details   | Rishab      |
| `"nearby"`  | GPS nearby        | Rishab      |
| `"saved"`   | Saved vehicles    | Salwan      |
| `"reviews"` | Reviews           | Humaa       |
| `"profile"` | Profile page      | Vigneshwar  |

## Adding a new screen
1. Create `screens/yourscreen.py`
2. Define `def yourscreen_screen(page, go_to):`
3. Import it in `main.py`
4. Add it to the `SCREENS` dict in `main.py`
