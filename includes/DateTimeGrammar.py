##################################################################################
"""
TODOs:
- Make sure every matching rule is sorted by matching length, e.g. day: DAY_AFTER_TOMORROW | TOMORROW
  otherwise wrong matching might happen, e.g. übermorgen matches über(optional_s) morgen(TOMORROW)
    => is mostly correct
- written digits: drei -> 3, sechzehn -> 16 ->
    => fixed in DateTimeExtractor by regex replace for 2-9
- specially named days: Weihnachten, Ostermontag, Muttertag
"""
##################################################################################
datetime_grammar = u"""

    //starting point
    root: SOS (only_date | only_time | date_time | time_date) EOS

    //only cover cases with either one date, one time or one date and one time
    //only_date.2: optional_s? date_wrapper optional_s?
    //do this to make sure, the date takes precedence over any optional characters, that could be part of the date
    only_date.2:  date_wrapper |  optional_s date_wrapper | date_wrapper optional_s | optional_s date_wrapper optional_s
    //same reasoning as before
    //only_time.0: optional_s? time_wrapper optional_s?
    only_time.0: time_wrapper |  optional_s time_wrapper | time_wrapper optional_s | optional_s time_wrapper optional_s
    //date_time.1: optional_s? date_wrapper optional_s? time_wrapper optional_s?
    date_time.1: date_wrapper time_wrapper | date_wrapper time_wrapper optional_s | date_wrapper optional_s time_wrapper | date_wrapper optional_s time_wrapper optional_s | optional_s date_wrapper time_wrapper | optional_s date_wrapper time_wrapper optional_s | optional_s date_wrapper optional_s time_wrapper | optional_s date_wrapper optional_s time_wrapper optional_s
    //time_date.1: optional_s? time_wrapper optional_s? date_wrapper optional_s?
    time_date.1: time_wrapper date_wrapper | time_wrapper date_wrapper optional_s | time_wrapper optional_s date_wrapper | time_wrapper optional_s date_wrapper optional_s | optional_s time_wrapper date_wrapper | optional_s time_wrapper date_wrapper optional_s | optional_s time_wrapper optional_s date_wrapper | optional_s time_wrapper optional_s date_wrapper optional_s

    

    //wrappers for all possible time and date subtrees
    date_wrapper.2: date_formatted | date | date_relative
    time_wrapper.1: (time | time_relative) WS?
    
    //formatted date, e.g. 20.5.2020
    //digit date spoken
    //date_formatted.2: digit_date_day DATE_SEPARATOR (MONTH | MONTH_ABBR | DIGIT_MONTH | DIGIT_MONTH_SPOKEN) year?
    //digit_date_day.1: (DIGIT_LIMITED_DAY? DIGIT) | DIGIT_DAY_SPOKEN  
    date_formatted.2: digit_date_day DATE_SEPARATOR (MONTH | MONTH_ABBR | DIGIT_MONTH) year?
    digit_date_day.1: (DIGIT_LIMITED_DAY? DIGIT) 
    year: (DATE_SEPARATOR YEAR) | YEAR
    
    //relative date, e.g. in 5 tagen
    date_relative.1: IN (THE? NEXT)? RELATIVE_DAYS DAYS_CHAR
    
    
    //date with time of day, including weekend
    date.1:  week | (weekday time_of_day) | weekend | weekday |date_interval
    
    weekday.1: (NEXT day) | day | DAY_ABBR | (NEXT DAY_ABBR) | TODAY
    day.1: DAY_AFTER_TOMORROW | TOMORROW | DAYS

    time_of_day.1: (TIME_OF_DAYS S_OPT?) | ON NEXT? TOMORROW | TOMORROW S_OPT

    weekend.2: (ON? (NEXT|THIS))? WEEK_END

    week.2: ((THIS | NEXT | IN_ONE) WEEK (DAYS | DAY_ABBR)) | ((THIS | NEXT | IN_ONE) WEEK)
    
    date_interval.1: date_until | date_from
    //e.g. von mittwoch bis donnerstag
    date_until.1: (FROM? weekday)? UNTIL weekday (time_of_day)?
    //e.g. ab heute morgen
    date_from.1: STARTING_FROM weekday time_of_day?
    
    
    //relative time, e.g. in 10 Minuten
    time_relative.1: (IN time_relative_minutes WS? MINUTES_CHAR) | (IN time_relative_hours WS? HOURS_CHAR) | (IN_ONE HOURS_CHAR) | (IN_ONE MINUTES_CHAR) 
    time_relative_minutes.1: DIGIT? DIGIT? DIGIT
    time_relative_hours.1: DIGIT? DIGIT
    
    
    //time with optional time of day to specify or just general time of day
    time.2: ((time_of_day) time_specific) | (time_specific (time_of_day)) | time_specific | time_of_day

    time_specific.1: clock_time | qualified_times
    clock_time.1: ((AT|TOWARDS) hour) | (hour CLOCK) | hour_clock_minutes
    //14:20 or 12
    hour.1: def_hour | digit_num 
    def_hour.1: digit_num COLON full_digit_num
    digit_num.1: one_digit | two_digit | DIGIT
    one_digit.1: ONE DIGIT
    two_digit.1: TWO DIGIT_LIMITED
    full_digit_num.1: DIGIT_LIMITED_SIXTY DIGIT
    hour_clock_minutes.1: digit_num CLOCK full_digit_num
    
    //relative times/intervals
    qualified_times.1: (from_clock_till_clock | between_clock | qualified_clock)
    from_clock_till_clock.1:  FROM (clock_time) UNTIL clock_time
    between_clock.1:  (BETWEEN)? (clock_time) (TILL|AND) clock_time
    qualified_clock.1:  (TOWARDS|AT|UNTIL|STARTING_FROM|FROM) (CIRCA)? clock_time   
  
    //terminals
    //all surrounded with possible whitespaces
    //TODO maybe change some WS* into WS+
    DATE_SEPARATOR: ("-"|"."|WS) WS?
    MONTH:("januar" | "februar" | "märz" | "april" | "mai" | "juni" | "juli" | "august" | "september" | "oktober" | "november" | "dezember") WS+
    MONTH_ABBR: ("jan" | "feb" | "mar" | "apr" | "mai" | "jun" | "jul" | "aug" | "sept" | "okt" | "nov" | "dez") WS+
    DIGIT_MONTH: (("0".."1" "0".."9") | ("0".."9"))WS?
    YEAR: ((DIGIT DIGIT DIGIT DIGIT) | (DIGIT DIGIT))WS+
    DIGIT_LIMITED_DAY: ("0".."3")WS?
    //spoken numbers
    //DIGIT_DAY_SPOKEN: ("erste"("r"|"n")?)  |( "zweite"("r"|"n")?)  |( "dritte"("r"|"n")?)  |( "vierte"("r"|"n")?)  |( "fünfte"("r"|"n")?)  |( "sechste"("r"|"n")?)  |( "siebte"("r"|"n")?)  |( "achte"("r"|"n")?)  |( "neunte"("r"|"n")?)  |( "zehnte"("r"|"n")?)  |( "elfte"("r"|"n")?)  |( "zwölfte"("r"|"n")?)  |( "dreizehnte"("r"|"n")?)  |( "vierzehnte"("r"|"n")?)  |( "fünfzehnte"("r"|"n")?)  |( "sechzehnte"("r"|"n")?)  |( "siebzehnte"("r"|"n")?)  |( "achtzehnte"("r"|"n")?)  |( "neunzehnte"("r"|"n")?)  |( "zwanzigste"("r"|"n")?)  |( "einundzwanzigste"("r"|"n")?)  |( "zweiundzwanzigste"("r"|"n")?)  |( "dreiundzwanzigste"("r"|"n")?)  |( "vierundzwanzigste"("r"|"n")?)  |( "fünfundzwanzigste"("r"|"n")?)  |( "sechsundzwanzigste"("r"|"n")?)  |( "siebenundzwanzigste"("r"|"n")?)  |( "achtundzwanzigste"("r"|"n")?)  |( "neunundzwanzigste"("r"|"n")?)  |( "dreißigste"("r"|"n")?)  |( "einundreißigste"("r"|"n")?) WS+
    //DIGIT_MONTH_SPOKEN: ("erste"("r"|"n")?)  |( "zweite"("r"|"n")?)  |( "dritte"("r"|"n")?)  |( "vierte"("r"|"n")?)  |( "fünfte"("r"|"n")?)  |( "sechste"("r"|"n")?)  |( "siebte"("r"|"n")?)  |( "achte"("r"|"n")?)  |( "neunte"("r"|"n")?)  |( "zehnte"("r"|"n")?)  |( "elfte"("r"|"n")?)  |( "zwölfte"("r"|"n")?) WS+
    THE: ("den")WS+
    IN: ("in")WS+
    DAYS_CHAR: ("tagen")WS+
    RELATIVE_DAYS: ("2".."9" | "1"("0".."5"))WS+
    NEXT: ("nächster" | "nächsten" | "nächste" | "nächster" | "nächsten" | "nächste" | "nächstes" | "kommendes" | "kommenden" | "kommender" | "kommende" | "kommenden")WS+
    TOMORROW: ("morgen")WS+
    DAY_AFTER_TOMORROW: ("übermorgen")WS+
    DAYS: ("montag" | "dienstag" | "mittwoch" | "donnerstag" | "freitag" | "samstag" | "sonntag" | "heute")WS+
    DAY_ABBR: ("mo" | "di" | "mi" | "do" | "fr" | "sa" | "so")WS+
    TODAY: ("heute")WS+
    TIME_OF_DAYS: ("vormittag" | "nachmittag" | "mittag" | "abend" | "nacht" | ("in" "der")? "früh")WS+
    S_OPT: ("s")WS+
    ON: ("am" | "an")WS+
    WEEK_END: ("wochenende")WS+
    THIS: ("diese" | "dieses" | "dieser")WS+
    IN_ONE: ("in" WS+ ("einer"|"1")) WS+
    WEEK: ("woche")WS+
    MINUTES_CHAR: ("minute"("n")?)WS+
    HOURS_CHAR: ("stunde"("n")?)WS+
    CLOCK: (("uhr" | "h"))WS+
    ONE: ("1")WS?
    TWO: ("2")WS?
    DIGIT_LIMITED: ("0".."4")WS?
    DIGIT_LIMITED_SIXTY: ("0".."6")WS?
    FROM: ("von" | "vom")WS+
    UNTIL: ("bis")WS+
    BETWEEN: ("zwischen" | "zw.")WS+
    TILL: ("-")WS?
    AND: ("und")WS+
    TOWARDS: ("gegen")WS+
    AT: ("um")WS+
    STARTING_FROM: ("ab")WS+
    CIRCA: ("ca." | "ca")WS+

    //further definitions
    optional.0: (WS+ term WS?) | WS+ (term optional) WS?
    optional_s:(term WS?) | (term optional) WS?
    term.0: word
    word.0: char+
    char.0: LETTER | special_char
    seq.0: char char+ //at least 2 characters
    SOS: "<--start-->"
    EOS: "<--end-->"
    LETTER: UCASE_LETTER | LCASE_LETTER
    LCASE_LETTER: "a".."z" | "ä" | "ü" | "ö" | "ß"
    UCASE_LETTER: "A".."Z" | "Ä" | "Ü" | "Ö"
    special_char.0: SPECIAL_CHARS | COLON 
    SPECIAL_CHARS: "-" | "." | "," | "+" | "#" | "*" | "~" | "#" | "'" | "<" | "|" | ">" | ";" | "_" | "!" | "$" | "%" | "?" | "´" | "`" 
    COLON: ":"
    WS: /[ \\t\\f\\r\\n]/+
    DIGIT: "0".."9"
    
"""
