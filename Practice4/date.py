import datetime
from datetime import date, time, timedelta

today = date.today()
print(f"\nToday: {today}")
print(f"Weekday: {today.strftime('%A')}")
print(f"Weekday number: {today.weekday()}")  # Monday = 0
print(f"ISO weekday: {today.isoweekday()}")  # Monday = 1

def days_until(target_date):
    today = date.today()
    delta = target_date - today
    return delta.days

new_year = date(2025, 1, 1)
days = days_until(new_year)
print(f"\nDays until New Year 2025: {days}")