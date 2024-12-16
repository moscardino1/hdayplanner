document.addEventListener('DOMContentLoaded', function() {
    // Handle mobile navigation toggle
    const navLinks = document.querySelector('.nav-links');

    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Handle form submissions with fetch API
    document.querySelectorAll('form[data-remote="true"]').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            try {
                const formData = new FormData(form);
                const response = await fetch(form.action, {
                    method: form.method,
                    body: formData,
                    headers: {
                        'Accept': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showNotification(data.message, 'success');
                } else {
                    showNotification(data.error, 'error');
                }
            } catch (error) {
                showNotification('An error occurred. Please try again.', 'error');
            }
        });
    });

    // Handle delete trip action
    const deleteButtons = document.querySelectorAll('.delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const tripId = this.getAttribute('data-trip-id');
            const confirmDelete = confirm('Are you sure you want to delete this trip? This action cannot be undone.');
            if (confirmDelete) {
                const response = await fetch(`/api/trips/${tripId}`, {
                    method: 'DELETE'
                });
                if (response.ok) {
                    window.location.href = '/'; // Redirect to home after deletion
                } else {
                    alert('Failed to delete the trip.');
                }
            }
        });
    });
});

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.classList.add('notification', type);
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

$(document).ready(function(){
    $('.trip-carousel').slick({
        dots: true, // Show dots for navigation
        infinite: true, // Infinite looping
        speed: 500, // Transition speed
        slidesToShow: 3, // Number of slides to show at once
        slidesToScroll: 1, // Number of slides to scroll at once
        responsive: [
            {
                breakpoint: 1024,
                settings: {
                    slidesToShow: 2, // Show 2 slides on medium screens
                    slidesToScroll: 1,
                    dots: true
                }
            },
            {
                breakpoint: 600,
                settings: {
                    slidesToShow: 1, // Show 1 slide on small screens
                    slidesToScroll: 1
                }
            }
        ]
    });
});