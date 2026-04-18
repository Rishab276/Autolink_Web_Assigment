/*
    1. jQuery event registration (.on('click', ...))
    2. AJAX request using $.ajax() / $.get()
    3. JSON production: Django views return JsonResponse
    4. JSON consumption: data captured from AJAX response
       and used to update the DOM without page reload
 
  Features:
    A) Unsave a vehicle via AJAX POST — removes card from DOM
       when server confirms deletion (JSON: { success: true })
    B) Fetch live weather for each saved vehicle via AJAX GET
       and display it under the vehicle card
       (JSON: { success: true, sentence: "...", code: 61 })
*/

$(document).ready(function () {
    $(document).on('click', '.ajax-delete-vehicle', function (e) {
        e.preventDefault();

        const btn = $(this);
        const card = btn.closest('.vehicle-card');
        const url = btn.attr('href');

        if (!confirm('Delete this vehicle?')) return;

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': getCSRF()
            },
            success: function (res) {
                if (res.success) {
                    card.fadeOut(300, function () {
                        $(this).remove();
                    });
                }
            }
        });
    });


    $(document).on('click', '.ajax-toggle-sold', function (e) {
        e.preventDefault();

        const btn = $(this);
        const card = btn.closest('.vehicle-card');
        const url = btn.attr('href');

        $.ajax({
            url: url,
            type: 'POST',
            headers: { 'X-CSRFToken': getCSRF() },

            success: function (res) {
                if (res.status === 'sold') {
                    card.addClass('sold-card');
                } else {
                    card.removeClass('sold-card');
                }
            }
        });
    });


    $(document).on('click', '.ajax-toggle-rented', function (e) {
        e.preventDefault();

        const btn = $(this);
        const card = btn.closest('.vehicle-card');
        const url = btn.attr('href');

        $.ajax({
            url: url,
            type: 'POST',
            headers: { 'X-CSRFToken': getCSRF() },

            success: function (res) {
                if (res.status === 'rented') {
                    card.addClass('rented-card');
                } else {
                    card.removeClass('rented-card');
                }
            }
        });
    });


    $(document).on('click', '.ajax-unsave-btn', function (e) {
        e.preventDefault();

        const btn = $(this);
        const card = btn.closest('.saved-vehicle-card');
        const id = btn.data('vehicle-id');

        $.ajax({
            url: `/profile/ajax-unsave/${id}/`,
            type: 'POST',
            headers: { 'X-CSRFToken': getCSRF() },
            dataType: 'json',

            success: function (res) {
                if (res.success) {
                    card.fadeOut(300, () => card.remove());
                }
            }
        });
    });


    $('.saved-vehicle-card').each(function () {

        const card = $(this);
        const id = card.data('vehicle-id');

        $.get(`/profile/ajax-weather/${id}/`, function (res) {
            if (res.success) {
                card.find('.weather-info').html(res.sentence);
            }
        }, 'json');

    });

    function getCSRF() {
        return $('[name=csrfmiddlewaretoken]').val();
    }

});