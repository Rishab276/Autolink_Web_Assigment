import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import Review, Report


# ── HTML VIEWS (keep these as they were) ─────────────────────

def review_page(request):
    """Display the review page"""
    return render(request, 'Reviews/review.html')


def report_page(request):
    """Display the report page"""
    return render(request, 'Reviews/report.html')


def recommendations_view(request):
    return render(request, 'Reviews/recommendations.html')


# ── REST API ENDPOINTS (used by Flet mobile app) ─────────────

@csrf_exempt
@require_http_methods(["GET"])
def api_reviews_list(request):
    """
    GET /api/reviews/
    Returns all reviews as JSON — no approval filter,
    so submitted reviews show up immediately.
    """
    reviews = Review.objects.all().order_by("-created_at")
    data = []
    for r in reviews:
        data.append({
            "id":             r.id,
            "title":          r.title or "",
            "review_text":    r.review_text or "",
            "rating":         r.rating,
            "author_name":    r.author_name or "",
            "email":          r.email or "",
            "sentiment":      getattr(r, "sentiment", ""),
            "location_label": getattr(r, "location_label", ""),
            "latitude":       str(getattr(r, "latitude", "") or ""),
            "longitude":      str(getattr(r, "longitude", "") or ""),
            "created_at":     r.created_at.isoformat() if hasattr(r, "created_at") and r.created_at else "",
        })
    return JsonResponse(data, safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def api_submit_review(request):
    """
    POST /api/reviews/submit/
    Accepts JSON or multipart form data from the Flet app.
    Returns 201 on success.
    """
    try:
        # Try JSON body first, fall back to form data
        if request.content_type and "application/json" in request.content_type:
            body    = json.loads(request.body)
            title          = body.get("title", "")
            review_text    = body.get("review_text", "")
            rating         = body.get("rating", 5)
            author_name    = body.get("author_name", "")
            email          = body.get("email", "")
            sentiment      = body.get("sentiment", "")
            location_label = body.get("location_label", "")
            latitude       = body.get("latitude")
            longitude      = body.get("longitude")
        else:
            # multipart / form-data (when photo is attached)
            title          = request.POST.get("title", "")
            review_text    = request.POST.get("review_text", "")
            rating         = request.POST.get("rating", 5)
            author_name    = request.POST.get("author_name", "")
            email          = request.POST.get("email", "")
            sentiment      = request.POST.get("sentiment", "")
            location_label = request.POST.get("location_label", "")
            latitude       = request.POST.get("latitude")
            longitude      = request.POST.get("longitude")

        # Build kwargs — only pass fields that exist on the model
        kwargs = {
            "title":       title,
            "review_text": review_text,
            "rating":      int(rating) if rating else 5,
            "author_name": author_name,
            "email":       email,
        }

        # Optional fields — add only if the model has them
        try:
            Review._meta.get_field("sentiment")
            kwargs["sentiment"] = sentiment
        except Exception:
            pass

        try:
            Review._meta.get_field("location_label")
            kwargs["location_label"] = location_label
        except Exception:
            pass

        try:
            Review._meta.get_field("latitude")
            if latitude:
                kwargs["latitude"] = latitude
        except Exception:
            pass

        try:
            Review._meta.get_field("longitude")
            if longitude:
                kwargs["longitude"] = longitude
        except Exception:
            pass

        # Handle optional photo upload
        if "photo" in request.FILES:
            try:
                Review._meta.get_field("photo")
                kwargs["photo"] = request.FILES["photo"]
            except Exception:
                pass

        review = Review.objects.create(**kwargs)

        return JsonResponse({
            "id":      review.id,
            "message": "Review submitted successfully.",
        }, status=201)

    except Exception as ex:
        return JsonResponse({"error": str(ex)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_report_review(request):
    """
    POST /api/reviews/report/
    Report a specific review.
    """
    try:
        body      = json.loads(request.body)
        review_id = body.get("review_id")
        reason    = body.get("reason", "")
        details   = body.get("details", "")

        Report.objects.create(
            subject=f"Review report: {reason}",
            report_content=details,
            reporter_name="",
            email="",
        )
        return JsonResponse({"message": "Report submitted."}, status=201)
    except Exception as ex:
        return JsonResponse({"error": str(ex)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_report_vehicle(request):
    """
    POST /api/reviews/report-vehicle/
    Report a vehicle listing.
    """
    try:
        body        = json.loads(request.body)
        vehicle_ref = body.get("vehicle_ref", "")
        reason      = body.get("reason", "")
        details     = body.get("details", "")

        Report.objects.create(
            subject=f"Vehicle report [{vehicle_ref}]: {reason}",
            report_content=details,
            reporter_name="",
            email="",
        )
        return JsonResponse({"message": "Report submitted."}, status=201)
    except Exception as ex:
        return JsonResponse({"error": str(ex)}, status=400)


# ── ORIGINAL HTML FORM VIEWS — now return JsonResponse for AJAX ──

def submit_review_html(request):
    """Handle review form submission from HTML page (AJAX)"""
    if request.method == "POST":
        Review.objects.create(
            title=request.POST.get("title"),
            review_text=request.POST.get("review_text"),
            rating=request.POST.get("rating"),
            author_name=request.POST.get("author_name"),
            email=request.POST.get("email"),
        )
        return JsonResponse({"success": True, "message": "Review submitted successfully!"})
    return HttpResponse("Use POST method to submit review")


def submit_report_html(request):
    """Handle report form submission from HTML page (AJAX)"""
    if request.method == "POST":
        Report.objects.create(
            reporter_name=request.POST.get("reporter_name"),
            email=request.POST.get("email"),
            subject=request.POST.get("subject"),
            report_content=request.POST.get("report_content"),
        )
        return JsonResponse({"success": True, "message": "Report submitted successfully!"})
    return render(request, "Reviews/report.html")