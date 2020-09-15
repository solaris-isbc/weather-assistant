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
    with open('question_model.pkl', 'rb') as fid:
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
    if bool(re.search("sonnenschirm|sonnencreme", query, re.IGNORECASE)):
        return "SUN"
    if bool(re.search("regenschirm", query, re.IGNORECASE)):
        return "RAIN"
    if bool(re.search("mantel", query, re.IGNORECASE)):
        return "COLD"
    if probability_of_predicted_label <= 0.2:
        return None
    if probability_of_predicted_label < 0.5 and id.query_has_relevant_tokens(query) is False:
        return None
    return label_pred

def get_time_info(query, datetime_relative):
    extractor = dte.DateTimeExtractor(dtg.datetime_grammar, datetime_relative_to=datetime_relative, mode="evaluation")
    extractor.parse(query)
    r = extractor.get_evaluation_result()
    return r

with open('evaluation.json', encoding='utf-8') as json_file:
    data = json.load(json_file)

labeled_queries = data["queries"]

# Statistics
amount_of_labeled_queries = len(labeled_queries)
data_with_valid_questions = 0
correct_question_type = 0
correct_city = 0
correct_time_type = 0
correct_time = 0
main_score = 0

for labeled_query in labeled_queries:
    print("-----------------------------------------------------------------------------")
    query_text = labeled_query["text"]
    found_question_type = get_question_type(query_text)
    found_city = cd.find_location_in_query(query_text)
    if labeled_query["question_type"] != "None":
        #The indication of the time/place is only evaluated if a valid question has been identified and a valid question is actually present.
        # This has to do with the fact that the Assistant will recognize beforehand that the question is not valid.
        # The Assistant will then also not bother to find a city/time in the query.
        data_with_valid_questions += 1
        found_time = td.get_formatted_time(query_text)
        found_time_type = found_time[0]
        found_time = found_time[1]
        found_when_question = bool(re.search("wann|zeitpunkt", query_text, re.IGNORECASE))
        # a question is also answered correctly if it is recognized that the time inquired is too far in the future or
        # lies in the past. The question is also answered correctly if it is recognized that more than one city was specified in the query.
        # This is checked by the following boolean variable.
        timeOutsideThePossibleSpectrumOrMoreThanOneCityWasFound = False
        if found_city == labeled_query["city"]:
            correct_city += 1
            found_city_bool = True
        elif labeled_query["city"] == "False" and cd.more_than_one_city():
            correct_city += 1
            found_city_bool = True
            timeOutsideThePossibleSpectrumOrMoreThanOneCityWasFound = True
        else:
            if labeled_query["city"] == "None" and found_city is None:
                correct_city += 1
                found_city_bool = True
            else:
                found_city_bool = False
        if found_question_type == labeled_query["question_type"] and found_when_question == labeled_query["when_question"]:
            found_question_type_bool = True
            correct_question_type += 1
        else:
            found_question_type_bool = False
        datetime_relative_to = datetime.datetime.strptime(labeled_query["timeinfo"], "%Y.%m.%d %H:%M")
        time_result = get_time_info(query_text, datetime_relative_to)

        found_time_type_bool = False
        try:
            time_bool = False
            if time_result["type"] == labeled_query["time"]["time_type"]:
                found_time_type_bool = True
            if time_result["type"] == "time_point" and labeled_query["time"]["time_type"] == "time_point":
                correct_time_type += 1

                extracted_date = time_result["extracted_date_datetime"]
                extracted_time = time_result["extracted_time_datetime"]

                ground_truth = datetime.datetime.strptime(labeled_query["time"]["time_objects"]["start"], "%Y.%m.%d %H:%M")
                ground_truth_date = ground_truth.date()
                ground_truth_time = ground_truth.time()

                if extracted_date == ground_truth_date and extracted_time == ground_truth_time:
                    correct_time += 1
                    time_bool = True
                else:
                    time_bool = False
                date_string = time_result["extracted_date"] + " " + time_result["extracted_time"]
                extracted_time = datetime.datetime.strptime(date_string, "%Y.%m.%d %H:%M")

            if time_result["type"] == "day" and labeled_query["time"]["time_type"] == "day":
                correct_time_type += 1
                extracted_date = time_result["extracted_date_datetime"]
                ground_truth_date = datetime.datetime.strptime(labeled_query["time"]["time_objects"]["start"],"%Y.%m.%d %H:%M").date()
                if extracted_date == ground_truth_date:
                    correct_time += 1
                    time_bool = True
                else:
                    time_bool = False

            if time_result["type"] == "range" and labeled_query["time"]["time_type"] == "range":
                correct_time_type += 1
                range_start = found_time[0]
                range_end = found_time[1]
                extracted_date_start = time_result["extracted_range_duration_start_datetime"].date()
                extracted_date_end = time_result["extracted_range_duration_end_datetime"].date()
                ground_truth_start = datetime.datetime.strptime(labeled_query["time"]["time_objects"]["start"],
                                                                "%Y.%m.%d %H:%M")
                ground_truth_start_date = ground_truth_start.date()
                ground_truth_end = datetime.datetime.strptime(labeled_query["time"]["time_objects"]["end"], "%Y.%m.%d %H:%M")
                ground_truth_end_date = ground_truth_end.date()
                if ground_truth_start_date == extracted_date_start and ground_truth_end_date == extracted_date_end:
                    correct_time += 1
                    time_bool = True
                else:
                    time_bool = False
            if time_result["type"] == "day" and td.check_if_day_is_one_of_the_next_15(time_result["extracted_date_datetime"]) == False and labeled_query["time"]["time_type"] == "False":
                correct_time += 1
                found_time_type_bool = True
                time_bool = True
                timeOutsideThePossibleSpectrumOrMoreThanOneCityWasFound = True

            if time_result["type"] == "time_point":
                date_string = time_result["extracted_date"] + " " + time_result["extracted_time"]
                extracted_time = datetime.datetime.strptime(date_string, "%Y.%m.%d %H:%M")
                if time_result["type"] == "time_point" and td.check_if_time_point_can_be_looked_up(extracted_time) == False and labeled_query["time"]["time_type"] == "False":
                    correct_time += 1
                    found_time_type_bool = True
                    time_bool = True
                    timeOutsideThePossibleSpectrumOrMoreThanOneCityWasFound = True

        except BaseException as e:
            #print(str(e))
            time_bool = False
        if found_question_type_bool is True and ((found_city_bool is True and found_question_type_bool is True and time_bool is True) or (timeOutsideThePossibleSpectrumOrMoreThanOneCityWasFound)):
            main_score += 1
            correct_interpretation_of_query = True
        else:
            correct_interpretation_of_query = False


        print("| Query: ", query_text, "| question type: ", str(found_question_type_bool), "| city: ",str(found_city_bool), "| time type: ", str(found_time_type_bool), "| time: ", str(time_bool),"| system will give a suitable answer: ", str(correct_interpretation_of_query), "|")
    else:
        if found_question_type is None and labeled_query["question_type"] == "None":
            print("| Query: ", query_text, "|", "Korrekterweise wurde kein Fragetyp gefunden.")
            main_score += 1
            correct_question_type += 1
        if found_question_type != None and labeled_query["question_type"] == "None":
            print("| Query: ", query_text, "|","Es wurde ein Fragetyp gefunden, obwohl die Query sinnlos ist.")

print("#---------------------------------------------------------------------------#")
print("| Correct Question Types: ", correct_question_type / amount_of_labeled_queries)
print("| Correct City: ", correct_city / data_with_valid_questions)
print("| Correct Time Type: ", correct_time_type / data_with_valid_questions)
print("| Correct Time: ", correct_time / data_with_valid_questions)
print("#---------------------------------------------------------------------------#")
print("| General Accuracy: ", main_score / amount_of_labeled_queries)

