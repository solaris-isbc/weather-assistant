import datetime

from includes import DateTimeGrammar as dtg, DateTimeExtractor as dte


class TimeDetector:
    extractor = None
    def get_formatted_time(self,query):
        if self.extractor is not None:
            del self.extractor
        self.extractor = dte.DateTimeExtractor(dtg.datetime_grammar)
        self.extractor.parse(query)
        self.result = self.extractor.get_formatted_time()
        return self.result

    def check_if_time_point_can_be_looked_up(self,selected_time, relative):
        if relative == None:
            starting_time = self.get_current_day()
        else:
            starting_time = datetime.datetime.strptime(relative, "%Y.%m.%d %H:%M")
        datetime_object_for_day_in_48_hours = starting_time + datetime.timedelta(hours=46)
        if datetime_object_for_day_in_48_hours > selected_time and selected_time + datetime.timedelta(seconds=1) >= starting_time:
            return True
        return False

    def check_if_day_is_one_of_the_next_14(self,selected_time,relative):
        if relative == None:
            starting_time = self.get_current_day()
        else:
            starting_time = datetime.datetime.strptime(relative, "%Y.%m.%d %H:%M")
        datetime_object_for_day_in_15_days = (starting_time + datetime.timedelta(days=15)).date()
        if datetime_object_for_day_in_15_days > selected_time and starting_time.date() <= selected_time:
            return True
        return False

    def get_current_day(self):
        return datetime.datetime.now()
time_detector = TimeDetector()
