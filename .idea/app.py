from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger, swag_from
from datetime import datetime
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://<17070006016@stu.yasar.edu.tr>:<Denizyaşar1>@denizserver.database.windows.net:1433/Denizserver?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
swagger = Swagger(app)


class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(50), nullable=False)
    departure_airport = db.Column(db.String(50), nullable=False)
    arrival_airport = db.Column(db.String(50), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    miles = db.Column(db.Integer, default=0)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    passenger_name = db.Column(db.String(100), nullable=False)
    passengers = db.Column(db.Integer, nullable=False)
    total_cost = db.Column(db.Integer, nullable=False)


def admin_required(f):
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if auth == 'AdminSecret':
            return f(*args, **kwargs)
        else:
            return jsonify({"message": "Admin authentication required"}), 403
    return wrapper


add_flight_docs = {
    'tags': ['Flights'],
    'description': 'Endpoint to add a new flight. Only accessible to admin users.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'flight_number': {
                        'type': 'string',
                        'example': 'TK123'
                    },
                    'departure_airport': {
                        'type': 'string',
                        'example': 'IST'
                    },
                    'arrival_airport': {
                        'type': 'string',
                        'example': 'JFK'
                    },
                    'departure_time': {
                        'type': 'string',
                        'example': '2024-07-01 10:00:00'
                    },
                    'arrival_time': {
                        'type': 'string',
                        'example': '2024-07-01 14:00:00'
                    },
                    'capacity': {
                        'type': 'integer',
                        'example': 200
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Flight added successfully',
            'examples': {
                'application/json': {
                    'message': 'Flight added successfully!'
                }
            }
        },
        403: {
            'description': 'Admin authentication required',
            'examples': {
                'application/json': {
                    'message': 'Admin authentication required'
                }
            }
        }
    }
}

@app.route('/add_flight', methods=['POST'])
@admin_required
@swag_from(add_flight_docs)
def add_flight():
    data = request.get_json()

    flight_number = data.get('flight_number')
    departure_airport = data.get('departure_airport')
    arrival_airport = data.get('arrival_airport')
    departure_time = datetime.strptime(data.get('departure_time'), '%Y-%m-%d %H:%M:%S')
    arrival_time = datetime.strptime(data.get('arrival_time'), '%Y-%m-%d %H:%M:%S')
    capacity = data.get('capacity')

    new_flight = Flight(
        flight_number=flight_number,
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        departure_time=departure_time,
        arrival_time=arrival_time,
        capacity=capacity
    )

    db.session.add(new_flight)
    db.session.commit()

    return jsonify({"message": "Flight added successfully!"}), 201


search_flights_docs = {
    'tags': ['Flights'],
    'description': 'Endpoint to search for flights based on parameters.',
    'parameters': [
        {
            'name': 'departure_airport',
            'in': 'query',
            'type': 'string',
            'required': True,
            'example': 'IST'
        },
        {
            'name': 'arrival_airport',
            'in': 'query',
            'type': 'string',
            'required': True,
            'example': 'JFK'
        },
        {
            'name': 'departure_date',
            'in': 'query',
            'type': 'string',
            'required': True,
            'example': '2024-07-01'
        },
        {
            'name': 'passengers',
            'in': 'query',
            'type': 'integer',
            'required': True,
            'example': 1
        }
    ],
    'responses': {
        200: {
            'description': 'Flights found',
            'examples': {
                'application/json': [
                    {
                        'flight_number': 'TK123',
                        'departure_airport': 'IST',
                        'arrival_airport': 'JFK',
                        'departure_time': '2024-07-01 10:00:00',
                        'arrival_time': '2024-07-01 14:00:00',
                        'capacity': 200
                    }
                ]
            }
        },
        404: {
            'description': 'No flights found',
            'examples': {
                'application/json': {
                    'message': 'No flights found'
                }
            }
        }
    }
}

@app.route('/search_flights', methods=['GET'])
@swag_from(search_flights_docs)
def search_flights():
    departure_airport = request.args.get('departure_airport')
    arrival_airport = request.args.get('arrival_airport')
    departure_date = request.args.get('departure_date')
    passengers = int(request.args.get('passengers'))

    departure_datetime_start = datetime.strptime(departure_date, '%Y-%m-%d')
    departure_datetime_end = departure_datetime_start.replace(hour=23, minute=59, second=59)

    flights = Flight.query.filter(
        Flight.departure_airport == departure_airport,
        Flight.arrival_airport == arrival_airport,
        Flight.departure_time >= departure_datetime_start,
        Flight.departure_time <= departure_datetime_end,
        Flight.capacity >= passengers
    ).all()

    if not flights:
        return jsonify({"message": "No flights found"}), 404

    results = []
    for flight in flights:
        results.append({
            'flight_number': flight.flight_number,
            'departure_airport': flight.departure_airport,
            'arrival_airport': flight.arrival_airport,
            'departure_time': flight.departure_time.strftime('%Y-%m-%d %H:%M:%S'),
            'arrival_time': flight.arrival_time.strftime('%Y-%m-%d %H:%M:%S'),
            'capacity': flight.capacity
        })

    return jsonify(results), 200


buy_ticket_docs = {
    'tags': ['Tickets'],
    'description': 'Endpoint to buy a ticket for a flight.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'flight_id': {
                        'type': 'integer',
                        'example': 1
                    },
                    'passenger_name': {
                        'type': 'string',
                        'example': 'John Doe'
                    },
                    'passengers': {
                        'type': 'integer',
                        'example': 2
                    },
                    'total_cost': {
                        'type': 'integer',
                        'example': 500
                    },
                    'user_email': {
                        'type': 'string',
                        'example': 'john.doe@example.com'
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Ticket purchased successfully',
            'examples': {
                'application/json': {
                    'message': 'Ticket purchased successfully!'
                }
            }
        },
        400: {
            'description': 'Bad request',
            'examples': {
                'application/json': {
                    'message': 'Invalid request parameters'
                }
            }
        }
    }
}

@app.route('/buy_ticket', methods=['POST'])
@swag_from(buy_ticket_docs)
def buy_ticket():
    data = request.get_json()

    flight_id = data.get('flight_id')
    passenger_name = data.get('passenger_name')
    passengers = data.get('passengers')
    total_cost = data.get('total_cost')
    user_email = data.get('user_email')

    flight = Flight.query.get(flight_id)
    if not flight or flight.capacity < passengers:
        return jsonify({"message": "Flight not found or not enough capacity"}), 400

    flight.capacity -= passengers

    user = User.query.filter_by(email=user_email).first()
    if user:
        user_id = user.id
    else:
        user_id = None

    ticket = Ticket(
        flight_id=flight_id,
        user_id=user_id,
        passenger_name=passenger_name,
        passengers=passengers,
        total_cost=total_cost
    )

    db.session.add(ticket)
    db.session.commit()

    return jsonify({"message": "Ticket purchased successfully!"}), 201


add_miles_docs = {
    'tags': ['Miles'],
    'description': 'Endpoint to add miles to a Miles&Smiles account.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_email': {
                        'type': 'string',
                        'example': 'john.doe@example.com'
                    },
                    'miles': {
                        'type': 'integer',
                        'example': 500
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Miles added successfully',
            'examples': {
                'application/json': {
                    'message': 'Miles added successfully!'
                }
            }
        },
        400: {
            'description': 'Bad request',
            'examples': {
                'application/json': {
                    'message': 'Invalid request parameters'
                }
            }
        }
    }
}

@app.route('/add_miles', methods=['POST'])
@swag_from(add_miles_docs)
def add_miles():
    data = request.get_json()

    user_email = data.get('user_email')
    miles = data.get('miles')

    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"message": "User not found"}), 400

    user.miles += miles
    db.session.commit()

    return jsonify({"message": "Miles added successfully!"}), 200

def update_miles():
    flights = Flight.query.filter(Flight.departure_time < datetime.now()).all()
    for flight in flights:
        tickets = Ticket.query.filter(Ticket.flight_id == flight.id).all()
        for ticket in tickets:
            if ticket.user_id:
                user = User.query.get(ticket.user_id)
                user.miles += 100
                db.session.commit()


def send_welcome_emails():
    users = User.query.filter(User.miles == 0).all()
    for user in users:
        msg = Message('Welcome to Miles&Smiles', recipients=[user.email])
        msg.body = 'Welcome to Miles&Smiles program!'
        mail.send(msg)

scheduler.add_job(update_miles, 'cron', hour=0, minute=0)
scheduler.add_job(send_welcome_emails, 'cron', hour=1, minute=0)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
