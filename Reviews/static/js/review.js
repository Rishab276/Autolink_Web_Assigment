// Star Rating Functionality for Review Page
document.addEventListener('DOMContentLoaded', function() {
    const stars = document.querySelectorAll('#starRating span');
    const ratingInput = document.getElementById('ratingValue');
    
    // Initialize with no rating
    ratingInput.value = "0";
    
    stars.forEach(star => {
        star.addEventListener('click', function() {
            const rating = this.getAttribute('data-value');
            
            // Update hidden input value for form submission
            ratingInput.value = rating;
            
            // Update stars visual appearance
            stars.forEach(s => {
                const starValue = s.getAttribute('data-value');
                if (starValue <= rating) {
                    s.classList.add('active');
                    s.style.color = 'gold';
                } else {
                    s.classList.remove('active');
                    s.style.color = '#fff';
                }
            });
            
            // Optional: Show confirmation message
            console.log(`Rating submitted: ${rating}/5`);
            
            // Auto-submit behavior (if you want immediate submission)
            // If you want it to submit immediately when star is clicked, uncomment:
            // document.querySelector('form').submit();
        });
        
        // Hover effects
        star.addEventListener('mouseover', function() {
            const rating = this.getAttribute('data-value');
            stars.forEach(s => {
                const starValue = s.getAttribute('data-value');
                if (starValue <= rating) {
                    s.style.color = '#ffd700';
                } else {
                    s.style.color = '#fff';
                }
            });
        });
        
        star.addEventListener('mouseout', function() {
            const currentRating = ratingInput.value;
            stars.forEach(s => {
                const starValue = s.getAttribute('data-value');
                if (starValue <= currentRating) {
                    s.style.color = 'gold';
                } else {
                    s.style.color = '#fff';
                }
            });
        });
    });
    
    // Form submission handler
    const form = document.querySelector('form');
    form.addEventListener('submit', function(e) {
        if (ratingInput.value === "0") {
            e.preventDefault();
            alert('Please select a rating before submitting your review.');
            return false;
        }
        
        console.log(`Submitting review with rating: ${ratingInput.value}/5`);
    });
});