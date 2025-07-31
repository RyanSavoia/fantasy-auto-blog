# app.py - Render deployment version

import json
import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load blogs data (we'll populate this)
BLOGS_DATA = {}

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Fantasy Football Blogs API',
        'total_blogs': len(BLOGS_DATA),
        'endpoints': {
            '/api/blogs': 'GET - All blogs',
            '/api/blogs/<player_name>': 'GET - Specific player',
            '/api/stats': 'GET - Statistics'
        }
    })

@app.route('/api/blogs')
def get_all_blogs():
    """Get all blogs"""
    return jsonify({
        'count': len(BLOGS_DATA),
        'blogs': list(BLOGS_DATA.values())
    })

@app.route('/api/blogs/<player_name>')
def get_player_blog(player_name):
    """Get specific player blog"""
    # Try exact match first
    if player_name in BLOGS_DATA:
        return jsonify(BLOGS_DATA[player_name])
    
    # Try case-insensitive search
    for name, data in BLOGS_DATA.items():
        if name.lower() == player_name.lower():
            return jsonify(data)
    
    return jsonify({'error': 'Player not found'}), 404

@app.route('/api/stats')
def get_stats():
    """Get statistics"""
    if not BLOGS_DATA:
        return jsonify({'total_blogs': 0, 'message': 'No blogs loaded'})
    
    total_words = sum(blog.get('word_count', 0) for blog in BLOGS_DATA.values())
    positions = {}
    
    for blog in BLOGS_DATA.values():
        pos = blog.get('position', 'Unknown')
        positions[pos] = positions.get(pos, 0) + 1
    
    return jsonify({
        'total_blogs': len(BLOGS_DATA),
        'total_words': total_words,
        'positions': positions
    })

def load_blogs_from_json():
    """Load blogs from the exported JSON file"""
    json_file = 'fantasy_blogs_export_20250731_001535.json'  # Your actual filename
    
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to our format
        for blog in data.get('blogs', []):
            player_name = blog.get('player_name')
            if player_name:
                BLOGS_DATA[player_name] = blog
        
        print(f"✅ Loaded {len(BLOGS_DATA)} blogs from {json_file}")
    else:
        print(f"❌ JSON file not found: {json_file}")

if __name__ == '__main__':
    load_blogs_from_json()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
