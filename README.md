# TempoLog

A time management and music recommendation application that helps you track your tasks and provides personalized music recommendations.

## Features

- Task time tracking with cumulative statistics
- Daily/Weekly/Monthly time analysis
- Personalized music recommendations based on your Spotify history
- Rhythm analysis using AI
- Spotify Web Playback integration

## Setup Guide

### 1. Clone the Repository
```bash
git clone <repository-url>
cd tempolog
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install and Configure ngrok
```bash
# Download ngrok
curl -O https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.zip

# Unzip ngrok
unzip ngrok-v3-stable-darwin-amd64.zip

# Configure ngrok with your authtoken
./ngrok config add-authtoken 2vutkkbUDzAihrmdmq896upZ1Ln_45gxNminR8WTHUTEYYV67
```

### 5. Start the Application
1. Start ngrok in one terminal:
```bash
./ngrok http --domain=tempolog.ngrok.app 3000
```

2. Start the Flask application in another terminal:
```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the application
python app.py
```

3. Open your browser and visit:
```
https://tempolog.ngrok.app
```

## Usage

1. Open the application in your browser
2. Click "Login with Spotify" to authenticate
3. Add tasks and start tracking your time
4. Get personalized music recommendations
5. View your daily rhythm analysis

## Troubleshooting

### Common Issues

1. **ngrok not found**
   - Make sure you're in the project directory
   - Check if ngrok is executable: `chmod +x ngrok`

2. **Invalid redirect URI**
   - Verify the redirect URI in Spotify Developer Dashboard matches exactly
   - Check your `.env` file for correct URLs

3. **Module not found errors**
   - Make sure you're in the virtual environment
   - Try reinstalling dependencies: `pip install -r requirements.txt`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

