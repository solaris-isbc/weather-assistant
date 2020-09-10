import datetime
import re
import dateutil.parser

class TimeDetector():

    # init
    def get_formatted_time(self,query):
        self.query_with_removals = query
        current_day = self.get_current_day()
        if self.get_day(query,current_day) is None:
            if self.get_time(query, current_day) is None:
                return self.check_alternative_formulations(query,current_day)
            else:
                return ["time_point",self.get_time(query, current_day)]
        else:
            if self.get_time(query, current_day) is None:
                return ["day",self.get_day(query,current_day)]
            else:
                return ["time_point",self.get_time(query, self.get_day(query,current_day))]

    def check_if_time_point_can_be_looked_up(self,selected_time):
        datetime_object_for_day_in_48_hours = self.get_current_day() + datetime.timedelta(hours=48)
        if datetime_object_for_day_in_48_hours > selected_time:
            return True
        return False

    def check_if_day_is_one_of_the_next_15(self,selected_time):
        datetime_object_for_day_in_15_days = self.get_current_day() + datetime.timedelta(days=15)
        if datetime_object_for_day_in_15_days > selected_time:
            return True
        return False

    def check_alternative_formulations(self,query,current_day):
        if bool(re.search("nächste woche|kommende woche|darauffolgende woche", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("nächste woche|kommende woche|darauffolgende woche")
            return ["range", current_day + datetime.timedelta(days=self.next_weekday(current_day, 0)),current_day + datetime.timedelta(days=self.next_weekday(current_day, 6))]
        if bool(re.search("woche", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("woche")
            return ["range", current_day,current_day + datetime.timedelta(days=self.next_weekday(current_day, 6))]
        if bool(re.search("(2|zwei) tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("(2|zwei) tag[e]?")
            return ["range", current_day, current_day + datetime.timedelta(days=2)]
        if bool(re.search("(3|drei) tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("(3|drei) tag[e]?")
            return ["range", current_day, current_day + datetime.timedelta(days=3)]
        if bool(re.search("(4|vier) tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("(4|vier) tag[e]?")
            return ["range", current_day, current_day + datetime.timedelta(days=4)]
        if bool(re.search("(5|fünf) tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("(5|fünf) tag[e]?")
            return ["range", current_day, current_day + datetime.timedelta(days=5)]
        if bool(re.search("(6|sechs) tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("(6|sechs) tag[e]?")
            return ["range", current_day, current_day + datetime.timedelta(days=6)]
        if bool(re.search("(7|sieben) tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("(7|sieben) tag[e]?")
            return ["range", current_day, current_day + datetime.timedelta(days=7)]
        if bool(re.search("(8|acht) tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("(8|acht) tag[e]?")
            return ["range", current_day, current_day + datetime.timedelta(days=8)]
        if bool(re.search("(9|neun) tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("(9|neun) tag[e]?")
            return ["range", current_day, current_day + datetime.timedelta(days=9)]
        if bool(re.search("(10|zehn) tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("(10|zehn) tag[e]?")
            return ["range", current_day, current_day + datetime.timedelta(days=10)]
        if bool(re.search("(11|elf) tag[s]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("(11|elf) tag[s]?")
            return ["range", current_day, current_day + datetime.timedelta(days=11)]
        if bool(re.search("(12|zwölf) tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("(12|zwölf) tag[e]?")
            return ["range", current_day, current_day + datetime.timedelta(days=12)]
        if bool(re.search("(13|dreizehn) tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("(13|dreizehn) tag[e]?")
            return ["range", current_day, current_day + datetime.timedelta(days=13)]
        if bool(re.search("(14|vierzehn) tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("(14|vierzehn) tag[e]?")
            return ["range", current_day, current_day + datetime.timedelta(days=14)]
        if bool(re.search("(15|fünfzehn) tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("(15|fünfzehn) tag[e]?")
            return ["range", current_day, current_day + datetime.timedelta(days=15)]
        if bool(re.search("nacht", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("nacht[s]?")
            return ["time_point", current_day.replace(hour=0,minute=0) + datetime.timedelta(days=1)]

        return ["day", self.get_current_day()]

    def get_current_day(self):
        today = datetime.datetime.now()
        return today

    def remove_time_attributes_from_query(self,expression):
        self.query_with_removals = re.sub(expression, '', self.query_with_removals)

    def get_day(self,query,current_day):
        if bool(re.search("heute|(diese +tag)", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("heute|(diese +tag)")
            return current_day
        current_day = current_day.replace(hour=0,minute=0,microsecond=0,second=0)
        if bool(re.search("morgen", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("morgen")
            return current_day + datetime.timedelta(days=1)
        if bool(re.search("übermorgen", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("übermorgen")
            return current_day + datetime.timedelta(days=2)
        if bool(re.search(r"(in) [0-9]+ tag", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query(r"\b((in) [0-9]+ tag[e]?[n]?)\b")
            return current_day + datetime.timedelta(days=int(re.findall("[1-9]+",re.findall(r"\b((in) [0-9]+ tagen)\b", query, re.IGNORECASE)[0][0])[0]))
        if bool(re.search("in einem tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("in einem tag[e]?")
            return current_day + datetime.timedelta(days=1)
        if bool(re.search("in zwei tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("in zwei tag[e]?")
            return current_day + datetime.timedelta(days=2)
        if bool(re.search("in drei tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("in drei tag[e]?")
            return current_day + datetime.timedelta(days=3)
        if bool(re.search("in vier tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("in vier tag[e]?")
            return current_day + datetime.timedelta(days=4)
        if bool(re.search("in fünf tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("in fünf tag[e]?")
            return current_day + datetime.timedelta(days=5)
        if bool(re.search("in sechs tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("in sechs tag[e]?")
            return current_day + datetime.timedelta(days=6)
        if bool(re.search("in sieben tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("in sieben tag[e]?")
            return current_day + datetime.timedelta(days=7)
        if bool(re.search("in acht tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("in acht tag[e]?")
            return current_day + datetime.timedelta(days=8)
        if bool(re.search("in neun tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("in neun tag[e]?")
            return current_day + datetime.timedelta(days=9)
        if bool(re.search("in zehn tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("in zehn tag[e]?")
            return current_day + datetime.timedelta(days=10)
        if bool(re.search("in elf tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("in elf tag[e]?")
            return current_day + datetime.timedelta(days=11)
        if bool(re.search("in zwölf tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("in zwölf tag[e]?")
            return current_day + datetime.timedelta(days=12)
        if bool(re.search("in dreizehn tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("in dreizehn tag[e]?")
            return current_day + datetime.timedelta(days=13)
        if bool(re.search("in vierzehn tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("in vierzehn tag[e]?")
            return current_day + datetime.timedelta(days=14)
        if bool(re.search("in fünfzehn tag[e]?", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("in fünfzehn tag[e]?")
            return current_day + datetime.timedelta(days=15)
        if bool(re.search("montag", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("montag")
            return current_day + datetime.timedelta(days=self.next_weekday(current_day, 0))
        if bool(re.search("dienstag", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("dienstag")
            return current_day + datetime.timedelta(days=self.next_weekday(current_day, 1))
        if bool(re.search("mittwoch", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("mittwoch")
            return current_day + datetime.timedelta(days=self.next_weekday(current_day, 2))
        if bool(re.search("donnerstag", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("donnerstag")
            return current_day + datetime.timedelta(days=self.next_weekday(current_day, 3))
        if bool(re.search("freitag", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("freitag")
            return current_day + datetime.timedelta(days=self.next_weekday(current_day, 4))
        if bool(re.search("samstag", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("samstag")
            return current_day + datetime.timedelta(days=self.next_weekday(current_day, 5))
        if bool(re.search("sonntag", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("sonntag")
            return current_day + datetime.timedelta(days=self.next_weekday(current_day, 6))
        if bool(re.search("(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d", query, re.IGNORECASE)):
            self.remove_time_attributes_from_query("(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d")
            date = re.findall("(0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])[- /.](19|20)\d\d", query, re.IGNORECASE)
            month = int(date[0][0])
            day = int(date[0][1])
            year = int(date[0][2])
            return current_day.replace(month= month, day = day, year = year)
        return None

    def next_weekday(self, d, weekday):
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return days_ahead

    def get_time(self,query,current_day):
        hours = ["eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf", "dreizehn",
                 "vierzehn", "fünfzehn", "sechzehn", "siebzehn", "achtzehn", "neunzehn", "zwanzig", "einundzwanzig", "zweiundzwanzig",
                 "dreiundzwanzig"]
        for i in range(0,23):
            if bool(re.search(r"in "+hours[i]+" ?stunde[n]?",query,re.IGNORECASE)) or bool(re.search(r"in "+str(i)+" ?stunde[n]?",query,re.IGNORECASE)):
               self.remove_time_attributes_from_query(r"in "+hours[i]+" ?stunde[n]?")
               self.remove_time_attributes_from_query(r"in "+str(i)+" ?stunde[n]?")
               hours = self.get_current_day().hour+i+1
               if hours >= 24:
                 return current_day.replace(hour=hours-24)+datetime.timedelta(days=1)
               else:
                 return current_day.replace(hour = self.get_current_day().hour+i+1)

        if bool(re.search(r"( |^)(((([0]?[0-9])|[1][0-1])(:(([0-5][0-9])|60))?)|12(:00)?) ?(pm|am)",query, re.IGNORECASE)):
           time = re.search(r"( |^)(((([0]?[0-9])|[1][0-1])(:(([0-5][0-9])|60))?)|12(:00)?) ?(pm|am)",query, re.IGNORECASE).group()
           self.remove_time_attributes_from_query(r"( |^)(((([0]?[0-9])|[1][0-1])(:(([0-5][0-9])|60))?)|12(:00)?) ?(pm|am)")
           time_object = dateutil.parser.parse(time)
           hours = time_object.hour
           minutes = time_object.minute
           return current_day.replace(hour = hours, minute = minutes)

        if bool(re.search(r"((es ist)|(es schlägt)|(um))[0-9:]+",query, re.IGNORECASE)):
           time = re.findall("[0-9:]+",re.search(r"((es ist)|(es schlägt)|(um))[0-9:]+",query, re.IGNORECASE).group())[0]
           self.remove_time_attributes_from_query(r"((es ist)|(es schlägt)|(um))[0-9:]+")
           if len(re.findall(r"[:]",query, re.IGNORECASE)) is 0:
               time+=":00"
           try:
               time_object = dateutil.parser.parse(time)
               hours = time_object.hour
               minutes = time_object.minute
               return current_day.replace(hour=hours, minute=minutes)
           except:
               pass

        if bool(re.search(r"[0-9:]+( uhr)",query, re.IGNORECASE)):
           time = re.findall("[0-9:]+",re.search(r"[0-9:]+( uhr)",query, re.IGNORECASE).group())[0]
           self.remove_time_attributes_from_query(r"[0-9:]+( uhr)")
           if len(re.findall(r"[:]",query, re.IGNORECASE)) is 0:
               time+=":00"
           try:
               time_object = dateutil.parser.parse(time)
               hours = time_object.hour
               minutes = time_object.minute
               return current_day.replace(hour=hours, minute=minutes)
           except:
               pass

        if bool(re.search(r"[0-9:]+[:][0-9:]+",query, re.IGNORECASE)):
           time = re.findall("[0-9:]+[:][0-9:]+",re.search(r"[0-9:]+[:][0-9:]+",query, re.IGNORECASE).group())[0]
           if len(re.findall(r"[:]",query, re.IGNORECASE)) is 0:
               time+=":00"
           try:
               self.remove_time_attributes_from_query(r"[0-9:]+")
               time_object = dateutil.parser.parse(time)
               hours = time_object.hour
               minutes = time_object.minute
               return current_day.replace(hour=hours, minute=minutes)
           except:
               pass
        if bool(re.search(r"\b(mitter)?nacht[s]?\b",query, re.IGNORECASE)):
            self.remove_time_attributes_from_query(r"\b(mitter)?nacht[s]?\b")
            return current_day.replace(hour=0,minute=0) + datetime.timedelta(days=1)
        if bool(re.search(r"\b(morgens|am morgen)\b",query, re.IGNORECASE)):
            self.remove_time_attributes_from_query(r"\bmorgen[s]?\b")
            return current_day.replace(hour=6,minute=0)
        if bool(re.search(r"\bmittag[s]?\b",query, re.IGNORECASE)):
            self.remove_time_attributes_from_query(r"\bmittag[s]?\b")
            return current_day.replace(hour=12, minute=0)
        if bool(re.search(r"\bnachmittag[s]?\b",query, re.IGNORECASE)):
            self.remove_time_attributes_from_query(r"\bnachmittag[s]?\b")
            return current_day.replace(hour=15, minute=0)
        if bool(re.search(r"\babend[s]?\b",query, re.IGNORECASE)):
            self.remove_time_attributes_from_query(r"\babend[s]?\b")
            return current_day.replace(hour=18, minute=0)
        return None


time_detector = TimeDetector()