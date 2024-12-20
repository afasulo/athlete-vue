# app/dashboard.py
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request
from app.services.data_processor import DataProcessor
from app.models.hittrax_models import User, Session

# Create blueprint
bp = Blueprint('dashboard', __name__)

@bp.route('/player')
def player_index():
    """Landing page for player search"""
    try:
        # Get all active users
        users = User.query.filter_by(active=1).order_by(User.lastname, User.firstname).all()
        return render_template('dashboard/player.html', users=users)
    except Exception as e:
        print(f"Error accessing dashboard: {str(e)}")
        raise

@bp.route('/player/<int:user_id>')
def player_dashboard(user_id):
    """Player dashboard view"""
    # Get all active users for the dropdown
    users = User.query.filter_by(active=1).order_by(User.lastname, User.firstname).all()
    
    # Get the selected user
    user = User.query.get_or_404(user_id)
    
    # Get filter parameters
    date_from = request.args.get('date_from', 
                               (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    date_to = request.args.get('date_to', datetime.now().strftime('%Y-%m-%d'))
    min_pitch_speed = request.args.get('min_pitch_speed', type=float)
    max_pitch_speed = request.args.get('max_pitch_speed', type=float)
    
    # Query sessions with filters using converted view
    sessions_query = Session.query.filter(
        Session.userid == user_id,
        Session.active == 1
    )
    
    if date_from:
        sessions_query = sessions_query.filter(
            Session.timestamp >= datetime.strptime(date_from, '%Y-%m-%d')
        )
    if date_to:
        sessions_query = sessions_query.filter(
            Session.timestamp <= datetime.strptime(date_to, '%Y-%m-%d')
        )
    
    # Order sessions by date, most recent first
    sessions = sessions_query.order_by(Session.timestamp.desc()).all()
    
    # Get player stats for visualizations using converted values
    stats = DataProcessor.get_player_stats(
        user_id,
        date_from=datetime.strptime(date_from, '%Y-%m-%d'),
        date_to=datetime.strptime(date_to, '%Y-%m-%d'),
        min_pitch_speed=min_pitch_speed,
        max_pitch_speed=max_pitch_speed
    )
    
    return render_template(
        'dashboard/player.html',
        users=users,
        user=user,
        stats=stats,
        sessions=sessions,
        filters={
            'date_from': date_from,
            'date_to': date_to,
            'min_pitch_speed': min_pitch_speed,
            'max_pitch_speed': max_pitch_speed
        }
    )