from datetime import datetime, timedelta

current_date = datetime.now()
new_date = current_date - timedelta(days=5)

print("Current date:", current_date)
print("5 days ago:", new_date)




from datetime import datetime, timedelta

today = datetime.now().date()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)

print("Yesterday:", yesterday)
print("Today:", today)
print("Tomorrow:", tomorrow)




from datetime import datetime

now = datetime.now()
without_microseconds = now.replace(microsecond=0)

print("Original:", now)
print("Without microseconds:", without_microseconds)





from datetime import datetime

date1 = datetime(2026, 2, 18, 10, 0, 0)
date2 = datetime(2026, 2, 17, 8, 30, 0)

difference = abs((date1 - date2).total_seconds())

print("Difference in seconds:", int(difference))
