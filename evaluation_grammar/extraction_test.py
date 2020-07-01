import csv
from includes import DateTimeGrammar as dtg, DateTimeExtractor as dte
import time
from lark import Lark, Tree
import datetime
header = True
out = []
counter = 0

"""sentence = "Stürmt es in 2 Stunden?"
datetime_relative = datetime.datetime.strptime("2020.06.27" + " " + "00:00", "%Y.%m.%d %H:%M")
extractor = dte.DateTimeExtractor(dtg.datetime_grammar, datetime_relative_to=datetime_relative, mode="evaluation", debug=True)
extractor.parse(sentence)
print(extractor.tree.pretty())
print(extractor.date)
print(extractor.time)
print(extractor.date_range)
print(extractor.get_evaluation_result())
exit()
"""

with open("evaluation_grammar/evaluation_grammatik.csv", "r", encoding='UTF-8') as f:
    reader = csv.reader(f, delimiter=";")
    for line in reader:
        if header:
            out.append(["query", "extracted_date", "extracted_time", "extracted_range_start", "extracted_range_end", "date_relative_to", "time_relative_to", "grammar_predicted_date", "grammar_predicted_time", "grammar_predicted_range_start", "grammar_predicted_range_end", "grammar_match_date", "grammar_match_time", "grammar_match_range_start", "grammar_match_range_end"])
            header = False
            continue
        counter = counter + 1
        #date and time relative in columns 5/6
        datetime_relative =  datetime.datetime.strptime(line[5] + " " + line[6], "%Y.%m.%d %H:%M")
        #print("[" + str( time.process_time()) + "] ", line[0])
        extractor = dte.DateTimeExtractor(dtg.datetime_grammar, datetime_relative_to=datetime_relative, mode="evaluation")
        extractor.parse(line[0])
        r = extractor.get_evaluation_result()
        del extractor
        outl = line
        outl.append(r["extracted_date"])
        outl.append(r["extracted_time"])
        outl.append(r["extracted_duration_start"])
        outl.append(r["extracted_duration_end"])
        #evaluation
        if outl[1] == outl[7]:
            outl.append("1")
        else:
            outl.append("0")
        if outl[2] == outl[8]:
            outl.append("1")
        else:
            outl.append("0")
        if outl[3] == outl[9]:
            outl.append("1")
        else:
            outl.append("0")
        if outl[4] == outl[10]:
            outl.append("1")
        else:
            outl.append("0")

        print("[" + str( time.process_time()) + "] ", outl)
        out.append(outl)
        #if counter == 10:
        #    break

with open("evaluation_grammar/out.csv", "w", encoding='UTF-8', newline='') as csv_file:
    writer = csv.writer(csv_file, delimiter=',')
    for line in out:
        writer.writerow(line)