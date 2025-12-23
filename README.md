# Habit-Tracker
A data-driven habit tracking application designed to help users build consistency through automated streak calculations, persistent storage, and simple analytics.
The project supports daily and weekly habits, prevents duplicate completions, and provides insight into user progress over time.

Features

* Add Habits
Create new habits with a defined periodicity (daily or weekly). Invalid periodicities are rejected.

* Complete Habits
Mark habits as completed for the current period.
The system prevents duplicate completions within the same day or week.

* Delete Habits
Remove habits cleanly from the tracker.

* View Habits
Display all habits with their name, periodicity, and current streak.

* Analytics

Filter habits by periodicity (daily or weekly)

Identify the habit with the longest streak

View the current streak for a specific habit

Technologies Used

* Python 3

* datetime for time-based logic

* json for data persistence

* unittest for automated testing

Testing

Unit tests were implemented to validate system behavior and prevent regressions.

Test Coverage Includes:

- Habit creation and validation

- Daily and weekly completion rules

- Correct streak calculation

- Prevention of duplicate completions

- Habit deletion and filtering

- Persistence (save/load from JSON)












Persistent Storage
Habit data is automatically saved to a JSON file and restored when the application restarts.
