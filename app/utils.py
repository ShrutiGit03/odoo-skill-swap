from datetime import datetime
from flask import current_app
import os
from PIL import Image
from app import db

def save_picture(form_picture):
    # Generate random filename
    random_hex = os.urandom(8).hex()
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    
    # Resize image
    output_size = current_app.config['PROFILE_PIC_RESOLUTION']
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    
    # Save image
    i.save(picture_path)
    
    return picture_fn

def time_ago(dt):
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    weeks = days // 7
    months = days // 30
    years = days // 365
    
    if years > 0:
        return f"{int(years)} year{'s' if years > 1 else ''} ago"
    elif months > 0:
        return f"{int(months)} month{'s' if months > 1 else ''} ago"
    elif weeks > 0:
        return f"{int(weeks)} week{'s' if weeks > 1 else ''} ago"
    elif days > 0:
        return f"{int(days)} day{'s' if days > 1 else ''} ago"
    elif hours > 0:
        return f"{int(hours)} hour{'s' if hours > 1 else ''} ago"
    elif minutes > 0:
        return f"{int(minutes)} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"