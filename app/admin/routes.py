from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import User, SkillOffered, SkillWanted, SwapRequest, AdminLog
from app.admin import admin
from datetime import datetime

@admin.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        abort(403)
    
    pending_offered = SkillOffered.query.filter_by(is_approved=False).all()
    pending_wanted = SkillWanted.query.filter_by(is_approved=False).all()
    pending_skills = pending_offered + pending_wanted
    
    recent_swaps = SwapRequest.query.order_by(SwapRequest.created_at.desc()).limit(10).all()
    
    total_users = User.query.count()
    banned_users = User.query.filter_by(is_active=False).count()
    all_users = User.query.all()
    
    return render_template('admin/dashboard.html',
                         pending_skills=pending_skills,
                         recent_swaps=recent_swaps,
                         total_users=total_users,
                         banned_users=banned_users,
                         all_users=all_users)

@admin.route('/approve_skill/<int:skill_id>/<skill_type>', methods=['POST'])
@login_required
def approve_skill(skill_id, skill_type):
    if not current_user.is_admin:
        abort(403)
    
    if skill_type == 'offer':
        skill = SkillOffered.query.get_or_404(skill_id)
    else:
        skill = SkillWanted.query.get_or_404(skill_id)
    
    skill.is_approved = True
    db.session.commit()
    
    log = AdminLog(
        admin_id=current_user.id,
        action=f'skill_approved_{skill_type}',
        target_id=skill.id,
        details=f'Approved skill: {skill.name}'
    )
    db.session.add(log)
    db.session.commit()
    
    flash('Skill approved!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/reject_skill/<int:skill_id>/<skill_type>', methods=['POST'])
@login_required
def reject_skill(skill_id, skill_type):
    if not current_user.is_admin:
        abort(403)
    
    if skill_type == 'offer':
        skill = SkillOffered.query.get_or_404(skill_id)
    else:
        skill = SkillWanted.query.get_or_404(skill_id)
    
    log = AdminLog(
        admin_id=current_user.id,
        action=f'skill_rejected_{skill_type}',
        target_id=skill.id,
        details=f'Rejected skill: {skill.name}'
    )
    db.session.add(log)
    
    db.session.delete(skill)
    db.session.commit()
    
    flash('Skill rejected and removed!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/ban_user/<int:user_id>', methods=['POST'])
@login_required
def ban_user(user_id):
    if not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    user.is_active = False
    
    log = AdminLog(
        admin_id=current_user.id,
        action='user_banned',
        target_id=user.id,
        details=f'Banned user: {user.username}'
    )
    db.session.add(log)
    db.session.commit()
    
    flash('User banned!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/unban_user/<int:user_id>', methods=['POST'])
@login_required
def unban_user(user_id):
    if not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    user.is_active = True
    
    log = AdminLog(
        admin_id=current_user.id,
        action='user_unbanned',
        target_id=user.id,
        details=f'Unbanned user: {user.username}'
    )
    db.session.add(log)
    db.session.commit()
    
    flash('User unbanned!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/send_message/<int:user_id>', methods=['POST'])
@login_required
def send_message(user_id):
    if not current_user.is_admin:
        abort(403)
    
    user = User.query.get_or_404(user_id)
    subject = request.form.get('subject')
    message = request.form.get('message')
    
    log = AdminLog(
        admin_id=current_user.id,
        action='admin_message_sent',
        target_id=user.id,
        details=f'Message sent to {user.username}: {subject} - {message}'
    )
    db.session.add(log)
    db.session.commit()
    
    flash('Message sent!', 'success')
    return redirect(url_for('admin.dashboard'))