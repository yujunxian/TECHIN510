# TempoLog - A Rhythmic Time and Emotion Tracker

## Project Scope

TempoLog is a lightweight, web-based time and emotion management tool built with Streamlit. It helps users log tasks, track time spent, and record emotional state upon completion. The system evaluates task efficiency and visualizes daily performance through a dynamic “tempo spectrum,” helping users reflect on productivity and mental rhythms.

## Target Users

- Students with structured study goals (e.g., exam preparation)
- Remote workers managing solo workflows
- Anyone seeking to increase time awareness and emotional insight

## Key Features

### 1. Task Management
- Input task name and expected duration in minutes
- Start, pause, and end timer with one click
- Prompt for mood selection upon completion

### 2. Efficiency and Emotion Logging
- Efficiency score = (Expected Time / Actual Time) × 100%
- Performance rating: High, Normal, or Low
- Mood options: Happy, Neutral, Stressed

### 3. Data Storage
- Local storage using SQLite
- Records task name, start/end time, mood, and efficiency

### 4. Tempo Spectrum Visualization
- X-axis: Task time span
- Y-axis: Task name
- Bar color represents mood
- Color intensity indicates efficiency (darker = more efficient)

### 5. Optional Extensions
- Integration with external APIs (e.g., mood-based music suggestions)

## Project Timeline

| Week | Milestone                             | What is Expected                                     | What is Delivered               |
|------|----------------------------------------|------------------------------------------------------|----------------------------------|
| 3    | Set up Streamlit UI and Git repository | Basic interface skeleton and GitHub project created  | ✅ GitHub repo & UI started      |
| 4    | Implement task input and timer backend | Functional input form and timer logic in place       | 🔄 Timer partially working       |
| 5    | Connect and test SQLite storage        | Tasks saved with timestamps and moods in database    | 🔄  Under Development                        |
| 6    | Develop visualization features         | Tempo spectrum renders from stored data              | ⏳ Remain to be Started                        |
| 7    | Polish UI and optional API integration | Improved styling and optional API functionality      | ⏳ Remain to be Started                        |
| 8    | Final testing and documentation        | Bug fixing, performance test, README & user guide    | ⏳ Remain to be Started                        |

## Technical Stack

| Layer         | Technology         |
|---------------|--------------------|
| Frontend      | Streamlit (Python) |
| Backend       | Python             |
| Database      | SQLite             |
| Visualization | matplotlib or plotly |

## Challenges

- Ensuring timer accuracy across sessions
- Designing a quick and meaningful mood selection UI
- Creating clean visualizations without overwhelming the user
- Managing API authentication and reliability for optional features
- Considering future need for multi-user support

## Contact Information

| Name        | Role      | GitHub                                   | Email               |
|-------------|-----------|------------------------------------------|---------------------|
| Junxian Yu  | Developer | https://github.com/yujunxian             | yujux1998@gmail.com |
| Siyang Shen | Client    | https://github.com/kumamonlove           | andyshen@uw.edu     |

##  Project Roadmap
The TempoLog project will follow a phased development roadmap:

###  Phase 1 – Core Functionality (Weeks 3–5)
- [x] Set up Git repository and Streamlit app structure
- [x] Build basic task input interface and timer
- [ ] Implement SQLite database for storing tasks
- [ ] Record actual time, expected time, and mood per task

###  Phase 2 – Visualization & Feedback (Weeks 6–7)
- [ ] Design and render tempo spectrum (based on mood and efficiency)
- [ ] Add performance rating (High, Normal, Low)
- [ ] Style UI for clarity and emotional friendliness

###  Phase 3 – Extensions & Finalization (Weeks 7–8)
- [ ] Explore API-based mood-based music suggestions (optional)
- [ ] Perform full usability testing
- [ ] Finalize README and developer/client documentation

>  Core features are prioritized to ensure a functional, single-user productivity tracker.  
>  Optional features will be added based on available time and technical feasibility.

