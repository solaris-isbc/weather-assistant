import de_core_news_sm


class CityDetector():
    global found_cities
    global geocoder

    def get_data(self, location):
        response = self.geocoder.forward(location)
        return response.json()  # returns the geocoding result as GeoJSON.

    def more_than_one_city(self):
        if len(self.found_cities) > 1:
            return True
        return False

    def find_location_in_query(self, query):
        self.found_cities = []
        nlp = de_core_news_sm.load()
        doc = nlp(query)
        found_locations = set()
        for ent in doc.ents:
            if ent.label_ == "LOC":
                found_locations.add(ent.text)
                for token in doc:
                    # If the name of the city consists of only one word, then it should be checked whether the word belongs
                    # to the tag "NE", since cities always belong to this tag.
                    if token.text == ent.text and token.tag_ != "NE":
                        # If the word cannot be assigned to the tag "NE", then it is not recognized as a city.
                        found_locations.remove(token.text)
        self.found_cities = list(found_locations)
        if len(self.found_cities) == 0:
            return None
        return self.found_cities[0]


city_detector = CityDetector()
