import unittest
from datetime import datetime, timedelta
import os
from habit_tracker import Habit, HabitTracker


class TestHabit(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.today = datetime(2024, 1, 15, 10, 0, 0)  # Monday

    def test_create_daily_habit(self):
        """Test creating a daily habit."""
        habit = Habit("Exercise", "daily")
        self.assertEqual(habit.name, "Exercise")
        self.assertEqual(habit.periodicity, "daily")
        self.assertEqual(len(habit.completions), 0)

    def test_create_weekly_habit(self):
        """Test creating a weekly habit."""
        habit = Habit("Call Family", "weekly")
        self.assertEqual(habit.name, "Call Family")
        self.assertEqual(habit.periodicity, "weekly")
        self.assertEqual(len(habit.completions), 0)

    def test_invalid_periodicity(self):
        """Test that invalid periodicity raises ValueError."""
        with self.assertRaises(ValueError):
            Habit("Test", "monthly")

    def test_daily_habit_complete_once(self):
        """Test completing a daily habit once."""
        habit = Habit("Exercise", "daily")
        habit.complete(self.today)
        self.assertEqual(len(habit.completions), 1)
        self.assertEqual(habit.completions[0].date(), self.today.date())

    def test_daily_habit_complete_twice_same_day(self):
        """Test that completing a daily habit twice on the same day only counts once."""
        habit = Habit("Exercise", "daily")
        habit.complete(self.today)
        habit.complete(self.today)
        self.assertEqual(len(habit.completions), 1)

    def test_weekly_habit_complete_once(self):
        """Test completing a weekly habit once."""
        habit = Habit("Call Family", "weekly")
        habit.complete(self.today)
        self.assertEqual(len(habit.completions), 1)

    def test_weekly_habit_complete_twice_same_week(self):
        """Test that completing a weekly habit twice in the same week only counts once."""
        habit = Habit("Call Family", "weekly")
        monday = datetime(2024, 1, 15, 10, 0, 0)
        wednesday = datetime(2024, 1, 17, 10, 0, 0)

        habit.complete(monday)
        habit.complete(wednesday)
        self.assertEqual(len(habit.completions), 1)

    def test_weekly_habit_complete_different_weeks(self):
        """Test completing a weekly habit in different weeks."""
        habit = Habit("Call Family", "weekly")
        week1 = datetime(2024, 1, 15, 10, 0, 0)  # Monday week 1
        week2 = datetime(2024, 1, 22, 10, 0, 0)  # Monday week 2

        habit.complete(week1)
        habit.complete(week2)
        self.assertEqual(len(habit.completions), 2)

    def test_daily_streak_zero_no_completions(self):
        """Test that streak is 0 when there are no completions."""
        habit = Habit("Exercise", "daily")
        self.assertEqual(habit.streak(self.today), 0)

    def test_daily_streak_one_today_only(self):
        """Test daily streak of 1 when only today is completed."""
        habit = Habit("Exercise", "daily")
        habit.complete(self.today)
        self.assertEqual(habit.streak(self.today), 1)

    def test_daily_streak_consecutive_days(self):
        """Test daily streak with consecutive days."""
        habit = Habit("Exercise", "daily")
        # Complete 5 consecutive days ending today
        for i in range(5):
            date = self.today - timedelta(days=4 - i)
            habit.complete(date)

        self.assertEqual(habit.streak(self.today), 5)

    def test_daily_streak_broken(self):
        """Test that daily streak breaks when a day is missed."""
        habit = Habit("Exercise", "daily")
        # Complete today and yesterday, skip day before, complete 3 days before
        habit.complete(self.today)
        habit.complete(self.today - timedelta(days=1))
        habit.complete(self.today - timedelta(days=3))

        self.assertEqual(habit.streak(self.today), 2)  # Only today and yesterday count

    def test_daily_streak_zero_if_today_not_completed(self):
        """Test that daily streak is 0 if today is not completed."""
        habit = Habit("Exercise", "daily")
        # Complete yesterday and day before
        habit.complete(self.today - timedelta(days=1))
        habit.complete(self.today - timedelta(days=2))

        self.assertEqual(habit.streak(self.today), 0)

    def test_weekly_streak_zero_no_completions(self):
        """Test that weekly streak is 0 when there are no completions."""
        habit = Habit("Call Family", "weekly")
        self.assertEqual(habit.streak(self.today), 0)

    def test_weekly_streak_one_this_week_only(self):
        """Test weekly streak of 1 when only this week is completed."""
        habit = Habit("Call Family", "weekly")
        habit.complete(self.today)
        self.assertEqual(habit.streak(self.today), 1)

    def test_weekly_streak_consecutive_weeks(self):
        """Test weekly streak with consecutive weeks."""
        habit = Habit("Call Family", "weekly")
        # Complete 4 consecutive weeks ending this week
        for i in range(4):
            date = self.today - timedelta(days=(3 - i) * 7)
            habit.complete(date)

        self.assertEqual(habit.streak(self.today), 4)

    def test_weekly_streak_broken(self):
        """Test that weekly streak breaks when a week is missed."""
        habit = Habit("Call Family", "weekly")
        # Complete this week, last week, skip 2 weeks ago, complete 3 weeks ago
        habit.complete(self.today)
        habit.complete(self.today - timedelta(days=7))
        habit.complete(self.today - timedelta(days=21))

        self.assertEqual(habit.streak(self.today), 2)  # Only this week and last week

    def test_weekly_streak_zero_if_this_week_not_completed(self):
        """Test that weekly streak is 0 if this week is not completed."""
        habit = Habit("Call Family", "weekly")
        # Complete last week and 2 weeks ago
        habit.complete(self.today - timedelta(days=7))
        habit.complete(self.today - timedelta(days=14))

        self.assertEqual(habit.streak(self.today), 0)

    def test_habit_serialization(self):
        """Test that habit can be converted to dict and back."""
        habit = Habit("Exercise", "daily", self.today, [self.today])
        habit_dict = habit.to_dict()

        self.assertEqual(habit_dict["name"], "Exercise")
        self.assertEqual(habit_dict["periodicity"], "daily")

        restored_habit = Habit.from_dict(habit_dict)
        self.assertEqual(restored_habit.name, habit.name)
        self.assertEqual(restored_habit.periodicity, habit.periodicity)
        self.assertEqual(len(restored_habit.completions), 1)


class TestHabitTracker(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_file = "test_habits.json"
        # Remove test file if it exists to ensure clean state
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.tracker = HabitTracker(self.test_file)
        # Clear seed data to start with empty tracker for most tests
        self.tracker.habits = []
        self.tracker.save()

    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_habit(self):
        """Test adding a habit."""
        initial_count = len(self.tracker.habits)
        self.tracker.add_habit("New Habit", "daily")
        self.assertEqual(len(self.tracker.habits), initial_count + 1)
        self.assertEqual(self.tracker.habits[-1].name, "New Habit")

    def test_delete_habit(self):
        """Test deleting a habit."""
        self.tracker.add_habit("To Delete", "daily")
        initial_count = len(self.tracker.habits)
        self.tracker.delete_habit(0)
        self.assertEqual(len(self.tracker.habits), initial_count - 1)

    def test_complete_habit(self):
        """Test completing a habit."""
        self.tracker.add_habit("Exercise", "daily")
        habit_index = len(self.tracker.habits) - 1
        initial_completions = len(self.tracker.habits[habit_index].completions)

        self.tracker.complete_habit(habit_index)
        self.assertEqual(
            len(self.tracker.habits[habit_index].completions),
            initial_completions + 1
        )

    def test_habits_by_periodicity(self):
        """Test filtering habits by periodicity."""
        # Start fresh
        self.tracker.habits = []

        self.tracker.add_habit("Daily 1", "daily")
        self.tracker.add_habit("Weekly 1", "weekly")
        self.tracker.add_habit("Daily 2", "daily")

        daily_habits = self.tracker.habits_by_periodicity("daily")
        weekly_habits = self.tracker.habits_by_periodicity("weekly")

        self.assertEqual(len(daily_habits), 2)
        self.assertEqual(len(weekly_habits), 1)

    def test_longest_streak_all(self):
        """Test finding habit with longest streak."""
        # Start fresh
        self.tracker.habits = []

        self.tracker.add_habit("Short Streak", "daily")
        self.tracker.add_habit("Long Streak", "daily")

        # Give "Long Streak" more completions
        today = datetime.now()
        for i in range(5):
            self.tracker.habits[1].complete(today - timedelta(days=4 - i))

        # Give "Short Streak" fewer completions
        for i in range(2):
            self.tracker.habits[0].complete(today - timedelta(days=1 - i))

        longest = self.tracker.longest_streak_all()
        self.assertEqual(longest.name, "Long Streak")
        self.assertEqual(longest.streak(), 5)

    def test_longest_streak_for(self):
        """Test getting streak for specific habit."""
        # Start fresh
        self.tracker.habits = []

        self.tracker.add_habit("Exercise", "daily")
        today = datetime.now()

        # Complete 3 consecutive days
        for i in range(3):
            self.tracker.habits[0].complete(today - timedelta(days=2 - i))

        streak = self.tracker.longest_streak_for(0)
        self.assertEqual(streak, 3)

    def test_persistence(self):
        """Test that habits are saved and loaded correctly."""
        # Start fresh
        self.tracker.habits = []

        self.tracker.add_habit("Persistent", "daily")

        # Create new tracker instance with same file
        new_tracker = HabitTracker(self.test_file)

        # Should load the saved habit (not seed data)
        self.assertEqual(len(new_tracker.habits), 1)
        self.assertEqual(new_tracker.habits[0].name, "Persistent")

    def test_all_habits(self):
        """Test getting all habits."""
        # Start fresh
        self.tracker.habits = []

        self.tracker.add_habit("Habit 1", "daily")
        self.tracker.add_habit("Habit 2", "weekly")

        all_habits = self.tracker.all_habits()
        self.assertEqual(len(all_habits), 2)

    def test_seed_data(self):
        """Test that seed data creates 5 habits with 4 weeks of data."""
        # Create a fresh tracker with a different file to test seed data
        seed_file = "test_seed_habits.json"
        if os.path.exists(seed_file):
            os.remove(seed_file)

        seed_tracker = HabitTracker(seed_file)

        # Should have 5 seeded habits
        self.assertEqual(len(seed_tracker.habits), 5)

        # Should have 3 daily and 2 weekly
        daily = seed_tracker.habits_by_periodicity("daily")
        weekly = seed_tracker.habits_by_periodicity("weekly")
        self.assertEqual(len(daily), 3)
        self.assertEqual(len(weekly), 2)

        # Clean up
        if os.path.exists(seed_file):
            os.remove(seed_file)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)