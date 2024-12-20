# app/api/routes.py

from datetime import datetime, timedelta
import numpy as np
from flask import jsonify, request
from app.api import bp
from app.models.hittrax_models import User, Session, Play

@bp.route('/player/<int:user_id>/interval-stats')
def get_interval_stats(user_id):
    """Get stats for specified time intervals with comparison"""
    try:
        interval = request.args.get('interval', '7')
        compare_to = request.args.get('compare_to')
        
        intervals = {
            '7': 7,
            '14': 14,
            '30': 30,
            '90': 90,
            '180': 180,
            '365': 365
        }
        
        def get_stats_for_period(days):
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = Play.query.join(Session).filter(
                Session.userid == user_id,
                Play.active == 1,
                Session.active == 1,
                Session.timestamp >= start_date,
                Session.timestamp <= end_date
            )
            
            plays = query.all()
            
            if not plays:
                return None
                
            valid_velos = [p.exitvelo for p in plays if p.exitvelo and p.exitvelo > 0]
            valid_distances = [p.distance for p in plays if p.distance and p.distance > 0]
            
            return {
                'period_days': days,
                'total_hits': len(plays),
                'avg_exit_velo': round(np.mean(valid_velos), 1) if valid_velos else 0,
                'max_exit_velo': round(max(valid_velos, default=0), 1),
                'avg_distance': round(np.mean(valid_distances) * 3.28084, 1) if valid_distances else 0,
                'max_distance': round(max(valid_distances, default=0) * 3.28084, 1),
                'singles': sum(1 for p in plays if p.result == 1),
                'doubles': sum(1 for p in plays if p.result == 2),
                'triples': sum(1 for p in plays if p.result == 3),
                'home_runs': sum(1 for p in plays if p.result == 4),
                'batting_avg': round(sum(1 for p in plays if p.result in [1,2,3,4]) / len(plays), 3) if plays else 0
            }
            
        # Get primary interval stats
        primary_stats = get_stats_for_period(intervals[interval])
        
        # Get comparison stats if requested
        comparison_stats = None
        improvements = None
        if compare_to and compare_to in intervals:
            comparison_stats = get_stats_for_period(intervals[compare_to])
            
            if primary_stats and comparison_stats:
                def calc_change(current_value, previous_value):
                    """Calculate improvement from previous period to current period"""
                    diff = current_value - previous_value
                    if previous_value != 0:
                        pct = ((current_value / previous_value) - 1) * 100
                    else:
                        pct = 0 if current_value == 0 else 100
                    return {
                        'diff': diff,
                        'pct': pct
                    }
                
                improvements = {
                    'total_hits': calc_change(primary_stats['total_hits'], comparison_stats['total_hits']),
                    'avg_exit_velo': calc_change(primary_stats['avg_exit_velo'], comparison_stats['avg_exit_velo']),
                    'max_exit_velo': calc_change(primary_stats['max_exit_velo'], comparison_stats['max_exit_velo']),
                    'avg_distance': calc_change(primary_stats['avg_distance'], comparison_stats['avg_distance']),
                    'max_distance': calc_change(primary_stats['max_distance'], comparison_stats['max_distance']),
                    'singles': calc_change(primary_stats['singles'], comparison_stats['singles']),
                    'doubles': calc_change(primary_stats['doubles'], comparison_stats['doubles']),
                    'triples': calc_change(primary_stats['triples'], comparison_stats['triples']),
                    'home_runs': calc_change(primary_stats['home_runs'], comparison_stats['home_runs']),
                    'batting_avg': calc_change(primary_stats['batting_avg'], comparison_stats['batting_avg'])
                }
        
        return jsonify({
            'primary_stats': primary_stats,
            'comparison_stats': comparison_stats,
            'improvements': improvements
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@bp.route('/player/<int:user_id>/exit-velo-trend')
def get_exit_velo_trend(user_id):
    """Get exit velocity trend data for visualization"""
    try:
        # Get filter parameters
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        min_pitch_speed = request.args.get('min_pitch_speed', type=float)
        max_pitch_speed = request.args.get('max_pitch_speed', type=float)
        
        # Build base query
        query = Play.query.join(Session).filter(
            Session.userid == user_id,
            Play.active == 1,
            Session.active == 1,
            Play.exitvelo > 0  # Only include valid exit velocities
        )
        
        # Apply filters
        if date_from:
            query = query.filter(Session.timestamp >= datetime.strptime(date_from, '%Y-%m-%d'))
        if date_to:
            query = query.filter(Session.timestamp <= datetime.strptime(date_to, '%Y-%m-%d'))
        if min_pitch_speed:
            query = query.filter(Play.pitchvel >= min_pitch_speed)
        if max_pitch_speed:
            query = query.filter(Play.pitchvel <= max_pitch_speed)
            
        # Order by timestamp
        plays = query.order_by(Play.timestamp).all()
        
        if not plays:
            return jsonify([])
            
        # Calculate moving averages and trend data
        trend_data = []
        window_size = 20  # Rolling average window
        
        # Calculate trend line using linear regression for all points
        timestamps = np.array([(p.timestamp - plays[0].timestamp).total_seconds() 
                            for p in plays])
        velocities = np.array([p.exitvelo for p in plays])
        
        # Fit linear regression
        z = np.polyfit(timestamps, velocities, 1)
        slope, intercept = z[0], z[1]
        
        for i, play in enumerate(plays):
            # Calculate rolling average (EMA)
            start_idx = max(0, i - window_size + 1)
            window_plays = plays[start_idx:i + 1]
            ema = sum(p.exitvelo for p in window_plays) / len(window_plays)
            
            # Calculate monthly average
            month_start = play.timestamp.replace(day=1, hour=0, minute=0, second=0)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            month_plays = [p for p in plays if month_start <= p.timestamp <= month_end]
            monthly_avg = sum(p.exitvelo for p in month_plays) / len(month_plays) if month_plays else None
            
            # Calculate trend value for this point
            seconds_from_start = (play.timestamp - plays[0].timestamp).total_seconds()
            trend_line = slope * seconds_from_start + intercept
            
            trend_data.append({
                'date': play.timestamp.strftime('%Y-%m-%d'),
                'exit_velo': play.exitvelo,
                'ema': round(ema, 1),
                'trend_line': round(trend_line, 1),
                'monthly_avg': round(monthly_avg, 1) if monthly_avg else None
            })
        
        return jsonify(trend_data)
        
    except Exception as e:
        return jsonify({'error': str(e)})