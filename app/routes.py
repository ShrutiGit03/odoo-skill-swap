from flask import render_template, url_for, flash, redirect, request, jsonify, abort
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, SkillForm, AvailabilityForm, RatingForm
from app.models import User, SkillOffered, SkillWanted, Availability, SwapRequest, Rating
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
from sqlalchemy import or_
from flask import Blueprint
from flask_login import current_user
main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    if current_user.is_authenticated:
        users = User.query.filter(
            User.is_public == True,
            User.id != current_user.id,
            or_(
                User.skills_offered.any(),
                User.skills_wanted.any()
            )
        ).order_by(User.last_active.desc()).limit(6).all()
        return render_template('home.html', users=users)
    return render_template('home.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            location=form.location.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    skill_form = SkillForm()
    availability_form = AvailabilityForm()
    
    if skill_form.validate_on_submit():
        if skill_form.skill_type.data == 'offer':
            skill = SkillOffered(
                name=skill_form.name.data,
                description=skill_form.description.data,
                proficiency=skill_form.proficiency.data,
                user_id=current_user.id
            )
        else:
            skill = SkillWanted(
                name=skill_form.name.data,
                description=skill_form.description.data,
                user_id=current_user.id
            )
        db.session.add(skill)
        db.session.commit()
        flash('Skill added!', 'success')
        return redirect(url_for('profile'))
    
    if availability_form.validate_on_submit():
        availability = Availability(
            day=availability_form.day.data,
            time_range=availability_form.time_range.data,
            user_id=current_user.id
        )
        db.session.add(availability)
        db.session.commit()
        flash('Availability added!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', 
                         skill_form=skill_form,
                         availability_form=availability_form,
                         offered_skills=current_user.skills_offered,
                         wanted_skills=current_user.skills_wanted,
                         availability=current_user.availability)

@app.route("/search", methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '')
    skill_type = request.args.get('type', 'offer')
    
    if skill_type == 'offer':
        results = SkillOffered.query.filter(
            SkillOffered.name.ilike(f'%{query}%'),
            SkillOffered.is_approved == True
        ).join(User).filter(
            User.is_public == True,
            User.id != current_user.id
        ).all()
    else:
        results = SkillWanted.query.filter(
            SkillWanted.name.ilike(f'%{query}%'),
            SkillWanted.is_approved == True
        ).join(User).filter(
            User.is_public == True,
            User.id != current_user.id
        ).all()
    
    return render_template('search.html', results=results, query=query, skill_type=skill_type)

@app.route("/user/<int:user_id>")
@login_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    if not user.is_public:
        flash('This profile is private', 'warning')
        return redirect(url_for('home'))
    return render_template('user_profile.html', user=user)

@app.route("/request_swap", methods=['POST'])
@login_required
def request_swap():
    data = request.get_json()
    receiver_id = data['receiver_id']
    offered_skill_id = data['offered_skill_id']
    wanted_skill_id = data['wanted_skill_id']
    message = data.get('message', '')
    
    swap = SwapRequest(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        offered_skill_id=offered_skill_id,
        wanted_skill_id=wanted_skill_id,
        message=message
    )
    db.session.add(swap)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Swap request sent!'})

@app.route("/manage_swap/<int:swap_id>", methods=['POST'])
@login_required
def manage_swap(swap_id):
    swap = SwapRequest.query.get_or_404(swap_id)
    if swap.receiver_id != current_user.id and swap.sender_id != current_user.id:
        abort(403)
    
    action = request.form.get('action')
    if action == 'accept':
        swap.status = 'accepted'
    elif action == 'reject':
        swap.status = 'rejected'
    elif action == 'cancel' and swap.sender_id == current_user.id:
        swap.status = 'cancelled'
    
    db.session.commit()
    return redirect(url_for('swap_requests'))

@app.route("/swap_requests")
@login_required
def swap_requests():
    sent = SwapRequest.query.filter_by(sender_id=current_user.id).all()
    received = SwapRequest.query.filter_by(receiver_id=current_user.id).all()
    return render_template('swap_requests.html', sent_requests=sent, received_requests=received)

@app.route("/rate_swap/<int:swap_id>", methods=['GET', 'POST'])
@login_required
def rate_swap(swap_id):
    swap = SwapRequest.query.get_or_404(swap_id)
    if swap.status != 'accepted' or (current_user.id != swap.sender_id and current_user.id != swap.receiver_id):
        abort(403)
    
    form = RatingForm()
    other_user = swap.sender if current_user.id == swap.receiver_id else swap.receiver
    
    if form.validate_on_submit():
        rating = Rating(
            swap_id=swap.id,
            rater_id=current_user.id,
            rated_id=other_user.id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(rating)
        db.session.commit()
        flash('Rating submitted!', 'success')
        return redirect(url_for('swap_requests'))
    
    return render_template('rate_swap.html', form=form, swap=swap, other_user=other_user)

@app.route("/api/user_skills/<int:user_id>/<skill_type>")
@login_required
def get_user_skills(user_id, skill_type):
    user = User.query.get_or_404(user_id)
    
    if skill_type == 'offer':
        skills = [{'id': s.id, 'name': s.name} for s in user.skills_offered if s.is_approved]
    else:
        skills = [{'id': s.id, 'name': s.name} for s in user.skills_wanted if s.is_approved]
    
    return jsonify({'skills': skills})

@app.route("/toggle_profile_visibility", methods=['POST'])
@login_required
def toggle_profile_visibility():
    current_user.is_public = not current_user.is_public
    db.session.commit()
    return jsonify({'success': True, 'is_public': current_user.is_public})

@app.route("/delete_skill/<skill_type>/<int:skill_id>", methods=['POST'])
@login_required
def delete_skill(skill_type, skill_id):
    if skill_type == 'offer':
        skill = SkillOffered.query.filter_by(id=skill_id, user_id=current_user.id).first_or_404()
    else:
        skill = SkillWanted.query.filter_by(id=skill_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(skill)
    db.session.commit()
    flash('Skill deleted!', 'success')
    return redirect(url_for('profile'))

@app.route("/delete_availability/<int:avail_id>", methods=['POST'])
@login_required
def delete_availability(avail_id):
    avail = Availability.query.filter_by(id=avail_id, user_id=current_user.id).first_or_404()
    db.session.delete(avail)
    db.session.commit()
    flash('Availability removed!', 'success')
    return redirect(url_for('profile'))

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500