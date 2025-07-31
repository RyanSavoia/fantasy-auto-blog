# app.py - Daily rotation fantasy football blogs API
import json
import os
from datetime import datetime, timezone
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load blogs data
BLOGS_DATA = {}
ALL_BLOGS = []

def get_daily_blogs():
    """Get the 5 blogs for today based on date rotation"""
    if not ALL_BLOGS:
        return []
    
    # Use current date to determine which blogs to show
    today = datetime.now(timezone.utc)
    
    # Calculate days since Jan 1, 2025
    start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    days_since_start = (today - start_date).days
    
    # Cycle through weeks (7 days)
    day_in_cycle = days_since_start % 7
    
    # Each day shows 5 blogs
    start_index = day_in_cycle * 5
    end_index = min(start_index + 5, len(ALL_BLOGS))
    
    return ALL_BLOGS[start_index:end_index]

@app.route('/')
def home():
    """Home endpoint"""
    daily_blogs = get_daily_blogs()
    today = datetime.now(timezone.utc)
    days_since_start = (today - datetime(2025, 1, 1, tzinfo=timezone.utc)).days
    day_in_cycle = days_since_start % 7
    
    return jsonify({
        'message': 'Fantasy Football Blogs API - Daily Rotation',
        'total_blogs_in_system': len(ALL_BLOGS),
        'blogs_showing_today': len(daily_blogs),
        'rotation_info': {
            'current_day_in_cycle': day_in_cycle + 1,
            'date': today.strftime('%Y-%m-%d'),
            'blogs_range': f"{day_in_cycle * 5 + 1}-{min((day_in_cycle + 1) * 5, len(ALL_BLOGS))}" if daily_blogs else "None"
        },
        'todays_players': [blog['player_name'] for blog in daily_blogs],
        'debug_info': {
            'current_directory': os.getcwd(),
            'files_in_directory': os.listdir('.'),
            'blogs_loaded': len(ALL_BLOGS) > 0,
            'total_blogs_loaded': len(ALL_BLOGS)
        },
        'endpoints': {
            '/api/blogs': 'GET - Today\'s 5 blogs only',
            '/api/blogs/all': 'GET - All blogs (admin)',
            '/api/blogs/<player_name>': 'GET - Specific player (if showing today)',
            '/api/stats': 'GET - Statistics'
        }
    })

@app.route('/api/blogs')
def get_daily_blogs_api():
    """Get today's 5 blogs only"""
    daily_blogs = get_daily_blogs()
    today = datetime.now(timezone.utc)
    days_since_start = (today - datetime(2025, 1, 1, tzinfo=timezone.utc)).days
    day_in_cycle = days_since_start % 7
    
    return jsonify({
        'date': today.strftime('%Y-%m-%d'),
        'day_in_cycle': day_in_cycle + 1,
        'count': len(daily_blogs),
        'blogs': daily_blogs,
        'next_rotation': 'Tomorrow at midnight UTC'
    })

@app.route('/api/blogs/all')
def get_all_blogs():
    """Get all blogs (admin endpoint)"""
    return jsonify({
        'message': 'All blogs (admin view)',
        'count': len(ALL_BLOGS),
        'blogs': ALL_BLOGS
    })

@app.route('/api/blogs/<player_name>')
def get_player_blog(player_name):
    """Get specific player blog (only if showing today)"""
    daily_blogs = get_daily_blogs()
    
    # Check if player is in today's rotation
    for blog in daily_blogs:
        if blog['player_name'].lower() == player_name.lower():
            return jsonify(blog)
    
    # Check if player exists in system but not showing today
    if any(blog['player_name'].lower() == player_name.lower() for blog in ALL_BLOGS):
        return jsonify({
            'error': 'Player not showing today',
            'message': f'{player_name} is not in today\'s rotation',
            'todays_players': [blog['player_name'] for blog in daily_blogs]
        }), 404
    
    return jsonify({'error': 'Player not found'}), 404

@app.route('/api/stats')
def get_stats():
    """Get statistics"""
    if not ALL_BLOGS:
        return jsonify({'total_blogs': 0, 'message': 'No blogs loaded'})
    
    daily_blogs = get_daily_blogs()
    total_words = sum(blog.get('word_count', 0) for blog in ALL_BLOGS)
    daily_words = sum(blog.get('word_count', 0) for blog in daily_blogs)
    
    positions = {}
    for blog in ALL_BLOGS:
        pos = blog.get('position', 'Unknown')
        positions[pos] = positions.get(pos, 0) + 1
    
    return jsonify({
        'total_blogs_in_system': len(ALL_BLOGS),
        'blogs_showing_today': len(daily_blogs),
        'total_words_all_blogs': total_words,
        'words_in_todays_blogs': daily_words,
        'positions': positions,
        'rotation_schedule': 'New 5 blogs every 24 hours'
    })

def load_blogs_from_json():
    """Load blogs from the exported JSON file"""
    global ALL_BLOGS, BLOGS_DATA
    
    json_file = 'fantasy_blogs_export_20250731_001535.json'
    
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"🔍 JSON structure: {list(data.keys()) if isinstance(data, dict) else 'List'}")
            
            # Handle the actual structure: {"blogs": [...], "count": 35}
            if isinstance(data, dict) and 'blogs' in data:
                ALL_BLOGS = data['blogs']
            elif isinstance(data, list):
                ALL_BLOGS = data
            else:
                print(f"❌ Unexpected JSON structure")
                print(f"Data type: {type(data)}")
                print(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                return False
            
            # Populate the BLOGS_DATA dict for compatibility
            for blog in ALL_BLOGS:
                player_name = blog.get('player_name')
                if player_name:
                    BLOGS_DATA[player_name] = blog
            
            print(f"✅ Loaded {len(ALL_BLOGS)} blogs from {json_file}")
            print(f"📅 Daily rotation: 5 blogs per day for 7 days")
            
            # Show first few player names for debugging
            if ALL_BLOGS:
                sample_names = [blog.get('player_name', 'No name') for blog in ALL_BLOGS[:3]]
                print(f"📝 Sample players: {sample_names}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading {json_file}: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print(f"❌ File not found: {json_file}")
        print(f"Available files: {os.listdir('.')}")
        return False

# Load blogs when the module is imported
load_blogs_from_json()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
