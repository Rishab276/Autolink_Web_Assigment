from django.urls import path
from . import views

urlpatterns = [

    # ── HTML pages ────────────────────────────────────────────
    path("",                  views.review_page,         name="review_page"),
    path("report/",           views.report_page,         name="report_page"),
    path("recommendations/",  views.recommendations_view, name="recommendations"),
    path("submit/",           views.submit_review_html,  name="submit_review_html"),
    path("submit-report/",    views.submit_report_html,  name="submit_report_html"),

    # ── REST API (used by Flet mobile app) ────────────────────
    path("api/reviews/",                views.api_reviews_list,    name="api_reviews_list"),
    path("api/reviews/submit/",         views.api_submit_review,   name="api_submit_review"),
    path("api/reviews/report/",         views.api_report_review,   name="api_report_review"),
    path("api/reviews/report-vehicle/", views.api_report_vehicle,  name="api_report_vehicle"),
   
]