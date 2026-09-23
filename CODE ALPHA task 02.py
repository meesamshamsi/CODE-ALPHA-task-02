from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    registrations = db.relationship('Registration', backref='user', lazy=True)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.String(50), nullable=False)
    registrations = db.relationship('Registration', backref='event', lazy=True)

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

with app.app_context():
    db.create_all()

# API Endpoints
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = User(name=data['name'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created", "user_id": user.id}), 201

@app.route('/events', methods=['GET', 'POST'])
def handle_events():
    if request.method == 'POST':
        data = request.get_json()
        event = Event(title=data['title'], description=data.get('description', ''), date=data['date'])
        db.session.add(event)
        db.session.commit()
        return jsonify({"message": "Event created", "event_id": event.id}), 201
    
    events = Event.query.all()
    return jsonify([{"id": e.id, "title": e.title, "description": e.description, "date": e.date} for e in events])

@app.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    return jsonify({"id": event.id, "title": event.title, "description": event.description, "date": event.date})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    reg = Registration(user_id=data['user_id'], event_id=data['event_id'])
    db.session.add(reg)
    db.session.commit()
    return jsonify({"message": "Registration successful", "registration_id": reg.id}), 201

@app.route('/users/<int:user_id>/registrations', methods=['GET'])
def user_registrations(user_id):
    regs = Registration.query.filter_by(user_id=user_id).all()
    return jsonify([{"registration_id": r.id, "event_id": r.event.id, "event_title": r.event.title, "event_date": r.event.date} for r in regs])

@app.route('/registrations/<int:reg_id>', methods=['DELETE'])
def cancel_registration(reg_id):
    reg = Registration.query.get_or_404(reg_id)
    db.session.delete(reg)
    db.session.commit()
    return jsonify({"message": "Registration cancelled successfully"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)