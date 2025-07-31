# app.py - Render deployment version with debugging
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
    """Home endpoint with debugging info"""
    return jsonify({
        'message': 'Fantasy Football Blogs API',
        'total_blogs': len(BLOGS_DATA),
        'debug_info': {
            'current_directory': os.getcwd(),
            'files_in_directory': os.listdir('.'),
            'blogs_loaded': len(BLOGS_DATA) > 0,
            'sample_player_names': list(BLOGS_DATA.keys())[:5] if BLOGS_DATA else []
        },
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
    
    return jsonify({
        'error': 'Player not found',
        'available_players': list(BLOGS_DATA.keys())
    }), 404

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
    # Primary file to look for (your actual local file)
    json_file = '

# Load blogs when the module is imported
load_blogs_from_json()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
