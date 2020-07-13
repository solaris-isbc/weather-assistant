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
        # read file
        with open('cities.json', 'r') as myfile:
            data = myfile.read()
        # parse file
        translator_to_english = Translator(to_lang="en", from_lang="de")
        query_english = translator_to_english.translate(query)
        obj = json.loads(data)
        cities = []
        for city in obj:
            cities.append(city["name"])
        found_cities = []

        for i in range(0,len(cities),677):
            section_cities = ""
            for k in range(i,i+677,1):
                section_cities = section_cities +"|"+cities[k]
            section_cities = "("+section_cities[1:]+")"
            if bool(re.search("( |^)"+section_cities+"(( |[\.\!\?\,])|$)", query_english)) or bool(re.search("( |^)"+section_cities+"(( |[\.\!\?\,])|$)", query)):
                for n in range(i,i+677,1):
                    if bool(re.search("( |^)" + cities[n] + "(( |[\.\!\?\,])|$)", query_english)):
                       found_cities.append(cities[n])
                    if bool(re.search("( |^)"+cities[n]+"(( |[\.\!\?\,])|$)", query)):
                       found_cities.append(cities[n])

        found_cities = set(found_cities)
        found_cities = list(found_cities)
        translator_to_german = Translator(to_lang="de", from_lang="en")
        for i in range(len(found_cities)):
            city = translator_to_german.translate(found_cities[i])
            found_cities[i] = city.title()
        found_cities = self.found_wrong_matches(query,found_cities)
        return found_cities

city_detector = CityDetector()