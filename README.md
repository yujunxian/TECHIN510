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

| Week | Milestone                             |
|------|----------------------------------------|
| 3    | Set up Streamlit UI and Git repository |
| 4    | Implement task input and timer backend |
| 5    | Connect and test SQLite storage        |
| 6    | Develop visualization features         |
| 7    | Polish UI and optional API integration |
| 8    | Final testing and documentation        |

## Technical Stack

| Layer       | Technology         |
|-------------|--------------------|
| Frontend    | Streamlit (Python) |
| Backend     | Python             |
| Database    | SQLite             |
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

