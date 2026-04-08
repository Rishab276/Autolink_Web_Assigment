# screens/reviews.py
# ─────────────────────────────────────────────────────────────
# REVIEWS SCREEN
# Owner: Humaa Faatimah Bukreedan (2412290)
# ─────────────────────────────────────────────────────────────

import flet as ft
import threading
from shared import api, big_btn, nav, section, field
from shared import PRIMARY, ACCENT, BG, TEXT_LIGHT, SUCCESS, ERROR


def reviews_screen(page, go_to):
    rev_col  = ft.Column(spacing=10)
    status   = ft.Text("", color=TEXT_LIGHT)
    spin     = ft.ProgressRing(visible=True, color=PRIMARY, width=30, height=30)

    # Write review fields
    title_f  = field("Review Title")
    body_f   = ft.TextField(
        label="Your Review", multiline=True, min_lines=3,
        border_color=PRIMARY,
    )
    author_f = field("Your Name")
    email_f  = field("Email", keyboard=ft.KeyboardType.EMAIL)
    rating_f = ft.Dropdown(
        label="Rating", border_color=PRIMARY, value="5",
        options=[ft.dropdown.Option(str(i), "⭐" * i) for i in range(1, 6)],
    )
    sub_msg  = ft.Text("", text_align=ft.TextAlign.CENTER)
    sub_spin = ft.ProgressRing(visible=False, color=PRIMARY, width=30, height=30)

    # Load existing reviews
    def load_reviews():
        def fetch():
            try:
                reviews = api.reviews()
                spin.visible = False
                if not reviews:
                    status.value = "No reviews yet. Be the first!"
                for r in reviews:
                    rev_col.controls.append(
                        ft.Card(elevation=2, content=ft.Container(
                            padding=ft.padding.all(14),
                            content=ft.Column(spacing=5, controls=[
                                ft.Row([
                                    ft.Text(r["title"], weight=ft.FontWeight.BOLD, size=15, expand=True),
                                    ft.Text("⭐" * r["rating"], size=13),
                                ]),
                                ft.Text(r["review_text"], size=13, color=TEXT_LIGHT),
                                ft.Text(f"— {r['author_name']}", size=12, color=ACCENT, italic=True),
                            ])
                        ))
                    )
                page.update()
            except Exception as ex:
                spin.visible = False
                status.value = f"Error: {ex}"
                page.update()

        threading.Thread(target=fetch).start()

    load_reviews()

    # Submit review
    def do_submit(e):
        sub_msg.value = ""
        if not all([title_f.value, body_f.value, author_f.value, email_f.value]):
            sub_msg.color = ERROR
            sub_msg.value = "Please fill in all fields."
            page.update()
            return

        sub_spin.visible = True
        page.update()

        def post():
            try:
                code, data = api.submit_review({
                    "title":       title_f.value,
                    "review_text": body_f.value,
                    "rating":      int(rating_f.value),
                    "author_name": author_f.value,
                    "email":       email_f.value,
                })
                if code == 201:
                    sub_msg.color = SUCCESS
                    sub_msg.value = "✅ Submitted! Awaiting approval."
                    title_f.value = body_f.value = author_f.value = email_f.value = ""
                else:
                    sub_msg.color = ERROR
                    sub_msg.value = str(data)
            except Exception as ex:
                sub_msg.color = ERROR
                sub_msg.value = f"Error: {ex}"
            finally:
                sub_spin.visible = False
                page.update()

        threading.Thread(target=post).start()

    return ft.View(
        route="/reviews", bgcolor=BG, scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(title=ft.Text("Reviews", color="white"), bgcolor=PRIMARY),
        navigation_bar=nav("reviews", go_to),
        controls=[
            ft.Container(
                padding=ft.padding.all(16),
                content=ft.Column(spacing=12, controls=[
                    section("Write a Review"),
                    ft.Card(elevation=3, content=ft.Container(
                        padding=ft.padding.all(16),
                        content=ft.Column(
                            spacing=10,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                title_f, rating_f, body_f,
                                author_f, email_f,
                                sub_msg, sub_spin,
                                big_btn("Submit Review", do_submit, width=250),
                            ]
                        )
                    )),
                    section("What People Say"),
                    ft.Row([spin], alignment=ft.MainAxisAlignment.CENTER),
                    status,
                    rev_col,
                ])
            )
        ]
    )
