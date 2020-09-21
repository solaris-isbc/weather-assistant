import datetime

from includes import DateTimeGrammar as dtg, DateTimeExtractor as dte


def get_current_day():
    return datetime.datetime.now()


class TimeDetector:
    extractor = None

    def __init__(self):
        self.result = None

    def get_formatted_time(self, query):
        if self.extractor is not None:
            del self.extractor
        self.extractor = dte.DateTimeExtractor(dtg.datetime_grammar)
        self.extractor.parse(query)
        self.result = self.extractor.get_formatted_time()
        return self.result

    def check_if_time_point_can_be_looked_up(self, selected_time, relative=None):
        if relative is None:
            starting_time = get_current_day()
        else:
            starting_time = datetime.datetime.strptime(relative, "%Y.%m.%d %H:%M")
        datetime_object_for_day_in_48_hours = starting_time + datetime.timedelta(hours=46)
        if datetime_object_for_day_in_48_hours > selected_time and selected_time + datetime.timedelta(seconds=1) >= starting_time:
            return True
        return False

    def check_if_day_is_one_of_the_next_14(self, selected_time, relative=None):
        if relative is None:
            starting_time = get_current_day()
        else:
            starting_time = datetime.datetime.strptime(relative, "%Y.%m.%d %H:%M")
        datetime_object_for_day_in_15_days = (starting_time + datetime.timedelta(days=15)).date()
        if datetime_object_for_day_in_15_days > selected_time and starting_time.date() <= selected_time:
            return True
        return False


time_detector = TimeDetector()
