import re

from time_detector import time_detector as td
from city_detector import city_detector as cd
from irrelevance_detection import irrelevance_detector as id
from weather_api_handler import weather_api_handler as weather_api_handler
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import geocoder
from geopy.geocoders import Nominatim
import colorama
from colorama import Fore, Style
import sys
import pickle

### Run this command in the project folder to install all packages needed:
# pip install -r requirements.txt

### Alternatively:
# pip install geocoder
# pip install geopy
# pip install pyweatherbit
# pip install xmltodict
# pip install lark-parser
# pip install translate
# pip install nltk
# pip install pandas
# pip install scikit-learn
# pip install colorama

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
    if probability_of_predicted_label <= 0.2:
        return None
    if probability_of_predicted_label < 0.5 and id.query_has_relevant_tokens(query) is False:
        return None
    return label_pred

def get_current_location():
    g = geocoder.ip('me')
    geolocator = Nominatim(user_agent="weather assistant")
    coord = str(g.latlng[0])+", "+str(g.latlng[1])
    location = geolocator.reverse(coord)
    return location.raw["address"]["city"]

def find_time_information_in_query(query):
    return td.get_formatted_time(query)

def find_question_type(query, city, selected_time_type, selected_time):
    question_type = get_question_type(query)
    next_appearance_mode = bool(re.search("wann", query, re.IGNORECASE))
    if question_type != None:
        # The only reason for an error is the absence of weather data for the requested location.
        try:
            weather_api_handler.interpret_data_and_create_answer(question_type, city, selected_time, selected_time_type, next_appearance_mode, query)
        except Exception as e:
            print("<!--")
            print(str(e))
            print("-->")
            print("Leider haben wir für diesen Ort keine Wetterdaten verfügbar. Fragen Sie doch einfach nochmal, indem Sie die nächstgelegene größere Stadt nennen!")
    else:
        print("Diese Frage kann ich dir nicht beantworten, tut mir leid.")

def query_processing(query):
    city = cd.find_location_in_query(query)
    if city is None:
       city = get_current_location()

    if cd.more_than_one_city() is True:
        print("Bitte geben Sie maximal einen Ort an. Bitte fordern Sie Wetterinformationen nur für eine Stadt an!")
    else:
        time_information = find_time_information_in_query(query)
        selected_time_type = time_information[0]
        selected_time = time_information[1]

        if selected_time_type == "range":
            range_start = time_information[1][0]
            range_end = time_information[1][1]
            find_question_type(query, city, selected_time_type, [range_start, range_end])
        if selected_time_type == "time_point":
            if td.check_if_time_point_can_be_looked_up(selected_time) is False:
                print("Es tut uns leid, aber manchmal haben wir nur Daten für die nächsten 48 Stunden. Fragen Sie einfach nach dem ganzen Tag, hier kann ich Ihnen etwas über die nächsten 15 Tage sagen!")
            else:
                find_question_type(query, city, selected_time_type, [selected_time])
        if selected_time_type == "day":
            if td.check_if_day_is_one_of_the_next_15(selected_time) is False:
                print("Hoppla. Wir können für Sie nur Wetterinformationen für die nächsten 15 Tage bereitstellen.")
            else:
                find_question_type(query, city, selected_time_type, [selected_time])

def display_assistant_information():
    print("--------------------------------------------------------------")
    print(f"{Fore.RED}Weather Assistant{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}weather-data by weatherbit.io{Style.RESET_ALL}")
    print("--------------------------------------------------------------")
    print("The system can answer the following questions: ")
    print("Weather, Rain, Snow, Sun, Air Pressure, Fog, Temperature,\nMinimum Temperature, Maximum Temperature, Average Temperature,"+
          " Warm Temperature,\nCold Temperature, Storm, Wind, Clouds, Wind Direction")
    print("--------------------------------------------------------------")

def start_assistant():
    while True:
        user_input = input(f"{Fore.BLUE}Please ask a question: {Style.RESET_ALL}")
        query_processing(user_input)

display_assistant_information()
start_assistant()
