from flask import Flask, render_template, request, redirect, session, url_for, jsonify, send_from_directory
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import logging
import google.generativeai as genai
import json
from google.api_core import exceptions as google_exceptions
import firebase_admin
from firebase_admin import credentials, firestore
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import random
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

# Configure Gemini
try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    print('Gemini API Key:', os.getenv('GEMINI_API_KEY'))  # 调试用，确认key
    model = genai.GenerativeModel('gemini-1.5-flash')
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
        show_dialog=False  # 只在第一次需要授权时弹窗
    )
    logger.info("Spotify OAuth setup successful")
except Exception as e:
    logger.error(f"Error setting up Spotify OAuth: {str(e)}")
    raise

cred = credentials.Certificate('tempolog-c8c18-firebase-adminsdk-fbsvc-ccdba97725.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'ssy1780626743@gmail.com'
app.config['MAIL_PASSWORD'] = 'jhsc nlpi uopu dchz'
mail = Mail(app)

# 生成验证码
def generate_code():
    return str(random.randint(100000, 999999))

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
        # 首先检查用户是否已登录
        if 'user_email' not in session:
            return redirect(url_for('user_auth'))
            
        # 用户已登录，检查是否已连接Spotify
        if 'token_info' not in session:
            # 已登录但未连接Spotify，显示需要连接Spotify的页面
            return render_template('login.html')
            
        # 用户已登录且已连接Spotify，显示主页
        tracks = get_recent_tracks()
        # 自动生成推荐
        response = generate_recommendations(tracks, "Recommend songs based on my recent listening history")
        if 'recommendations' in response:
            session['recommendations'] = response['recommendations']
        # 获取用户所有任务历史
        user_ref = db.collection('users').document(session['user_email'])
        user_doc = user_ref.get()
        user_tasks = user_doc.to_dict().get('tasks', []) if user_doc.exists else []
        return render_template('index.html', tracks=tracks, recommendations=response.get('recommendations', []), username=session.get('username', ''), user_tasks=user_tasks)
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

@app.route('/task')
def task_page():
    task_name = request.args.get('name', 'Your Task')
    return render_template('task_timer.html', task_name=task_name)

@app.route('/generate_background', methods=['POST'])
def generate_background():
    try:
        data = request.get_json()
        task = data.get('task', '')
        
        # 使用本地图片而不是外部API
        photos = ['forest.jpg', 'trail.jpg', 'bay.jpg', 'star.jpg']
        # 随机选择一张图片，但不是star.jpg（因为star.jpg用于主页）
        available_photos = [p for p in photos if p != 'star.jpg']
        selected_photo = random.choice(available_photos)
        
        # 返回本地图片URL
        return jsonify({
            "background": f"/static/photo/{selected_photo}"
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

        # 检查设备是否存在
        devices = sp.devices()
        if not any(d['id'] == device_id for d in devices['devices']):
            logger.error(f"Device {device_id} not found in available devices")
            return jsonify({"error": "Device not found"}), 400

        # 转移播放权并自动播放
        sp.transfer_playback(device_id=device_id, force_play=True)
        logger.info(f"Playback transferred to device {device_id}")
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error in transfer_playback: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/play_uris', methods=['POST'])
def play_uris():
    try:
        if 'token_info' not in session:
            return jsonify({"error": "Not authenticated"}), 401
        data = request.get_json()
        uris = data.get('uris')
        device_id = data.get('device_id')
        if not uris or not device_id:
            return jsonify({"error": "Missing uris or device_id"}), 400
        sp = spotipy.Spotify(auth=session['token_info']['access_token'])
        sp.start_playback(device_id=device_id, uris=uris)
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error in play_uris: {str(e)}")
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

@app.route('/firestore-test')
def firestore_test():
    # 写入一条测试数据
    db.collection('test').add({'msg': 'Hello Firebase!', 'timestamp': firestore.SERVER_TIMESTAMP})
    # 读取所有测试数据
    docs = db.collection('test').stream()
    result = [doc.to_dict() for doc in docs]
    return {'data': result}

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_email' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.get_json()
    task = data.get('task')
    if not task:
        return jsonify({'error': 'No task provided'}), 400
    user_ref = db.collection('users').document(session['user_email'])
    user_doc = user_ref.get()
    if not user_doc.exists:
        return jsonify({'error': 'User not found'}), 404
    user_data = user_doc.to_dict()
    tasks = user_data.get('tasks', [])
    # 新增任务历史结构：{'content': 内容, 'timestamp': 时间戳}
    tasks.append({'content': task, 'timestamp': datetime.utcnow().isoformat()})
    user_ref.update({'tasks': tasks})
    return jsonify({'success': True, 'tasks': tasks})

@app.route('/del_task', methods=['POST'])
def del_task():
    if 'user_email' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.get_json()
    content = data.get('content')
    timestamp = data.get('timestamp')
    if not content or not timestamp:
        return jsonify({'error': '参数不完整'}), 400
    user_ref = db.collection('users').document(session['user_email'])
    user_doc = user_ref.get()
    if not user_doc.exists:
        return jsonify({'error': 'User not found'}), 404
    user_data = user_doc.to_dict()
    tasks = user_data.get('tasks', [])
    new_tasks = [t for t in tasks if not (t.get('content') == content and t.get('timestamp') == timestamp)]
    user_ref.update({'tasks': new_tasks})
    return jsonify({'success': True, 'tasks': new_tasks})

@app.route('/user')
def user_auth():
    return render_template('user_auth.html')

@app.route('/send_verification_code', methods=['POST'])
def send_verification_code():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'success': False, 'error': 'Email required'})
    code = generate_code()
    session['email_verification_code'] = code
    session['email_to_verify'] = email
    session['code_expire_time'] = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
    try:
        msg = Message(
            subject="您的注册验证码",
            sender=app.config['MAIL_USERNAME'],
            recipients=[email],
            body=f"您的验证码是：{code}，5分钟内有效。"
        )
        mail.send(msg)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/verify_code', methods=['POST'])
def verify_code():
    data = request.get_json()
    code = data.get('code')
    email = data.get('email')
    expire_time = session.get('code_expire_time')
    if not (code and email and expire_time):
        return jsonify({'success': False, 'error': '参数不完整'})
    if datetime.utcnow() > datetime.fromisoformat(expire_time):
        return jsonify({'success': False, 'error': '验证码已过期'})
    if (session.get('email_verification_code') == code and session.get('email_to_verify') == email):
        session['email_verified'] = True
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': '验证码错误'})

@app.route('/auth', methods=['POST'])
def auth():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    is_login = data.get('isLogin', True)
    username = data.get('username')
    
    # 超级用户快速登录（仅用于调试）
    if is_login and email == 'ssy' and password == '11':
        session['user_email'] = 'ssy@debug.com'
        session['username'] = 'Super User (Debug)'
        # 确保超级用户在数据库中存在
        super_user_ref = db.collection('users').document('ssy@debug.com')
        if not super_user_ref.get().exists:
            super_user_ref.set({
                'email': 'ssy@debug.com', 
                'password': generate_password_hash('11'), 
                'username': 'Super User (Debug)', 
                'tasks': []
            })
        return jsonify({'success': True})
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    user_ref = db.collection('users').document(email)
    user_doc = user_ref.get()
    if is_login:
        # 登录
        if not user_doc.exists:
            return jsonify({'error': 'User not found'}), 404
        user_data = user_doc.to_dict()
        if not check_password_hash(user_data.get('password', ''), password):
            return jsonify({'error': 'Incorrect password'}), 401
        session['user_email'] = email
        session['username'] = user_data.get('username', '')
        return jsonify({'success': True})
    else:
        # 注册
        if user_doc.exists:
            return jsonify({'error': 'User already exists'}), 409
        # 检查邮箱验证码
        if not session.get('email_verified') or session.get('email_to_verify') != email:
            return jsonify({'error': '请先完成邮箱验证'}), 400
        if not username:
            return jsonify({'error': '用户名不能为空'}), 400
        hashed_pw = generate_password_hash(password)
        user_ref.set({'email': email, 'password': hashed_pw, 'username': username, 'tasks': []})
        session['user_email'] = email
        session['username'] = username
        session.pop('email_verified', None)
        session.pop('email_verification_code', None)
        session.pop('email_to_verify', None)
        session.pop('code_expire_time', None)
        return jsonify({'success': True})

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == '112233':
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='用户名或密码错误')
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    users = db.collection('users').stream()
    user_list = []
    for u in users:
        d = u.to_dict()
        user_list.append({'email': u.id, 'username': d.get('username', ''), 'tasks': d.get('tasks', [])})
    return render_template('admin_dashboard.html', users=user_list)

@app.route('/delete_user', methods=['POST'])
def delete_user():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'error': '未授权'}), 403
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'success': False, 'error': '缺少邮箱'})
    try:
        db.collection('users').document(email).delete()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/logout_admin')
def logout_admin():
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))

@app.route('/update_task_time', methods=['POST'])
def update_task_time():
    if 'user_email' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    data = request.get_json()
    content = data.get('content')
    timestamp = data.get('timestamp')
    time_spent = data.get('timeSpent')
    if not content or not timestamp or not time_spent:
        return jsonify({'error': '参数不完整'}), 400
    user_ref = db.collection('users').document(session['user_email'])
    user_doc = user_ref.get()
    if not user_doc.exists:
        return jsonify({'error': 'User not found'}), 404
    user_data = user_doc.to_dict()
    tasks = user_data.get('tasks', [])
    new_tasks = []
    from datetime import datetime
    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    for t in tasks:
        if t.get('content') == content and t.get('timestamp') == timestamp:
            # 新增/累加 times 字段
            if 'times' not in t:
                t['times'] = {}
            t['times'][today_str] = t['times'].get(today_str, 0) + int(time_spent)
        new_tasks.append(t)
    user_ref.update({'tasks': new_tasks})
    return jsonify({'success': True, 'tasks': new_tasks})

@app.route('/gemini_recommend', methods=['GET'])
def gemini_recommend():
    try:
        if 'token_info' not in session:
            return jsonify({"error": "Not authenticated with Spotify"}), 401
        
        # Get the user's recent tracks (limited to 10)
        try:
            sp = spotipy.Spotify(auth=session['token_info']['access_token'])
            recently_played = sp.current_user_recently_played(limit=10)
            recent_tracks = [item['track'] for item in recently_played['items']]
            
            if not recent_tracks:
                return jsonify({"error": "No recent tracks found. Please listen to some music on Spotify first."}), 400
            
            # Format the tracks for Gemini
            track_info = "\n".join([
                f"- {track['name']} by {', '.join([artist['name'] for artist in track['artists']])} ({track['album']['name']})"
                for track in recent_tracks
            ])
            
            # Create prompt for Gemini
            prompt = f"""Based on these 10 recently played tracks:
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

            # Generate recommendations using Gemini
            logger.info("Sending request to Gemini API for personalized recommendations")
            response = model.generate_content(prompt)
            
            if not response or not response.text:
                return jsonify({"error": "Empty response from Gemini API"}), 500
            
            # Parse the response into recommendations
            recommendations = []
            lines = response.text.strip().split('\n')
            current_rec = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if ' - ' in line and not line.startswith('Explanation:'):
                    if current_rec:
                        recommendations.append(current_rec)
                    song, artist = line.split(' - ', 1)
                    current_rec = {
                        'song': song.strip(),
                        'artist': artist.strip(),
                        'explanation': ''
                    }
                elif line.startswith('Explanation:'):
                    if current_rec:
                        current_rec['explanation'] = line.replace('Explanation:', '').strip()
            
            if current_rec:
                recommendations.append(current_rec)
            
            if len(recommendations) != 3:
                return jsonify({"error": f"Expected 3 recommendations, got {len(recommendations)}"}), 500
            
            # Search for each track on Spotify to get playable URIs
            for rec in recommendations:
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
            
            # Store recommendations in session
            session['recommendations'] = recommendations
            
            return jsonify({"success": True, "recommendations": recommendations})
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return jsonify({"error": f"Error generating recommendations: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"Error in gemini_recommend route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_todays_rhythm', methods=['GET'])
def get_todays_rhythm():
    try:
        if 'user_email' not in session:
            return jsonify({"error": "Not logged in"}), 401
        if 'token_info' not in session:
            return jsonify({"error": "Not authenticated with Spotify"}), 401
        
        # 获取用户所有任务历史
        user_ref = db.collection('users').document(session['user_email'])
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({"error": "User data not found"}), 404
            
        user_tasks = user_doc.to_dict().get('tasks', [])
        
        # 计算今天的任务时间
        today_str = datetime.utcnow().strftime('%Y-%m-%d')
        today_task_times = {}
        total_time_today = 0
        
        for task in user_tasks:
            if 'times' in task and today_str in task['times']:
                today_task_times[task['content']] = task['times'][today_str]
                total_time_today += task['times'][today_str]
        
        if not today_task_times:
            return jsonify({
                "analysis": "You haven't completed any tasks today. Start your day now!",
                "song": None
            })
        
        # 找出今天花费时间最长的任务
        max_task = max(today_task_times.items(), key=lambda x: x[1])
        max_task_name = max_task[0]
        max_task_time = max_task[1]
        
        # 创建提示 - 使用英文
        prompt = f"""Analyze the user's task completion for today:
Total time: {total_time_today} seconds
Task with most time: {max_task_name} ({max_task_time} seconds)
All task time distribution: {today_task_times}

Please provide the following in ENGLISH ONLY:
1. A short, poetic, and encouraging analysis of the user's work rhythm today (100-200 words)
2. Recommend EXACTLY ONE song that perfectly matches their work pattern today

Respond with a clean JSON object WITHOUT any Markdown formatting like ```json or ``` around it:
{{
  "analysis": "Your poetic analysis in English",
  "song": {{
    "title": "Exact song title",
    "artist": "Exact artist name",
    "reason": "Brief reason for recommendation (2-3 sentences)"
  }}
}}"""

        response = model.generate_content(prompt)
        if not response or not response.text:
            return jsonify({
                "analysis": "Unable to analyze today's rhythm. Please try again later.",
                "song": None
            })
        
        try:
            # 清理响应文本，删除可能的Markdown代码块格式
            text = response.text.strip()
            # 移除可能的markdown代码块格式
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            # 尝试解析Gemini的响应为JSON
            result = json.loads(text)
            
            # 确保只有一首歌曲推荐
            if isinstance(result.get('song'), list) and len(result.get('song')) > 0:
                result['song'] = result['song'][0]  # 只保留第一首歌
            
            # 如果有歌曲推荐，在Spotify上搜索
            if result.get('song') and result['song'].get('title') and result['song'].get('artist'):
                try:
                    sp = spotipy.Spotify(auth=session['token_info']['access_token'])
                    search_query = f"track:{result['song']['title']} artist:{result['song']['artist']}"
                    search_results = sp.search(q=search_query, type='track', limit=1)
                    
                    if search_results['tracks']['items']:
                        track = search_results['tracks']['items'][0]
                        result['song']['spotify_id'] = track['id']
                        result['song']['spotify_uri'] = track['uri']
                        result['song']['album_cover'] = track['album']['images'][0]['url'] if track['album']['images'] else None
                except Exception as e:
                    logger.error(f"Error searching for recommended song: {str(e)}")
            
            return jsonify(result)
        except json.JSONDecodeError as e:
            # Gemini可能没有返回正确的JSON格式，尝试提取文本分析
            logger.error(f"Error parsing Gemini response: {str(e)}, response: {response.text}")
            
            # 返回文本形式的分析
            return jsonify({
                "analysis": response.text.replace("```json", "").replace("```", "").strip(),
                "song": None
            })
            
    except Exception as e:
        logger.error(f"Error in get_todays_rhythm: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/task_recommendations', methods=['POST'])
def task_recommendations():
    try:
        if 'token_info' not in session:
            return jsonify({"error": "Not authenticated with Spotify"}), 401
        data = request.get_json()
        task_name = data.get('task')
        prompt = data.get('prompt')

        if not task_name or not prompt:
            return jsonify({"error": "Task name and prompt are required"}), 400
        
        response = model.generate_content(prompt)
        if not response or not response.text:
            return jsonify({"error": "AI failed to generate recommendations"}), 500

        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        try:
            recommendations = json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Gemini JSON response: {e}\nResponse was:\n{text}")
            return jsonify({"error": "AI returned malformed data"}), 500

        sp = spotipy.Spotify(auth=session['token_info']['access_token'])
        valid_recs = []
        for rec in recommendations:
            if not rec.get('title') or not rec.get('artist'):
                continue
            
            search_query = f"track:{rec['title']} artist:{rec['artist']}"
            search_results = sp.search(q=search_query, type='track', limit=1)

            if search_results['tracks']['items']:
                track = search_results['tracks']['items'][0]
                rec['spotify_id'] = track['id']
                rec['spotify_uri'] = track['uri']
                rec['album_cover'] = track['album']['images'][0]['url'] if track['album']['images'] else None
                rec['duration_ms'] = track.get('duration_ms')
                valid_recs.append(rec)
        
        if not valid_recs:
            return jsonify({"error": "AI recommendations could not be found on Spotify"}), 500

        return jsonify({
            "success": True,
            "recommendations": valid_recs
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        logger.error(f"Error in task_recommendations: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/remove_from_playlist', methods=['POST'])
def remove_from_playlist():
    try:
        if 'token_info' not in session:
            return jsonify({"error": "Not authenticated with Spotify"}), 401
            
        data = request.get_json()
        track_uri = data.get('track_uri')
        playlist_id = data.get('playlist_id')
        
        if not track_uri or not playlist_id:
            return jsonify({"error": "Track URI and playlist ID are required"}), 400
            
        sp = spotipy.Spotify(auth=session['token_info']['access_token'])
        
        # 从播放列表中移除歌曲
        sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_uri])
        
        # 播放下一首歌曲（如果有）
        try:
            sp.next_track()
        except:
            pass
            
        return jsonify({"success": True})
        
    except Exception as e:
        logger.error(f"Error in remove_from_playlist: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/static/photo/<path:filename>')
def serve_photo(filename):
    return send_from_directory('resource/photo', filename)

@app.route('/super')
def super_login():
    """Direct login with super admin credentials"""
    # Create super admin user if doesn't exist
    super_user_ref = db.collection('users').document('ssy@debug.com')
    if not super_user_ref.get().exists:
        super_user_ref.set({
            'email': 'ssy@debug.com', 
            'password': generate_password_hash('11'), 
            'username': 'Super User (Debug)', 
            'tasks': []
        })
    
    # Set session values for automatic login
    session['user_email'] = 'ssy@debug.com'
    session['username'] = 'Super User (Debug)'
    
    # Redirect to home page
    return redirect(url_for('index'))

@app.route('/create_or_update_playlist', methods=['POST'])
def create_or_update_playlist():
    try:
        if 'token_info' not in session:
            return jsonify({"error": "Not authenticated with Spotify"}), 401
        data = request.get_json()
        task_name = data.get('task')
        tracks = data.get('tracks', [])
        if not task_name or not tracks:
            return jsonify({"error": "Task name and tracks are required"}), 400
        sp = spotipy.Spotify(auth=session['token_info']['access_token'])
        playlist_id = None
        playlist_name = f"For {task_name}"
        # 检查是否已有同名播放列表
        playlists = sp.current_user_playlists()
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                playlist_id = playlist['id']
                break
        # 如果找不到同名播放列表，创建一个新的
        if not playlist_id:
            user_id = sp.current_user()['id']
            new_playlist = sp.user_playlist_create(
                user_id,
                playlist_name,
                public=False,
                description=f"Songs for {task_name}"
            )
            playlist_id = new_playlist['id']
        # 追加歌单内容（不替换）
        track_uris = [f"spotify:track:{tid}" for tid in tracks if tid]
        if track_uris:
            sp.playlist_add_items(playlist_id, track_uris)
        return jsonify({
            "success": True,
            "playlist_id": playlist_id,
            "playlist_name": playlist_name
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True) 