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
$(document).ready(function() {
    $('.fav-btn').on('click', function(e) {
        const userType = $(this).data('user-type');
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
        else if (userType === 'buyer' && $(this).text().includes('❤️')) {
            e.preventDefault();
            if (confirm('Are you sure you want to unsave this vehicle?')) {
                window.location.href = $(this).attr('href');
            }
        }
        // Buyer saving a vehicle (Grey Heart) - no confirmation needed
    });
});
