# Task 1: Calculate a date 5 days in the past
from datetime import datetime, timedelta

current_date = datetime.now()          # Get the current date and time
new_date = current_date - timedelta(days=5)  # Subtract 5 days from today

print("Current date:", current_date)
print("5 days ago:", new_date)


# Task 2: Get yesterday, today, and tomorrow's dates
from datetime import datetime, timedelta

today = datetime.now().date()          # Get only the date part (no time)
yesterday = today - timedelta(days=1)  # Go one day back
tomorrow = today + timedelta(days=1)   # Go one day forward

print("Yesterday:", yesterday)
print("Today:", today)
print("Tomorrow:", tomorrow)


# Task 3: Remove microseconds from the current datetime
from datetime import datetime

now = datetime.now()                              # Get current date and time (with microseconds)
without_microseconds = now.replace(microsecond=0) # Set microseconds to 0 to clean up the output

print("Original:", now)
print("Without microseconds:", without_microseconds)


# Task 4: Find the difference in seconds between two dates
from datetime import datetime

date1 = datetime(2026, 2, 18, 10, 0, 0)  # First date:  Feb 18, 2026 at 10:00 AM
date2 = datetime(2026, 2, 17, 8, 30, 0)  # Second date: Feb 17, 2026 at 08:30 AM

difference = abs((date1 - date2).total_seconds())  # abs() ensures the result is always positive

print("Difference in seconds:", int(difference))
