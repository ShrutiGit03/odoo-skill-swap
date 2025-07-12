from datetime import datetime
from flask_login import UserMixin
from app import db, login

# ─── USER TABLE ────────────────────────────────────────────────────────────────
class User(db.Model, UserMixin):
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(150), nullable=False)
    email           = db.Column(db.String(150), unique=True, nullable=False)
    password        = db.Column(db.String(150), nullable=False)
    location        = db.Column(db.String(100))
    photo           = db.Column(db.String(200))                 # stores filename or URL
    skills_offered  = db.Column(db.String(300))                 # “Python, Excel”
    skills_wanted   = db.Column(db.String(300))                 # “Photoshop”
    availability    = db.Column(db.String(100))                 # “Weekends 6‑9 PM”
    is_public       = db.Column(db.Boolean, default=True)

    sent_requests   = db.relationship('SwapRequest',
                          foreign_keys='SwapRequest.sender_id',
                          backref='sender', lazy=True)
    recv_requests   = db.relationship('SwapRequest',
                          foreign_keys='SwapRequest.receiver_id',
                          backref='receiver', lazy=True)

    def __repr__(self):
        return f"<User {self.name}>"

# ⬅️ Fixes the login manager error
@login.user_loader
def load_user(uid):
    return User.query.get(int(uid))


# ─── SWAP REQUEST TABLE ────────────────────────────────────────────────────────
class SwapRequest(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    sender_id     = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id   = db.Column(db.Integer, db.ForeignKey('user.id'))
    offered_skill = db.Column(db.String(100))
    wanted_skill  = db.Column(db.String(100))
    status        = db.Column(db.String(20), default="Pending")  # Pending/Accepted/Rejected
    message       = db.Column(db.Text)
    timestamp     = db.Column(db.DateTime, default=datetime.utcnow)


# ─── FEEDBACK / RATING TABLE ───────────────────────────────────────────────────
class Feedback(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating    = db.Column(db.Integer)         # 1‑5 stars
    comment   = db.Column(db.Text)
    created   = db.Column(db.DateTime, default=datetime.utcnow)
