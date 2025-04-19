# TempoLog - A Rhythmic Time and Emotion Tracker

## Project Scope

TempoLog is a lightweight, web-based time and emotion management tool built with Streamlit. It helps users log tasks, track time spent, and record emotional state upon completion. The system evaluates task efficiency and visualizes daily performance through a dynamic "tempo spectrum," helping users reflect on productivity and mental rhythms. To enhance emotional engagement, it now also recommends music based on mood and task efficiency.

## Target Users

- Students with structured study goals (e.g., exam preparation)
- Remote workers managing solo workflows
- Anyone seeking to increase time awareness and emotional insight
- Users who enjoy emotional feedback and music-based motivation

## Key Features

### 1. Task Management
- Input task name and expected duration (in minutes)
- Start, pause, and end timer with one click
- Prompt for mood selection upon task completion

### 2. Efficiency and Emotion Logging
- Efficiency score = (Expected Time / Actual Time) × 100%
- Automatic performance rating: High, Normal, or Low
- Mood options: Happy, Neutral, Stressed

### 3. Data Storage
- Local storage using SQLite
- Records task name, start/end time, mood, and efficiency per entry

### 4. Tempo Spectrum Visualization
- X-axis: Task time span
- Y-axis: Task name
- Bar color represents mood
- Color intensity indicates efficiency (darker = more efficient)

### 5. Mood-Based Music Recommendation
- Recommends music based on user's mood and efficiency using external APIs (e.g., Spotify, or other streaming services)
- Suggests 3–5 songs or playlists tailored to emotional state (e.g., lo-fi for stressed, upbeat for happy/high efficiency)
- Offers links to preview or open full tracks in the music service
- Enhances emotional connection to the rhythm spectrum

### 6. Optional Enhancements
- Natural language summary of daily productivity and mood
- Mood-based background soundtracks to accompany the spectrum
- Future support for user-connected music accounts for personalized recommendations

## Project Timeline

| Week | Milestone                             | What is Expected                                     | What is Delivered               |
|------|----------------------------------------|------------------------------------------------------|----------------------------------|
| 3    | Set up Streamlit UI and Git repository | Basic interface skeleton and GitHub project created  | GitHub repo & UI started      |
| 4    | Implement task input and timer backend | Functional input form and timer logic in place       | Timer partially working       |
| 5    | Connect and test SQLite storage        | Tasks saved with timestamps and moods in database    | Under Development             |
| 6    | Develop visualization features         | Tempo spectrum renders from stored data              | Remain to be Started          |
| 7    | Polish UI and API integration          | Styling + music recommendation feature integration   | Remain to be Started          |
| 8    | Final testing and documentation        | Bug fixing, performance test, README & user guide    | Remain to be Started          |

## Technical Stack

| Layer         | Technology         |
|---------------|--------------------|
| Frontend      | Streamlit (Python) |
| Backend       | Python             |
| Database      | SQLite             |
| Visualization | matplotlib or plotly |
| Music API     | Spotify Web API or similar music recommendation APIs |

## Challenges

- Ensuring timer accuracy across sessions
- Designing a quick and meaningful mood selection UI
- Creating clear, intuitive visualizations
- Mapping mood and efficiency to meaningful music categories
- Integrating with external music APIs and handling token/authentication securely
- Providing a smooth, responsive user interface for music suggestions

## Contact Information

| Name        | Role      | GitHub                                   | Email               | Teams Contact      |
|-------------|-----------|------------------------------------------|---------------------|-------------------|
| Junxian Yu  | Developer | https://github.com/yujunxian             | yujux1998@gmail.com | -                 |
| Siyang Shen | Client    | https://github.com/kumamonlove           | andyshen@uw.edu     | Siyang Shen       |

## Support

If you encounter any issues with the application:

1. First, check the troubleshooting sections in this README
2. For Spotify API or ngrok related issues, verify your setup following the setup guides
3. For urgent issues or questions, contact Siyang Shen on Microsoft Teams
4. For development-related questions, open an issue on the GitHub repository

## 📍 Project Roadmap

The TempoLog project will follow a phased development roadmap:

### Phase 1 – Core Functionality (Weeks 3–5)
- Setup Git repository and Streamlit structure
- Create task input UI and timer logic
- Store expected duration and completed time per task
- Prompt user for mood upon task completion

### Phase 2 – Data Storage & Visualization (Weeks 5–6)
- Implement local storage using SQLite
- Store complete task logs: name, mood, timestamps, efficiency
- Visualize tempo spectrum using mood and efficiency data
- Bar chart with time/mood/intensity mapped appropriately

### Phase 3 – Music Recommendation Module (Week 7)
- Define mood-to-music mapping rules (e.g., Happy → Upbeat, Stressed → Lo-fi)
- Integrate Spotify or other API to get playlist suggestions
- Display top 3–5 suggestions with title, artist, preview link
- Optional: allow refresh for new suggestions

### Phase 4 – UI Polish and Feedback (Week 8)
- Style UI and refine visual design
- Add tooltip, labels, or mood icons
- Add optional background audio for ambient feedback

### Phase 5 – Testing and Documentation (Week 9)
- Conduct usability testing and debug edge cases
- Finalize README and user documentation
- Prepare for class demo or final presentation

> Core features are prioritized to ensure a functional, single-user productivity tracker.  
> Music-based extensions enhance emotional engagement and will be implemented based on available time.

# Spotify Music Recommender

A web application that recommends music based on your preferences and recently played tracks on Spotify.

## Features

- Music recommendations based on your preferences
- Recently played tracks display
- Create playlists from recommendations
- Time management tools (Pomodoro timer and task list)

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=your_redirect_uri
   CURRENT_HOST=your_host
   GEMINI_API_KEY=your_gemini_api_key
   ```
4. Run the application:
   ```bash
   python app.py
   ```

## Virtual Environment Setup

To ensure a clean and isolated development environment, follow these steps to set up a virtual environment:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

3. Install dependencies in the virtual environment:
   ```bash
   pip install -r requirements.txt
   ```

4. To deactivate the virtual environment when you're done:
   ```bash
   deactivate
   ```

### Virtual Environment Best Practices

- Always activate the virtual environment before running the application
- Keep your `requirements.txt` up to date by running:
  ```bash
  pip freeze > requirements.txt
  ```
- Do not commit the `venv` directory to version control
- Add `venv/` to your `.gitignore` file

### Troubleshooting

If you encounter any issues with the virtual environment:

1. Make sure you're using Python 3.x
2. Try recreating the virtual environment:
   ```bash
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Check that all dependencies are installed correctly:
   ```bash
   pip list
   ```

## Spotify API Setup

To use the Spotify integration features, you'll need to set up a Spotify Developer account and configure your application:

1. Create a Spotify Developer Account:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Log in with your Spotify account
   - Click "Create App"

2. Configure Your Application:
   - Fill in the application details:
     - App name: Your app name
     - App description: Brief description
     - Website: Your website (can be placeholder)
     - Redirect URI: Will be set up with ngrok (see below)

3. Get Your API Credentials:
   - After creating the app, you'll receive:
     - Client ID
     - Client Secret
   - Add these to your `.env` file:
     ```
     SPOTIFY_CLIENT_ID=your_client_id
     SPOTIFY_CLIENT_SECRET=your_client_secret
     ```

## Ngrok Setup

Ngrok is used to create a secure tunnel to your local server, which is required for Spotify OAuth:

1. Download and Install Ngrok:
   - Go to [ngrok download page](https://ngrok.com/download)
   - Download the appropriate version for your OS
   - Unzip the file to your project directory

2. Start Ngrok:
   ```bash
   ./ngrok http 8080
   ```
   - This will create a tunnel to your local server running on port 8080
   - Ngrok will display a URL (e.g., `https://xxxx-xxxx-xxxx.ngrok-free.app`)

3. Update Spotify Redirect URI:
   - Copy the ngrok URL
   - Add `/callback` to the end (e.g., `https://xxxx-xxxx-xxxx.ngrok-free.app/callback`)
   - Update in Spotify Developer Dashboard:
     1. Go to your app settings
     2. Add the complete redirect URI to "Redirect URIs"
     3. Save changes

4. Update Your `.env` File:
   ```
   SPOTIFY_REDIRECT_URI=https://xxxx-xxxx-xxxx.ngrok-free.app/callback
   CURRENT_HOST=https://xxxx-xxxx-xxxx.ngrok-free.app/callback
   ```

### Important Notes

- Ngrok URLs change each time you restart ngrok
- You must update both the Spotify Developer Dashboard and `.env` file when the URL changes
- Keep ngrok running while testing the application
- The free version of ngrok provides a different URL each time
- For production, consider using a paid ngrok plan or a proper domain

## Complete Setup Process

1. Set up virtual environment (see Virtual Environment Setup section)
2. Install dependencies from requirements.txt
3. Create Spotify Developer account and get API credentials
4. Download and configure ngrok
5. Update `.env` file with all required credentials:
   ```
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   SPOTIFY_REDIRECT_URI=your_ngrok_url/callback
   CURRENT_HOST=your_ngrok_url/callback
   GEMINI_API_KEY=your_gemini_api_key
   ```
6. Start ngrok: `./ngrok http 8080`
7. Start the application: `python app.py`
8. Access the application through the ngrok URL

### Troubleshooting

If you encounter issues with Spotify authentication:

1. Verify all credentials in `.env` are correct
2. Ensure ngrok is running and the URL is current
3. Check that the redirect URI in Spotify Dashboard matches exactly
4. Clear browser cache and cookies if authentication fails
5. Check the terminal for error messages

