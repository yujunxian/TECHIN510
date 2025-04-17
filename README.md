# TempoLog - A Rhythmic Time and Emotion Tracker

## Project Scope

TempoLog is a lightweight, web-based time and emotion management tool built with Streamlit. It helps users log tasks, track time spent, and record emotional state upon completion. The system evaluates task efficiency and visualizes daily performance through a dynamic “tempo spectrum,” helping users reflect on productivity and mental rhythms. To enhance emotional engagement, it now also recommends music based on mood and task efficiency.

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

| Name        | Role      | GitHub                                   | Email               |
|-------------|-----------|------------------------------------------|---------------------|
| Junxian Yu  | Developer | https://github.com/yujunxian             | yujux1998@gmail.com |
| Siyang Shen | Client    | https://github.com/kumamonlove           | andyshen@uw.edu     |

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

### Phase 4 – UI Polish and Feedback (Week 7)
- Style UI and refine visual design
- Add tooltip, labels, or mood icons
- Add optional background audio for ambient feedback

### Phase 5 – Testing and Documentation (Week 8)
- Conduct usability testing and debug edge cases
- Finalize README and user documentation
- Prepare for class demo or final presentation

> Core features are prioritized to ensure a functional, single-user productivity tracker.  
> Music-based extensions enhance emotional engagement and will be implemented based on available time.

