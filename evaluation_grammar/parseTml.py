import datetime, csv, re

header = True
out = []
counter = 0
p = re.compile("(<TIMEX3.*>)")
with open("evaluation_grammar/heideltime_raw.csv", "r", encoding='UTF-8') as f:
    reader = csv.reader(f, delimiter=";")
    for line in reader:
        if header:
            #out.append(["query", "extracted_date", "extracted_time", "extracted_range_start", "extracted_range_end", "date_relative_to", "time_relative_to", "grammar_predicted_date", "grammar_predicted_time", "grammar_predicted_range_start", "grammar_predicted_range_end", "grammar_match_date", "grammar_match_time", "grammar_match_range_start", "grammar_match_range_end"])
            header = False
            continue
        counter = counter + 1
        line = line[0]
        res = p.search(line)
        print(res)

        #break