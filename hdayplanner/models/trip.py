from .database import db

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    itineraries = db.relationship('Itinerary', backref='trip', lazy=True)
    budgets = db.relationship('Budget', backref='trip', lazy=True)
