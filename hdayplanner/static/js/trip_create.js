document.addEventListener('DOMContentLoaded', function() {
    // Initialize date pickers
    flatpickr("#startDate", {
        minDate: "today",
        onChange: function(selectedDates) {
            endDatePicker.set("minDate", selectedDates[0]);
        }
    });
    
    const endDatePicker = flatpickr("#endDate", {
        minDate: "today"
    });

    // Handle trip form submission
    const tripForm = document.getElementById('tripForm');
    if (tripForm) {
        tripForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(tripForm);
            const tripData = Object.fromEntries(formData.entries());

            // Collect itinerary data
            const itineraryData = Array.from(document.querySelectorAll('#itineraryDays tr')).map(row => {
                const inputs = row.querySelectorAll('input');
                return {
                    date: inputs[0].value, // Assuming the first input is the date
                    city: inputs[1].value,
                    hotel: inputs[2].value,
                    morning_activity: inputs[3].value,
                    lunch: inputs[4].value,
                    afternoon_activity: inputs[5].value,
                    dinner: inputs[6].value
                };
            });

            try {
                const response = await fetch(tripForm.action, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ ...tripData, itinerary: itineraryData })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    window.location.href = `/trip/${data.trip_id}`;
                } else {
                    showNotification(data.error, 'error');
                }
            } catch (error) {
                showNotification('An error occurred while saving the trip.', 'error');
            }
        });
    } else {
        console.error('Trip form not found.');
    }

    // Modal controls
    const goToItineraryButton = document.getElementById('goToItinerary');
    console.log('Go to Itinerary Button:', goToItineraryButton); // Check if this is null

    if (goToItineraryButton) {
        goToItineraryButton.addEventListener('click', function() {
            window.location.href = '/trips/latest/itinerary';
        });
    } else {
        console.error('Element with ID "goToItinerary" not found.');
    }
    
    document.getElementById('closeModal').addEventListener('click', function() {
        modal.style.display = 'none';
    });

    // Budget calculation helpers
    const totalBudgetInput = document.getElementById('totalBudget');
    
    totalBudgetInput.addEventListener('input', function() {
        const budget = parseFloat(this.value);
        if (budget < 0) {
            this.value = 0;
        }
    });

    // Flight number validation
    function validateFlightNumber(input) {
        const flightNumberPattern = /^[A-Z]{2,3}\d{1,4}[A-Z]?$/;
        const value = input.value.toUpperCase();
        
        if (value && !flightNumberPattern.test(value)) {
            input.setCustomValidity('Please enter a valid flight number (e.g., AA123 or UA4567)');
        } else {
            input.setCustomValidity('');
        }
    }

    document.getElementById('departureFlightNumber').addEventListener('input', function() {
        validateFlightNumber(this);
    });

    document.getElementById('returnFlightNumber').addEventListener('input', function() {
        validateFlightNumber(this);
    });

    // Function to generate the calendar
    function generateCalendar(startDate, endDate) {
        const calendarDiv = document.getElementById('calendar');
        calendarDiv.innerHTML = ''; // Clear previous calendar
        const start = new Date(startDate);
        const end = new Date(endDate);
        const days = (end - start) / (1000 * 60 * 60 * 24) + 1; // Calculate number of days

        for (let i = 0; i < days; i++) {
            const date = new Date(start);
            date.setDate(start.getDate() + i);
            const dayElement = document.createElement('div');
            dayElement.className = 'calendar-day';
            dayElement.innerText = date.toDateString();
            calendarDiv.appendChild(dayElement);
        }
    }

    // Event listeners for date inputs
    document.getElementById('startDate').addEventListener('change', function() {
        const startDate = this.value;
        const endDate = document.getElementById('endDate').value;
        if (endDate) {
            generateCalendar(startDate, endDate);
        }
    });

    document.getElementById('endDate').addEventListener('change', function() {
        const endDate = this.value;
        const startDate = document.getElementById('startDate').value;
        if (startDate) {
            generateCalendar(startDate, endDate);
        }
    });

    // Function to calculate budget
    function calculateBudget() {
        const totalBudget = parseFloat(document.getElementById('totalBudget').value);
        const flightCost = parseFloat(document.getElementById('flightCost').value) || 0;
        const carRentalCost = parseFloat(document.getElementById('carRentalCost').value) || 0;
        const expenses = []; // This should be populated with actual expenses
        const totalExpenses = expenses.reduce((acc, expense) => acc + expense.cost, 0);
        const totalCosts = flightCost + carRentalCost + totalExpenses;
        const remainingBudget = totalBudget - totalCosts;

        // Display budget information
        const budgetInfo = document.getElementById('budgetInfo');
        budgetInfo.innerText = `Remaining Budget: $${remainingBudget.toFixed(2)}`;
    }

    // Call calculateBudget when the budget input changes
    document.getElementById('totalBudget').addEventListener('input', calculateBudget);
});