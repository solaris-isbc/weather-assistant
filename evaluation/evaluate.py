import json
import re

from time_detector import time_detector as td
from city_detector import city_detector as cd
from irrelevance_detection import irrelevance_detector as id
import datetime
from includes import DateTimeGrammar as dtg, DateTimeExtractor as dte
import pickle
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer


def clean_query(text):
    stopword_list = set(stopwords.words('german'))
    stemmer = SnowballStemmer("german")
    text = text.lower()  # lowercase the query
    text = ' '.join(word for word in text.split() if word not in stopword_list)  # delete stopwors from text
    text = ' '.join(stemmer.stem(word) for word in text.split())
    return text

def get_question_type(query):
    cleaned_query = clean_query(query)
    with open('../question_model.pkl', 'rb') as fid:
        question_model = pickle.load(fid)
    label_pred = question_model.predict([cleaned_query])
    probabilities = question_model.predict_proba([cleaned_query])[0]
    probability_of_predicted_label = max(probabilities)
    if bool(re.search("hpa", query, re.IGNORECASE)):
        return "AIR_PRESSURE"
    # If the classificator predicted warm or cold but there's a temperature specified in the query
    # we will automatically classify the query as "TEMPERATURE". The classifier is very likely to classify a query
    # like "when will it be 20 degrees warm?" as "WARM" but the user would like to know, however, when there will be 20°C again. Not, when it becomes warm again.
    if (label_pred == "WARM" or label_pred == "COLD") and bool(re.search("[0-9]+ *(Grad|°)", query, re.IGNORECASE)):
        return "TEMPERATURE"
    if probability_of_predicted_label <= 0.2:
        return None
    if probability_of_predicted_label < 0.5 and id.query_has_relevant_tokens(query) is False:
        return None
    return label_pred

def get_time_info(query, datetime_relative):
    extractor = dte.DateTimeExtractor(dtg.datetime_grammar, datetime_relative_to=datetime_relative)
    extractor.parse(query)
    result = extractor.get_evaluation_result()
    return result

with open('evaluation.json', encoding='utf-8') as json_file:
    labeled_queries = json.load(json_file)

labeled_queries = labeled_queries["queries"]

# Statistic variables
amount_of_labeled_queries = len(labeled_queries)
data_with_valid_questions = 0
correct_question_type = 0
correct_city_detection = 0
correct_time = 0
general_accuracy_score = 0
true_positives = 0
false_positives = 0
amount_of_actually_valid_questions = 0

for labeled_query in labeled_queries:
    print("-----------------------------------------------------------------------------")
    query_text = labeled_query["text"]
    print("Query: ",query_text)
    # question type recognized by the system
    found_question_type = get_question_type(query_text)
    found_city = cd.find_location_in_query(query_text)
    if found_city != None:
        found_city = found_city.title()

    if labeled_query["question_type"] != "None":
        # The indication of the time/place is only evaluated if the query actually can be assigned to a question type.
        # This has to do with the fact that the Assistant will recognize beforehand that the question is not valid.
        # The Assistant will then also not bother to find a city/time in the query.
        data_with_valid_questions += 1
        found_time = td.get_formatted_time(query_text)
        found_time_type = found_time[0] # time_point, day or range
        found_time = found_time[1]
        found_when_question = bool(re.search("wann|zeitpunkt", query_text, re.IGNORECASE))
        # a question is also answered correctly if it is recognized that the time inquired is too far in the future or
        # lies in the past. The question is also answered correctly if it is recognized that more than one city was specified in the query.
        # This is checked by the following boolean variable.
        time_is_outside_the_possible_spectrum_or_more_than_one_city_was_Found = False
        if labeled_query["time"]["time_type"] != "False" and labeled_query["city"] != "False":
            amount_of_actually_valid_questions +=1 # we need to count the amout of actually_valid_questions for the calculation of the recall.
        if found_city == labeled_query["city"] and cd.more_than_one_city() == False:
            print("✓ Die Stadt '"+found_city+"' wurde identifiziert.")
            correct_city_detection += 1
            found_city_bool = True
        elif labeled_query["city"] == "False" and cd.more_than_one_city():
            print("✓", "Es wurde identifiziert, dass der Nutzer fälschlicherweise mehr als eine Stadt spezifiziert hat. Daher wird das System eine angemessene Antwort geben.")
            correct_city_detection += 1
            found_city_bool = True
            time_is_outside_the_possible_spectrum_or_more_than_one_city_was_Found = True
        elif labeled_query["city"] == "None" and found_city is None:
             print("✓", "Korrekterweise wurde keine Stadt in der Query identifiziert.")
             correct_city_detection += 1
             found_city_bool = True
        elif labeled_query["city"] != "False" and labeled_query["city"] != "None" and cd.more_than_one_city():
             print("×", "Fälschlicherweise wurde mehr als ein Stadtname in der Query identifiziert.")
             found_city_bool = False
        else:
             if found_city == None and labeled_query['city'] != "False" and labeled_query['city'] != "None":
               print("×", "Die Stadt '"+labeled_query["city"]+"' wurde nicht gefunden.")
             elif found_city != None and labeled_query['city'] != "None" and labeled_query['city'] != "False" and cd.more_than_one_city() == False and found_city != labeled_query['city']:
                 print("×","Bei der Phrase '" + found_city + "' handelt es sich nicht um einen Stadtnamen, den das System hätte erkennen sollen.")
             elif found_city != None and labeled_query['city'] == "None":
               print("×", "Die Phrase '"+found_city+"' wurde gefunden, obwohl es sich dabei nicht um eine Stadt handelt.")
             found_city_bool = False
        if found_question_type == labeled_query["question_type"] and found_when_question == labeled_query["when_question"]:
            print("✓", "Es wurde die richtige Fragestellung erkannt: "+found_question_type[0]+" / when: "+str(found_when_question) + ".")
            found_question_type_bool = True
            correct_question_type += 1
        else:
            print("×", "Es wurde nicht erkannt, dass der Nutzer sich für die folgende Fragestellung interessiert:",labeled_query["question_type"]+" / when: "+str(labeled_query["when_question"]) + ".")
            found_question_type_bool = False
        datetime_relative_to = datetime.datetime.strptime(labeled_query["timeinfo"], "%Y.%m.%d %H:%M")
        time_result = get_time_info(query_text, datetime_relative_to)

        found_time_type_bool = False
        try:
            time_bool = False
            if time_result["type"] == labeled_query["time"]["time_type"]:
                found_time_type_bool = True
            if time_result["type"] == "time_point" and labeled_query["time"]["time_type"] == "time_point":
                extracted_date = time_result["extracted_date_datetime"]
                extracted_time = time_result["extracted_time_datetime"]
                ground_truth = datetime.datetime.strptime(labeled_query["time"]["time_objects"]["start"], "%Y.%m.%d %H:%M")
                ground_truth_date = ground_truth.date()
                ground_truth_time = ground_truth.time()
                if extracted_date == ground_truth_date and extracted_time == ground_truth_time:
                    print("✓", "Korrekterweise wurde der richtige Zeittyp (time_point) identifiziert:",extracted_date,extracted_time)
                    correct_time += 1
                    time_bool = True
                else:
                    print("×", "Es wurde zwar erkannt, dass es sich um einen time_point handelt, richtig wäre jedoch:",ground_truth,"statt",extracted_date,extracted_time)
                    time_bool = False
                date_string = time_result["extracted_date"] + " " + time_result["extracted_time"]
                extracted_time = datetime.datetime.strptime(date_string, "%Y.%m.%d %H:%M")

            if time_result["type"] == "day" and labeled_query["time"]["time_type"] == "day":
                extracted_date = time_result["extracted_date_datetime"]
                ground_truth_date = datetime.datetime.strptime(labeled_query["time"]["time_objects"]["start"],"%Y.%m.%d %H:%M").date()
                if extracted_date == ground_truth_date:
                    print("✓", "Korrekterweise wurde der richtige Zeittyp (day) identifiziert:", extracted_date)
                    correct_time += 1
                    time_bool = True
                else:
                    print("×", "Es wurde zwar erkannt, dass es sich um einen Tag (day) handelt, richtig wäre jedoch:",ground_truth_date, "statt", extracted_date)
                    time_bool = False

            if time_result["type"] == "range" and labeled_query["time"]["time_type"] == "range":
                range_start = found_time[0]
                range_end = found_time[1]
                extracted_date_start = time_result["extracted_range_duration_start_datetime"].date()
                extracted_date_end = time_result["extracted_range_duration_end_datetime"].date()
                ground_truth_start = datetime.datetime.strptime(labeled_query["time"]["time_objects"]["start"],"%Y.%m.%d %H:%M")
                ground_truth_start_date = ground_truth_start.date()
                ground_truth_end = datetime.datetime.strptime(labeled_query["time"]["time_objects"]["end"], "%Y.%m.%d %H:%M")
                ground_truth_end_date = ground_truth_end.date()
                if ground_truth_start_date == extracted_date_start and ground_truth_end_date == extracted_date_end:
                    print("✓", "Korrekterweise wurde der richtige Zeittyp (range) identifiziert:", extracted_date_start,"bis", extracted_date_end)
                    correct_time += 1
                    time_bool = True
                else:
                    print("×", "Es wurde zwar erkannt, dass es sich um eine Range handelt, richtig wäre jedoch:",ground_truth_start_date, "bis", ground_truth_end_date, "statt",  extracted_date_start, "bis", extracted_date_end)
                    time_bool = False
            if time_result["type"] == "day":
                if td.check_if_day_is_one_of_the_next_14(time_result["extracted_date_datetime"], labeled_query["timeinfo"]) == False and labeled_query["time"]["time_type"] == "False":
                  print("✓", "Korrekterweise wurde erkannt, dass die Zeit nicht im möglichen Zeitspektrum liegt (Tag ist nicht einer der nächsten 14 Tagen). Daher wird das System eine angemssene Antwort geben.")
                  correct_time += 1
                  found_time_type_bool = True
                  time_bool = True
                  time_is_outside_the_possible_spectrum_or_more_than_one_city_was_Found = True

            if time_result["type"] == "time_point":
                date_string = time_result["extracted_date"] + " " + time_result["extracted_time"]
                extracted_time = datetime.datetime.strptime(date_string, "%Y.%m.%d %H:%M")
                if td.check_if_time_point_can_be_looked_up(extracted_time, labeled_query["timeinfo"]) == False and labeled_query["time"]["time_type"] == "False":
                    print("✓", "Korrekterweise wurde erkannt, dass die Zeit nicht im möglichen Zeitspektrum liegt (liegt nicht in den nächsten 48 Stunden).")
                    correct_time += 1
                    found_time_type_bool = True
                    time_bool = True
                    time_is_outside_the_possible_spectrum_or_more_than_one_city_was_Found = True
            if (labeled_query["time"]["time_type"] == "False" or labeled_query["city"] == "False") and time_is_outside_the_possible_spectrum_or_more_than_one_city_was_Found == False:
                false_positives +=1
                if labeled_query["time"]["time_type"] == "False":
                    print("×","Es wurde nicht identifiziert, dass die Zeitangabe außerhalb des möglichen Spektrums liegt.")
                else:
                    print("×","Es wurde nicht identifiziert, dass mehr als ein Stadtname spezifiziert wurde.")
            if labeled_query["time"]["time_type"]!="False" and time_bool == False:
                print("×", "Die Zeitangabe wurde nicht richtig identifiziert.")

        except BaseException as e:
            time_bool = False
        if (found_question_type_bool is True and found_city_bool is True and found_question_type_bool is True and time_bool is True) or (time_is_outside_the_possible_spectrum_or_more_than_one_city_was_Found):
            print("✓","\033[1;32;48mZu dieser Frage wird das System eine angemessene Antwort generieren.",'\033[0m')
            general_accuracy_score += 1
            correct_interpretation_of_query = True
            if time_is_outside_the_possible_spectrum_or_more_than_one_city_was_Found == False:
                true_positives += 1
        else:
            print("×", "\033[91mZu dieser Frage wird das System keine angemessene Antwort generieren. ",'\033[0m')

            correct_interpretation_of_query = False
        print("| question type identification:", str(found_question_type_bool), "| city identification:",str(found_city_bool),"| time identification:", str(time_bool),"|")
    else:
        if found_question_type is None and labeled_query["question_type"] == "None":
            print("✓", "\033[1;32;48mZu dieser Frage wird das System eine angemessene Antwort generieren. Korrekterweise wurde keine Fragestellung erkannt (z.B. aufgrund von Spam).",'\033[0m')
            general_accuracy_score += 1
            correct_question_type += 1
            print("| question type identification: True | city identification: no evaluation | time identification: no evaluation |")
        if found_question_type != None and labeled_query["question_type"] == "None":
            print("×", "\033[91mEs wurde eine Fragestellung identifiziert, obwohl es sich entweder um eine Frage handelt, die Wetterdaten abfrägt, die nicht bereitgestellt werden können oder die Query eigentlich sinnlos ist (z.B. Spam)",'\033[0m')
            false_positives +=1
            print("| question type identification: False | city identification: no evaluation | time identification: no evaluation |")

print("#---------------------------------------------------------------------------#")
print("| Accuracy Question Type: ", round(correct_question_type / amount_of_labeled_queries,3))
print("| Accuracy City: ", round(correct_city_detection / data_with_valid_questions,3))
print("| Accuracy Time: ", round(correct_time / data_with_valid_questions,3))
print("#---------------------------------------------------------------------------#")
precision = true_positives / (true_positives + false_positives)
recall = true_positives / amount_of_actually_valid_questions
false_negatives = amount_of_actually_valid_questions - true_positives
true_negatives = amount_of_labeled_queries-true_positives-false_positives-false_negatives
print("| True Negatives:",true_negatives,"True Positives:", true_positives," False Negatives:",false_negatives," False Positives:", false_positives)
print("| General Accuracy: ", round(general_accuracy_score / amount_of_labeled_queries,3))
print("| General Precision: ", round(precision,3))
print("| General Recall: ", round(recall,3))
print("| General F1-Measure: ", round((2*precision*recall)/(precision+recall),3))
print("#---------------------------------------------------------------------------#")