// main.js

// Category Chart Functionality
function initCategoryChart() {
    const categoryData = {
        labels: [],
        counts: [],
        colors: ['#1e3a8a', '#0f766e', '#d97706', '#dc2626', '#7c3aed', '#0891b2'],
        hoverColors: ['#1e40af', '#115e59', '#b45309', '#b91c1c', '#6d28d9', '#0e7490']
    };

    const categoryCards = document.querySelectorAll('.category-card');
    categoryCards.forEach((card, index) => {
        const categoryName = card.querySelector('h3').textContent;
        
        const countElement = card.querySelector('.category-count');
        let count = 0;
        
        if (countElement) {
            const countText = countElement.textContent;
            count = parseInt(countText) || 0; 
        }
        
        console.log(`Category: ${categoryName}, Count: ${count}`);
        
        categoryData.labels.push(categoryName);
        categoryData.counts.push(count);
    });

    console.log('Final data:', categoryData);

    const ctx = document.getElementById('categoryChart').getContext('2d');
    const totalVehiclesElement = document.querySelector('.chart-total');
    const totalVehicles = totalVehiclesElement ? parseInt(totalVehiclesElement.textContent) : 0;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categoryData.labels,
            datasets: [{
                data: categoryData.counts,
                backgroundColor: categoryData.colors,
                hoverBackgroundColor: categoryData.hoverColors,
                borderWidth: 2,
                borderColor: '#ffffff',
                hoverBorderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '65%',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const percentage = totalVehicles > 0 ? ((value / totalVehicles) * 100).toFixed(1) : 0;
                            return `${label}: ${value} vehicles (${percentage}%)`;
                        }
                    },
                    backgroundColor: '#1e3a8a',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#d97706',
                    borderWidth: 1
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 2000,
                easing: 'easeOutQuart'
            }
        }
    });
}

// Testimonials Carousel Functionality
function initTestimonialsCarousel() {
    const track = document.getElementById('testimonialsTrack');
    const cards = document.querySelectorAll('.testimonial-card');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    const dotsContainer = document.getElementById('carouselDots');
    
    console.log('Carousel elements:', { track, cards: cards.length, prevBtn, nextBtn, dotsContainer });
    
    // If no cards or only 1-3 cards, don't initialize carousel
    if (!cards.length || cards.length <= 3) {
        console.log('Not enough cards for carousel:', cards.length);
        if (prevBtn) prevBtn.style.display = 'none';
        if (nextBtn) nextBtn.style.display = 'none';
        if (dotsContainer) dotsContainer.style.display = 'none';
        return;
    }
    
    let currentIndex = 0;
    const CARDS_PER_SLIDE = 3;
    const totalSlides = Math.ceil(cards.length / CARDS_PER_SLIDE);
    
    console.log('Carousel setup:', { totalSlides, cardsPerSlide: CARDS_PER_SLIDE });
    
    // Initialize dots
    if (dotsContainer) {
        dotsContainer.innerHTML = '';
        for (let i = 0; i < totalSlides; i++) {
            const dot = document.createElement('button');
            dot.className = `carousel-dot ${i === 0 ? 'active' : ''}`;
            dot.setAttribute('aria-label', `Go to slide ${i + 1}`);
            dot.innerHTML = '•';
            dot.addEventListener('click', () => goToSlide(i));
            dotsContainer.appendChild(dot);
        }
    }
    
    function updateCarousel() {
        if (!track) return;
        
        const cardWidth = cards[0].offsetWidth;
        const gap = 32; // 2rem gap from CSS
        const slideWidth = (cardWidth + gap) * CARDS_PER_SLIDE;
        const translateX = -currentIndex * slideWidth;
        
        console.log('Updating carousel:', { currentIndex, cardWidth, translateX });
        
        track.style.transform = `translateX(${translateX}px)`;
        track.style.transition = 'transform 0.5s ease-in-out';
        
        // Update dots
        if (dotsContainer) {
            document.querySelectorAll('.carousel-dot').forEach((dot, index) => {
                dot.classList.toggle('active', index === currentIndex);
            });
        }
        
        // Update buttons
        if (prevBtn) {
            prevBtn.disabled = currentIndex === 0;
            prevBtn.style.opacity = currentIndex === 0 ? '0.5' : '1';
        }
        if (nextBtn) {
            nextBtn.disabled = currentIndex >= totalSlides - 1;
            nextBtn.style.opacity = currentIndex >= totalSlides - 1 ? '0.5' : '1';
        }
    }
    
    function goToSlide(index) {
        if (index < 0 || index >= totalSlides) return;
        currentIndex = index;
        updateCarousel();
    }
    
    function nextSlide() {
        if (currentIndex < totalSlides - 1) {
            currentIndex++;
            updateCarousel();
        }
    }
    
    function prevSlide() {
        if (currentIndex > 0) {
            currentIndex--;
            updateCarousel();
        }
    }
    
    // Event listeners
    if (prevBtn) {
        prevBtn.addEventListener('click', prevSlide);
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', nextSlide);
    }
    
    // Touch support for mobile
    let startX = 0;
    let currentX = 0;
    let isDragging = false;
    
    if (track) {
        track.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            currentX = -currentIndex * (cards[0].offsetWidth + 32) * CARDS_PER_SLIDE;
            isDragging = true;
            track.style.transition = 'none';
        });
        
        track.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            const x = e.touches[0].clientX;
            const walk = x - startX;
            track.style.transform = `translateX(${currentX + walk}px)`;
        });
        
        track.addEventListener('touchend', (e) => {
            if (!isDragging) return;
            isDragging = false;
            track.style.transition = 'transform 0.5s ease-in-out';
            
            const endX = e.changedTouches[0].clientX;
            const diff = startX - endX;
            
            if (Math.abs(diff) > 50) {
                if (diff > 0) nextSlide();
                else prevSlide();
            } else {
                updateCarousel(); // Return to current position
            }
        });
    }
    
    // Handle window resize
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            updateCarousel();
        }, 250);
    });
    
    // Initial update
    updateCarousel();
    console.log('Carousel initialized successfully');
}

// Initialize all functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize category chart if element exists
    if (document.getElementById('categoryChart')) {
        initCategoryChart();
    }
    
    // Initialize testimonials carousel
    initTestimonialsCarousel();
});