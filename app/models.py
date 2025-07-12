from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(100))
    profile_pic = db.Column(db.String(20), nullable=False, default='default.jpg')
    is_public = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    skills_offered = db.relationship('SkillOffered', backref='user', lazy=True, cascade="all, delete-orphan")
    skills_wanted = db.relationship('SkillWanted', backref='user', lazy=True, cascade="all, delete-orphan")
    availability = db.relationship('Availability', backref='user', lazy=True, cascade="all, delete-orphan")
    sent_requests = db.relationship('SwapRequest', foreign_keys='SwapRequest.sender_id', backref='sender', lazy=True)
    received_requests = db.relationship('SwapRequest', foreign_keys='SwapRequest.receiver_id', backref='receiver', lazy=True)
    ratings_given = db.relationship('Rating', foreign_keys='Rating.rater_id', backref='rater', lazy=True)
    ratings_received = db.relationship('Rating', foreign_keys='Rating.rated_id', backref='rated', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_avg_rating(self):
        if not self.ratings_received:
            return 0
        return sum(r.rating for r in self.ratings_received) / len(self.ratings_received)

# ... (other models from previous implementation remain the same) ...