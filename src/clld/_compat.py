import datetime


def utcnow():
    # compatible with py3.9 and py3.10
    try:
        # >= py3.11
        return datetime.datetime.now(datetime.UTC)
    except AttributeError:  # pragma: no cover  < py3.11
        return datetime.datetime.utcnow()
