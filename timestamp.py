from datetime import datetime, timezone, tzinfo


def now():
    return datetime.timestamp(datetime.now())


def fromtimestamp(timestamp):
    return datetime.fromtimestamp(timestamp)


print(now())
print(fromtimestamp(now()))
print(fromtimestamp(258745698))
