import json
import os
from time_detector import time_detector as td
from city_detector import city_detector as cd
from irrelevance_detection import irrelevance_detector as id
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

with open('evaluation.json') as json_file:
    data = json.load(json_file)


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

        if found_time_type == query["time"]["time_type"]:
            found_time_type_bool = True
        else:
            found_time_type_bool = False

        if found_time_type == "time_point" and query["time"]["time_type"] == "time_point":
            correct_time_type += 1
            if found_time.hour == query["time"]["time_objects"]["time_object"]["hour"] and found_time.day == \
                    query["time"]["time_objects"]["time_object"]["day"] and found_time.month == \
                    query["time"]["time_objects"]["time_object"]["month"] and found_time.year == \
                    query["time"]["time_objects"]["time_object"]["year"]:
                correct_time += 1
                time_bool = True
            else:
                time_bool = False

        if found_time_type == "day" and query["time"]["time_type"] == "day":
            correct_time_type += 1
            if found_time.day == query["time"]["time_objects"]["time_object"]["day"] and found_time.month == \
                    query["time"]["time_objects"]["time_object"]["month"] and found_time.year == \
                    query["time"]["time_objects"]["time_object"]["year"]:
                correct_time += 1
                time_bool = True
            else:
                time_bool = False

        if found_time_type == "range" and query["time"]["time_type"] == "range":
            correct_time_type += 1
            range_start = found_time[0]
            range_end = found_time[1]
            if range_start.day == query["time"]["time_objects"][0]["day"] and range_start.month == \
                    query["time"]["time_objects"][0]["month"] and range_start.year == query["time"]["time_objects"][0][
                "year"] and range_end.day == query["time"]["time_objects"][1]["day"] and range_end.month == \
                    query["time"]["time_objects"][1]["month"] and range_end.year == query["time"]["time_objects"][1][
                "year"]:
                correct_time += 1
                time_bool = True
            else:
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