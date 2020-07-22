import json
import os
from time_detector import time_detector as td
from city_detector import city_detector as cd
from irrelevance_detection import irrelevance_detector as id
import datetime
from includes import DateTimeGrammar as dtg, DateTimeExtractor as dte
import spacy

output_dir = os.getcwd()+"/question_model"
nlp_categorizer = spacy.load(output_dir)

def get_question_type(query):
    query_doc = nlp_categorizer(query)
    docs = query_doc.cats
    categorized_label = max(docs, key=docs.get)
    if docs[categorized_label] <= 0.99999 and id.query_has_relevant_tokens(query) is False:
        return None
    else:
        return categorized_label

def get_time_info(query, datetime_relative):
    extractor = dte.DateTimeExtractor(dtg.datetime_grammar, datetime_relative_to=datetime_relative, mode="evaluation")
    extractor.parse(query)
    r = extractor.get_evaluation_result()
    return r

with open('evaluation.json', encoding='utf-8') as json_file:
    data = json.load(json_file)

data = data["queries"]
# Statistics
data_size = len(data)
data_with_valid_questions = 0
correct_question_type = 0
correct_city = 0
correct_time_type = 0
correct_time = 0
main_score = 0


for query in data:
    print("-----------------------------------------------------------------------------")
    query_text = query["text"]
    found_question_type = get_question_type(query_text)
#    print(found_question_type, query["question_type"])
    if query["question_type"] != "None" or found_question_type!=None:
        data_with_valid_questions += 1
        found_city = cd.find_location_in_query(query_text)
        found_time = td.get_formatted_time(query_text)
        found_time_type = found_time[0]
        found_time = found_time[1]
        if found_city == query["city"]:
            correct_city += 1
            found_city_bool = True
        else:
            if query["city"] == "None" and found_city is None:
                correct_city += 1
                found_city_bool = True
            else:
                found_city_bool = False

        if found_question_type == query["question_type"]:
            found_question_type_bool = True
            correct_question_type += 1
        else:
            found_question_type_bool = False

        datetime_relative_to = datetime.datetime.strptime(query["timeinfo"], "%Y.%m.%d %H:%M")

        time_result = get_time_info(query_text, datetime_relative_to)
        found_time_type_bool = False

        try:
            if time_result["type"] == query["time"]["time_type"]:
                found_time_type_bool = True


            if time_result["type"] == "time_point" and query["time"]["time_type"] == "time_point":
                correct_time_type += 1

                extracted_date = time_result["extracted_date_datetime"].date()
                extracted_time = time_result["extracted_time_datetime"]

                ground_truth = datetime.datetime.strptime(query["time"]["time_objects"]["start"], "%Y.%m.%d %H:%M")
                ground_truth_date = ground_truth.date()
                ground_truth_time = ground_truth.time()


#                print(ground_truth_date, "-----", extracted_date)
#                print(ground_truth_time, "-----", extracted_time)

                if extracted_date == ground_truth_date and extracted_time == ground_truth_time:
                    correct_time += 1
                    time_bool = True
                else:
                    time_bool = False

            if time_result["type"] == "day" and query["time"]["time_type"] == "day":
                correct_time_type += 1

                extracted_date = time_result["extracted_date_datetime"].date()

                ground_truth_date = datetime.datetime.strptime(query["time"]["time_objects"]["start"], "%Y.%m.%d %H:%M").date()

#                print(ground_truth_date, "-----", extracted_date)


                if extracted_date == ground_truth_date:
                    correct_time += 1
                    time_bool = True
                else:
                    time_bool = False

            if time_result["type"] == "range" and query["time"]["time_type"] == "range":
                correct_time_type += 1
                range_start = found_time[0]
                range_end = found_time[1]

                extracted_date_start = time_result["extracted_range_duration_start_datetime"].date()
                extracted_date_end = time_result["extracted_range_duration_end_datetime"].date()

                ground_truth_start = datetime.datetime.strptime(query["time"]["time_objects"]["start"], "%Y.%m.%d %H:%M")
                ground_truth_start_date = ground_truth_start.date()
                ground_truth_end = datetime.datetime.strptime(query["time"]["time_objects"]["end"], "%Y.%m.%d %H:%M")
                ground_truth_end_date = ground_truth_end.date()

#                print(ground_truth_start, "-----", extracted_date_start)
#                print(ground_truth_end, "-----", extracted_date_end)



                if ground_truth_start_date == extracted_date_start and ground_truth_end_date == extracted_date_end:
                    correct_time += 1
                    time_bool = True
                else:
                    time_bool = False
        except:
            time_bool = False

        if found_question_type_bool is True and found_city_bool is True and found_question_type_bool is True and time_bool is True:
            main_score += 1
            correct_interpretation_of_query = True
        else:
            correct_interpretation_of_query = False

        print("| Query: ", query_text, "| question type: ",
              str(found_question_type_bool),
              "| city: ", str(found_city_bool),
              "| time type: ", str(found_time_type_bool),
              "| time: ", str(time_bool), "|",
              "| correct interpretation of query: ", str(correct_interpretation_of_query), "|")
    else:
        if found_question_type is None and query["question_type"] == "None":
            print("| Query: ", query_text, "|","Korrekterweise wurde kein Fragetyp gefunden.")
            main_score += 1
            correct_question_type += 1
        if found_question_type is None and query["question_type"] != "None":
            print("| Query: ", query_text, "|","Es wurde ein Fragetyp gefunden, obwohl die Query sinnlos ist.")
        if found_question_type is None and query["question_type"] != "None":
            print("| Query: ", query_text, "|","Es wurde kein Fragetyp gefunden, obwohl die Query eine valide Frage ist.")

print("#---------------------------------------------------------------------------#")
print("| Correct Question Types: ",correct_question_type/data_size)
print("| Correct City: ",correct_city/data_with_valid_questions)
print("| Correct Time Type: ",correct_time_type/data_with_valid_questions)
print("| Correct Time: ",correct_time/data_with_valid_questions)
print("#---------------------------------------------------------------------------#")
print("| Main Score: ",main_score/data_size)
