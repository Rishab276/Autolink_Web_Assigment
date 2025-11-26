/*MAIGHUN-2412258*/
document.addEventListener('DOMContentLoaded', function() {
        const featureCards = document.querySelectorAll('.feature-card');
        featureCards.forEach(card => {
            card.addEventListener('mouseenter', () => card.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.1)');
            card.addEventListener('mouseleave', () => card.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.05)');
        });
    });