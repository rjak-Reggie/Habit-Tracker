import json
import os
from datetime import datetime, timedelta
from functools import reduce

DATA_FILE = "habits.json"


# =========================
# Habit Model
# =========================
class Habit:
    def __init__(self, name, periodicity, created_at=None, completions=None):
        if periodicity not in ("daily", "weekly"):
            raise ValueError("Periodicity must be 'daily' or 'weekly'")

        self.name = name
        self.periodicity = periodicity
        self.created_at = created_at or datetime.now()
        self.completions = completions or []

    def complete(self, date=None):
        date = date or datetime.now()

        if self.periodicity == "daily":
            already_completed = any(c.date() == date.date() for c in self.completions)
        else:  # weekly
            # Get the Monday of the week for the given date
            week_start = (date - timedelta(days=date.weekday())).date()
            # Check if any completion falls in the same week
            already_completed = any(
                (c - timedelta(days=c.weekday())).date() == week_start
                for c in self.completions
            )

        if not already_completed:
            self.completions.append(date)

    def completed_in_period(self, date):
        start = self.period_start(date)
        return any(c >= start for c in self.completions)

    def period_start(self, date):
        if self.periodicity == "daily":
            return datetime(date.year, date.month, date.day)
        start = date - timedelta(days=date.weekday())
        return datetime(start.year, start.month, start.day)

    def streak(self, reference=None):
        reference = reference or datetime.now()

        if not self.completions:
            return 0

        if self.periodicity == "daily":
            # Get unique completion dates
            completed_dates = {c.date() for c in self.completions}

            # Start from today
            current_date = reference.date()
            streak = 0

            # Count backwards only if today is completed
            if current_date not in completed_dates:
                return 0

            # Count consecutive days backwards
            while current_date in completed_dates:
                streak += 1
                current_date -= timedelta(days=1)

            return streak

        # ---------- WEEKLY ----------
        # Get all unique weeks (represented by their Monday)
        completed_weeks = set()
        for c in self.completions:
            week_monday = c.date() - timedelta(days=c.date().weekday())
            completed_weeks.add(week_monday)

        # Get Monday of current week
        current_week = reference.date() - timedelta(days=reference.date().weekday())

        # Must complete current week to have a streak
        if current_week not in completed_weeks:
            return 0

        streak = 0
        # Count consecutive weeks backwards
        while current_week in completed_weeks:
            streak += 1
            current_week -= timedelta(days=7)

        return streak

    def to_dict(self):
        return {
            "name": self.name,
            "periodicity": self.periodicity,
            "created_at": self.created_at.isoformat(),
            "completions": [c.isoformat() for c in self.completions],
        }

    @staticmethod
    def from_dict(data):
        return Habit(
            data["name"],
            data["periodicity"],
            datetime.fromisoformat(data["created_at"]),
            [datetime.fromisoformat(c) for c in data["completions"]],
        )


# =========================
# Habit Tracker
# =========================
class HabitTracker:
    def __init__(self, filename=DATA_FILE):
        self.filename = filename
        self.habits = self.load()

    def add_habit(self, name, periodicity):
        self.habits.append(Habit(name, periodicity))
        self.save()

    def complete_habit(self, index, date=None):
        self.habits[index].complete(date)
        self.save()

    def delete_habit(self, index):
        del self.habits[index]
        self.save()

    # -------- Analytics (Functional Programming) --------
    def all_habits(self):
        return self.habits

    def habits_by_periodicity(self, period):
        return list(filter(lambda h: h.periodicity == period, self.habits))

    def longest_streak_all(self):
        if not self.habits:
            return None
        return reduce(
            lambda a, b: a if a.streak() >= b.streak() else b,
            self.habits,
        )

    def longest_streak_for(self, index):
        return self.habits[index].streak()

    # -------- Persistence --------
    def save(self):
        with open(self.filename, "w") as f:
            json.dump([h.to_dict() for h in self.habits], f, indent=4)

    def load(self):
        if not os.path.exists(self.filename):
            return self.seed_data()

        with open(self.filename, "r") as f:
            return [Habit.from_dict(d) for d in json.load(f)]

    # -------- Seed Data (5 habits, 4 weeks) --------
    def seed_data(self):
        base = datetime.now() - timedelta(days=35)


        # Weekly habits should have ONE completion per week, not daily
        def gen_daily(weeks):
            return [base + timedelta(days=i) for i in range(weeks * 7)]

        def gen_weekly(weeks):
            return [base + timedelta(days=i * 7) for i in range(weeks)]

        self.habits = [
            Habit("Exercise", "daily", base, gen_daily(4)),
            Habit("Read", "daily", base, gen_daily(4)),
            Habit("Meditate", "daily", base, gen_daily(4)),
            Habit("Call Family", "weekly", base, gen_weekly(4)),
            Habit("Clean House", "weekly", base, gen_weekly(4)),
        ]
        self.save()
        return self.habits


# =========================
# CLI
# =========================
def main():
    tracker = HabitTracker()

    while True:
        print("\n1 Add | 2 Complete | 3 Delete | 4 View | 5 Analytics | 6 Exit")
        choice = input("> ")

        if choice == "1":
            tracker.add_habit(input("Name: "), input("daily/weekly: "))
        elif choice == "2":
            show(tracker)
            tracker.complete_habit(int(input("Index: ")))
        elif choice == "3":
            show(tracker)
            tracker.delete_habit(int(input("Index: ")))
        elif choice == "4":
            show(tracker)
        elif choice == "5":
            analytics(tracker)
        elif choice == "6":
            break


def show(tracker):
    for i, h in enumerate(tracker.all_habits()):
        print(f"{i}. {h.name} ({h.periodicity}) | streak: {h.streak()}")


def analytics(tracker):
    print("1 order periodicity | 2 Longest streak  | 3 show streak count ")
    c = input("> ")

    if c == "1":
        p = input("daily/weekly: ")
        for h in tracker.habits_by_periodicity(p):
            print(h.name)
    elif c == "2":
        h = tracker.longest_streak_all()
        print(f"{h.name}: {h.streak()}")
    elif c == "3":
        show(tracker)
        i = int(input("Index: "))
        print(tracker.longest_streak_for(i))


if __name__ == "__main__":

    main()
