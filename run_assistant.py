from time_detector import time_detector as td
from city_detector import city_detector as cd
from irrelevance_detection import irrelevance_detector as id
from weather_api_handler import weather_api_handler as weather_api_handler
from nltk.corpus import stopwords
import geocoder
from geopy.geocoders import Nominatim
import sys
import pickle


# IMPORTANT:

# pip install geocoder
# pip install geopy
# pip install pyweatherbit
# pip install xmltodict
# pip install lark-parser
# pip install translate
# pip install nltk
# pip install pandas
# pip install scikit-learn

# Run this command in the project folder to install all packages needed:
# pip install -r requirements.txt

def clean_query(text):
    STOPWORDS = set(stopwords.words('german'))
    text = text.lower() #lowercase the query
    text = ' '.join(word for word in text.split() if word not in STOPWORDS)  # delete stopwors from text
    return text

def get_question_type(query):
    query = clean_query(query)
    with open('question_model.pkl', 'rb') as fid:
        question_model = pickle.load(fid)
    label_pred = question_model.predict([query])
    probabilities = question_model.predict_proba([query])[0]
    for prob in probabilities:
        if prob <= 0.2 and id.query_has_relevant_tokens(query) is False:
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
    if question_type != None:
        # The only reason for an error is the absence of weather data for the requested location.
        try:
            weather_api_handler.interpret_data_and_create_answer(question_type, city, selected_time, selected_time_type)
        except Exception as e:
            print("<!--")
            print(str(e))
            print("-->")
            print("Leider haben wir für diesen Ort keine Wetterdaten verfügbar. Fragen Sie doch einfach nochmal, indem Sie die nächstgelegene größere Stadt!")
    else:
        print("Diese Frage kann ich dir nicht beantworten, tut mir leid.")

def query_processing(query):
    city = cd.find_location_in_query(query)
    if city is None:
       city = get_current_location()

    if cd.more_than_one_city(query) is True:
        print("Sie haben mehr als eine Stadt angegeben. Bitte fordern Sie Wetterinformationen nur für eine Stadt an!")
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
                print("Hoppla. Wir können Ihnen nur Wetterinformationen für die nächsten 15 Tage geben.")
            else:
                find_question_type(query, city, selected_time_type, [selected_time])

def main():
    if len(sys.argv) > 1:
        query = sys.argv[1]
        query_processing(query)

if __name__ == "__main__":
    main()
