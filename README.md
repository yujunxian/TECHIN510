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

# TempoLog – Client Milestone 1 Meeting Note - May 02

## 1. Features Reviewed

### Task Time Tracking & Statistics
- Users can add tasks and track time per task.
- Cumulative time is displayed with support for daily/weekly/monthly views.

### Spotify Music Recommendation & Web Playback
- Integrated Spotify login.
- Fetches recommended songs and plays them directly via Spotify Web Playback SDK.

### AI Rhythm Analysis
- Integrated Gemini API to auto-generate daily rhythm summaries based on user task distribution.
- Enhances motivation and engagement.

---

## 2. Unit Testing
- Unit tests implemented for key backend functions:
  - Task time accumulation logic
  - Music recommendation interface
- Ensures correctness of main business logic.

---

## 3. README Update
README has been thoroughly updated to include:
- Environment setup & dependencies
- ngrok configuration and startup
- Virtual environment instructions
- Project feature overview
- Troubleshooting for common issues

---

## 4. Client Review

### Code Review
*Approved.* Code structure is clean, well-commented, and easy to maintain.

### Functional Review
- Personally tested: task creation, timing, music recommendation, AI analysis.
- UI is intuitive and responsive.

---

## 5. Approvals & Requested Changes
  - Core features approved.
  - Recommended improvements:
  - Task deletion & editing support
  - Better mobile responsiveness

---

## 6. Bug Reports & Suggestions

### Bug Feedback
- Spotify login occasionally fails due to token expiration; requires page refresh.

### Suggestions
- Add celebration animation after task completion.
- Implement task categorization and labeling for better management.

---

## 7. Reflection
The project has achieved all major goals: task tracking, Spotify integration, and AI rhythm analysis. Third-party services work smoothly, and documentation is clear. Improvements should focus on exception handling, UI polishing, and more test coverage—especially for edge cases and mobile behavior.

