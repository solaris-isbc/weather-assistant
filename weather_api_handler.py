from weatherbit.api import Api
import re
import datetime
import requests
import xmltodict
import operator


class WeatherAPIHandler():

    def interpret_data_and_create_answer(self, question_type, city, selected_time, selected_time_type, next_appearance_mode, query):
        if next_appearance_mode:
          if selected_time_type == "day":
             if len(self.get_forecasts_for_next_hours(selected_time, city)) != 0:
                 self.identify_question_type_for_next_appearance_mode(question_type, city, selected_time, selected_time_type,query)
             else:
                 print("Für die einzelnen Stunden von diesem Tag können leider keine Vorhersagen getroffen werden (nur die nächsten 48 Stunden).")
          if selected_time_type == "range":
             self.identify_question_type_for_next_appearance_mode(question_type, city, selected_time, selected_time_type)
        else:
          self.identify_question_type(question_type, city, selected_time, selected_time_type)

    def identify_question_type_for_next_appearance_mode(self, question_type, city, selected_time, selected_time_type, query):
        # Depending on the type of question recognized, a method is called to answer the respective question.
        # Information about the city and time found is also passed.
        if question_type == "WEATHER":
            print("Hoppla! Diese Frage kann so nicht beatwortet werden!")
        if question_type == "RAIN":
            self.create_rain_answer_next_appearance(city, selected_time, selected_time_type)
        if question_type == "SUN":
            self.create_sun_answer_next_appearance(city, selected_time, selected_time_type)
        if question_type == "WIND":
            self.create_wind_answer_next_appearance(city, selected_time, selected_time_type, query)
        if question_type == "THUNDER":
            self.create_thunder_answer_next_appearance(city, selected_time, selected_time_type)
        if question_type == "SNOW":
            self.create_snow_answer_next_appearance(city, selected_time, selected_time_type)
        if question_type == "FOG":
            self.create_fog_answer_next_appearance(city, selected_time, selected_time_type)
        if question_type == "AIR_PRESSURE":
            self.create_air_pressure_answer_next_appearance(city, selected_time, selected_time_type, query)
        if question_type == "TEMPERATURE" or question_type == "AVERAGE_TEMPERATURE" or question_type == "MAX_TEMPERATURE" or question_type == "MIN_TEMPERATURE":
           temperature_extracted = self.find_temperature(query)
           comparison_operator_extracted = self.find_comparison_operator_extracted(query)
           if question_type == "MAX_TEMPERATURE":
               comparison_operator_extracted = operator.le
           if question_type == "MIN_TEMPERATURE":
               comparison_operator_extracted = operator.ge
           if temperature_extracted == None:
               print("Hoppla! Diese Frage kann leider nicht beantwortet werden! [Temperature Error]")
           else:
               if ((question_type == "TEMPERATURE" or question_type == "AVERAGE_TEMPERATURE") and comparison_operator_extracted.__name__=="eq") or ((question_type == "MAX_TEMPERATURE" or question_type == "MIN_TEMPERATURE") and selected_time_type=="day"):
                   self.create_temperature_answer_next_appearance(city, selected_time, selected_time_type, temperature_extracted, comparison_operator_extracted, question_type)
               if (question_type == "MAX_TEMPERATURE" or comparison_operator_extracted.__name__=="le" or comparison_operator_extracted.__name__=="lt") and selected_time_type!="day":
                   self.create_max_temperature_answer_next_appearance(city, selected_time, selected_time_type, temperature_extracted, comparison_operator_extracted)
               if (question_type == "MIN_TEMPERATURE" or comparison_operator_extracted.__name__=="ge" or comparison_operator_extracted.__name__=="gt") and selected_time_type!="day":
                   self.create_min_temperature_answer_next_appearance(city, selected_time, selected_time_type, temperature_extracted, comparison_operator_extracted)
        if question_type == "COLD":
            self.create_cold_answer_next_appearance(city, selected_time, selected_time_type)
        if question_type == "WARM":
            self.create_warm_answer_next_appearance(city, selected_time, selected_time_type)
        if question_type == "WIND_DIRECTION":
            self.create_wind_direction_answer_next_appearance(city, selected_time, selected_time_type, query)
        if question_type == "CLOUDS":
            self.create_clouds_answer_next_appearance(city, selected_time, selected_time_type)

    def find_temperature(self,query):
        temperature_match = re.search("-?([0-9])+ *((grad)|(°))",query,re.IGNORECASE).group(0)
        if len(temperature_match) == 0:
            return None
        else:
            return re.search("-?([0-9])+",temperature_match,re.IGNORECASE).group(0)

    def find_comparison_operator_extracted(self,query):
        if bool(re.search("mindest|größer als|>=", query, re.IGNORECASE)):
            return operator.ge # a>=b
        if bool(re.search("mehr|größer|>", query, re.IGNORECASE)):
            return operator.gt # a>b
        if bool(re.search("höchstens|bis|<=", query, re.IGNORECASE)):
            return operator.le # a<=b
        if bool(re.search("weniger|<", query, re.IGNORECASE)):
            return operator.lt # a<b
        return operator.eq

    def identify_question_type(self, question_type, city, selected_time, selected_time_type):
        # Depending on the type of question recognized, a method is called to answer the respective question.
        # Information about the city and time found is also passed.
        if question_type == "WEATHER":
            self.create_weather_answer(city, selected_time, selected_time_type)
        if question_type == "RAIN":
            self.create_rain_answer(city, selected_time, selected_time_type)
        if question_type == "SUN":
            self.create_sun_answer(city, selected_time, selected_time_type)
        if question_type == "WIND":
            self.create_wind_answer(city, selected_time, selected_time_type)
        if question_type == "THUNDER":
            self.create_thunder_answer(city, selected_time, selected_time_type)
        if question_type == "SNOW":
            self.create_snow_answer(city, selected_time, selected_time_type)
        if question_type == "FOG":
            self.create_fog_answer(city, selected_time, selected_time_type)
        if question_type == "AIR_PRESSURE":
            self.create_air_pressure_answer(city, selected_time, selected_time_type)
        if question_type == "TEMPERATURE":
            self.create_temperature_answer(city, selected_time, selected_time_type)
        if question_type == "COLD" or question_type == "WARM":
            self.create_cold_warm_answer(city, selected_time, selected_time_type)
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

    def create_rain_answer_next_appearance(self, city, selected_time, selected_time_type):
        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forcasts_for_hours_of_day_requested = self.get_forecasts_for_next_hours(selected_time, city)
            forecasts_with_rain = [x for x in forcasts_for_hours_of_day_requested if bool(re.search("rain", x['weather']['description']))]
            next_day = datetime.datetime(selected_time[0].year, selected_time[0].month, selected_time[0].day)  + datetime.timedelta(days=1)
            if len(forecasts_with_rain) == 0:
                print("Am "+formatted_date+" ist nicht mit Regen zu rechnen in "+city+"! Auch in den restlichen Stunden, für die Wetterinformationen vorliegen ist nicht mit Regen zu rechnen!")
            elif forecasts_with_rain[0]['datetime'] > next_day:
                print("Am "+str(formatted_date)+" ist nicht mehr mit Regen zu rechnen. Dafür kann jedoch am "+self.convert_date_to_formatted_text(forecasts_with_rain[0]['datetime'])+" um "+str(forecasts_with_rain[0]['datetime'].hour)+" Uhr mit "+self.translate_weather_description(forecasts_with_rain[0]["weather"]["description"])+" gerechnet werden.")
            else:
                print("Es ist mit Regen zu rechnen in "+city+". Am " + self.convert_date_to_formatted_text(forecasts_with_rain[0]['datetime']) + " um " + str(
                    forecasts_with_rain[0]['datetime'].hour) + " Uhr kann mit " + self.translate_weather_description(
                    forecasts_with_rain[0]["weather"]["description"]) + " gerechnet werden.")

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            forecasts_with_rain = [x for x in forecasts if bool(re.search("rain", x['weather']['description']))]
            if len(forecasts_with_rain) == 0:
                print("In diesem Zeitraum ist nicht mit Regen zu rechnen in "+city+"!")
            else:
                print("Es ist mit Regen zu rechnen in " + city + ". Am " + self.convert_date_to_formatted_text(forecasts_with_rain[0]['datetime']) + " kann mit " + self.translate_weather_description(forecasts_with_rain[0]["weather"]["description"]) + " gerechnet werden.")

    def create_sun_answer_next_appearance(self, city, selected_time, selected_time_type):
        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forcasts_for_hours_of_day_requested = self.get_forecasts_for_next_hours(selected_time, city)
            forecasts_with_sun = [x for x in forcasts_for_hours_of_day_requested if x['clouds']<100 and x['datetime'].hour > 8 and x['datetime'].hour < 20]
            next_day = datetime.datetime(selected_time[0].year, selected_time[0].month,selected_time[0].day) + datetime.timedelta(days=1)
            if len(forecasts_with_sun) == 0:
                print(
                    "Am " + formatted_date + " ist nicht mit Sonne zu rechnen in " + city + "! Auch in den restlichen Stunden, für die Wetterinformationen vorliegen ist nicht mit Sonne zu rechnen!")
            elif forecasts_with_sun[0]['datetime'] > next_day:
                print("Am " + str(formatted_date) + " ist nicht mehr mit Sonne zu rechnen. Dafür kann jedoch am " + self.convert_date_to_formatted_text(forecasts_with_sun[0]['datetime']) + " um " + str(forecasts_with_sun[0]['datetime'].hour) + " Uhr mit Sonnenschein gerechnet werden!")
            else:
                print("Am " + self.convert_date_to_formatted_text(forecasts_with_sun[0]['datetime']) +" um "+str(forecasts_with_sun[0]['datetime'].hour)+ " Uhr können Sie mit Sonnenschein rechnen in "+city+"!")

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            forecasts_with_sun = [x for x in forecasts if x['clouds']<100 and x['datetime'].hour > 8 and x['datetime'].hour < 20]
            if len(forecasts_with_sun) == 0:
                print("In diesem Zeitraum ist nicht mit Sonnenschein zu rechnen in " + city + "!")
            else:
                print("Am " + self.convert_date_to_formatted_text(forecasts_with_sun[0]['datetime']) + " können Sie mit Sonnenschein rechnen in "+city+"!")

    def create_wind_answer_next_appearance(self, city, selected_time, selected_time_type, wind):
        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forcasts_for_hours_of_day_requested = self.get_forecasts_for_next_hours(selected_time, city)
            forecasts_with_wind = [x for x in forcasts_for_hours_of_day_requested if 20 > x["wind_spd"] * 3.6 >= 1]
            next_day = datetime.datetime(selected_time[0].year, selected_time[0].month,selected_time[0].day) + datetime.timedelta(days=1)
            if len(forecasts_with_wind) == 0:
                print("Am " + formatted_date + " ist nicht mit Wind zu rechnen in " + city + "! Auch in den restlichen Stunden, für die Wetterinformationen vorliegen ist nicht mit Wind zu rechnen!")
            elif forecasts_with_wind[0]['datetime'] > next_day:
                print("Am " + str(formatted_date) + " ist nicht mehr mit Wind zu rechnen. Dafür kann jedoch am " + self.convert_date_to_formatted_text(forecasts_with_wind[0]['datetime']) + " um " + str(forecasts_with_wind[0]['datetime'].hour) + " Uhr mit Wind gerechnet werden!")
            else:
                print("Am " + self.convert_date_to_formatted_text(forecasts_with_wind[0]['datetime']) +" um "+str(forecasts_with_wind[0]['datetime'].hour)+ " Uhr können Sie mit Wind rechnen in "+city+"!")

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            forecasts_with_wind = [x for x in forecasts if 20 > x["wind_spd"] * 3.6 >= 1]
            if len(forecasts_with_wind) == 0:
                print("In diesem Zeitraum wird es nicht windig werden in " + city + "!")
            else:
                print("Am " + self.convert_date_to_formatted_text(forecasts_with_wind[0]['datetime']) + " können Sie mit Wind rechnen in "+city+"!")

    def create_thunder_answer_next_appearance(self, city, selected_time, selected_time_type):
        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forcasts_for_hours_of_day_requested = self.get_forecasts_for_next_hours(selected_time, city)
            forecasts_with_thunderstorm = [x for x in forcasts_for_hours_of_day_requested if bool(re.search("Thunderstorm", x['weather']['description']))]
            next_day = datetime.datetime(selected_time[0].year, selected_time[0].month, selected_time[0].day) + datetime.timedelta(days=1)
            if len(forecasts_with_thunderstorm) == 0:
                print("Am " + formatted_date + " ist nicht mit einem Sturm zu rechnen in " + city + "! Auch in den restlichen Stunden, für die Wetterinformationen vorliegen ist nicht mit eienm Sturm zu rechnen!")
            elif forecasts_with_thunderstorm[0]['datetime'] > next_day:
                print("Am " + str(
                    formatted_date) + " ist nicht mehr mit Sturm zu rechnen. Dafür kann jedoch am " + self.convert_date_to_formatted_text(
                    forecasts_with_thunderstorm[0]['datetime']) + " um " + str(
                    forecasts_with_thunderstorm[0]['datetime'].hour) + " Uhr mit " + self.translate_weather_description(
                    forecasts_with_thunderstorm[0]["weather"]["description"]) + " gerechnet werden.")
            else:
                print("Es ist mit Sturm zu rechnen in " + city + ". Am " + self.convert_date_to_formatted_text(
                    forecasts_with_thunderstorm[0]['datetime']) + " um " + str(
                    forecasts_with_thunderstorm[0]['datetime'].hour) + " Uhr kann mit " + self.translate_weather_description(
                    forecasts_with_thunderstorm[0]["weather"]["description"]) + " gerechnet werden.")

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            forecasts_with_thunderstorm = [x for x in forecasts if bool(re.search("Thunderstorm", x['weather']['description']))]
            if len(forecasts_with_thunderstorm) == 0:
                print("In diesem Zeitraum ist nicht mit einem Sturm zu rechnen in " + city + "!")
            else:
                print("Es ist mit Sturm zu rechnen in " + city + ". Am " + self.convert_date_to_formatted_text(
                    forecasts_with_thunderstorm[0]['datetime']) + " kann mit " + self.translate_weather_description(
                    forecasts_with_thunderstorm[0]["weather"]["description"]) + " gerechnet werden.")

    def create_snow_answer_next_appearance(self, city, selected_time, selected_time_type):
        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forcasts_for_hours_of_day_requested = self.get_forecasts_for_next_hours(selected_time, city)
            forecasts_with_snow = [x for x in forcasts_for_hours_of_day_requested if bool(re.search("snow", x['weather']['description']))]
            next_day = datetime.datetime(selected_time[0].year, selected_time[0].month,selected_time[0].day) + datetime.timedelta(days=1)
            if len(forecasts_with_snow) == 0:
                print("Am " + formatted_date + " ist nicht mit Schnee zu rechnen in " + city + "! Auch in den restlichen Stunden, für die Wetterinformationen vorliegen ist nicht mit Schnee zu rechnen!")
            elif forecasts_with_snow[0]['datetime'] > next_day:
                print("Am " + str(
                    formatted_date) + " ist nicht mehr mit Schnee zu rechnen. Dafür kann jedoch am " + self.convert_date_to_formatted_text(
                    forecasts_with_snow[0]['datetime']) + " um " + str(
                    forecasts_with_snow[0]['datetime'].hour) + " Uhr mit " + self.translate_weather_description(
                    forecasts_with_snow[0]["weather"]["description"]) + " gerechnet werden.")
            else:
                print("Es ist mit Schnee zu rechnen in " + city + ". Am " + self.convert_date_to_formatted_text(
                    forecasts_with_snow[0]['datetime']) + " um " + str(
                    forecasts_with_snow[0]['datetime'].hour) + " Uhr kann mit " + self.translate_weather_description(
                    forecasts_with_snow[0]["weather"]["description"]) + " gerechnet werden.")

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            forecasts_with_snow = [x for x in forecasts if bool(re.search("snow", x['weather']['description']))]
            if len(forecasts_with_snow) == 0:
                print("In diesem Zeitraum ist nicht mit Schnee zu rechnen in " + city + "!")
            else:
                print("Es ist mit Schnee zu rechnen in " + city + ". Am " + self.convert_date_to_formatted_text(
                    forecasts_with_snow[0]['datetime']) + " kann mit " + self.translate_weather_description(
                    forecasts_with_snow[0]["weather"]["description"]) + " gerechnet werden.")

    def create_fog_answer_next_appearance(self, city, selected_time, selected_time_type):
        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forcasts_for_hours_of_day_requested = self.get_forecasts_for_next_hours(selected_time, city)
            forecasts_with_fog = [x for x in forcasts_for_hours_of_day_requested if
                                   bool(re.search("fog", x['weather']['description']))]
            next_day = datetime.datetime(selected_time[0].year, selected_time[0].month,
                                         selected_time[0].day) + datetime.timedelta(days=1)
            if len(forecasts_with_fog) == 0:
                print("Am " + formatted_date + " ist nicht mit Nebel zu rechnen in " + city + "! Auch in den restlichen Stunden, für die Wetterinformationen vorliegen ist nicht mit Nebel zu rechnen!")
            elif forecasts_with_fog[0]['datetime'] > next_day:
                print("Am " + str(
                    formatted_date) + " ist nicht mehr mit Nebel zu rechnen. Dafür kann jedoch am " + self.convert_date_to_formatted_text(
                    forecasts_with_fog[0]['datetime']) + " um " + str(
                    forecasts_with_fog[0]['datetime'].hour) + " Uhr mit " + self.translate_weather_description(
                    forecasts_with_fog[0]["weather"]["description"]) + " gerechnet werden.")
            else:
                print("Es ist mit Nebel zu rechnen in " + city + ". Am " + self.convert_date_to_formatted_text(
                    forecasts_with_fog[0]['datetime']) + " um " + str(
                    forecasts_with_fog[0]['datetime'].hour) + " Uhr kann mit " + self.translate_weather_description(
                    forecasts_with_fog[0]["weather"]["description"]) + " gerechnet werden.")

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            forecasts_with_fog = [x for x in forecasts if bool(re.search("fog", x['weather']['description']))]
            if len(forecasts_with_fog) == 0:
                print("In diesem Zeitraum ist nicht mit Nebel zu rechnen in " + city + "!")
            else:
                print("Es ist mit Nebel zu rechnen in " + city + ". Am " + self.convert_date_to_formatted_text(
                    forecasts_with_fog[0]['datetime']) + " kann mit " + self.translate_weather_description(
                    forecasts_with_fog[0]["weather"]["description"]) + " gerechnet werden.")

    def create_air_pressure_answer_next_appearance(self, city, selected_time, selected_time_type, query):
        operator_found = self.find_comparison_operator_extracted(query)
        operator_to_text = self.ap_operator_to_text(operator_found)
        air_pressure_found = re.search("[0-9]+ ?hpa", query, re.IGNORECASE).group(0)
        air_pressure_found = re.search("[0-9]+",air_pressure_found, re.IGNORECASE).group(0)
        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forcasts_for_hours_of_day_requested = self.get_forecasts_for_next_hours(selected_time, city)
            forecasts_with_specific_air_pressure = [x for x in forcasts_for_hours_of_day_requested if operator_found(x['pres'],int(air_pressure_found))]
            next_day = datetime.datetime(selected_time[0].year, selected_time[0].month,selected_time[0].day) + datetime.timedelta(days=1)
            if len(forecasts_with_specific_air_pressure) == 0:
                print("Am " + formatted_date + " ist nicht mit "+operator_to_text+air_pressure_found+" hPa zu rechnen in " + city + "! Auch in den restlichen Stunden, für die Wetterinformationen vorliegen ist damit nicht zu rechnen!")
            elif forecasts_with_specific_air_pressure[0]['datetime'] > next_day:
                print("Am " + str(formatted_date) + " ist nicht mehr mit "+operator_to_text+air_pressure_found+" hPa ("+str(forecasts_with_specific_air_pressure[0]['pres'])+" hPa)"+" zu rechnen. Dafür kann jedoch am " + self.convert_date_to_formatted_text(forecasts_with_specific_air_pressure[0]['datetime']) + " um " + str(forecasts_with_specific_air_pressure[0]['datetime'].hour) + " Uhr mit "+operator_to_text+air_pressure_found+" hPa ("+str(forecasts_with_specific_air_pressure[0]['pres'])+" hPa)"+" gerechnet werden.")
            else:
                print("In " + city + " kann am " + self.convert_date_to_formatted_text(forecasts_with_specific_air_pressure[0]['datetime']) + " um " + str(forecasts_with_specific_air_pressure[0]['datetime'].hour) + " Uhr kann mit "+operator_to_text+air_pressure_found+" hPa ("+str(forecasts_with_specific_air_pressure[0]['pres'])+" hPa)"+" gerechnet werden.")

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            forecasts_with_specific_air_pressure = [x for x in forecasts if operator_found(x['pres'],int(air_pressure_found))]
            if len(forecasts_with_specific_air_pressure) == 0:
                print("In diesem Zeitraum ist nicht mit "+operator_to_text+air_pressure_found+" hPa ("+str(forecasts_with_specific_air_pressure[0]['pres'])+" hPa)"+" zu rechnen in " + city + "!")
            else:
                print("In " + city + "kann am " + self.convert_date_to_formatted_text(forecasts_with_specific_air_pressure[0]['datetime']) + " kann mit "+operator_to_text+air_pressure_found+" hPa ("+str(forecasts_with_specific_air_pressure[0]['pres'])+" hPa)"+" gerechnet werden.")

    def ap_operator_to_text(self, comparison_operator_extracted):
        if comparison_operator_extracted.__name__ == "ge":
            return "mindestens "
        if comparison_operator_extracted.__name__ == "gt":
            return "mehr als "
        if comparison_operator_extracted.__name__ == "le":
            return "bis zu "
        if comparison_operator_extracted.__name__ == "lt":
            return "weniger als "
        return "genau "

    def create_warm_answer_next_appearance(self, city, selected_time, selected_time_type):
        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forcasts_for_hours_of_day_requested = self.get_forecasts_for_next_hours(selected_time, city)
            forecasts_with_warm_weather = [x for x in forcasts_for_hours_of_day_requested if x['temp'] > 22]
            next_day = datetime.datetime(selected_time[0].year, selected_time[0].month, selected_time[0].day) + datetime.timedelta(days=1)
            if len(forecasts_with_warm_weather) == 0:
                print("Am " + formatted_date + " kann nicht mit warmer Temperatur gerechnet werden in " + city + "! Auch in den restlichen Stunden, für die Wetterinformationen vorliegen ist nicht mit warmen Temperaturen zu rechnen!")
            elif forecasts_with_warm_weather[0]['datetime'] > next_day:
                print("Am " + str(
                    formatted_date) + " kann nicht mit warmer Temperatur gerechnet werden. Dafür kann jedoch am " + self.convert_date_to_formatted_text(
                    forecasts_with_warm_weather[0]['datetime']) + " um " + str(forecasts_with_warm_weather[0]['datetime'].hour) + " Uhr wieder mit warmen Temperaturen gerechnet werden ("+str(forecasts_with_warm_weather[0]["temp"])+")!")
            else:
                print("Es ist mit warmer Temperatur zu rechnen in " + city + ". Am " + self.convert_date_to_formatted_text(
                    forecasts_with_warm_weather[0]['datetime']) + " um " + str(
                    forecasts_with_warm_weather[0]['datetime'].hour) + " Uhr kann mit warmen Temperaturen gerechnet werden ("+str(forecasts_with_warm_weather[0]["temp"])+"°C)!")

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            forecasts_with_warm_weather = [x for x in forecasts if x['temp'] > 22]
            if len(forecasts_with_warm_weather) == 0:
                print("In diesem Zeitraum kann nicht mit warmen Temperaturen zu rechnen in " + city + "!")
            else:
                print(". Am " + self.convert_date_to_formatted_text(
                    forecasts_with_warm_weather[0]['datetime']) + " kann das nächste mal mit warmen Temperaturen gerechnet werden ("+str(forecasts_with_warm_weather[0]["temp"])+"°C)!")

    def create_cold_answer_next_appearance(self, city, selected_time, selected_time_type):
        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forcasts_for_hours_of_day_requested = self.get_forecasts_for_next_hours(selected_time, city)
            forecasts_with_cold_weather = [x for x in forcasts_for_hours_of_day_requested if x['temp'] < 10]
            next_day = datetime.datetime(selected_time[0].year, selected_time[0].month,
                                         selected_time[0].day) + datetime.timedelta(days=1)
            if len(forecasts_with_cold_weather) == 0:
                print(
                    "Am " + formatted_date + " kann nicht mit kalten Temperatur gerechnet werden in " + city + "! Auch in den restlichen Stunden, für die Wetterinformationen vorliegen ist nicht mit warmen Temperaturen zu rechnen!")
            elif forecasts_with_cold_weather[0]['datetime'] > next_day:
                print("Am " + str(
                    formatted_date) + " kann nicht mit kalten Temperatur gerechnet werden. Dafür kann jedoch am " + self.convert_date_to_formatted_text(
                    forecasts_with_cold_weather[0]['datetime']) + " um " + str(forecasts_with_cold_weather[0][
                                                                                   'datetime'].hour) + " Uhr wieder mit kalten Temperaturen gerechnet werden (" + str(
                    forecasts_with_cold_weather[0]["temp"]) + "°C )!")
            else:
                print(
                    "Es ist mit kalten Temperaturen zu rechnen in " + city + ". Am " + self.convert_date_to_formatted_text(
                        forecasts_with_cold_weather[0]['datetime']) + " um " + str(
                        forecasts_with_cold_weather[0][
                            'datetime'].hour) + " Uhr kann mit kalten Temperaturen gerechnet werden (" + str(
                        forecasts_with_cold_weather[0]["temp"]) + "°C )!")

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            forecasts_with_cold_weather = [x for x in forecasts if x['temp'] < 10]
            if len(forecasts_with_cold_weather) == 0:
                print("In diesem Zeitraum ist nicht mit kalten Temperaturen zu rechnen in " + city + "!")
            else:
                print("Am " + self.convert_date_to_formatted_text(forecasts_with_cold_weather[0]['datetime']) + " kann das nächste mal mit kalten Temperaturen gerechnet werden (" + str(forecasts_with_cold_weather[0]["temp"]) + "°C )!")

    def create_wind_direction_answer_next_appearance(self, city, selected_time, selected_time_type,query):
        direction_found_in_query = self.degree_text_to_range(query)
        if direction_found_in_query == None:
            print("Diese Frage kann leider nicht beantwortet werden")
        else:
            if selected_time_type == "day":
                formatted_date = self.convert_date_to_formatted_text(selected_time[0])
                forcasts_for_hours_of_day_requested = self.get_forecasts_for_next_hours(selected_time, city)
                wind_direction_as_text = self.direction_degrees_to_text(direction_found_in_query[0])
                if len(direction_found_in_query) == 2:
                    forecasts_with_wind_direction = [x for x in forcasts_for_hours_of_day_requested if x["wind_dir"] >= direction_found_in_query[0] and x["wind_dir"] < direction_found_in_query[1]]
                else:
                    forecasts_with_wind_direction = [x for x in forcasts_for_hours_of_day_requested if x["wind_dir"] >= direction_found_in_query[1] and x["wind_dir"] < direction_found_in_query[0]]
                next_day = datetime.datetime(selected_time[0].year, selected_time[0].month,selected_time[0].day) + datetime.timedelta(days=1)
                if len(forecasts_with_wind_direction) == 0:
                    print("Am " + formatted_date + " wird der Wind nicht " +wind_direction_as_text+ " wehen in " + city + "! Auch in den restlichen Stunden, für die Wetterinformationen vorliegen ist damit nicht zu rechnen!")
                elif forecasts_with_wind_direction[0]['datetime'] > next_day:
                    print("Am " + str(formatted_date) + " ist nicht mehr damit zu rechnen, dass der Wind "+wind_direction_as_text+" weht. Dafür wird der Wind am " + self.convert_date_to_formatted_text(forecasts_with_wind_direction[0]['datetime']) + " um " + str(forecasts_with_wind_direction[0]['datetime'].hour) + " Uhr " + wind_direction_as_text + " wehen!")
                else:
                    print("Am " + self.convert_date_to_formatted_text(forecasts_with_wind_direction[0]['datetime']) + " um " + str(forecasts_with_wind_direction[0]['datetime'].hour) + " Uhr wird der Wind " + wind_direction_as_text + " wehen in " + city + "!")

            if selected_time_type == "range":
                forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
                wind_direction_as_text = self.direction_degrees_to_text(direction_found_in_query[0])
                if len(direction_found_in_query) == 2:
                    forecasts_with_wind_direction = [x for x in forecasts if x["wind_dir"] >= direction_found_in_query[0] and x["wind_dir"] < direction_found_in_query[1]]
                else:
                    forecasts_with_wind_direction = [x for x in forecasts if x["wind_dir"] >= direction_found_in_query[1] and x["wind_dir"] < direction_found_in_query[0]]
                if len(forecasts_with_wind_direction) == 0:
                    print("In diesem Zeitraum wird der Wind nicht " + wind_direction_as_text+ " wehen in " + city + "!")
                else:
                    print("Am " + self.convert_date_to_formatted_text(forecasts_with_wind_direction[0]['datetime']) + " wird der Wind " + wind_direction_as_text + " wehen in " + city + "!")

    def degree_text_to_range(self,text):
        if bool(re.search("nord ?\-?osten", text, re.IGNORECASE)):
            return [22.5,67.5]
        if bool(re.search("nord ?\-?west", text, re.IGNORECASE)):
            print("enter")
            return [292.5,337.5]
        if bool(re.search("süd ?\-?osten", text, re.IGNORECASE)):
            return [112.5,157.5]
        if bool(re.search("süd ?\-?westen", text, re.IGNORECASE)):
            return [202.5,247.5]
        if bool(re.search("süd", text, re.IGNORECASE)):
            return [157.5,202.5]
        if bool(re.search("west", text, re.IGNORECASE)):
            return [247.5,292.5]
        if bool(re.search(" [öo]st", text, re.IGNORECASE)):
            return [67.5,112.5]
        if bool(re.search("nord", text, re.IGNORECASE)):
            return [337.5,22.5,"n"]
        return None

    def create_clouds_answer_next_appearance(self, city, selected_time, selected_time_type):
        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forcasts_for_hours_of_day_requested = self.get_forecasts_for_next_hours(selected_time, city)
            forecasts_with_clouds = [x for x in forcasts_for_hours_of_day_requested if x["clouds"] > 0]
            next_day = datetime.datetime(selected_time[0].year, selected_time[0].month,selected_time[0].day) + datetime.timedelta(days=1)
            if len(forecasts_with_clouds) == 0:
                print("Am " + formatted_date + " wird es nicht bewölkt sein in " + city + "! Auch in den restlichen Stunden, für die Wetterinformationen vorliegen ist nicht mit bewölktem Wetter zu rechnen!")
            elif forecasts_with_clouds[0]['datetime'] > next_day:
                next_cloud_description = self.get_cloud_description(forecasts_with_clouds[0]['clouds'])
                print("Am " + str(formatted_date) + " ist nicht mehr mit bewölktem Wetter zu rechnen. Dafür wird das Wetter am " + self.convert_date_to_formatted_text(forecasts_with_clouds[0]['datetime']) + " um " + str(forecasts_with_clouds[0]['datetime'].hour) + " Uhr "+next_cloud_description+" sein!")
            else:
                next_cloud_description = self.get_cloud_description(forecasts_with_clouds[0]['clouds'])
                print("Am " + self.convert_date_to_formatted_text(forecasts_with_clouds[0]['datetime']) + " um " + str(forecasts_with_clouds[0]['datetime'].hour) + " Uhr wird das Wetter "+next_cloud_description+" sein in " + city + "!")

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            forecasts_with_clouds = [x for x in forecasts if 20 > x["wind_spd"] * 3.6 >= 1]
            if len(forecasts_with_clouds) == 0:
                print("In diesem Zeitraum wird das Wetter nicht bewölkt sein in " + city + "!")
            else:
                next_cloud_description = self.get_cloud_description(forecasts_with_clouds[0]['clouds'])
                print("Am " + self.convert_date_to_formatted_text(forecasts_with_clouds[0]['datetime']) + " wird das Wetter "+next_cloud_description+" in " + city + "!")

    def create_temperature_answer_next_appearance(self, city, selected_time, selected_time_type, temperature_extracted, comparison_operator_extracted, question_type):
        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forcasts_for_hours_of_day_requested = self.get_forecasts_for_next_hours(selected_time, city)
            op_func = comparison_operator_extracted
            forecasts_with_specific_temperature = [x for x in forcasts_for_hours_of_day_requested if op_func(x['temp'],int(temperature_extracted))]
            next_day = datetime.datetime(selected_time[0].year, selected_time[0].month,selected_time[0].day) + datetime.timedelta(days=1)
            temperature_requested_formatted_text = self.operator_to_text(temperature_extracted, comparison_operator_extracted, question_type)
            if len(forecasts_with_specific_temperature) == 0:
                print("Am " + formatted_date + " ist nicht mit "+temperature_requested_formatted_text+" zu rechnen in " + city + "! Auch in den restlichen Stunden, für die Wetterinformationen vorliegen ist nicht mit "+temperature_requested_formatted_text+" zu rechnen!")
            elif forecasts_with_specific_temperature[0]['datetime'] > next_day:
                print("Am " + str(
                    formatted_date) + " ist nicht mehr mit "+temperature_requested_formatted_text+" zu rechnen. Dafür kann jedoch am " + self.convert_date_to_formatted_text(
                    forecasts_with_specific_temperature[0]['datetime']) + " um " + str(
                    forecasts_with_specific_temperature[0]['datetime'].hour) + " Uhr mit " + temperature_requested_formatted_text + " gerechnet werden.")
            else:
                print("In " + city + " kann am " + self.convert_date_to_formatted_text(
                    forecasts_with_specific_temperature[0]['datetime']) + " um " + str(
                    forecasts_with_specific_temperature[0]['datetime'].hour) + " Uhr kann mit " + temperature_requested_formatted_text + " gerechnet werden.")

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            op_func = comparison_operator_extracted
            forecasts_with_specific_temperature = [x for x in forecasts if op_func(x['temp'],int(temperature_extracted))]
            temperature_requested_formatted_text = self.operator_to_text(temperature_extracted,comparison_operator_extracted,question_type)
            if len(forecasts_with_specific_temperature) == 0:
                print("In diesem Zeitraum ist nicht mit "+temperature_requested_formatted_text+" zu rechnen in " + city + "!")
            else:
                print("In " + city + " ist am " + self.convert_date_to_formatted_text(
                    forecasts_with_specific_temperature[0]['datetime']) + " mit " + temperature_requested_formatted_text + " zu rechnen.")

    def operator_to_text(self,temperature_extracted, comparison_operator_extracted, question_type):
        if question_type == "MIN_TEMPERATURE":
            return "mindestens "+temperature_extracted+" °C (Minimaltemperatur)"
        if question_type == "MAX_TEMPERATURE":
            return "maximal "+temperature_extracted+" °C (Maximaltemperatur)"
        if comparison_operator_extracted.__name__ == "ge":
            return "mindestens "+temperature_extracted+" °C"
        if comparison_operator_extracted.__name__ == "gt":
            return "mehr als " + temperature_extracted + " °C"
        if comparison_operator_extracted.__name__ == "le":
            return "bis zu " + temperature_extracted + " °C"
        if comparison_operator_extracted.__name__ == "lt":
            return "weniger als " + temperature_extracted + " °C"
        return "genau "+temperature_extracted+" °C"

    def create_max_temperature_answer_next_appearance(self, city, selected_time, selected_time_type, temperature_extracted, comparison_operator_extracted):
        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            op_func = comparison_operator_extracted
            forecasts_with_max_temperature = [x for x in forecasts if op_func(x['max_temp'], int(temperature_extracted))]
            if len(forecasts_with_max_temperature) == 0:
                print(
                    "In diesem Zeitraum ist nicht mit einer Maximaltemperatur von " + str(temperature_extracted) + "°C zu rechnen in " + city + "!")
            else:
                print("In " + city + " ist am " + self.convert_date_to_formatted_text(forecasts_with_max_temperature[0]['datetime']) + " mit einer Maximaltemperatur von " + str(temperature_extracted) + "°C zu rechnen.")

    def create_min_temperature_answer_next_appearance(self, city, selected_time, selected_time_type, temperature_extracted, comparison_operator_extracted):
        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            op_func = comparison_operator_extracted
            forecasts_with_min_temperature = [x for x in forecasts if
                                              op_func(x['min_temp'], int(temperature_extracted))]
            if len(forecasts_with_min_temperature) == 0:
                print(
                    "In diesem Zeitraum ist nicht mit einer Minimaltemperatur von " + str(
                        temperature_extracted) + "°C zu rechnen in " + city + "!")
            else:
                print("In " + city + " ist am " + self.convert_date_to_formatted_text(
                    forecasts_with_min_temperature[0]['datetime']) + " mit einer Minimaltemperatur von " + str(
                    temperature_extracted) + "°C zu rechnen.")

    def create_average_temperature_answer_next_appearance(self, city, selected_time, selected_time_type, temperature_extracted, comparison_operator_extracted):
        # enter
        print("test")

    def create_max_temperature_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            answer = "Am " + formatted_date + " um " + str(
                selected_time[0].hour) + " Uhr kann mit einer Durschschnittstemperatur von " + str(
                forecast_object_time_point[
                    "temp"]) + " Grad Celsius gerechnet werden in " + city + "! \n" + '\033[93m' + "Leider bietet der Wetterdienst für einzelne Stunden keine Maxmialtemperatur/Minimaltemperatur, jedoch eine Durchschnittstemperatur." + '\033[0m'
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            answer = "Die Maximaltemperatur in " + city + " beträgt ungefähr " + str(
                forecast_object["max_temp"]) + " Grad Celsius am " + formatted_date + "."
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                answer = "Am " + formatted_date + " beträgt die Maximaltemperatur in " + city + " ungefähr " + str(
                    forecast_object["max_temp"]) + " Grad Celsius!"
                print(answer)

    def create_min_temperature_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            answer = "Sie können am " + formatted_date + " um " + str(
                selected_time[0].hour) + " Uhr mit einer Durchschnittstemperatur von " + str(forecast_object_time_point[
                                                                                                 "temp"]) + " Grad Celsius rechen in " + city + "! \n" + '\033[93m' + "Leider bietet der Wetterdienst für einzelne Stunden keine Maxmialtemperatur/Minimaltemperatur, jedoch eine Durchschnittstemperatur." + '\033[0m'
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            answer = "Die Minimaltemperatur in " + city + " beträgt ungefähr " + str(
                forecast_object["min_temp"]) + " Grad Celsius am " + formatted_date + "."
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                answer = "Am " + formatted_date + " beträgt die Minimaltemperatur in " + city + " ungefähr " + str(
                    forecast_object["min_temp"]) + " Grad Celsius!"
                print(answer)

    def create_clouds_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            cloud_coverage = forecast_object_time_point["clouds"]
            cloud_description = self.get_cloud_description(cloud_coverage)
            answer = "Sie können am " + formatted_date + " in " + city + " um " + str(
                selected_time[0].hour) + " Uhr damit rechnen, dass der Himmel " + cloud_description + " ist! " + str(
                cloud_coverage) + " % des Himmels sind mit Wolken bedeckt!"
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            cloud_coverage = forecast_object["clouds"]
            cloud_description = self.get_cloud_description(cloud_coverage)
            answer = "Man kann am " + formatted_date + " in " + city + " damit rechnen, dass der Himmel " + cloud_description + " ist! " + str(
                cloud_coverage) + " % des Himmels sind mit Wolken bedeckt!"
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                cloud_coverage = forecast_object["clouds"]
                cloud_description = self.get_cloud_description(cloud_coverage)
                answer = "Am " + formatted_date + " kann in " + city + " damit gerechnet werden, dass der Himmel " + cloud_description + " ist! " + str(
                    cloud_coverage) + " % des Himmels sind mit Wolken bedeckt!"
                print(answer)

    def get_cloud_description(self, coverage):
        # We need to convert the percentage 0-100 of cloud coverage into a text that is unterstandable for the user of the assistant
        if 0 <= coverage < 3:
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
            answer = "Der Wind weht am " + formatted_date + " um " + str(
                selected_time[0].hour) + " Uhr in " + city + " " + wind_dir_description + "."
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            wind_dir = forecast_object["wind_dir"]
            wind_dir_description = self.direction_degrees_to_text(wind_dir)
            answer = "Am " + formatted_date + " weht der Wind in " + city + " " + wind_dir_description + "!"
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                wind_dir = forecast_object["wind_dir"]
                wind_dir_description = self.direction_degrees_to_text(wind_dir)
                answer = "Am " + formatted_date + " weht der Wind in " + city + " " + wind_dir_description + "!"
                print(answer)

    def direction_degrees_to_text(self, degree):
        if 22.5 > degree or degree >= 337.5:
            return 'in Richtung Norden'
        if (degree >= 292.5):
            return 'in Richtung Nord-Westen'
        if (degree >= 247.5):
            return 'in Richtung Westen'
        if (degree >= 202.5):
            return 'in Richtung Süd-Westen'
        if (degree >= 157.5):
            return 'in Richtung Süden'
        if (degree >= 112.5):
            return 'in Richtung Süd-Osten'
        if (degree >= 67.5):
            return 'in Richtung Osten'
        if (degree >= 22.5):
            return 'in Richtung Nord-Osten'
        return 'in Richtung Norden'

    def create_average_temperature_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            answer = "Sie können am " + formatted_date + " um " + str(
                selected_time[0].hour) + " Uhr mit einer Durschschnittstemperatur von " + str(
                forecast_object_time_point["temp"]) + " Grad Celsius rechen in " + city + "!"
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            answer = "Die Durschnittstemperatur in " + city + " beträgt ungefähr " + str(
                forecast_object["temp"]) + " Grad Celsius am " + formatted_date + "."
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                answer = "Am " + formatted_date + " beträgt die Durschnittstemperatur in " + city + " ungefähr " + str(
                    forecast_object["temp"]) + " Grad Celsius!"
                print(answer)

    def create_cold_warm_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            answer = ""
            if 0 < forecast_object_time_point["temp"] < 15:
                answer = "Sie werden wärmere Kleidung benötigen, da es etwas kälter draußen ist. " + "Um " + str(
                    selected_time[0].hour) + " Uhr am " + formatted_date + " kann mit ungefähr " + str(
                    forecast_object_time_point["temp"]) + " Grad Celsius gerechnet werden in " + city + "!"
            if 0 > forecast_object_time_point["temp"]:
                answer = "Es ist sehr kalt draußen. Die zu erwartende Temperatur liegt bei unter 0 Grad Celsius!" + "Um " + str(
                    selected_time[0].hour) + " Uhr am " + formatted_date + " kann mit ungefähr " + str(
                    forecast_object_time_point["temp"]) + " Grad Celsius gerechnet werden in " + city + "!"
            if 15 <= forecast_object_time_point["temp"] < 22:
                answer = "Es sind milde Temperaturen zu erwarten. " + "Um " + str(
                    selected_time[0].hour) + " Uhr am " + formatted_date + " kann mit ungefähr " + str(
                    forecast_object_time_point["temp"]) + " Grad Celsius gerechnet werden in " + city + "!"
            if 22 <= forecast_object_time_point["temp"] < 30:
                answer = "Es wird warm. Eine Jacke benötigt man nicht unbedingt." + "Um " + str(
                    selected_time[0].hour) + " Uhr am " + formatted_date + " kann mit ungefähr " + str(
                    forecast_object_time_point["temp"]) + " Grad Celsius gerechnet werden in " + city + "!"
            if 30 <= forecast_object_time_point["temp"]:
                answer = "Es wird sehr warm! Ein T-Shirt reicht auf jeden Fall!" + " Um " + str(
                    selected_time[0].hour) + " Uhr am " + formatted_date + " kann mit ungefähr " + str(
                    forecast_object_time_point["temp"]) + " Grad Celsius gerechnet werden in " + city + "!"
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            answer = ""
            if 0 < forecast_object["temp"] < 15:
                answer = "Sie werden wärmere Kleidung benötigen, da es etwas kälter draußen ist. " + "Sie können in " + city + " am " + formatted_date + " über den Tag verteilt ungefähr mit Temperaturen von mindestens " + str(
                    forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(
                    forecast_object["max_temp"]) + " Grad Celsius rechen!" + " Durchschnittlich wird es etwa " + str(
                    forecast_object["temp"]) + " Grad Celsius geben!"
            if 0 > forecast_object["temp"]:
                answer = "Es ist sehr kalt draußen. Die zu erwartende Temperatur liegt bei unter 0 Grad Celsius!" + "Sie können in " + city + " am " + formatted_date + " über den Tag verteilt ungefähr mit Temperaturen von mindestens " + str(
                    forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(
                    forecast_object["max_temp"]) + " Grad Celsius rechen!" + " Durchschnittlich wird es etwa " + str(
                    forecast_object["temp"]) + " Grad Celsius geben!"
            if 15 <= forecast_object["temp"] < 22:
                answer = "Es sind milde Temperaturen zu erwarten. " + "Sie können in " + city + " am " + formatted_date + " über den Tag verteilt ungefähr mit Temperaturen von mindestens " + str(
                    forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(
                    forecast_object["max_temp"]) + " Grad Celsius rechen!" + " Durchschnittlich wird es etwa " + str(
                    forecast_object["temp"]) + " Grad Celsius geben!"
            if 22 <= forecast_object["temp"] < 30:
                answer = "Es wird warm. Eine Jacke benötigt man nicht unbedingt." + "Sie können in " + city + " am " + formatted_date + " über den Tag verteilt ungefähr mit Temperaturen von mindestens " + str(
                    forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(
                    forecast_object["max_temp"]) + " Grad Celsius rechen!" + " Durchschnittlich wird es etwa " + str(
                    forecast_object["temp"]) + " Grad Celsius geben!"
            if 30 <= forecast_object["temp"]:
                answer = "Es wird sehr warm! Ein T-Shirt reicht auf jeden Fall!" + "Sie können in " + city + " am " + formatted_date + " über den Tag verteilt ungefähr mit Temperaturen von mindestens " + str(
                    forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(
                    forecast_object["max_temp"]) + " Grad Celsius rechen!" + " Durchschnittlich wird es etwa " + str(
                    forecast_object["temp"]) + " Grad Celsius geben!"
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                answer = ""
                if 0 < forecast_object["temp"] < 15:
                    answer = "Am " + formatted_date + " werden Sie werden wärmere Kleidung benötigen, da es etwas kälter draußen ist. " + "Es kann in " + city + " über den Tag verteilt ungefähr mit Temperaturen von mindestens " + str(
                        forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(forecast_object[
                                                                                                 "max_temp"]) + " Grad Celsius gerechnet werden!" + " Durchschnittlich wird es etwa " + str(
                        forecast_object["temp"]) + " Grad Celsius geben!"
                if 0 > forecast_object["temp"]:
                    answer = "Am " + formatted_date + " wird es sehr kalt draußen. Die zu erwartende Temperatur liegt bei unter 0 Grad Celsius!" + "Es kann in " + city + " über den Tag verteilt ungefähr mit Temperaturen von mindestens " + str(
                        forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(forecast_object[
                                                                                                 "max_temp"]) + " Grad Celsius gerechnet werde!" + " Durchschnittlich wird es etwa " + str(
                        forecast_object["temp"]) + " Grad Celsius geben!"
                if 15 <= forecast_object["temp"] < 22:
                    answer = "Am " + formatted_date + " sind milde Temperaturen zu erwarten. " + "In " + city + " wird es über den Tag verteilt ungefähr " + str(
                        forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(
                        forecast_object["max_temp"]) + " Grad Celsius geben!" + " Durchschnittlich wird es etwa " + str(
                        forecast_object["temp"]) + " Grad Celsius geben!"
                if 22 <= forecast_object["temp"] < 30:
                    answer = "Am " + formatted_date + " wird es warm. Eine Jacke benötigt man nicht unbedingt." + " In " + city + " kann über den Tag verteilt ungefähr mit Temperaturen von mindestens " + str(
                        forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(forecast_object[
                                                                                                 "max_temp"]) + " Grad Celsius gerechnet!" + " Durchschnittlich wird es etwa " + str(
                        forecast_object["temp"]) + " Grad Celsius geben!"
                if 30 <= forecast_object["temp"]:
                    answer = "Am " + formatted_date + " wird es sehr warm! Ein T-Shirt reicht auf jeden Fall!" + "In " + city + " kann über den Tag verteilt ungefähr mit Temperaturen von mindestens " + str(
                        forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(forecast_object[
                                                                                                 "max_temp"]) + " Grad Celsius gerechnet werden!" + " Durchschnittlich wird es etwa " + str(
                        forecast_object["temp"]) + " Grad Celsius geben!"
                print(answer)

    def create_temperature_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            answer = "Um " + str(selected_time[0].hour) + " Uhr am " + formatted_date + " kann mit ungefähr " + str(
                forecast_object_time_point["temp"]) + " Grad Celsius gerechnet werden in " + city + "!"
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            answer = "Sie können in " + city + " am " + formatted_date + " über den Tag verteilt ungefähr mit " + str(
                forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(
                forecast_object["max_temp"]) + " Grad Celsius erwarten!" + " Durchschnittlich wird es etwa " + str(
                forecast_object["temp"]) + " Grad Celsius geben!"
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                answer = "Am " + formatted_date + " kann in " + city + " über den Tag verteilt ungefähr mit Temperaturen von mindestens " + str(
                    forecast_object["min_temp"]) + " Grad Celsius bis zu maximal " + str(
                    forecast_object["max_temp"]) + " Grad Celsius rechen!" + " Durchschnittlich wird es etwa " + str(
                    forecast_object["temp"]) + " Grad Celsius geben!"
                print(answer)

    def create_air_pressure_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            answer = "Sie können am " + formatted_date + " um " + str(
                selected_time[0].hour) + " Uhr von einem Luftdruck von " + str(
                forecast_object_time_point["pres"]) + " hPa ausgehen in " + city + "!"
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            answer = "Der Luftdruck wird in " + city + " am " + formatted_date + " bei ungefähr " + str(
                forecast_object["pres"]) + " hPa liegen!"
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                answer = "Am " + formatted_date + " wird der Luftdruck in " + city + " bei ungefähr " + str(
                    forecast_object["pres"]) + " hPa liegen!"
                print(answer)

    def create_weather_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            answer = "Am " + formatted_date + " um " + str(selected_time[0].hour) + " Uhr" + " können Sie mit " + str(
                self.translate_weather_description(forecast_object_time_point["weather"][
                                                       "description"])) + " rechnen in " + city + ". Sie können außerdem mit Temperaturen von " + str(
                forecast_object_time_point["temp"]) + " Grad Celsius ausgehen!"
            print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object = self.get_forecast_object_for_day(selected_time[0], city)
            answer = "Am " + formatted_date + " sollten Sie mit " + str(self.translate_weather_description(
                forecast_object["weather"][
                    "description"])) + " in " + city + " rechnen. Sie können außerdem von " + str(
                forecast_object["max_temp"]) + " Grad Celsius ausgehen!"
            print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                forecast_object = fc
                answer = "Am " + formatted_date + " sollten Sie mit " + str(self.translate_weather_description(
                    forecast_object["weather"][
                        "description"])) + " in " + city + " rechnen. Sie können außerdem von " + str(
                    forecast_object["max_temp"]) + " Grad Celsius ausgehen!"
                print(answer)

    def create_snow_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            if len(re.findall("Snow", forecast_object_time_point["weather"]["description"])) > 0:
                answer = "Es kann mit " + str(self.translate_weather_description(forecast_object_time_point["weather"][
                                                                                     "description"])) + " in " + city + " gerechnet werden! \nEs liegen " + str(
                    forecast_object_time_point["snow_depth"]) + " mm Schnee!"
                print(answer)
            else:
                answer = "Am " + formatted_date + " um " + str(
                    selected_time[0].hour) + " Uhr wird es keinen Schnee geben in " + city + "!\nEs liegen " + str(
                    forecast_object_time_point["snow_depth"]) + " mm Schnee!"
                print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_for_day = self.get_forecast_object_for_day(selected_time[0], city)
            if len(re.findall("Snow", forecast_object_for_day["weather"]["description"])) > 0:
                answer = "Es kann mit " + str(self.translate_weather_description(forecast_object_for_day["weather"][
                                                                                     "description"])) + " gerechnet werden in " + city + " am " + formatted_date + "!\nEs liegen " + str(
                    forecast_object_for_day["snow_depth"]) + " mm Schnee!"
                print(answer)
            else:
                answer = "Am " + formatted_date + " wird es keinen Schnee geben in " + city + "!\nEs liegen " + str(
                    forecast_object_for_day["snow_depth"]) + " mm Schnee!"
                print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                if len(re.findall("Snow", fc["weather"]["description"])) > 0:
                    answer = "Es kann mit " + str(self.translate_weather_description(fc["weather"][
                                                                                         "description"])) + " in " + city + " gerechnet werden am " + formatted_date + " geben!\nEs liegen " + str(
                        fc["snow_depth"]) + " mm Schnee!"
                    print(answer)
                else:
                    answer = "Am " + formatted_date + " wird es keinen Schnee geben in " + city + "!\nEs liegen " + str(
                        fc["snow_depth"]) + " mm Schnee!"
                    print(answer)

    def create_fog_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            if len(re.findall("fog", forecast_object_time_point["weather"]["description"])) > 0:
                answer = "Es kann mit " + str(self.translate_weather_description(
                    forecast_object_time_point["weather"]["description"])) + " in " + city + " gerechnet werden!"
                print(answer)
            else:
                answer = "Am " + formatted_date + " um " + str(
                    selected_time[0].hour) + " Uhr wird es keinen Nebel geben in " + city + "!"
                print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_for_day = self.get_forecast_object_for_day(selected_time[0], city)
            if len(re.findall("fog", forecast_object_for_day["weather"]["description"])) > 0:
                answer = "Es kann mit " + str(self.translate_weather_description(forecast_object_for_day["weather"][
                                                                                     "description"])) + " gerechnet werden in " + city + " am " + formatted_date + "!"
                print(answer)
            else:
                answer = "Am " + formatted_date + " wird es keinen Nebel geben in " + city + "!"
                print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                if len(re.findall("fog", fc["weather"]["description"])) > 0:
                    answer = "Es kann mit " + str(self.translate_weather_description(fc["weather"][
                                                                                         "description"])) + " in " + city + " gerechnet werden am " + formatted_date + " geben!"
                    print(answer)
                else:
                    answer = "Am " + formatted_date + " wird es keinen Nebel geben in " + city + "!"
                    print(answer)

    def create_thunder_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            if len(re.findall("Thunderstorm", forecast_object_time_point["weather"]["description"])) > 0:
                answer = "Es kann mit " + str(self.translate_weather_description(
                    forecast_object_time_point["weather"]["description"])) + " in " + city + " gerechnet werden!"
                print(answer)
            else:
                answer = "Am " + formatted_date + " um " + str(
                    selected_time[0].hour) + " Uhr wird es keinen Sturm/Gewitter geben in " + city + "!"
                print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_for_day = self.get_forecast_object_for_day(selected_time[0], city)
            if len(re.findall("Thunderstorm", forecast_object_for_day["weather"]["description"])) > 0:
                answer = "Es kann mit " + str(self.translate_weather_description(forecast_object_for_day["weather"][
                                                                                     "description"])) + " gerechnet werden in " + city + " am " + formatted_date + "!"
                print(answer)
            else:
                answer = "Am " + formatted_date + " wird es keinen Sturm/Gewitter geben in " + city + "!"
                print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                if len(re.findall("Thunderstorm", fc["weather"]["description"])) > 0:
                    answer = "Es kann mit " + str(self.translate_weather_description(
                        fc["weather"]["description"])) + " in " + city + " gerechnet werden am " + formatted_date + "!"
                    print(answer)
                else:
                    answer = "Am " + formatted_date + " wird es keinen Sturm/Gewitter geben in " + city + "!"
                    print(answer)

    def create_rain_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            if len(re.findall("rain", forecast_object_time_point["weather"]["description"])) > 0:
                answer = "Es kann mit " + str(self.translate_weather_description(
                    forecast_object_time_point["weather"]["description"])) + " gerechnet wrrden in " + city + "!"
                print(answer)
            else:
                answer = "Am " + formatted_date + " um " + str(
                    selected_time[0].hour) + " Uhr wird es keinen Regen geben in " + city + "!"
                print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_for_day = self.get_forecast_object_for_day(selected_time[0], city)
            if len(re.findall("rain", forecast_object_for_day["weather"]["description"])) > 0:
                answer = "Es kann mit " + str(self.translate_weather_description(forecast_object_for_day["weather"][
                                                                                     "description"])) + " gerechnet werden in " + city + " am " + formatted_date + "!"
                print(answer)
            else:
                answer = "Am " + formatted_date + " wird es keinen Regen geben in " + city + "!"
                print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                if len(re.findall("rain", fc["weather"]["description"])) > 0:
                    answer = "Es kann mit " + str(self.translate_weather_description(
                        fc["weather"]["description"])) + " gerechnet werden in " + city + " am " + formatted_date + "!"
                    print(answer)
                else:
                    answer = "Am " + formatted_date + " wird es keinen Regen geben in " + city + "!"
                    print(answer)

    def create_sun_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "day" or selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_for_day = self.get_forecast_object_for_day(selected_time[0], city)
            if forecast_object_for_day["clouds"] < 100:
                answer = "Am " + formatted_date + " kann in " + city + " mit Sonne gerechnet werden!\n"+"\033[95m"+"Hinweis: Informationen zu Sonnenschein können nur zu ganzen Tagen gegeben werden."+"\033[0m"
                print(answer)
            else:
                answer = "Am " + formatted_date + " wird es leider keine Sonne geben in " + city + "!"
                print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                if fc["clouds"] <100 and fc['datetime'].hour > 8 and fc['datetime'].hour < 20:
                    answer = "Am " + formatted_date + " kann in " + city + " mit Sonne gerechnet werden!"
                    print(answer)
                else:
                    answer = "Am " + formatted_date + " wird es leider keine Sonne geben in " + city + "!"
                    print(answer)

    def create_wind_answer(self, city, selected_time, selected_time_type):
        if selected_time_type == "time_point":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_time_point = self.get_forecast_object_for_time_point(selected_time[0], city)
            if forecast_object_time_point["wind_spd"] * 3.6 < 1:
                answer = "Am " + formatted_date + " um " + str(selected_time[
                                                                   0].hour) + " Uhr wird es in " + city + " kaum Wind geben! Die Windgeschwindigkeit liegt bei " + str(
                    "{0:.2f}".format(forecast_object_time_point["wind_spd"] * 3.6)) + " km/h" + " !"
                print(answer)
            if 20 > forecast_object_time_point["wind_spd"] * 3.6 >= 1:
                answer = "Es wird am " + formatted_date + " um " + str(selected_time[
                                                                           0].hour) + " Uhr in " + city + " ein wenig Wind geben! Die Windgeschwindigkeit liegt bei " + str(
                    "{0:.2f}".format(forecast_object_time_point["wind_spd"] * 3.6)) + " km/h" + " !"
                print(answer)
            if 39 > forecast_object_time_point["wind_spd"] * 3.6 >= 20:
                answer = "Es wird am " + formatted_date + " um " + str(selected_time[
                                                                           0].hour) + " Uhr in " + city + " Wind geben (moderat)! Die Windgeschwindigkeit liegt bei " + str(
                    "{0:.2f}".format(forecast_object_time_point["wind_spd"] * 3.6)) + " km/h" + " !"
                print(answer)
            if 39 < forecast_object_time_point["wind_spd"] * 3.6 <= 118:
                answer = "Man kann am " + formatted_date + " um " + str(selected_time[
                                                                            0].hour) + " Uhr in " + city + " mit starkem Wind rechnen! Die Windgeschwindigkeit liegt bei " + str(
                    "{0:.2f}".format(forecast_object_time_point["wind_spd"] * 3.6)) + " km/h" + " !"
                print(answer)
            if forecast_object_time_point["wind_spd"] * 3.6 > 118:
                answer = "Achtung! Bitte passen Sie auf, es wird am " + formatted_date + " um " + str(selected_time[
                                                                                                          0].hour) + " Uhr in " + city + " einen Orkan geben! Die Windgeschwindigkeit liegt bei " + str(
                    "{0:.2f}".format(forecast_object_time_point["wind_spd"] * 3.6)) + " km/h" + " !"
                print(answer)

        if selected_time_type == "day":
            formatted_date = self.convert_date_to_formatted_text(selected_time[0])
            forecast_object_for_day = self.get_forecast_object_for_day(selected_time[0], city)
            if forecast_object_for_day["wind_spd"] * 3.6 < 3:
                answer = "Am " + formatted_date + " um " + str(selected_time[
                                                                   0].hour) + " Uhr wird es in " + city + " kaum Wind geben! Die Windgeschwindigkeit liegt bei " + str(
                    "{0:.2f}".format(forecast_object_for_day["wind_spd"] * 3.6)) + " km/h" + " !"
                print(answer)
            if 20 > forecast_object_for_day["wind_spd"] * 3.6 >= 3:
                answer = "Es wird am " + formatted_date + " in " + city + " ein wenig Wind geben! Die Windgeschwindigkeit liegt bei " + str(
                    "{0:.2f}".format(forecast_object_for_day["wind_spd"] * 3.6)) + " km/h" + " !"
                print(answer)
            if 39 > forecast_object_for_day["wind_spd"] * 3.6 >= 20:
                answer = "Es wird am " + formatted_date + " in " + city + " Wind geben (moderat)! Die Windgeschwindigkeit liegt bei " + str(
                    "{0:.2f}".format(forecast_object_for_day["wind_spd"] * 3.6)) + " km/h" + " !"
                print(answer)
            if 39 < forecast_object_for_day["wind_spd"] * 3.6 <= 118:
                answer = "Man kann am " + formatted_date + " in " + city + " mit starkem Wind rechnen! Die Windgeschwindigkeit liegt bei " + str(
                    "{0:.2f}".format(forecast_object_for_day["wind_spd"] * 3.6)) + " km/h" + " !"
                print(answer)
            if forecast_object_for_day["wind_spd"] * 3.6 > 118:
                answer = "Achtung! Bitte passen Sie auf, es wird am " + formatted_date + " in " + city + " einen Orkan geben! Die Windgeschwindigkeit liegt bei " + str(
                    "{0:.2f}".format(forecast_object_for_day["wind_spd"] * 3.6)) + " km/h" + " !"
                print(answer)

        if selected_time_type == "range":
            forecasts = self.get_forecast_object_for_range(selected_time[0], selected_time[1], city)
            for fc in forecasts:
                formatted_date = self.convert_date_to_formatted_text(fc["datetime"])
                if fc["wind_spd"] * 3.6 < 3:
                    answer = "Am " + formatted_date + " um " + str(selected_time[
                                                                       0].hour) + " Uhr wird es in " + city + " kaum Wind geben! Die Windgeschwindigkeit liegt bei " + str(
                        "{0:.2f}".format(fc["wind_spd"] * 3.6)) + " km/h" + " !"
                    print(answer)
                if 20 > fc["wind_spd"] * 3.6 >= 3:
                    answer = "Am " + formatted_date + " wird es in " + city + " ein wenig Wind geben! Die Windgeschwindigkeit liegt bei " + str(
                        "{0:.2f}".format(fc["wind_spd"] * 3.6)) + " km/h" + " !"
                    print(answer)
                if 39 > fc["wind_spd"] * 3.6 >= 20:
                    answer = "Am " + formatted_date + " wird es in " + city + " Wind geben (moderat)! Die Windgeschwindigkeit liegt bei " + str(
                        "{0:.2f}".format(fc["wind_spd"] * 3.6)) + " km/h" + " !"
                    print(answer)
                if 39 < fc["wind_spd"] * 3.6 <= 118:
                    answer = "Am " + formatted_date + " wird es in " + city + " starken Wind geben! Die Windgeschwindigkeit liegt bei " + str(
                        "{0:.2f}".format(fc["wind_spd"] * 3.6)) + " km/h" + " !"
                    print(answer)
                if fc["wind_spd"] * 3.6 > 118:
                    answer = "Achtung! Bitte passen Sie auf, es wird am " + formatted_date + " in " + city + " einen Orkan geben! Die Windgeschwindigkeit liegt bei " + str(
                        "{0:.2f}".format(fc["wind_spd"] * 3.6)) + " km/h" + " !"
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
        forecasts = forecast.get_series(['clouds', 'precip', "temp", "min_temp", "max_temp", "weather", "pres", "datetime", "wind_dir", "clouds","snow", "wind_spd", "snow_depth"])
        for fc in forecasts:
            if fc["datetime"].year == selected_time.year and fc["datetime"].month == selected_time.month and fc["datetime"].day == selected_time.day:
                return fc

    def get_forecasts_for_next_hours(self, selected_time, city):
        api_key = self.get_api_key()
        api = Api(api_key)
        api.set_granularity('hourly')
        forecast = api.get_forecast(city=city)
        forecasts = forecast.get_series(
            ['clouds', 'precip', "temp", "min_temp", "max_temp", "weather", "pres", "datetime", "wind_dir", "clouds",
             "snow", "wind_spd", "snow_depth"])
        # Filter python objects by requested time
        forecasts = [x for x in forecasts if x['datetime'].year >= selected_time[0].year and x['datetime'].month >= selected_time[0].month and x['datetime'].day >= selected_time[0].day]
        # Filter old time objects (sometimes forecast objects from previous hours are still provided, which are not relevant for the system)
        forecasts = [x for x in forecasts if (x['datetime'] - datetime.timedelta(hours=-1)) > datetime.datetime.now()]
        return forecasts

    def get_forecast_object_for_time_point(self, selected_time, city):
        api_key = self.get_api_key()
        api = Api(api_key)
        api.set_granularity('hourly')
        forecast = api.get_forecast(city=city)
        forecasts = forecast.get_series(
            ['clouds', 'precip', "temp", "min_temp", "max_temp", "weather", "pres", "datetime", "wind_dir", "clouds",
             "snow", "wind_spd", "snow_depth"])
        for fc in forecasts:
            if fc["datetime"].year == selected_time.year and fc["datetime"].month == selected_time.month and fc[
                "datetime"].day == selected_time.day and fc["datetime"].hour == selected_time.hour:
                return fc

    def get_forecast_object_for_range(self, start, end, city):
        api_key = self.get_api_key()
        api = Api(api_key)
        api.set_granularity('daily')
        forecast = api.get_forecast(city=city)
        start_counter = 0
        start_index = 0
        end_counter = 0
        end_index = 0
        forecasts = forecast.get_series(
            ['clouds', 'precip', "temp", "min_temp", "max_temp", "weather", "pres", "datetime", "wind_dir", "clouds",
             "snow", "wind_spd", "snow_depth"])
        for fc in forecasts:
            if fc["datetime"].year == start.year and fc["datetime"].month == start.month and fc[
                "datetime"].day == start.day:
                start_index = start_counter
            start_counter = start_counter + 1
        for fc in forecasts:
            if fc["datetime"].year == end.year and fc["datetime"].month == end.month and fc["datetime"].day == end.day:
                end_index = end_counter
            end_counter = end_counter + 1
        forecasts_return = []
        for i in range(start_index, end_index + 1):
            forecasts_return.append(forecasts[i])
        return forecasts_return

    def convert_date_to_formatted_text(self, selected_time):
        months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober",
                  "November", "Dezember"]
        month_index = selected_time.month - 1
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        is_tomorrow = ""
        if selected_time.year == tomorrow.year and selected_time.month == tomorrow.month and selected_time.day == tomorrow.day:
            is_tomorrow = " (morgen)"
        return str(selected_time.day) + ". " + months[month_index] + " " + str(selected_time.year) + is_tomorrow

    def translate_weather_description(self, text):
        # The API with the weather data provides the descriptions of the weather in English.
        # Therefore we translate them into German first.
        english_descriptions = ["Thunderstorm with light rain", "Thunderstorm with rain",
                                "Thunderstorm with heavy rain", "Thunderstorm with light drizzle",
                                "Thunderstorm with drizzle", "Thunderstorm with heavy drizzle",
                                "Thunderstorm with hail", "Light drizzle", "Drizzle", "Heavy drizzle", "Light rain",
                                "Moderate rain", "Heavy rain", "Freezing rain", "Light shower rain", "Shower rain",
                                "Heavy shower rain", "Light snow", "Snow", "Heavy snow", "Mix snow/rain", "Sleet",
                                "Heavy sleet", "Snow shower", "Heavy snow shower", "Flurries", "Mist", "Smoke", "Haze",
                                "Sand/dust", "Fog", "Freezing fog", "Clear Sky", "Few clouds", "Scattered clouds",
                                "Broken clouds", "Overcast clouds", "Unknown precipitation"]
        german_descriptions = ["Gewitter und leichtem Regen", "Gewitter und Regen", "Gewitter und starkem Regen",
                               "Gewitter mit leichtem Nieselregen", "Gewitter mit Nieselregen",
                               "Gewitter mit starkem Nieselregen", "Gewitter mit Hagel", "leichtem Nieselregen",
                               "Nieselregen", "starkem Nieselregen", "leichtem Regen", "mäßigem Regen", "starkem Regen",
                               "Eisregen", "leichtem Schauerregen", "Schauerregen", "starkem Schauerregen",
                               "leichtem Schnee", "Schnee", "starkem Schnee", "Schnee und Regen mischen", "Graupel",
                               "starkem Graupel", "Schneeschauer", "starkem Schneeschauer", "Schauer", "Nebel", "Rauch",
                               "Dunst", "Sand/Staub", "Nebel", "gefrierendem Nebel", "klarem Himmel", "wenigen Wolken",
                               "verstreuten Wolken", "zerbrochenen Wolken", "bedeckten Wolken",
                               "unbekannter Niederschlag"]
        counter = 0
        for decription in english_descriptions:
            if text == decription:
                return german_descriptions[counter]
            counter = counter + 1


weather_api_handler = WeatherAPIHandler()
