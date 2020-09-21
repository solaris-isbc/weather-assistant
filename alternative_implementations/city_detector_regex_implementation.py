import re
from translate import Translator
import json

class CityDetector():

    global found_cities

    def find_location_in_query(self, query):
        self.found_cities = []
        try:
            cities = self.find_cities_in_query(query)
            self.found_cities = cities
            return cities[0]
        except:
            return None

    # returns false if user talks about more than one city
    def more_than_one_city(self,query):
        if len(self.found_cities) > 1:
            return True
        return False

    def delete_city(self,cityx, found_cities):
        counter = 0
        for city in found_cities:
            if city == cityx:
                found_cities.pop(counter)
            counter = counter + 1
        return found_cities

    def found_wrong_matches(self,query,found_cities):
        matches = []+found_cities
        citys_that_occur_in_other_city_strings = [] # For example the String "York" can be found in "New York" and we want to find Strings like York
        for cityx in found_cities:
            citys_without_cityx = matches+[]
            citys_without_cityx = self.delete_city(cityx, citys_without_cityx)
            for cityy in citys_without_cityx:
                if bool(re.search(cityx,cityy)):
                    citys_that_occur_in_other_city_strings.append(cityx)
        citys_that_occur_in_other_city_strings = set(citys_that_occur_in_other_city_strings)
        citys_that_occur_in_other_city_strings = list(citys_that_occur_in_other_city_strings)
        for city in citys_that_occur_in_other_city_strings:
            x = 0
            for other_city in found_cities:
                if other_city!=city:
                    x = x + len(re.findall("( |^)"+other_city+"(( |[\.\!\?\,])|$)", query))
            y = len(re.findall("( |^)"+city+"(( |[\.\!\?\,])|$)", query))
            if y <= x:
                found_cities = set(found_cities)
                found_cities -= {city}
                found_cities = list(found_cities)
        return found_cities

    def find_cities_in_query(self,query):
        # we first load thousands of cities from a JSON file
        # Source of this collection: https://datahub.io/core/world-cities
        with open('alternative_implementations/cities.json', 'r', encoding="UTF-8") as myfile:
            data = myfile.read()
        # The names of the cities in the list can also be in English. Therefore, we also translate the query into English,
        # so that we can possibly find a city.
        translator_to_english = Translator(to_lang="en", from_lang="de")
        query_english = translator_to_english.translate(query)
        # now we will store all city names in the city array
        json_file_obj = json.loads(data)
        cities = []
        for city_json_object in json_file_obj:
            cities.append(city_json_object["name"])
        found_cities = []
        regex = "( |^)("
        for city in cities:
            regex += city+"|"
        regex = regex[:-1]+")( |[\.\!\?\,]|$)"
        found_cities_german = re.findall(regex,query)
        if len(found_cities_german) > 0:
            for list_match in found_cities_german:
                for i in range(len(list(list_match))):
                    if len(re.findall("[a-zäöüß]+", list(list_match)[i], re.IGNORECASE)) > 0:
                        found_cities.append(list(list_match)[i])

        found_cities_english = re.findall(regex,query_english)
        if len(found_cities_english) > 0:
            for list_match in found_cities_english:
                for i in range(len(list(list_match))):
                    if len(re.findall("[a-zäöüß]+", list(list_match)[i], re.IGNORECASE)) > 0:
                        found_cities.append(list(list_match)[i])
        found_cities = list(set(found_cities))
        translator_to_german = Translator(to_lang="de", from_lang="en")
        for i in range(len(found_cities)):
            city = translator_to_german.translate(found_cities[i])
            found_cities[i] = city.title()
        found_cities = self.found_wrong_matches(query,found_cities)
        return found_cities


city_detector = CityDetector()