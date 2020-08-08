from weatherbit.api import Api
import re
import datetime
import requests
import xmltodict

class WeatherAPIHandler():

    def interpret_data_and_create_answer(self, question_type, city, selected_time, selected_time_type):
        self.identify_question_type(question_type, city, selected_time, selected_time_type)

    def identify_question_type(self, question_type, city, selected_time, selected_time_type):
        if question_type == "WEATHER":
            self.create_weather_answer(city, selected_time, selected_time_type)
        if question_type == "RAIN":
            self.create_rain_answer(city,selected_time,selected_time_type)
        if question_type == "SUN":
            self.create_sun_answer(city,selected_time,selected_time_type)
        if question_type == "WIND":
            self.create_wind_answer(city,selected_time,selected_time_type)
        if question_type == "THUNDER":
            self.create_thunder_answer(city,selected_time,selected_time_type)
        if question_type == "SNOW":
            self.create_snow_answer(city,selected_time,selected_time_type)
        if question_type == "FOG":
            self.create_fog_answer(city,selected_time,selected_time_type)
        if question_type == "AIR PRESSURE":
            self.create_air_pressure_answer(city,selected_time,selected_time_type)
        if question_type == "TEMPERATURE":
            self.create_temperature_answer(city,selected_time,selected_time_type)
        if question_type == "COLD" or question_type == "WARM":
            self.create_cold_warm_answer(city,selected_time,selected_time_type)
        if question_type == "AVERAGE_TEMPERATURE":
            self.create_average_temperature_answer(city, selected_time, selected_time_type)
        if question_type == "WIND_DIRECTION":
            self.create_wind_direction_answer(city, selected_time, selected_time_type)
        if question_type == "CLOUDS":
            self.create_clouds_answer(city, selected_time, selected_time_type)
        if question_type == "MAX_TEMPERATURE":
            self.create_max_temperature_answer(city, selected_time, selected_time_type)
        if question_type == "MIN_TEMPERATURE":
            self.create_min_temperature_answer(city, selected_time, selected_time_type)

    # Processing methods for each question type
    def create_max_temperature_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            answer = "Am "+formatted_date+" um "+str(selected_time[0].hour) +" Uhr kann mit einer Durschschnittstemperatur von " + str(forecast_object_time_point["temp"]) + " Grad Celsius gerechnet werden in "+ city + "! \n"+'\033[93m'+"Leider bietet der Wetterdienst für einzelne Stunden keine Maxmialtemperatur/Minimaltemperatur, jedoch eine Durchschnittstemperatur."+ '\033[0m'
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            answer = "Die Maximaltemperatur in "+city+" beträgt ungefähr "+ str(forecast_object["max_temp"])+" Grad Celsius am "+ formatted_date+"."
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0],selected_time[1],city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                answer = "Am "+formatted_date+" beträgt die Maximaltemperatur in "+city+" ungefähr "+str(forecast_object["max_temp"])+ " Grad Celsius!"
                print(answer)

    def create_min_temperature_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            answer = "Sie können am "+formatted_date+" um "+str(selected_time[0].hour) +" Uhr mit einer Durchschnittstemperatur von " + str(forecast_object_time_point["temp"]) + " Grad Celsius rechen in "+ city + "! \n"+'\033[93m'+"Leider bietet der Wetterdienst für einzelne Stunden keine Maxmialtemperatur/Minimaltemperatur, jedoch eine Durchschnittstemperatur."+ '\033[0m'
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            answer = "Die Minimaltemperatur in "+city+" beträgt ungefähr "+ str(forecast_object["min_temp"])+" Grad Celsius am "+ formatted_date+"."
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0],selected_time[1],city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                answer = "Am "+formatted_date+" beträgt die Minimaltemperatur in "+city+" ungefähr "+str(forecast_object["min_temp"])+ " Grad Celsius!"
                print(answer)

    def create_clouds_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            cloud_coverage = forecast_object_time_point["clouds"]
            cloud_description = self.get_cloud_description(cloud_coverage)
            answer = "Sie können am "+formatted_date+" in "+city+" um "+str(selected_time[0].hour)+" Uhr damit rechnen, dass der Himmel "+ cloud_description + " ist! "+str(cloud_coverage)+" % des Himmels sind mit Wolken bedeckt!"
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            cloud_coverage = forecast_object["clouds"]
            cloud_description = self.get_cloud_description(cloud_coverage)
            answer = "Man kann am " + formatted_date + " in " + city + " damit rechnen, dass der Himmel " + cloud_description + " ist! " + str(cloud_coverage) + " % des Himmels sind mit Wolken bedeckt!"
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0],selected_time[1],city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                cloud_coverage = forecast_object["clouds"]
                cloud_description = self.get_cloud_description(cloud_coverage)
                answer = "Am " + formatted_date + " kann in " + city + " damit gerechnet werden, dass der Himmel " + cloud_description + " ist! " + str(cloud_coverage) + " % des Himmels sind mit Wolken bedeckt!"
                print(answer)

    def get_cloud_description(self,coverage):
        # Der Himmel ist...
        if 0 < coverage < 3:
            return "nicht bewölkt(freier Himmel)"
        if 3 <= coverage < 10:
            return "sehr wenig bewölkt"
        if 10 <= coverage < 30:
            return "ein wenig bewölkt"
        if 30 <= coverage < 50:
            return "leicht bewölkt"
        if 50 <= coverage < 80:
            return "bewölkt"
        if 80 <= coverage < 95:
            return "fast komplett bewölkt"
        if 95 <= coverage <= 100:
            return "komplett bewölkt"

    def create_wind_direction_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            wind_dir = forecast_object_time_point["wind_dir"]
            wind_dir_description = self.direction_degrees_to_text(wind_dir)
            answer = "Der Wind weht am "+formatted_date+" um "+str(selected_time[0].hour)+" Uhr in "+city+" "+wind_dir_description+"."
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            wind_dir = forecast_object["wind_dir"]
            wind_dir_description = self.direction_degrees_to_text(wind_dir)
            answer = "Am "+formatted_date+" weht der Wind in "+city+" "+wind_dir_description+"!"
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0],selected_time[1],city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                wind_dir = forecast_object["wind_dir"]
                wind_dir_description = self.direction_degrees_to_text(wind_dir)
                answer = "Am " + formatted_date + " weht der Wind in " + city + " " + wind_dir_description + "!"
                print(answer)

    def direction_degrees_to_text(self,degree):
        if degree > 337.5:
            return 'in Richtung Norden'
        if (degree > 292.5):
            return 'in Richtung Nord-Westen'
        if (degree > 247.5):
            return 'in Richtung Westen'
        if (degree > 202.5):
            return 'in Richtung Süd-Westen'
        if (degree > 157.5):
            return 'in Richtung Sünden'
        if (degree > 122.5):
            return 'in Richtung Süde-Osten'
        if (degree > 67.5):
            return 'in Richtung Osten'
        if (degree > 22.5):
           return 'in Richtung Nord-Osten'
        return 'in Richtung Norden'

    def create_average_temperature_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            answer = "Sie können am "+formatted_date+" um "+str(selected_time[0].hour) +" Uhr mit einer Durschschnittstemperatur von " + str(forecast_object_time_point["temp"]) + " Grad Celsius rechen in "+ city + "!"
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            answer = "Die Durschnittstemperatur in "+city+" beträgt ungefähr "+ str(forecast_object["temp"])+" Grad Celsius am "+ formatted_date+"."
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0],selected_time[1],city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                answer = "Am "+formatted_date+" beträgt die Durschnittstemperatur in "+city+" ungefähr "+str(forecast_object["temp"])+ " Grad Celsius!"
                print(answer)

    def create_cold_warm_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            answer = ""
            if 0 < forecast_object_time_point["temp"] < 15:
                answer = "Sie werden wärmere Kleidung benötigen, da es etwas kälter draußen ist. "+"Um " +  str(selected_time[0].hour) +" Uhr am "+formatted_date + " kann mit ungefähr " + str(forecast_object_time_point["temp"]) + " Grad Celsius gerechnet werden in " + city + "!"
            if 0 > forecast_object_time_point["temp"]:
                answer = "Es ist sehr kalt draußen. Die zu erwartende Temperatur liegt bei unter 0 Grad Celsius!" + "Um " + str(selected_time[0].hour) + " Uhr am " + formatted_date + " kann mit ungefähr " + str(forecast_object_time_point["temp"]) + " Grad Celsius gerechnet werden in " + city + "!"
            if 15 <= forecast_object_time_point["temp"] < 22:
                answer = "Es sind milde Temperaturen zu erwarten. "+"Um " + str(selected_time[0].hour) + " Uhr am " + formatted_date + " kann mit ungefähr " + str(forecast_object_time_point["temp"]) + " Grad Celsius gerechnet werden in " + city + "!"
            if 22 <= forecast_object_time_point["temp"] < 30:
                answer = "Es wird warm. Eine Jacke benötigt man nicht unbedingt." + "Um " + str(selected_time[0].hour) + " Uhr am " + formatted_date + " kann mit ungefähr " + str(forecast_object_time_point["temp"]) + " Grad Celsius gerechnet werden in " + city + "!"
            if 30 <= forecast_object_time_point["temp"]:
                answer = "Es wird sehr warm! Ein T-Shirt reicht auf jeden Fall!" + " Um " + str(selected_time[0].hour) + " Uhr am " + formatted_date + " kann mit ungefähr " + str(forecast_object_time_point["temp"]) + " Grad Celsius gerechnet werden in " + city + "!"
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            answer = ""
            if 0 < forecast_object["temp"] < 15:
                answer = "Sie werden wärmere Kleidung benötigen, da es etwas kälter draußen ist. " + "Sie können in "+city + " am "+formatted_date+" über den Tag verteilt ungefähr mit Temperaturen von mindestens "+str(forecast_object["min_temp"]) + " Grad Celsius bis zu maximal "+str(forecast_object["max_temp"]) + " Grad Celsius rechen!" + " Durchschnittlich wird es etwa "+str(forecast_object["temp"]) + " Grad Celsius geben!"
            if 0 > forecast_object["temp"]:
                answer = "Es ist sehr kalt draußen. Die zu erwartende Temperatur liegt bei unter 0 Grad Celsius!" + "Sie können in "+city + " am "+formatted_date+" über den Tag verteilt ungefähr mit Temperaturen von mindestens "+str(forecast_object["min_temp"]) + " Grad Celsius bis zu maximal "+str(forecast_object["max_temp"]) + " Grad Celsius rechen!" + " Durchschnittlich wird es etwa "+str(forecast_object["temp"]) + " Grad Celsius geben!"
            if 15 <= forecast_object["temp"] < 22:
                answer = "Es sind milde Temperaturen zu erwarten. " + "Sie können in "+city + " am "+formatted_date+" über den Tag verteilt ungefähr mit Temperaturen von mindestens "+str(forecast_object["min_temp"]) + " Grad Celsius bis zu maximal "+str(forecast_object["max_temp"]) + " Grad Celsius rechen!" + " Durchschnittlich wird es etwa "+str(forecast_object["temp"]) + " Grad Celsius geben!"
            if 22 <= forecast_object["temp"] < 30:
                answer = "Es wird warm. Eine Jacke benötigt man nicht unbedingt." + "Sie können in "+city + " am "+formatted_date+" über den Tag verteilt ungefähr mit Temperaturen von mindestens "+str(forecast_object["min_temp"]) + " Grad Celsius bis zu maximal "+str(forecast_object["max_temp"]) + " Grad Celsius rechen!" + " Durchschnittlich wird es etwa "+str(forecast_object["temp"]) + " Grad Celsius geben!"
            if 30 <= forecast_object["temp"]:
                answer = "Es wird sehr warm! Ein T-Shirt reicht auf jeden Fall!" + "Sie können in "+city + " am "+formatted_date+" über den Tag verteilt ungefähr mit Temperaturen von mindestens "+str(forecast_object["min_temp"]) + " Grad Celsius bis zu maximal "+str(forecast_object["max_temp"]) + " Grad Celsius rechen!" + " Durchschnittlich wird es etwa "+str(forecast_object["temp"]) + " Grad Celsius geben!"
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0],selected_time[1],city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                answer = ""
                if 0 < forecast_object["temp"] < 15:
                    answer = "Am " + formatted_date + " werden Sie werden wärmere Kleidung benötigen, da es etwas kälter draußen ist. " +"Es kann in "+city+" über den Tag verteilt ungefähr mit Temperaturen von mindestens " + str(forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(forecast_object["max_temp"]) + " Grad Celsius gerechnet werden!" + " Durchschnittlich wird es etwa " + str(forecast_object["temp"]) + " Grad Celsius geben!"
                if 0 > forecast_object["temp"]:
                    answer = "Am " + formatted_date +" wird es sehr kalt draußen. Die zu erwartende Temperatur liegt bei unter 0 Grad Celsius!" + "Es kann in "+city+" über den Tag verteilt ungefähr mit Temperaturen von mindestens " + str(forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(forecast_object["max_temp"]) + " Grad Celsius gerechnet werde!" + " Durchschnittlich wird es etwa " + str(forecast_object["temp"]) + " Grad Celsius geben!"
                if 15 <= forecast_object["temp"] < 22:
                    answer = "Am " + formatted_date +" sind milde Temperaturen zu erwarten. " + "In "+city+" wird es über den Tag verteilt ungefähr " + str(forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(forecast_object["max_temp"]) + " Grad Celsius geben!" + " Durchschnittlich wird es etwa " + str(forecast_object["temp"]) + " Grad Celsius geben!"
                if 22 <= forecast_object["temp"] < 30:
                    answer = "Am " + formatted_date +" wird es warm. Eine Jacke benötigt man nicht unbedingt." + " In "+city+" kann über den Tag verteilt ungefähr mit Temperaturen von mindestens " + str(forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(forecast_object["max_temp"]) + " Grad Celsius gerechnet!" + " Durchschnittlich wird es etwa " + str(forecast_object["temp"]) + " Grad Celsius geben!"
                if 30 <= forecast_object["temp"]:
                    answer = "Am " + formatted_date +" wird es sehr warm! Ein T-Shirt reicht auf jeden Fall!" + "In "+city+" kann über den Tag verteilt ungefähr mit Temperaturen von mindestens " + str(forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(forecast_object["max_temp"]) + " Grad Celsius gerechnet werden!" + " Durchschnittlich wird es etwa " + str(forecast_object["temp"]) + " Grad Celsius geben!"
                print(answer)

    def create_temperature_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            answer = "Um " +  str(selected_time[0].hour) +" Uhr am "+formatted_date + " kann mit ungefähr " + str(forecast_object_time_point["temp"]) + " Grad Celsius gerechnet werden in " + city + "!"
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            answer = "Sie können in "+city + " am "+formatted_date+" über den Tag verteilt ungefähr mit "+str(forecast_object["min_temp"]) + " Grad Celsius bis zu maximal "+str(forecast_object["max_temp"]) + " Grad Celsius erwarten!" + " Durchschnittlich wird es etwa "+str(forecast_object["temp"]) + " Grad Celsius geben!"
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0],selected_time[1],city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                answer = "Am " + formatted_date +" kann in "+city+" über den Tag verteilt ungefähr mit Temperaturen von mindestens " + str(forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(forecast_object["max_temp"]) + " Grad Celsius rechen!" + " Durchschnittlich wird es etwa " + str(forecast_object["temp"]) + " Grad Celsius geben!"
                print(answer)

    def create_air_pressure_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            answer = "Sie können am "+ formatted_date + " um " + str(selected_time[0].hour) + " Uhr von einem Luftdruck von " + str(forecast_object_time_point["pres"]) + " hPa ausgehen in "+city+"!"
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            answer = "Der Luftdruck wird in "+city+" am " + formatted_date + " bei ungefähr " + str(forecast_object["pres"]) + " hPa liegen!"
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0],selected_time[1],city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                answer = "Am " + formatted_date + " wird der Luftdruck in "+city+" bei ungefähr " + str(forecast_object["pres"]) + " hPa liegen!"
                print(answer)

    def create_weather_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            answer = "Am " + formatted_date +" um "+str(selected_time[0].hour)+" Uhr"+" kannst du mit " + str(self.translate_weather_description(forecast_object_time_point["weather"]["description"])) + " rechnen in " + city + ". Du kannst außerdem mit Temperaturen von " + str(forecast_object_time_point["temp"]) + " Grad Celsius ausgehen!"
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            answer = "Am "+formatted_date+" solltest du mit "+str(self.translate_weather_description(forecast_object["weather"]["description"]))+" in "+city+" rechnen. Du kannst außerdem von "+str(forecast_object["max_temp"])+" Grad Celsius ausgehen!"
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0],selected_time[1],city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                answer = "Am " + formatted_date + " solltest du mit " + str(self.translate_weather_description(forecast_object["weather"]["description"])) + " in " + city + " rechnen. Du kannst außerdem von " + str(forecast_object["max_temp"]) + " Grad Celsius ausgehen!"
                print(answer)

    def create_snow_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            if len(re.findall("Snow", forecast_object_time_point["weather"]["description"])) > 0:
                answer = "Es kann mit "+ str(self.translate_weather_description(forecast_object_time_point["weather"]["description"])) + " in "+ city + " gerechnet werden! \n Es liegen "+str(forecast_object_time_point["snow_depth"])+" mm Schnee!"
                print(answer)
            else:
                answer = "Am " + formatted_date +" um "+str(selected_time[0].hour)+" Uhr wird es keinen Schnee geben in "+city+"!\n Es liegen "+str(forecast_object_time_point["snow_depth"])+" mm Schnee!"
                print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_for_day = self.get_forecast_object_for_day(selected_time[0], city)
            if len(re.findall("Snow", forecast_object_for_day["weather"]["description"])) > 0:
                answer = "Es kann mit "+ str(self.translate_weather_description(forecast_object_for_day["weather"]["description"])) + " gerechnet werden in "+ city + " am "+formatted_date+"!\n Es liegen "+str(forecast_object_for_day["snow_depth"])+" mm Schnee!"
                print(answer)
            else:
                answer = "Am " + formatted_date+" wird es keinen Schnee geben in "+city+"!\n Es liegen "+str(forecast_object_for_day["snow_depth"])+" mm Schnee!"
                print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0],selected_time[1],city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                if len(re.findall("Snow", fc["weather"]["description"])) > 0:
                    answer = "Es kann mit " + str(self.translate_weather_description(fc["weather"]["description"])) + " in " + city + " gerechnet werden am " + formatted_date + " geben!\n Es liegen "+str(fc["snow_depth"])+" mm Schnee!"
                    print(answer)
                else:
                    answer = "Am " + formatted_date + " wird es keinen Schnee geben in " + city + "!\n Es liegen "+str(fc["snow_depth"])+" mm Schnee!"
                    print(answer)

    def create_fog_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            if len(re.findall("fog", forecast_object_time_point["weather"]["description"])) > 0:
                answer = "Es kann mit "+ str(self.translate_weather_description(forecast_object_time_point["weather"]["description"])) + " in "+ city + " gerechnet werden!"
                print(answer)
            else:
                answer = "Am " + formatted_date +" um "+str(selected_time[0].hour)+" Uhr wird es keinen Nebel geben in "+city+"!"
                print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_for_day = self.get_forecast_object_for_day(selected_time[0], city)
            if len(re.findall("fog", forecast_object_for_day["weather"]["description"])) > 0:
                answer = "Es kann mit "+ str(self.translate_weather_description(forecast_object_for_day["weather"]["description"])) + " gerechnet werden in "+ city + " am "+formatted_date+"!"
                print(answer)
            else:
                answer = "Am " + formatted_date+" wird es keinen Nebel geben in "+city+"!"
                print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0],selected_time[1],city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                if len(re.findall("fog", fc["weather"]["description"])) > 0:
                    answer = "Es kann mit " + str(self.translate_weather_description(fc["weather"]["description"])) + " in " + city + " gerechnet werden am " + formatted_date + " geben!"
                    print(answer)
                else:
                    answer = "Am " + formatted_date + " wird es keinen Nebel geben in " + city + "!"
                    print(answer)

    def create_thunder_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            if len(re.findall("Thunderstorm", forecast_object_time_point["weather"]["description"])) > 0:
                answer = "Es kann mit "+ str(self.translate_weather_description(forecast_object_time_point["weather"]["description"])) + " in "+ city + " gerechnet werden!"
                print(answer)
            else:
                answer = "Am " + formatted_date +" um "+str(selected_time[0].hour)+" Uhr wird es keinen Sturm/Gewitter geben in "+city+"!"
                print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_for_day = self.get_forecast_object_for_day(selected_time[0], city)
            if len(re.findall("Thunderstorm", forecast_object_for_day["weather"]["description"])) > 0:
                answer = "Es kann mit "+ str(self.translate_weather_description(forecast_object_for_day["weather"]["description"])) + " gerechnet werden in "+ city + " am "+formatted_date+"!"
                print(answer)
            else:
                answer = "Am " + formatted_date+" wird es keinen Sturm/Gewitter geben in "+city+"!"
                print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0],selected_time[1],city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                if len(re.findall("Thunderstorm", fc["weather"]["description"])) > 0:
                    answer = "Es kann mit " + str(self.translate_weather_description(fc["weather"]["description"])) + " in " + city + " gerechnet werden am " + formatted_date + "!"
                    print(answer)
                else:
                    answer = "Am " + formatted_date + " wird es keinen Sturm/Gewitter geben in " + city + "!"
                    print(answer)

    def create_rain_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            if len(re.findall("rain", forecast_object_time_point["weather"]["description"])) > 0:
                answer = "Es kann mit "+ str(self.translate_weather_description(forecast_object_time_point["weather"]["description"])) + " gerechnet wrrden in "+ city + "!"
                print(answer)
            else:
                answer = "Am " + formatted_date +" um "+str(selected_time[0].hour)+" Uhr wird es keinen Regen geben in "+city+"!"
                print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_for_day = self.get_forecast_object_for_day(selected_time[0], city)
            if len(re.findall("rain", forecast_object_for_day["weather"]["description"])) > 0:
                answer = "Es kann mit "+ str(self.translate_weather_description(forecast_object_for_day["weather"]["description"])) + " gerechnet werden in "+ city + " am "+formatted_date+"!"
                print(answer)
            else:
                answer = "Am " + formatted_date+" wird es keinen Regen geben in "+city+"!"
                print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0],selected_time[1],city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                if len(re.findall("rain", fc["weather"]["description"])) > 0:
                    answer = "Es kann mit " + str(self.translate_weather_description(fc["weather"]["description"])) + " gerechnet werden in " + city + " am " + formatted_date + "!"
                    print(answer)
                else:
                    answer = "Am " + formatted_date + " wird es keinen Regen geben in " + city + "!"
                    print(answer)

    def create_sun_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "day" or selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_for_day = self.get_forecast_object_for_day(selected_time[0], city)
            if len(re.findall("clear sky", forecast_object_for_day["weather"]["description"], re.IGNORECASE)) > 0:
                answer = "Am " + formatted_date + " kann in " + city + " mit einem klaren Himmel und Sonne rechnen!"
                print(answer)
            if len(re.findall("few clouds", forecast_object_for_day["weather"]["description"], re.IGNORECASE)) > 0:
                answer = "Am " + formatted_date + " kann in " + city + " mit ein paar Wolken und ein bisschen Sonne gerechnet werden!"
                print(answer)
            if len(re.findall("scattered clouds", forecast_object_for_day["weather"]["description"],re.IGNORECASE)) > 0:
                answer = "Am " + formatted_date + " kann in " + city + " mit ein paar zerstreuten Wolken und ein wenig Sonne gerechnet werden!"
                print(answer)
            else:
                answer = "Am " + formatted_date + " wird es leider keine Sonne geben in " + city + "!"
                print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0],selected_time[1],city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                if len(re.findall("clear sky", fc["weather"]["description"], re.IGNORECASE)) > 0:
                    answer = "Am " + formatted_date + " kann in " + city + " mit einem klaren Himmel und Sonne rechnen!"
                    print(answer)
                if len(re.findall("few clouds", fc["weather"]["description"], re.IGNORECASE)) > 0:
                    answer = "Am " + formatted_date + " kann in " + city + " mit ein paar Wolken und ein bisschen Sonne gerechnet werden!"
                    print(answer)
                if len(re.findall("scattered clouds", fc["weather"]["description"],re.IGNORECASE)) > 0:
                    answer = "Am " + formatted_date + " kann in " + city + " mit ein paar zerstreuten Wolken und ein wenig Sonne gerechnet werden!"
                    print(answer)
                else:
                    answer = "Am " + formatted_date + " wird es leider keine Sonne geben in " + city + "!"
                    print(answer)

    def create_wind_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            if forecast_object_time_point["wind_spd"]*3.6 < 1:
                answer = "Am " + formatted_date + " um " + str(selected_time[0].hour) + " Uhr wird es in " + city + " kaum Wind geben! Die Windgeschwindigkeit liegt bei " + str("{0:.2f}".format(forecast_object_time_point["wind_spd"]*3.6)) + " km/h" + " !"
                print(answer)
            if 20 > forecast_object_time_point["wind_spd"]*3.6 >= 1:
                answer = "Es wird am " + formatted_date + " um " + str(selected_time[0].hour) + " Uhr in " + city + " ein wenig Wind geben! Die Windgeschwindigkeit liegt bei " + str("{0:.2f}".format(forecast_object_time_point["wind_spd"]*3.6)) + " km/h" + " !"
                print(answer)
            if 39 > forecast_object_time_point["wind_spd"]*3.6 >= 20:
                answer = "Es wird am " + formatted_date + " um " + str(selected_time[0].hour) + " Uhr in " + city + " Wind geben (moderat)! Die Windgeschwindigkeit liegt bei " + str("{0:.2f}".format(forecast_object_time_point["wind_spd"]*3.6)) + " km/h" + " !"
                print(answer)
            if 39 < forecast_object_time_point["wind_spd"]*3.6 <= 118:
                answer = "Man kann am " + formatted_date + " um " + str(selected_time[0].hour) + " Uhr in " + city + " mit starkem Wind rechnen! Die Windgeschwindigkeit liegt bei " + str("{0:.2f}".format(forecast_object_time_point["wind_spd"]*3.6)) + " km/h" + " !"
                print(answer)
            if forecast_object_time_point["wind_spd"]*3.6 > 118:
                answer = "Achtung! Bitte passen Sie auf, es wird am " + formatted_date + " um " + str(selected_time[0].hour) + " Uhr in " + city + " einen Orkan geben! Die Windgeschwindigkeit liegt bei " + str("{0:.2f}".format(forecast_object_time_point["wind_spd"]*3.6)) + " km/h" + " !"
                print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_for_day = self.get_forecast_object_for_day(selected_time[0], city)
            if forecast_object_for_day["wind_spd"]*3.6 < 3:
                answer = "Am " + formatted_date + " um " + str(selected_time[0].hour) + " Uhr wird es in " + city + " kaum Wind geben! Die Windgeschwindigkeit liegt bei " + str("{0:.2f}".format(forecast_object_for_day["wind_spd"]*3.6)) + " km/h" + " !"
                print(answer)
            if 20 > forecast_object_for_day["wind_spd"]*3.6 >= 3:
                answer = "Es wird am " + formatted_date + " in " + city + " ein wenig Wind geben! Die Windgeschwindigkeit liegt bei " + str("{0:.2f}".format(forecast_object_for_day["wind_spd"]*3.6)) + " km/h" + " !"
                print(answer)
            if 39 > forecast_object_for_day["wind_spd"]*3.6 >= 20:
                answer = "Es wird am " + formatted_date + " in " + city + " Wind geben (moderat)! Die Windgeschwindigkeit liegt bei " + str("{0:.2f}".format(forecast_object_for_day["wind_spd"]*3.6)) + " km/h" + " !"
                print(answer)
            if 39 < forecast_object_for_day["wind_spd"]*3.6 <= 118:
                answer = "Man kann am " + formatted_date + " in " + city + " mit starkem Wind rechnen! Die Windgeschwindigkeit liegt bei " + str("{0:.2f}".format(forecast_object_for_day["wind_spd"]*3.6)) + " km/h" + " !"
                print(answer)
            if forecast_object_for_day["wind_spd"]*3.6 > 118:
                answer = "Achtung! Bitte passen Sie auf, es wird am " + formatted_date + " in " + city + " einen Orkan geben! Die Windgeschwindigkeit liegt bei " + str("{0:.2f}".format(forecast_object_for_day["wind_spd"]*3.6)) + " km/h" + " !"
                print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0],selected_time[1],city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                if fc["wind_spd"]*3.6 < 3:
                    answer = "Am " + formatted_date + " um " + str(selected_time[0].hour) + " Uhr wird es in " + city + " kaum Wind geben! Die Windgeschwindigkeit liegt bei " + str("{0:.2f}".format(fc["wind_spd"]*3.6)) + " km/h" + " !"
                    print(answer)
                if 20 > fc["wind_spd"]*3.6 >= 3:
                    answer = "Am " + formatted_date + " wird es in " + city + " ein wenig Wind geben! Die Windgeschwindigkeit liegt bei " + str("{0:.2f}".format(fc["wind_spd"]*3.6)) + " km/h" + " !"
                    print(answer)
                if 39 > fc["wind_spd"]*3.6 >= 20:
                    answer = "Am " + formatted_date + " wird es in " + city + " Wind geben (moderat)! Die Windgeschwindigkeit liegt bei " + str("{0:.2f}".format(fc["wind_spd"]*3.6)) + " km/h" + " !"
                    print(answer)
                if 39 < fc["wind_spd"]*3.6 <= 118:
                    answer = "Am " + formatted_date + " wird es in " + city + " staren Wind geben! Die Windgeschwindigkeit liegt bei " + str("{0:.2f}".format(fc["wind_spd"]*3.6)) + " km/h" + " !"
                    print(answer)
                if fc["wind_spd"]*3.6 > 118:
                    answer = "Achtung! Bitte passen Sie auf, es wird am " + formatted_date + " in " + city + " einen Orkan geben! Die Windgeschwindigkeit liegt bei " + str("{0:.2f}".format(fc["wind_spd"]*3.6)) + " km/h" + " !"
                    print(answer)

    def get_api_key(self):
        url = "https://homepages.ur.de/~hen58277/weather_assistant/api_key.xml"
        response = requests.get(url)
        data = xmltodict.parse(response.content)
        return data["key"]

    # Methods that can be used for every request:
    # get_forecast_object_for_day returns the forecast for a specific day
    # get_forecast_object_for_time_point returns the forecast for a specific time
    # get_forecast_object_for_range returns the forecast for several days
    # convert_data_to_formatted_text converts a date object to text. (for example 12.12.2020 -> "December 12, 2020")

    def get_forecast_object_for_day(self, selected_time, city):
        api_key = self.get_api_key()
        api = Api(api_key)
        api.set_granularity('daily')
        forecast = api.get_forecast(city=city)
        forecasts = forecast.get_series(
            ['clouds', 'precip', "temp", "min_temp", "max_temp", "weather", "pres", "datetime", "wind_dir", "clouds","snow","wind_spd","snow_depth"])
        for fc in forecasts:
            if fc["datetime"].year == selected_time.year and fc["datetime"].month == selected_time.month and fc["datetime"].day == selected_time.day:
                return fc

    def get_forecast_object_for_time_point(self, selected_time, city):
        api_key = self.get_api_key()
        api = Api(api_key)
        api.set_granularity('hourly')
        forecast = api.get_forecast(city=city)
        forecasts = forecast.get_series(
            ['clouds', 'precip', "temp", "min_temp", "max_temp", "weather", "pres", "datetime", "wind_dir", "clouds","snow","wind_spd","snow_depth"])
        for fc in forecasts:
            if fc["datetime"].year == selected_time.year and fc["datetime"].month == selected_time.month and fc["datetime"].day == selected_time.day and fc["datetime"].hour == selected_time.hour:
                return fc

    def get_forecast_object_for_range(self,start,end,city):
        api_key = self.get_api_key()
        api = Api(api_key)
        api.set_granularity('daily')
        print(city)
        forecast = api.get_forecast(city=city)
        start_counter = 0
        start_index = 0
        end_counter = 0
        end_index = 0
        forecasts = forecast.get_series(['clouds', 'precip', "temp", "min_temp", "max_temp", "weather", "pres", "datetime", "wind_dir", "clouds","snow", "wind_spd","snow_depth"])
        for fc in forecasts:
            if fc["datetime"].year == start.year and fc["datetime"].month == start.month and fc["datetime"].day == start.day:
                start_index = start_counter
            start_counter = start_counter + 1
        for fc in forecasts:
            if fc["datetime"].year == end.year and fc["datetime"].month == end.month and fc["datetime"].day == end.day:
                end_index = end_counter
            end_counter = end_counter + 1
        forecasts_return = []
        for i in range(start_index,end_index+1):
            forecasts_return.append(forecasts[i])
        return forecasts_return


    def convert_date_to_formatted_text(self,selected_time):
        months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
        month_index = selected_time.month - 1
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        is_tomorrow = ""
        if selected_time.year == tomorrow.year and selected_time.month == tomorrow.month and selected_time.day == tomorrow.day:
            is_tomorrow = " (morgen)"
        return str(selected_time.day)+ ". " + months[month_index] + " "+str(selected_time.year)+is_tomorrow

    def translate_weather_description(self, text):
        english_descriptions = ["Thunderstorm with light rain","Thunderstorm with rain","Thunderstorm with heavy rain","Thunderstorm with light drizzle","Thunderstorm with drizzle","Thunderstorm with heavy drizzle","Thunderstorm with hail","Light drizzle","Drizzle","Heavy drizzle","Light rain","Moderate rain","Heavy rain","Freezing rain","Light shower rain","Shower rain","Heavy shower rain","Light snow","Snow","Heavy snow","Mix snow/rain","Sleet","Heavy sleet","Snow shower","Heavy snow shower","Flurries","Mist","Smoke","Haze","Sand/dust","Fog","Freezing fog","Clear Sky","Few clouds","Scattered clouds","Broken clouds","Overcast clouds","Unknown precipitation"]
        german_descriptions = ["Gewitter und leichtem Regen", "Gewitter und Regen", "Gewitter und starkem Regen", "Gewitter mit leichtem Nieselregen", "Gewitter mit Nieselregen", "Gewitter mit starkem Nieselregen", "Gewitter mit Hagel", "leichtem Nieselregen", "Nieselregen", "starkem Nieselregen", "leichtem Regen", "mäßigem Regen", "starkem Regen", "Eisregen", "leichtem Schauerregen", "Schauerregen", "starkem Schauerregen", "leichtem Schnee", "Schnee", "starkem Schnee", "Schnee und Regen mischen", "Graupel", "starkem Graupel", "Schneeschauer", "starkem Schneeschauer", "Schauer", "Nebel", "Rauch", "Dunst", "Sand/Staub", "Nebel", "gefrierendem Nebel", "klarem Himmel", "wenigen Wolken", "verstreuten Wolken", "zerbrochenen Wolken", "bedeckten Wolken", "unbekannter Niederschlag"]
        counter = 0
        for decription in english_descriptions:
            if text == decription:
                return german_descriptions[counter]
            counter = counter + 1

weather_api_handler = WeatherAPIHandler()