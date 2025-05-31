Meeting note(5/16): https://github.com/yujunxian/TempoLog/issues/4


[Client Milestone 2 - Issue #5](https://github.com/yujunxian/TempoLog/issues/5)

Client has passed my code.(5/16)


# TempoLog: Time Management with Music

TempoLog is a web application that combines time management with Spotify music integration, helping users track their tasks while enjoying personalized music recommendations.

## Features

- **Task Tracking**: Create and manage tasks with built-in time tracking functionality
- **Spotify Integration**: Connect with your Spotify account to access personalized music
- **Today's Rhythm**: AI-powered analysis of your daily activities with custom music recommendations
- **Task-Specific Playlists**: Get tailored music recommendations for specific tasks
- **Visual Experience**: Modern UI with dynamic visual elements and animations
- **Firebase Backend**: Secure user authentication and data storage

## Project Status

✅ **Feature Complete**: All planned features have been successfully implemented and are fully functional.

- The application has undergone extensive testing and debugging
- All core functionality works as expected
- User feedback has been incorporated into the latest version
- The development team has addressed all critical issues

The project is now in a stable state with ongoing maintenance and potential future enhancements based on user feedback.

## Quick Start

For demo purposes, you can access the application directly through the provided ngrok URL:
```
https://tempolog.ngrok.app/super
```
This allows you to bypass the registration and login process and start using the app immediately.

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tempolog.git
cd tempolog
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. The project uses the following environment variables:
```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=https://tempolog.ngrok.app/callback
GEMINI_API_KEY=your_gemini_api_key
CURRENT_HOST=https://tempolog.ngrok.app
```

4. Configure Firebase:
   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
   - Generate a service account key and save it as `tempolog-xxxx-firebase-adminsdk-xxxx-xxxx.json` in the project root
   - Enable Firestore database in your Firebase project

5. Start ngrok:
```bash
./ngrok http --domain=tempolog.ngrok.app 3000
```

6. Run the application in a separate terminal:
```bash
python app.py
```

7. Access the application at:
```
https://tempolog.ngrok.app
```

8. For quick access without registration, use:
```
https://tempolog.ngrok.app/super
```

## Usage Guide

1. **Authentication**: 
   - Register with your email or use the `/super` route to bypass registration
   - Connect your Spotify account when prompted

2. **Task Management**:
   - Add tasks using the input field in the Task List section
   - Start timer for a task by clicking the play button
   - View your time spent on each task

3. **Music Integration**:
   - View "Today's Rhythm" for AI-generated insights about your day with a music recommendation
   - Get personalized music recommendations based on your listening history
   - Receive task-specific playlists when starting a timer for focused work

## Recent Updates

### Version 1.2 (Current)
- **New Feature**: Added `/super` route for quick access without registration
- **UI Enhancement**: Improved interface with modern, transparent panels and Spline animations
- **Music Experience**: Enhanced music player controls at the bottom of the interface
- **Performance**: Updated to Gemini Flash model for faster AI responses

### Version 1.1
- **Core Functionality**: Fixed task time tracking with accurate recording to Firebase
- **Music Integration**: Added task-specific playlist recommendations
- **Analytics**: Implemented English-language poetic text for "Today's Rhythm" analysis
- **Stability**: Fixed automatic music playback issues
- **User Experience**: Enhanced login error messaging

### Version 1.0
- Initial release with basic task tracking and Spotify integration
- Firebase authentication system
- Basic music recommendations

## Known Issues

The development team is aware of and working on the following issues:

- Music player may sometimes require manual refresh to show current track
- Some Spotify content might be unavailable depending on user's Spotify subscription level
- Task timer continues to run if window is closed before stopping the timer
- Limited support for mobile devices (best experience on desktop)
- Occasional delays when generating AI content with Gemini

None of these issues affect the core functionality of the application, and workarounds are available for all of them. Updates addressing these concerns will be released in future versions.

## Technologies Used

- **Backend**: Flask, Firebase
- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS
- **APIs**: Spotify Web API, Google Gemini AI
- **Visual**: Spline 3D animations

## Feedback Addressed

All client feedback has been addressed, including:
- Improved task timer functionality
- Enhanced UI transparency and visual appeal
- Fixed playlist creation and recommendation system
- Added persistent music controls
- Resolved login issues
- Implemented superuser account for debugging

## License

This project is licensed under the MIT License - see the LICENSE file for details.

