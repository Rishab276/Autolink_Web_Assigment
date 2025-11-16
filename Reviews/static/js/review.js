/* By humaa */
document.addEventListener('DOMContentLoaded', function () {

    const starContainer = document.getElementById('starRating');
    const ratingInput = document.getElementById('ratingValue');
    const form = document.getElementById('reviewForm');

    if (!starContainer || !ratingInput || !form) return;

    const stars = starContainer.querySelectorAll('span');
    stars.forEach(s => s.style.cursor = 'pointer');

    function paintStars(value, activeColor = 'gold', inactiveColor = '#ccc') {
        stars.forEach(s => {
            const v = s.getAttribute('data-value');
            s.style.color = (Number(v) <= Number(value)) ? activeColor : inactiveColor;
        });
    }

    // Star click
    starContainer.addEventListener('click', function (e) {
        const target = e.target.closest('span');
        if (!target) return;
        ratingInput.value = target.getAttribute('data-value');
        paintStars(ratingInput.value);
    });

    // Hover
    starContainer.addEventListener('mouseover', function (e) {
        const target = e.target.closest('span');
        if (!target) return;
        paintStars(target.getAttribute('data-value'), '#ffd700');
    });
    starContainer.addEventListener('mouseout', function () {
        paintStars(ratingInput.value);
    });

    // Create modal elements
    function createModal() {
        const overlay = document.createElement('div');
        overlay.id = 'reviewModalOverlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        `;

        const modal = document.createElement('div');
        modal.style.cssText = `
            background: #1a3a3a;
            border-radius: 12px;
            padding: 30px 40px;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        `;

        const title = document.createElement('div');
        title.textContent = '127.0.0.1:8000 says';
        title.style.cssText = `
            color: white;
            font-size: 16px;
            margin-bottom: 20px;
            font-weight: 500;
        `;

        const message = document.createElement('div');
        message.textContent = 'Your review has been submitted successfully!';
        message.style.cssText = `
            color: white;
            font-size: 14px;
            margin-bottom: 30px;
            line-height: 1.5;
        `;

        const buttonContainer = document.createElement('div');
        buttonContainer.style.cssText = `
            display: flex;
            justify-content: flex-end;
        `;

        const okButton = document.createElement('button');
        okButton.textContent = 'OK';
        okButton.style.cssText = `
            background: #5dbbbb;
            color: #1a3a3a;
            border: none;
            border-radius: 6px;
            padding: 10px 30px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        `;
        
        okButton.addEventListener('mouseover', function() {
            this.style.background = '#4da9a9';
        });
        okButton.addEventListener('mouseout', function() {
            this.style.background = '#5dbbbb';
        });
        
        okButton.addEventListener('click', function() {
            overlay.remove();
            form.submit(); // Submit the form after modal is closed
        });

        buttonContainer.appendChild(okButton);
        modal.appendChild(title);
        modal.appendChild(message);
        modal.appendChild(buttonContainer);
        overlay.appendChild(modal);

        return overlay;
    }

    // Form submit
    form.addEventListener('submit', function (e) {
        if (!ratingInput.value || ratingInput.value === "0") {
            e.preventDefault();
            alert("Please select a star for your review.");
            return;
        }

        e.preventDefault(); // Prevent default after validation
        
        // Show modal
        const modal = createModal();
        document.body.appendChild(modal);
    });

    // Initial paint
    paintStars(ratingInput.value);
});