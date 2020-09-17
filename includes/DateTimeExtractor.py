from lark import Lark, Tree, Token
import datetime
from datetime import timedelta
import time, re
from colorama import Fore, Style

def isTreeType(tree, type):
    return tree.data == type
def isTree(obj):
    return isinstance(obj, Tree)
def isToken(obj):
    return isinstance(obj, Token)
def isTokenType(token, type):
    return token.type == type
def debug(msg):
    print("[" + str(time.process_time()) + "] ", msg)

class DateTimeExtractor:

    day_abbreviations = {
        "mo": "montag",
        "di": "dienstag",
        "mi": "mittwoch",
        "do": "donnerstag",
        "fr": "freitag",
        "sa": "samstag",
        "so": "sonntag",
    }

    day_date_mapping = {
        "montag": 0,
        "dienstag": 1,
        "mittwoch": 2,
        "donnerstag": 3,
        "freitag": 4,
        "samstag": 5,
        "sonntag": 6,
    }

    month_abbreviations = {
        "jan": "januar",
        "feb": "februar",
        "mar": "märz",
        "apr": "april",
        "mai": "mai",
        "jun": "juni",
        "jul": "juli",
        "aug": "august",
        "sep": "september",
        "okt": "oktober",
        "nov": "november",
        "dez": "dezember"
    }

    month_date_mapping = {
        "januar": 1,
        "februar": 2,
        "märz": 3,
        "april": 4,
        "mai": 5,
        "juni": 6,
        "juli": 7,
        "august": 8,
        "september": 9,
        "oktober": 10,
        "november": 11,
        "dezember": 12
    }

    time_of_day_mapping = {
        "vormittag": 9,
        "morgen": 9,
        "nachmittag": 15,
        "mittag": 12,
        "abend": 19,
        "nacht":23,
        "früh": 7,
        "in der früh": 7
    }

    flag_weekday_next = True

    #result variables
    date_range = None
    date = None
    time = None

    def __init__(self, grammar, debug = False, datetime_relative_to=None, mode="production"):
        self.grammar = grammar
        self.debug = debug
        self.parser = Lark(grammar, parser="earley", start="root")
        if datetime_relative_to is None:
            datetime_relative_to = datetime.datetime.now()
        self.datetime_relative_to = datetime_relative_to
        self.mode = mode
        self.date_delta = None
        self.date_offset = None

    def parse(self, input_sentence):
        query_with_removals = input_sentence

        input_sentence = self.prepare_input_sentence(input_sentence)

        if self.debug:
            print(input_sentence)
        try:
            self.tree = self.parser.parse(input_sentence)

            self.parse_root()

            # add modifiers
            if self.date_delta is not None:
                if self.date is None:
                    self.date = self.datetime_relative_to.date() + self.date_delta
            if  self.date_offset is not None and self.date_offset is not False:
                if self.date is None:
                    self.date = self.datetime_relative_to
                if isinstance(self.date, datetime.date):
                    self.date = datetime.datetime.combine(self.date, self.datetime_relative_to.time())
                self.date = self.date + self.date_offset
            # quickfix for date/datetime issues
            self.date = self.date.date() if isinstance(self.date, datetime.datetime) else self.date

        except Exception as e:
            if self.debug:
                debug(str(e))
                try:
                    print(self.tree.pretty())
                except Exception as ex:
                    debug(str(ex))

            if self.mode == "production":
                self.date = datetime.datetime.now().date()
                self.time = datetime.datetime.now().time()
            else:
                self.date = self.datetime_relative_to.date()
                self.time = self.datetime_relative_to.time()


    def prepare_input_sentence(self, s):
        #case folding
        s = s.lower()
        #remove unneccessary stuff
        s = re.sub(r"[^\da-zA-ZÖÄÜäöüß\.:\-\s]","",s)
        #remove unneccessary whitespaces
        s = re.sub(r"\s+", " ", s)

        #replace lone numbers 2-9 with digits
        s = re.sub(r"(\s+)zwei(\s+)", r"\1空2\2", s)
        s = re.sub(r"(\s+)drei(\s+)", r"\1空3\2", s)
        s = re.sub(r"(\s+)vier(\s+)", r"\1空4\2", s)
        s = re.sub(r"(\s+)fünf(\s+)", r"\1空5\2", s)
        s = re.sub(r"(\s+)sechs(\s+)", r"\1空6\2", s)
        s = re.sub(r"(\s+)sieben(\s+)", r"\1空7\2", s)
        s = re.sub(r"(\s+)acht(\s+)", r"\1空8\2", s)
        s = re.sub(r"(\s+)neun(\s+)", r"\1空9\2", s)
        s = s.replace("空", "")

        #add whitespace in the end
        if s[-1] == ".":
            s = s[:(len(s)-1)] + " "
        else:
            s = s + " "
        #add start and end (and " . " because it somehow fixes some bugs and doesnt change the meaning)
        s = "<--start-->" + s.strip() + "  <--end-->"
        return s

    def parse_root(self):
        predecessors = [self.tree]
        for c in self.tree.children:
            if isTree(c) and isTreeType(c, "only_date"):
                self.handle_only_date(c, predecessors)
            elif isTree(c) and isTreeType(c, "only_time"):
                self.handle_only_time(c, predecessors)
            elif isTree(c) and (isTreeType(c, "date_time") or isTreeType(c, "time_date")):
                self.handle_date_time(c, predecessors)

    #date only
    def handle_only_date(self, tree, predecessors):
        for c in tree.children:
            if isTree(c) and isTreeType(c, "optional"):
                continue
            elif isTree(c) and isTreeType(c, "date_wrapper"):
                self.handle_date_wrapper(c, predecessors + [c])

    def handle_date_wrapper(self, tree, predecessors):
        for c in tree.children:
            if isTree(c) and isTreeType(c, "date"):
                self.handle_date(c, predecessors + [c])
            elif isTree(c) and isTreeType(c, "date_formatted"):
                self.handle_date_formatted(c, predecessors + [c])
            elif isTree(c) and isTreeType(c, "date_relative"):
                self.handle_date_relative(c, predecessors + [c])

    def handle_date(self, tree, predecessors):
        for c in tree.children:
            if isTree(c) and isTreeType(c, "weekday"):
                self.handle_weekday(c, predecessors + [c])
            if isTree(c) and isTreeType(c, "next_weekday"):
                self.handle_weekday(c, predecessors + [c])
            elif isTree(c) and isTreeType(c, "time_of_day"):
                self.handle_time_of_day(c, predecessors + [c])
            elif isTree(c) and isTreeType(c, "weekend"):
                self.handle_weekend(c, predecessors + [c])
            elif isTree(c) and isTreeType(c, "week"):
                self.handle_week(c, predecessors + [c])
            elif isTree(c) and isTreeType(c, "date_interval"):
                self.handle_date_interval(c, predecessors + [c])

    def handle_weekday(self, tree, predecessors, return_value = False):
        temp_value_weekday = -1
        temp_flag_weekday_next = False
        # we're handling a certain day, so we'll avoid any offsets on time
        self.date_offset = False
        for c in tree.children:
            if isTree(c) and isTreeType(c, "day"):
                temp_value_weekday = self.handle_day(c, predecessors + [c], True)
                if not return_value:
                    self.handle_day(c, predecessors + [c], return_value)
            if isToken(c) and isTokenType(c, "NEXT"):
                temp_flag_weekday_next = True
                if not return_value:
                    self.flag_weekday_next = temp_flag_weekday_next
            if isToken(c) and isTokenType(c, "DAY_ABBR"):
                temp_value_weekday = self.day_date_mapping[self.day_abbreviations[str(c).strip()]]
                if not return_value:
                    self.value_weekday = temp_value_weekday
                continue
            if isToken(c) and isTokenType(c, "TODAY"):
                temp_value_weekday = -1
                if not return_value:
                    self.value_weekday = temp_value_weekday
                continue

        #d = datetime.date.today()
        d = self.datetime_relative_to
        if temp_value_weekday >= 0:
            d = self.get_datetime_for_next(temp_value_weekday)
            if temp_flag_weekday_next:
                d = d + timedelta(days=7)
        elif temp_value_weekday == -1:
            #noop, its today
            d = d
        elif temp_value_weekday == -2:
            #tomorrow
            d = d + timedelta(days=1)
        elif temp_value_weekday == -3:
            #day after tomorrow
            d = d + timedelta(days=2)
        if return_value:
            return d

        self.date = d.date()

    def handle_day(self, tree, predecessors, return_value = False):
        #TOMORROW | DAY_AFTER_TOMORROW | DAYS
        for c in tree.children:
            if isToken(c) and isTokenType(c, "TOMORROW"):
                if return_value:
                    return -2
                else:
                    self.value_weekday = -2
            if isToken(c) and isTokenType(c, "DAY_AFTER_TOMORROW"):
                if return_value:
                    return -3
                else:
                    self.value_weekday = -3
            if isToken(c) and isTokenType(c, "DAYS"):
                if return_value:
                    return self.day_date_mapping[c.strip()]
                else:
                    self.value_weekday = self.day_date_mapping[c.strip()]

    def handle_time_of_day(self, tree, predecessors, return_value = False):
        temp_time_of_day_value_raw = 12
        for c in tree.children:
            if isToken(c) and isTokenType(c, "TIME_OF_DAYS"):
                # remove trailing s if possible
                time_of_day_value = c.strip().rstrip('s')
                temp_time_of_day_value_raw = self.time_of_day_mapping[time_of_day_value]
            if isToken(c) and isTokenType(c, "TOMORROW"):
                temp_time_of_day_value_raw = self.time_of_day_mapping[c.strip()]
            elif isToken(c) and isTokenType(c, "S_OPT"):
                continue
            elif isToken(c) and isTokenType(c, "ON"):
                continue
            elif isToken(c) and isTokenType(c, "NEXT"):
                #bit unclear what to do here, just ignore for now
                continue
        t = datetime.time(temp_time_of_day_value_raw, 0)

        if self.time is not None:
            if self.time.hour < 12 and t is not None and t.hour > 12:
                self.time = (datetime.datetime.combine(datetime.date(1,1,1), self.time) + timedelta(hours=12)).time()
                return self.time
        if return_value:
            return t
        self.time_of_day_value_raw = temp_time_of_day_value_raw
        self.time = t

    def handle_weekend(self, tree, predecessors):
        self.modifier_weekend = 0
        for c in tree.children:
            if isToken(c) and isTokenType(c, "THIS"):
                continue
            if isToken(c) and isTokenType(c, "NEXT"):
                self.modifier_weekend = 1
            if isToken(c) and isTokenType(c, "WEEK_END"):
                #no need to do anything here
                continue
        #create day range for saturday and sunday
        sat = self.get_datetime_for_next(5)
        sun = sat + timedelta(days=1)
        if self.modifier_weekend == 1:
            sat = sat + timedelta(days=7)
            sun = sun + timedelta(days=7)
        self.date_range = (sat, sun)

    def handle_week(self, tree, predecessors):
        day_temp = None
        for c in tree.children:
            if isToken(c) and isTokenType(c, "THIS"):
                self.modifier_week = 0
            if isToken(c) and isTokenType(c, "NEXT"):
                self.modifier_week = 1
            if isToken(c) and isTokenType(c, "IN_ONE"):
                # used to be this before
                # self.modifier_week = 1
                # now get a day and change it to a certain day
                day_temp = (self.datetime_relative_to + timedelta(days=7)).date()
                self.date = day_temp
                # stop caring about the rest
                return
            if isToken(c) and isTokenType(c, "WEEK"):
                #no need to do anything here
                continue
            if isToken(c) and isTokenType(c, "DAYS"):
                #case weekday specified
                day_temp = self.day_date_mapping[c.strip()]
            if isToken(c) and isTokenType(c, "DAY_ABBR"):
                #case weekday specified
                day_temp = self.day_date_mapping[self.day_abbreviations[str(c).strip()]]

        if day_temp is None:
            #either start today until weekend
            #or from upcoming monday to sunday
            start = self.datetime_relative_to
            end = self.get_datetime_for_next(self.day_date_mapping["sonntag"])

            if start.date() == end.date():
                end = end + timedelta(days=6)

            """
            #start is today
            #start = datetime.date.today()
            start = self.datetime_relative_to
            end = start + timedelta(days=7)
            """
            if self.modifier_week == 1:
                start = end + timedelta(days=1)
                end = start + timedelta(days=6)

            self.date_range = (start, end)
        else:
            #case day is specified
            date_temp = self.get_datetime_for_next(day_temp)
            next_sunday = self.get_datetime_for_next(6)
            if date_temp < next_sunday:
                date_temp = date_temp + timedelta(days=7)
            self.date = date_temp.date()

    def handle_date_interval(self, tree, predecessors):
        for c in tree.children:
            if isTree(c) and isTreeType(c, "date_until"):
                self.handle_date_until(c, predecessors + [c])
            if isTree(c) and isTreeType(c, "date_from"):
                self.handle_date_from(c, predecessors + [c])

    def handle_date_until(self, tree, predecessors):
        #this time need context of previous token
        previous_token = None
        #initialize with now, overwrite if date is set
        #start = datetime.date.today()
        start = self.datetime_relative_to
        #end = datetime.date.today()
        end = self.datetime_relative_to
        for c in tree.children:
            if isTree(c) and isTreeType(c, "weekday"):
                if previous_token is None or (isToken(previous_token) and isTokenType(previous_token, "FROM")):
                    # last token is nothing or FROM -> start
                    start = self.handle_weekday(c, predecessors+[c], True)
                else:
                    # last token is something else -> end
                    end = self.handle_weekday(c, predecessors+[c], True)
            elif isTree(c) and isTreeType(c, "time_of_day"):
                # don't do anything, because date intervals only go on date base, not time base
                # can be implemented later though
                continue
            previous_token = c
            #ignore other tokens because not relevant
            continue
        self.date_range = (start, end)

    def handle_date_from(self, tree, predecessors):
        #initialize with now, overwrite if date is set
        #start = datetime.date.today()
        start = self.datetime_relative_to

        for c in tree.children:
            if isTree(c) and isTreeType(c, "weekday"):
                start = self.handle_weekday(c, predecessors+[c], True)
            elif isTree(c) and isTreeType(c, "time_of_day"):
                # don't do anything, because date intervals only go on date base, not time base
                # can be implemented later though
                continue
            previous_token = c
            #ignore other tokens because not relevant
            continue

        # default for end date for +2 days
        end = start + timedelta(days=2)

        self.date_range = (start, end)

    def handle_date_formatted(self, tree, predecessors):
        #today = datetime.date.today()
        today = self.datetime_relative_to
        self.date_month = today.month
        self.date_year = today.year
        self.date_day = today.day

        for c in tree.children:
            if isTree(c) and isTreeType(c, "digit_date_day"):
                self.handle_digit_date_day(c, predecessors + [c])
            elif isToken(c) and isTokenType(c, "MONTH"):
                self.date_month = int(self.month_date_mapping[c.strip()])
            elif isToken(c) and isTokenType(c, "MONTH_ABBR"):
                self.date_month = int(self.month_date_mapping[self.month_abbreviations[c.strip()]])
            elif isToken(c) and isTokenType(c, "DIGIT_MONTH"):
                self.date_month = int (c)
            elif isTree(c) and isTreeType(c, "year"):
                self.handle_year(c, predecessors + [c])
            #ignore other tokens because not relevant
            continue
        d = datetime.datetime(year=self.date_year, month=self.date_month, day=self.date_day)
        self.date = d.date()

    def handle_digit_date_day(self, tree, predecessors):
        day_upper = 0
        day_lower = 0
        for c in tree.children:
            if isToken(c) and isTokenType(c, "DIGIT_LIMITED_DAY"):
                day_upper = int(c) * 10
            elif isToken(c) and isTokenType(c, "DIGIT"):
                day_lower = int(c)
        self.date_day = day_upper + day_lower

    def handle_year(self, tree, predecessors):
        year = 0
        for c in tree.children:
            if isToken(c) and isTokenType(c, "YEAR"):
                year = int(c)
                if year < 1000:
                    year = year + 2000
                self.date_year = year

    def handle_date_relative(self, tree, predecessors):
        temp_next_flag = False
        #start = datetime.date.today()
        #start = self.datetime_relative_to + timedelta(days=1)
        start = datetime.datetime.combine(self.datetime_relative_to.date(), datetime.time(0,0))
        #end = datetime.date.today()
        end = start + timedelta(days=1)
        for c in tree.children:
            if (isToken(c) and isTokenType(c, "NEXT")) or (isToken(c) and isTokenType(c, "DAY_CHAR")):
                temp_next_flag = True
            elif isToken(c) and isTokenType(c, "RELATIVE_DAYS"):
                end = end + timedelta(days=(int(c)-1))
        # no fixed amount of relative days, default to today until in 3 days
        if end == (self.datetime_relative_to + timedelta(days=1)):
            end = self.datetime_relative_to + timedelta(days=3)
        if not temp_next_flag:
            self.date = end.date()
        else:
            self.date_range = (start, end)

    # time only
    def handle_only_time(self, tree, predecessors):
        for c in tree.children:
            if isTree(c) and isTreeType(c, "optional"):
                continue
            elif isTree(c) and isTreeType(c, "time_wrapper"):
                self.handle_time_wrapper(c, predecessors + [c])

    def handle_time_wrapper(self, tree, predecessors):
        for c in tree.children:
            if isTree(c) and isTreeType(c, "time"):
                self.handle_time(c, predecessors + [c])
            elif isTree(c) and isTreeType(c, "time_relative"):
                self.handle_time_relative(c, predecessors + [c])

    def handle_time(self, tree, predecessors):
        time_hint = None
        for c in tree.children:
            if isTree(c) and isTreeType(c, "time_of_day"):
                time_hint = self.handle_time_of_day(c, predecessors + [c], True)
            if isTree(c) and isTreeType(c, "time_specific"):
                self.handle_time_specific(c, predecessors + [c])
        #if self.time.hour < 12 and time_hint is not None and time_hint.hour > 12:
        #    #case like 8 Uhr abends
        #    self.time = self.time + timedelta(hours = 12)
        if time_hint is not None:
            if self.time is None:
                self.time = time_hint
            if self.time is not None:
                if self.time.hour < 12 and time_hint is not None and time_hint.hour > 12:
                    self.time = self.time + timedelta(hours=12)

    def handle_time_specific(self, tree, predecessors):
        for c in tree.children:
            if isTree(c) and isTreeType(c, "clock_time"):
                self.handle_clock_time(c, predecessors + [c])
            elif isTree(c) and isTreeType(c, "qualified_times"):
                self.handle_qualified_times(c, predecessors + [c])

    def handle_clock_time(self, tree, predecessors, return_value = False):
        for c in tree.children:
            if isTree(c) and isTreeType(c, "hour"):
                time = self.handle_hour(c, predecessors + [c], True)
                # extracted time <= 12 and actual time > 12 -> offset 12 hours
                twelve = datetime.time(12, 0)
                time_combined = (datetime.datetime.combine(self.datetime_relative_to, time) + timedelta(hours=12)).time()

                # turns query for 5 Uhr into 17 Uhr if its already past 5 and before 17
                if time <= twelve and self.datetime_relative_to.time() > twelve and time_combined > self.datetime_relative_to.time():
                    time = (datetime.datetime.combine(self.datetime_relative_to, time) + timedelta(hours=12)).time()
                # if its past 12 and the queried time is before 12, check the next day
                # only if no day has actually been specified:
                elif self.date_offset is not False:
                    if time < twelve and self.datetime_relative_to.time() > twelve:
                        self.date_offset = timedelta(days=1)
                self.time = time
                return
            elif isTree(c) and isTreeType(c, "hour_clock_minutes"):
                return self.handle_hour_clock_minutes(c, predecessors + [c])

    def handle_hour(self, tree, predecessors, return_value = False):
        hours = 0
        for c in tree.children:
            if isTree(c) and isTreeType(c, "def_hour"):
                hours = self.handle_def_hour(c, predecessors + [c], True).hour
            elif isTree(c) and isTreeType(c, "digit_num"):
                hours = self.handle_digit_num(c, predecessors + [c], True)
        time = datetime.time(hour=hours)
        if return_value:
            return time
        self.time = time

    def handle_def_hour(self, tree, predecessors, return_value = False):
        #hour = datetime.datetime.now().hour
        hour = self.datetime_relative_to.hour
        minute = 0
        for c in tree.children:
            if isTree(c) and isTreeType(c, "digit_num"):
                hour = self.handle_digit_num(c, predecessors + [c], True)
            elif isTree(c) and isTreeType(c, "full_digit_num"):
                minute = self.handle_full_digit_num(c, predecessors + [c], True)
        t = datetime.time(hour=hour, minute=minute)
        if return_value:
            return t
        self.time = t

    def handle_digit_num(self, tree, predecessors, return_value = False):
        digit = 0
        for c in tree.children:
            if isTree(c) and isTreeType(c, "one_digit"):
                digit = self.handle_one_digit(c, predecessors + [c], True)
            elif isTree(c) and isTreeType(c, "two_digit"):
                digit = self.handle_two_digit(c, predecessors + [c], True)
            elif isToken(c) and isTokenType(c, "DIGIT"):
                digit = int(c)
        if return_value:
            return digit
        self.handle_digit_num_val = digit

    def handle_one_digit(self, tree, predecessors, return_value = False):
        digit = ""
        for c in tree.children:
            if isToken(c) and isTokenType(c, "DIGIT"):
                digit = digit + c
            if isToken(c) and isTokenType(c, "ONE"):
                digit = digit + c
        if return_value:
            return int(digit)
        self.one_digit_val = int(digit)

    def handle_two_digit(self, tree, predecessors, return_value = False):
        digit = ""
        for c in tree.children:
            if isToken(c) and isTokenType(c, "DIGIT"):
                digit = digit + c
            if isToken(c) and isTokenType(c, "TWO"):
                digit = digit + c
        if return_value:
            return int(digit)
        self.two_digit_val = int(digit)

    def handle_full_digit_num(self, tree, predecessors, return_value = False):
        digit = ""
        for c in tree.children:
            if isToken(c) and isTokenType(c, "DIGIT_LIMITED_SIXTY"):
                digit = digit + c
            if isToken(c) and isTokenType(c, "DIGIT"):
                digit = digit + c
        if return_value:
            return int(digit)
        self.full_digit_num = int(digit)

    def handle_hour_clock_minutes(self, tree, predecessors, return_value = False):
        #hour = datetime.datetime.now().hour
        hour = self.datetime_relative_to.hour
        minute = 0
        for c in tree.children:
            if isTree(c) and isTreeType(c, "digit_num"):
                hour = self.handle_digit_num(c, predecessors + [c], True)
            elif isTree(c) and isTreeType(c, "full_digit_num"):
                minute = self.handle_full_digit_num(c, predecessors + [c], True)
        t = datetime.time(hour=hour, minute=minute)
        if return_value:
            return t
        self.time = t

    def handle_qualified_times(self, tree, predecessors):
        for c in tree.children:
            if isTree(c) and isTreeType(c, "from_clock_till_clock"):
                self.handle_from_clock_till_clock(c, predecessors + [c])
            elif isTree(c) and isTreeType(c, "between_clock"):
                self.handle_between_clock(c, predecessors + [c], True)
            elif isTree(c) and isTreeType(c, "qualified_clock"):
                self.handle_qualified_clock(c, predecessors + [c], True)

    def handle_from_clock_till_clock(self, tree, predecessors):
        #start = datetime.datetime.now()
        start = self.datetime_relative_to
        end = start + timedelta(hours=1)
        for c in tree.children:
            if isTree(c) and isTreeType(c, "clock_time"):
                if start is None:
                    start = self.handle_clock_time(c, predecessors + [c], True)
                else:
                    end = self.handle_clock_time(c, predecessors + [c], True)
        #cant handle intervalls on non-day base on API level yet -> return first found value
        self.time = start

    def handle_between_clock(self, tree, predecessors):
        #start = datetime.datetime.now()
        start = self.datetime_relative_to
        end = start + timedelta(hours=1)
        for c in tree.children:
            if isTree(c) and isTreeType(c, "clock_time"):
                if start is None:
                    start = self.handle_clock_time(c, predecessors + [c], True)
                else:
                    end = self.handle_clock_time(c, predecessors + [c], True)
        #cant handle intervalls on non-day base on API level yet -> return first found value
        self.time = start

    def handle_qualified_clock(self, tree, predecessors):
        #start = datetime.datetime.now()
        start = self.datetime_relative_to
        for c in tree.children:
            if isTree(c) and isTreeType(c, "clock_time"):
                    start = self.handle_clock_time(c, predecessors + [c], True)
        #cant handle intervalls on non-day base on API level yet -> return first found value
        end = start + timedelta(hours=5)
        self.time = start

    def handle_time_relative(self, tree, predecessors):
        self.relative_timedelta = timedelta(seconds=0)
        #now = datetime.datetime.now()
        now = self.datetime_relative_to
        in_one = False
        in_type = None
        for c in tree.children:
            if isTree(c) and isTreeType(c, "time_relative_minutes"):
                self.handle_time_relative_minutes(c, predecessors + [c])
            elif isTree(c) and isTreeType(c, "time_relative_hours"):
                self.handle_time_relative_hours(c, predecessors + [c])
            elif isToken(c) and isTokenType(c, "IN_ONE"):
                in_one = True
            elif isToken(c) and isTokenType(c, "HOURS_CHAR"):
                in_type = "h"
            elif isToken(c) and isTokenType(c, "MINUTES_CHAR"):
                in_type = "m"
        # handle in 1 hour / in 1 minute first
        if in_one and in_type is not None:
            if in_type == "m":
                self.relative_timedelta = timedelta(minutes=1)
            else:
                self.relative_timedelta = timedelta(hours=1)
        t = now + self.relative_timedelta
        # handle hours > 24
        if(t.date() > now.date()):
            self.date_delta = t.date() - now.date()
        if isinstance(t, datetime.datetime):
            self.time = t.time()
        else:
           self.time = t


    def handle_time_relative_minutes(self, tree, predecessors):
        minutes = ""
        for c in tree.children:
            if isToken(c) and isTokenType(c, "DIGIT"):
                #concat not add
                minutes = minutes + c
        self.relative_timedelta = timedelta(minutes=(int(minutes)))

    def handle_time_relative_hours(self, tree, predecessors):
        hours = ""
        for c in tree.children:
            if isToken(c) and isTokenType(c, "DIGIT"):
                hours = hours + c
        self.relative_timedelta = timedelta(hours=(int(hours)))

    def handle_date_time(self, tree, predecessors):
        for c in tree.children:
            if isTree(c) and isTreeType(c, "optional"):
                continue
            elif isTree(c) and isTreeType(c, "date_wrapper"):
                self.handle_date_wrapper(c, predecessors + [c])
            elif isTree(c) and isTreeType(c, "time_wrapper"):
                self.handle_time_wrapper(c, predecessors + [c])

    def get_formatted_time(self):
        if self.date_range is not None:
            return ["range", self.date_range]
        if self.time is not None:
            if self.date is None:
                #self.date = datetime.date.today()
                #not changing to relative time here for now
                self.date = datetime.date.today()
            return ["time_point", datetime.datetime.combine(self.date, self.time)]
        if self.date is not None:
            return ["day", self.date]
        return None

    def get_evaluation_result(self):
        result = {'extracted_date': "None", 'extracted_time': "None","extracted_duration_start": "None","extracted_duration_end": "None"}
        if self.date_range is not None:
            result["type"] = "range"
            result["extracted_range_duration_start"] = self.date_range[0].strftime("%Y.%m.%d")
            result["extracted_range_duration_start_datetime"] = self.date_range[0]
            result["extracted_range_duration_end"] = self.date_range[1].strftime("%Y.%m.%d")
            result["extracted_range_duration_end_datetime"] = self.date_range[1]
        if self.time is not None:
            result["extracted_time"] = self.time.strftime("%H:%M")
            result["extracted_time_datetime"] = self.time
            result["type"] = "time_point"
            if self.date is None:
                self.date = self.datetime_relative_to.date()
        if self.date is not None:
            if "type" not in result:
                result["type"] = "day"
            result["extracted_date_datetime"] = self.date
            result["extracted_date"] = self.date.strftime("%Y.%m.%d")

        return result
    def check_if_time_point_can_be_looked_up(self, selected_time):
        datetime_object_for_day_in_48_hours = self.get_current_day() + datetime.timedelta(hours=48)
        #now = datetime.datetime.now()
        now = self.datetime_relative_to
        if datetime_object_for_day_in_48_hours > selected_time > now:
            return True
        return False

    def check_if_day_is_one_of_the_next_15(self, selected_time):
        datetime_object_for_day_in_15_days = self.get_current_day() + datetime.timedelta(days=15)
        #now = datetime.datetime.now()
        now = self.datetime_relative_to
        if datetime_object_for_day_in_15_days > selected_time > now:
            return True
        return False

    def get_datetime_for_next(self, day):
        d = self.datetime_relative_to
        # create datetime and iterate until day matches
        while d.weekday() != day:
            d = d + timedelta(days=1)
        return d