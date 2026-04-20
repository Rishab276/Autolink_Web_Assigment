/*FIRST SEMESTER JAVASCRIPT FILE FOR PROFILE PAGE - SAVE BUTTON LOGIC*/

/*document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.fav-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const userType = this.getAttribute('data-user-type');

            // Visitor has to login as a buyer to save vehicles
            if (userType === 'visitor') {
                e.preventDefault();
                alert('Login as a buyer to save vehicles');
            }
            // Seller cannot save vehicles
            else if (userType === 'seller') {
                e.preventDefault();
                alert('Sellers cannot save vehicles. You can only view and browse.');
            }
            // Renter cannot save vehicles
            else if (userType === 'renter') {
                e.preventDefault();
                alert('Renters cannot save vehicles. You can only view and browse.');
            }
            // Buyer unsaving a vehicle from his profile (Red Heart) - confirm before unsaving
            else if (userType === 'buyer' && this.textContent.includes('❤️')) {
                e.preventDefault();
                if (confirm('Are you sure you want to unsave this vehicle?')) {
                    window.location.href = this.getAttribute('href');
                }
            }
            // Buyer saving a vehicle (Grey Heart) - no confirmation needed
        });
    });
});
*/

/*SECOND SEMESTER FILE FOR PROFILE PAGE - SAVE BUTTON LOGIC USING JQUERY*/
/* Save Button Role-Based Logic */
$(document).ready(function () {

    function getCSRF() {
        return $('[name=csrfmiddlewaretoken]').val();
    }

    $('.fav-btn').on('click', function (e) {
        e.preventDefault();

        const userType = $(this).data('user-type');
        const url = $(this).attr('href');
        const btn = $(this);

        if (userType === 'visitor') {
            alert('Login as a buyer to save vehicles');
            return;
        }

        if (userType === 'seller') {
            alert('Sellers cannot save vehicles.');
            return;
        }

        if (userType === 'renter') {
            alert('Renters cannot save vehicles.');
            return;
        }

        if (userType === 'buyer') {

            let isSaved = btn.text().includes('❤️');
            let action = isSaved ? 'unsave' : 'save';

            $.ajax({
                url: url,
                type: "POST",
                data: {
                    action: action,
                    csrfmiddlewaretoken: getCSRF()
                },
                success: function (response) {

                    console.log("AJAX RESPONSE:", response);

                    if (response.status === "saved") {
                        btn.html("❤️");
                    }

                    if (response.status === "unsaved") {
                        btn.html("🤍");
                    }
                },
                error: function (xhr) {
                    console.log("ERROR:", xhr.responseText);
                }
            });
        }
    });

});