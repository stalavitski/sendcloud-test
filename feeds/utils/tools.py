from datetime import datetime
from time import mktime


def get_date_from_struct_time(struct_time):
    time = mktime(struct_time) if struct_time else None
    return datetime.fromtimestamp(time) if time else datetime.now()
