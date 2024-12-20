# app/services/data_processor.py

from datetime import datetime
import pandas as pd
import numpy as np
from sqlalchemy import and_
from app.models.hittrax_models import User, Session, Play

class DataProcessor:
    @staticmethod
    def get_player_stats(user_id, date_from=None, date_to=None, min_pitch_speed=None, max_pitch_speed=None):
        """Get comprehensive player statistics with filtering options"""
        
        # Build base query
        query = Play.query.join(Session).filter(
            Session.userid == user_id,
            Play.active == 1,
            Session.active == 1
        )
        
        # Apply filters
        if date_from:
            query = query.filter(Session.timestamp >= date_from)
        if date_to:
            query = query.filter(Session.timestamp <= date_to)
        if min_pitch_speed:
            query = query.filter(Play.pitchvelmph >= min_pitch_speed)
        if max_pitch_speed:
            query = query.filter(Play.pitchvelmph <= max_pitch_speed)
            
        plays = query.all()
        
        if not plays:
            return {
                'total_hits': 0,
                'avg_exit_velo': 0,
                'max_exit_velo': 0,
                'avg_distance': 0,
                'max_distance': 0,
                'zones_summary': {},
                'exit_velo_trends': []
            }
            
        # Calculate basic stats
        stats = {
            'total_hits': len(plays),
            'avg_exit_velo': np.mean([p.exitvelmph for p in plays if p.exitvelmph and p.exitvelmph > 0]) if plays else 0,
            'max_exit_velo': max([p.exitvelmph for p in plays if p.exitvelmph and p.exitvelmph > 0], default=0),
            'avg_distance': np.mean([p.distancefeet for p in plays if p.distancefeet and p.distancefeet > 0]) if plays else 0,
            'max_distance': max([p.distancefeet for p in plays if p.distancefeet and p.distancefeet > 0], default=0),
            'zones_summary': DataProcessor._calculate_zone_stats(plays),
            'exit_velo_trends': DataProcessor._calculate_exit_velo_trends(plays),
        }
        
        return stats
    
    @staticmethod
    def _calculate_zone_stats(plays):
        """Calculate statistics for each strike zone quadrant"""
        zone_stats = {i: {'count': 0, 'avg_exit_velo': 0} for i in range(0, 15)}
        
        for play in plays:
            if play.quadrant is not None and play.exitvelmph and play.exitvelmph > 0:
                zone = zone_stats.get(play.quadrant, {'count': 0, 'avg_exit_velo': 0})
                zone['count'] += 1
                zone['avg_exit_velo'] = (
                    (zone['avg_exit_velo'] * (zone['count'] - 1) + play.exitvelmph) 
                    / zone['count']
                )
                zone_stats[play.quadrant] = zone
        
        return zone_stats
    
    @staticmethod
    def _calculate_exit_velo_trends(plays):
        """Calculate exit velocity trends over time"""
        if not plays:
            return []
            
        # Convert to pandas for easier time-series analysis
        df = pd.DataFrame([{
            'timestamp': p.timestamp,
            'exit_velo': p.exitvelmph
        } for p in plays if p.exitvelmph and p.exitvelmph > 0])
        
        if df.empty:
            return []
            
        # Sort by timestamp and calculate rolling averages
        df = df.sort_values('timestamp')
        df['rolling_avg'] = df['exit_velo'].rolling(window=20, min_periods=1).mean()
        
        trends = df.apply(lambda row: {
            'date': row['timestamp'].strftime('%Y-%m-%d'),
            'exit_velo': float(row['exit_velo']),
            'rolling_avg': float(row['rolling_avg'])
        }, axis=1).tolist()
        
        return trends