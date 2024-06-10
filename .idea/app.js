
document.getElementById("adminLoginForm").addEventListener("submit", function(event) {
  event.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  adminLogin(username, password);
});


document.getElementById("addFlightForm").addEventListener("submit", function(event) {
  event.preventDefault();
  const date = document.getElementById("flightDate").value;
  const airport = document.getElementById("airport").value;
  const capacity = document.getElementById("capacity").value;
  addFlight(date, airport, capacity);
});

document.getElementById("searchFlightsForm").addEventListener("submit", function(event) {
  event.preventDefault();
  const departureAirport = document.getElementById("departureAirport").value;
  const arrivalAirport = document.getElementById("arrivalAirport").value;
  const date = document.getElementById("searchDate").value;
  const passengerCount = document.getElementById("passengerCount").value;
  searchFlights(departureAirport, arrivalAirport, date, passengerCount);
});


function displayFlightResults(flights) {
  const flightResultsDiv = document.getElementById("flightResults");
  flightResultsDiv.innerHTML = ""; // Temizle
  flights.forEach(function(flight) {
    const flightDiv = document.createElement("div");
    flightDiv.textContent = `Flight ${flight.id}: ${flight.departureAirport} to ${flight.arrivalAirport}, Departure: ${flight.departureTime}, Arrival: ${flight.arrivalTime}, Price: ${flight.price}`;
    flightResultsDiv.appendChild(flightDiv);
  });
}

document.getElementById("buyTicketForm").addEventListener("submit", function(event) {
  event.preventDefault();
  const passengerName = document.getElementById("passengerName").value;
  const milesSmilesNumber = document.getElementById("milesSmilesNumber").value;
  const useMiles = document.getElementById("useMiles").checked;
  buyTicket(passengerName, milesSmilesNumber, useMiles);
});

document.getElementById("addMilesForm").addEventListener("submit", function(event) {
  event.preventDefault();
  const flightNumber = document.getElementById("flightNumber").value;
  const mileDate = document.getElementById("mileDate").value;
  const miles = document.getElementById("miles").value;
  addMilesToAccount(flightNumber, mileDate, miles);
});


function adminLogin(username, password) {
  if (username === "admin" && password === "admin123") {
    localStorage.setItem("adminAuth", "AdminSecret");
    alert("Giriş başarılı!");
  } else {
    alert("Geçersiz kullanıcı adı veya parola.");
  }
}


function addFlight(flightNumber, departureAirport, arrivalAirport, departureTime, arrivalTime, capacity) {
  const adminAuth = localStorage.getItem("adminAuth");

  fetch('/add_flight', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': adminAuth
    },
    body: JSON.stringify({
      flight_number: flightNumber,
      departure_airport: departureAirport,
      arrival_airport: arrivalAirport,
      departure_time: departureTime,
      arrival_time: arrivalTime,
      capacity: capacity
    })
  })
    .then(response => response.json())
    .then(data => {
      if (data.message === "Flight added successfully!") {
        alert("Uçuş başarıyla eklendi!");
      } else {
        alert(data.message);
      }
    })
    .catch(error => console.error("Error:", error));
}


function searchFlights(departureAirport, arrivalAirport, date, passengerCount) {
  fetch(`/search_flights?departure_airport=${departureAirport}&arrival_airport=${arrivalAirport}&departure_date=${date}&passengers=${passengerCount}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(response => response.json())
    .then(data => {
      if (data.message) {
        alert(data.message);
      } else {
        displayFlightResults(data);
      }
    })
    .catch(error => console.error("Error:", error));
}



function buyTicket(flightID, passengerName, email, passengers, totalCost, milesSmilesNumber, useMiles) {
  fetch('/buy_ticket', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      flight_id: flightID,
      passenger_name: passengerName,
      email: email,
      passengers: passengers,
      total_cost: totalCost,
      milesSmilesNumber: milesSmilesNumber,
      useMiles: useMiles
    })
  })
    .then(response => response.json())
    .then(data => {
      if (data.message === "Ticket bought successfully!") {
        alert("Bilet başarıyla satın alındı!");
      } else {
        alert(data.message);
      }
    })
    .catch(error => console.error("Error:", error));
}

function addMilesToAccount(userEmail, miles) {
  const adminAuth = localStorage.getItem("adminAuth");

  fetch('/add_miles', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': adminAuth
    },
    body: JSON.stringify({
      user_email: userEmail,
      miles: miles
    })
  })
    .then(response => response.json())
    .then(data => {
      if (data.message === "Miles added successfully!") {
        alert("Mil başarıyla eklendi!");
      } else {
        alert(data.message);
      }
    })
    .catch(error => console.error("Error:", error));
}


