from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import logging
import google.generativeai as genai
import json
from google.api_core import exceptions as google_exceptions

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

# Configure Gemini
try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-pro')
    logger.info("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Error configuring Gemini API: {str(e)}")
    raise

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Get the current host from environment variable or use default
current_host = os.getenv('CURRENT_HOST', 'http://localhost:3000')

# Spotify OAuth setup
try:
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
        scope='user-read-private user-read-email user-read-playback-state user-modify-playback-state user-read-currently-playing user-library-modify user-library-read user-read-recently-played streaming',
        cache_handler=None,  # 禁用缓存，强制重新获取令牌
        show_dialog=True  # 强制显示授权对话框
    )
    logger.info("Spotify OAuth setup successful")
except Exception as e:
    logger.error(f"Error setting up Spotify OAuth: {str(e)}")
    raise

def get_recent_tracks():
    if 'token_info' not in session:
        return []
    try:
        sp = spotipy.Spotify(auth=session['token_info']['access_token'])
        recently_played = sp.current_user_recently_played(limit=20)
        return [item['track'] for item in recently_played['items']]
    except Exception as e:
        logger.error(f"Error getting recent tracks: {str(e)}")
        return []

def generate_recommendations(tracks, user_message):
    try:
        if not tracks:
            return {"error": "I notice you don't have any recent listening history. Please listen to some music on Spotify and try again!"}
            
        # Format track information for the AI
        track_info = "\n".join([
            f"- {track['name']} by {track['artists'][0]['name']} ({track['album']['name']})"
            for track in tracks
        ])
        
        # Create the prompt for Gemini
        prompt = f"""Based on these recently played tracks:
{track_info}

Please recommend exactly 3 songs that would match the user's taste. For each song, provide:
1. The exact song title
2. The exact artist name
3. A brief explanation (2-3 sentences) of why you're recommending it

Format your response as a simple list, with each recommendation on a new line, like this:
Song Title - Artist Name
Explanation: [your explanation]

Song Title - Artist Name
Explanation: [your explanation]

Song Title - Artist Name
Explanation: [your explanation]"""

        logger.info("Sending request to Gemini API")
        try:
            response = model.generate_content(prompt)
            if not response or not response.text:
                logger.error("Empty response from Gemini API")
                return {"error": "I'm having trouble generating recommendations at the moment. Please try again later."}
            
            # Parse the response into recommendations
            recommendations = []
            lines = response.text.strip().split('\n')
            current_rec = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if ' - ' in line and not line.startswith('Explanation:'):
                    # This is a song line
                    if current_rec:
                        recommendations.append(current_rec)
                    song, artist = line.split(' - ', 1)
                    current_rec = {
                        'song': song.strip(),
                        'artist': artist.strip(),
                        'explanation': ''
                    }
                elif line.startswith('Explanation:'):
                    # This is an explanation line
                    if current_rec:
                        current_rec['explanation'] = line.replace('Explanation:', '').strip()
            
            if current_rec:
                recommendations.append(current_rec)
            
            if len(recommendations) != 3:
                logger.error(f"Expected 3 recommendations, got {len(recommendations)}")
                return {"error": "I had trouble generating the right number of recommendations. Please try again."}
            
            # Search for each track on Spotify
            sp = spotipy.Spotify(auth=session['token_info']['access_token'])
            for rec in recommendations:
                # Search for the track
                results = sp.search(q=f"track:{rec['song']} artist:{rec['artist']}", type='track', limit=1)
                if results['tracks']['items']:
                    track = results['tracks']['items'][0]
                    rec['spotify_id'] = track['id']
                    rec['spotify_uri'] = track['uri']
                    rec['album_cover'] = track['album']['images'][0]['url'] if track['album']['images'] else None
                else:
                    rec['spotify_id'] = None
                    rec['spotify_uri'] = None
                    rec['album_cover'] = None
            
            logger.info("Successfully processed recommendations")
            return {"recommendations": recommendations}
            
        except Exception as e:
            logger.error(f"Unexpected error from Gemini API: {str(e)}")
            return {"error": f"I encountered an error while generating recommendations: {str(e)}"}
            
    except Exception as e:
        logger.error(f"Error in generate_recommendations: {str(e)}")
        return {"error": f"I encountered an error while generating recommendations: {str(e)}"}

def create_playlist(tracks):
    try:
        if 'token_info' not in session:
            return None
        
        sp = spotipy.Spotify(auth=session['token_info']['access_token'])
        
        # 获取用户ID
        user_id = sp.current_user()['id']
        
        # 创建播放列表
        playlist = sp.user_playlist_create(
            user_id,
            'Reading',
            public=True,
            description='Recommended songs for reading'
        )
        
        # 添加歌曲到播放列表
        track_uris = [track['spotify_uri'] for track in tracks if track.get('spotify_uri')]
        if track_uris:
            sp.playlist_add_items(playlist['id'], track_uris)
        
        return playlist['id']
    except Exception as e:
        logger.error(f"Error creating playlist: {str(e)}")
        return None

@app.route('/')
def index():
    try:
        if 'token_info' not in session:
            return render_template('login.html')
        
        tracks = get_recent_tracks()
        # 自动生成推荐
        response = generate_recommendations(tracks, "Recommend songs based on my recent listening history")
        if 'recommendations' in response:
            session['recommendations'] = response['recommendations']
        
        return render_template('index.html', tracks=tracks, recommendations=response.get('recommendations', []))
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/auto_recommend')
def auto_recommend():
    try:
        if 'token_info' not in session:
            return jsonify({"error": "Not authenticated"}), 401
        
        tracks = get_recent_tracks()
        response = generate_recommendations(tracks, "Recommend songs based on my recent listening history")
        
        if 'recommendations' in response:
            session['recommendations'] = response['recommendations']
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in auto_recommend route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if 'token_info' not in session:
            return jsonify({"error": "Not authenticated"}), 401
        
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        tracks = get_recent_tracks()
        response = generate_recommendations(tracks, user_message)
        
        # Save recommendations to session if successful
        if 'recommendations' in response:
            session['recommendations'] = response['recommendations']
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in chat route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/login')
def login():
    try:
        auth_url = sp_oauth.get_authorize_url()
        logger.info(f"Generated auth URL: {auth_url}")
        return redirect(auth_url)
    except Exception as e:
        logger.error(f"Error in login route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/callback')
def callback():
    try:
        code = request.args.get('code')
        if not code:
            logger.error("No code received in callback")
            return jsonify({"error": "No authorization code received"}), 400
            
        logger.info("Received authorization code")
        token_info = sp_oauth.get_access_token(code)
        session['token_info'] = token_info
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error in callback route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/logout')
def logout():
    try:
        session.clear()
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error in logout route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/time-management')
def time_management():
    try:
        if 'token_info' not in session:
            return redirect(url_for('login'))
        
        # Get recent tracks and generate recommendations
        tracks = get_recent_tracks()
        response = generate_recommendations(tracks, "Recommend songs based on my recent listening history")
        
        return render_template('time_management.html', recommendations=response.get('recommendations', []))
    except Exception as e:
        logger.error(f"Error in time_management route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/create_playlist', methods=['POST'])
def create_playlist_route():
    try:
        if 'token_info' not in session:
            return jsonify({"error": "Not authenticated"}), 401
        
        # Get the recommendations from the session
        recommendations = session.get('recommendations', [])
        if not recommendations:
            return jsonify({"error": "No recommendations found"}), 400
        
        # Create the playlist
        playlist_id = create_playlist(recommendations)
        if playlist_id:
            return jsonify({"success": True, "playlist_id": playlist_id})
        else:
            return jsonify({"error": "Failed to create playlist"}), 500
    except Exception as e:
        logger.error(f"Error in create_playlist route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/timer')
def timer():
    return render_template('timer.html')

@app.route('/generate_background', methods=['POST'])
def generate_background():
    try:
        data = request.get_json()
        task = data.get('task', '')
        
        # 使用 Gemini API 生成适合任务的背景描述
        prompt = f"Generate a beautiful, calming background image description for someone doing {task}. The image should be suitable for a focus timer app."
        response = model.generate_content(prompt)
        
        # 使用生成的描述来获取图片 URL
        # 这里可以使用 Unsplash API 或其他图片服务
        # 暂时返回一个默认背景
        return jsonify({
            "background": "https://images.unsplash.com/photo-1519681393784-d120267933ba"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/next_track', methods=['POST'])
def next_track():
    try:
        if 'token_info' not in session:
            return jsonify({"error": "Not authenticated"}), 401
        
        sp = spotipy.Spotify(auth=session['token_info']['access_token'])
        current_track = sp.current_playback()
        
        if current_track and current_track['is_playing']:
            sp.next_track()
            # 获取新的当前播放歌曲信息
            new_track = sp.current_playback()
            return jsonify({
                "success": True,
                "track": {
                    "id": new_track['item']['id'],
                    "name": new_track['item']['name'],
                    "artists": new_track['item']['artists'],
                    "album": new_track['item']['album']
                }
            })
        else:
            return jsonify({"error": "No track currently playing"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_user_playlists')
def get_user_playlists():
    try:
        sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
        playlists = sp.current_user_playlists()
        return jsonify({
            "success": True,
            "playlists": playlists['items']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_token')
def get_token():
    try:
        if 'token_info' not in session:
            logger.error("No token_info in session")
            return jsonify({"error": "Not authenticated"}), 401
        
        # 检查令牌是否过期
        if sp_oauth.is_token_expired(session['token_info']):
            logger.info("Token expired, refreshing...")
            try:
                session['token_info'] = sp_oauth.refresh_access_token(session['token_info']['refresh_token'])
                logger.info("Token refreshed successfully")
            except Exception as e:
                logger.error(f"Error refreshing token: {str(e)}")
                return jsonify({"error": "Failed to refresh token"}), 401
        
        # 验证令牌
        sp = spotipy.Spotify(auth=session['token_info']['access_token'])
        try:
            user = sp.current_user()
            logger.info(f"Token validated for user: {user['id']}")
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return jsonify({"error": "Invalid token"}), 401
        
        return jsonify({
            "access_token": session['token_info']['access_token']
        })
    except Exception as e:
        logger.error(f"Error in get_token: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/transfer_playback', methods=['POST'])
def transfer_playback():
    try:
        if 'token_info' not in session:
            logger.error("No token_info in session")
            return jsonify({"error": "Not authenticated"}), 401
        
        data = request.get_json()
        device_id = data.get('device_id')
        
        if not device_id:
            logger.error("No device ID provided")
            return jsonify({"error": "No device ID provided"}), 400
        
        sp = spotipy.Spotify(auth=session['token_info']['access_token'])
        
        # 验证设备
        try:
            devices = sp.devices()
            if not any(d['id'] == device_id for d in devices['devices']):
                logger.error(f"Device {device_id} not found in available devices")
                return jsonify({"error": "Device not found"}), 400
        except Exception as e:
            logger.error(f"Error getting devices: {str(e)}")
            return jsonify({"error": "Failed to get devices"}), 500
        
        # 转移播放
        try:
            sp.transfer_playback(device_id=device_id, force_play=True)
            logger.info(f"Playback transferred to device {device_id}")
            return jsonify({"success": True})
        except Exception as e:
            logger.error(f"Error transferring playback: {str(e)}")
            return jsonify({"error": "Failed to transfer playback"}), 500
    except Exception as e:
        logger.error(f"Error in transfer_playback: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/save_track', methods=['POST'])
def save_track():
    try:
        if 'token_info' not in session:
            return jsonify({"error": "Not authenticated"}), 401
        
        sp = spotipy.Spotify(auth=session['token_info']['access_token'])
        current_track = sp.current_playback()
        
        if current_track and current_track['item']:
            track_id = current_track['item']['id']
            sp.current_user_saved_tracks_add([track_id])
            return jsonify({"success": True})
        else:
            return jsonify({"error": "No track currently playing"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze_rhythm', methods=['POST'])
def analyze_rhythm():
    try:
        data = request.get_json()
        task_times = data.get('taskTimes', {})
        
        if not task_times:
            return jsonify({"analysis": "No tasks completed today. Start your journey!"})
        
        # 计算总时间
        total_time = sum(task_times.values())
        
        # 找出最长时间的任务
        max_task = max(task_times.items(), key=lambda x: x[1])
        
        # 创建提示
        prompt = f"""Based on today's task completion times:
Total time: {total_time} seconds
Most focused task: {max_task[0]} ({max_task[1]} seconds)
Task distribution: {task_times}

Please provide a brief, encouraging analysis of the user's work rhythm today. Focus on:
1. Overall productivity pattern
2. Most productive areas
3. Suggestions for improvement
Keep it concise and motivational."""

        try:
            response = model.generate_content(prompt)
            if response and response.text:
                return jsonify({"analysis": response.text})
            else:
                return jsonify({"analysis": "Unable to analyze rhythm at the moment."})
        except Exception as e:
            logger.error(f"Error generating rhythm analysis: {str(e)}")
            return jsonify({"analysis": "Error analyzing rhythm."})
            
    except Exception as e:
        logger.error(f"Error in analyze_rhythm: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True) 