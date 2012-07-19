#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# This process of enhancing plugins has been performed by Twisted.
#
# Unmerged versions of these plugins may function differently or lack some modification.
# All original headers and licensing information are labeled by the derived plugin name.
#
# Weather / Time Plugin  
# created by Eichhoernchen
#
# It uses various the services from yahoo
#
#
# This file is free for private use, you need a commercial license for paid servers
#
# It's distributed under the same license as SiriServerCore
#
# You can view the license here:
# https://github.com/Eichhoernchen/SiriServerCore/blob/master/LICENSE
#
# So if you have a SiriServerCore commercial license 
# you are allowed to use this plugin commercially otherwise you are breaking the law
#
# You must make sure to get propper allowens from yahoo to use their API commercially
#
# This file can be freely modified, but this header must retain untouched
#
# Combo Enhancement
# integrated by Twisted
#
# Places the weather and time into a single view, with
# extra introduction speech to inlude temperature info
#

import random
import urllib
import urllib2
import json
import random
import types
import os
import locale
import re
import time, datetime
import urllib2, urllib
import logging
from time import gmtime, strftime
from uuid import uuid4
from plugin import *
from fractions import Fraction
from datetime import date
from plugin import *
from siriObjects.weatherObjects import WeatherHourlyForecast, \
    WeatherCurrentConditions, WeatherCondition, WeatherUnits, \
    WeatherBarometricPressure, WeatherWindSpeed, WeatherDailyForecast, \
    WeatherForecast, WeatherObject, WeatherLocation, WeatherForecastSnippet
from xml.etree import ElementTree
from siriObjects.clockObjects import ClockSnippet, ClockObject
from siriObjects.baseObjects import AceObject, ClientBoundCommand
from siriObjects.uiObjects import AddViews, AssistantUtteranceView

localizations = {
    "search":
    {
      "de-DE": [u"Es wird gesucht ..."], 
      "en-US": [u"Looking up ..."]
    },                  
    "currentTime": 
    {
     "de-DE": [u"Es ist @{fn#currentTime}"], 
     "en-US": [u"It is currently @{fn#currentTime}"]
    }, 
    "currentTimeIn": 
    {
      "de-DE": [u"Die Uhrzeit in {0} ist @{{fn#currentTimeIn#{1}}}:"], 
      "en-US": [u"The time in {0} is @{{fn#currentTimeIn#{1}}}:"]
    },
    "failure":
    {
      "de-DE": [u"Es tut mir leid aber für eine Anfrage habe ich keine Uhrzeit."],
      "en-US": [u"I'm sorry but I don't have a time for this request"]
    }
}

appleWeek = {
'Sun': 1,
'Mon': 2,
'Tue': 3,
'Wed': 4,
'Thu': 5,
'Fri': 6,
'Sat': 7
}

countries = {
    "af": "Afghanistan",
    "al": "Albania",
    "dz": "Algeria",
    "as": "American Samoa",
    "ad": "Andorra",
    "ao": "Angola",
    "ai": "Anguilla",
    "aq": "Antarctica",
    "ag": "Antigua and Barbuda",
    "ar": "Argentina",
    "am": "Armenia",
    "aw": "Aruba",
    "au": "Australia",
    "at": "Austria",
    "az": "Azerbaijan",
    "bs": "Bahamas",
    "bh": "Bahrain",
    "bd": "Bangladesh",
    "bb": "Barbados",
    "by": "Belarus",
    "be": "Belgium",
    "bz": "Belize",
    "bj": "Benin",
    "bm": "Bermuda",
    "bt": "Bhutan",
    "bo": "Bolivia",
    "ba": "Bosnia and Herzegowina",
    "bw": "Botswana",
    "bv": "Bouvet Island",
    "br": "Brazil",
    "io": "British Indian Ocean Territory",
    "bn": "Brunei Darussalam",
    "bg": "Bulgaria",
    "bf": "Burkina Faso",
    "bi": "Burundi",
    "kh": "Cambodia",
    "cm": "Cameroon",
    "ca": "Canada",
    "cv": "Cape Verde",
    "ky": "Cayman Islands",
    "cf": "Central African Republic",
    "td": "Chad",
    "cl": "Chile",
    "cn": "China",
    "cx": "Christmas Island",
    "cc": "Cocos (Keeling) Islands",
    "co": "Colombia",
    "km": "Comoros",
    "cg": "Congo",
    "cd": "Congo, The Democratic Republic of the",
    "ck": "Cook Islands",
    "cr": "Costa Rica",
    "ci": "Cote D'Ivoire",
    "hr": "Croatia (local name: Hrvatska)",
    "cu": "Cuba",
    "cy": "Cyprus",
    "cz": "Czech Republic",
    "dk": "Denmark",
    "dj": "Djibouti",
    "dm": "Dominica",
    "do": "Dominican Republic",
    "tp": "East Timor",
    "ec": "Ecuador",
    "eg": "Egypt",
    "sv": "El Salvador",
    "gq": "Equatorial Guinea",
    "er": "Eritrea",
    "ee": "Estonia",
    "et": "Ethiopia",
    "fk": "Falkland Islands (Malvinas)",
    "fo": "Faroe Islands",
    "fj": "Fiji",
    "fi": "Finland",
    "fr": "France",
    "fx": "France, metropolitan",
    "gf": "French Guiana",
    "pf": "French Polynesia",
    "tf": "French Southern Territories",
    "ga": "Gabon",
    "gm": "Gambia",
    "ge": "Georgia",
    "de": "Germany",
    "gh": "Ghana",
    "gi": "Gibraltar",
    "gr": "Greece",
    "gl": "Greenland",
    "gd": "Grenada",
    "gp": "Guadeloupe",
    "gu": "Guam",
    "gt": "Guatemala",
    "gn": "Guinea",
    "gw": "Guinea-Bissau",
    "gy": "Guyana",
    "ht": "Haiti",
    "hm": "Heard and Mc Donald Islands",
    "va": "Holy See (Vatican City State)",
    "hn": "Honduras",
    "hk": "Hong Kong",
    "hu": "Hungary",
    "is": "Iceland",
    "in": "India",
    "id": "Indonesia",
    "ir": "Iran (Islamic Republic of)",
    "iq": "Iraq",
    "ie": "Ireland",
    "il": "Israel",
    "it": "Italy",
    "jm": "Jamaica",
    "jp": "Japan",
    "jo": "Jordan",
    "kz": "Kazakhstan",
    "ke": "Kenya",
    "ki": "Kiribati",
    "kp": "Korea, Democratic People's Republic of",
    "kr": "Korea, Republic of",
    "kw": "Kuwait",
    "kg": "Kyrgyzstan",
    "la": "Lao People's Democratic Republic",
    "lv": "Latvia",
    "lb": "Lebanon",
    "ls": "Lesotho",
    "lr": "Liberia",
    "ly": "Libyan Arab Jamahiriya",
    "li": "Liechtenstein",
    "lt": "Lithuania",
    "lu": "Luxembourg",
    "mo": "Macau",
    "mk": "Macedonia, The Former Yugoslav Republic of",
    "mg": "Madagascar",
    "mw": "Malawi",
    "my": "Malaysia",
    "mv": "Maldives",
    "ml": "Mali",
    "mt": "Malta",
    "mh": "Marshall Islands",
    "mq": "Martinique",
    "mr": "Mauritania",
    "mu": "Mauritius",
    "yt": "Mayotte",
    "mx": "Mexico",
    "fm": "Micronesia, Federated States of",
    "md": "Moldova, Republic of",
    "mc": "Monaco",
    "mn": "Mongolia",
    "ms": "Montserrat",
    "ma": "Morocco",
    "mz": "Mozambique",
    "mm": "Myanmar",
    "na": "Namibia",
    "nr": "Nauru",
    "np": "Nepal",
    "nl": "Netherlands",
    "an": "Netherlands Antilles",
    "nc": "New Caledonia",
    "nz": "New Zealand",
    "ni": "Nicaragua",
    "ne": "Niger",
    "ng": "Nigeria",
    "nu": "Niue",
    "nf": "Norfolk Island",
    "mp": "Northern Mariana Islands",
    "no": "Norway",
    "om": "Oman",
    "pk": "Pakistan",
    "pw": "Palau",
    "pa": "Panama",
    "pg": "Papua New Guinea",
    "py": "Paraguay",
    "pe": "Peru",
    "ph": "Philippines",
    "pn": "Pitcairn",
    "pl": "Poland",
    "pt": "Portugal",
    "pr": "Puerto Rico",
    "qa": "Qatar",
    "re": "Reunion",
    "ro": "Romania",
    "ru": "Russian Federation",
    "rw": "Rwanda",
    "kn": "Saint Kitts and Nevis",
    "lc": "Saint Lucia",
    "vc": "Saint Vincent and the Grenadines",
    "ws": "Samoa",
    "sm": "San Marino",
    "st": "Sao Tome and Principe",
    "sa": "Saudi Arabia",
    "sn": "Senegal",
    "sc": "Seychelles",
    "sl": "Sierra Leone",
    "sg": "Singapore",
    "sk": "Slovakia (Slovak Republic)",
    "si": "Slovenia",
    "sb": "Solomon Islands",
    "so": "Somalia",
    "za": "South Africa",
    "gs": "South Georgia and the South Sandwich Islands",
    "es": "Spain",
    "lk": "Sri Lanka",
    "sh": "St. Helena",
    "pm": "St. Pierre and Miquelon",
    "sd": "Sudan",
    "sr": "Suriname",
    "sj": "Svalbard and Jan Mayen Islands",
    "sz": "Swaziland",
    "se": "Sweden",
    "ch": "Switzerland",
    "sy": "Syrian Arab Republic",
    "tw": "Taiwan, Province of China",
    "tj": "Tajikistan",
    "tz": "Tanzania, United Republic of",
    "th": "Thailand",
    "tg": "Togo",
    "tk": "Tokelau",
    "to": "Tonga",
    "tt": "Trinidad and Tobago",
    "tn": "Tunisia",
    "tr": "Turkey",
    "tm": "Turkmenistan",
    "tc": "Turks and Caicos Islands",
    "tv": "Tuvalu",
    "ug": "Uganda",
    "ua": "Ukraine",
    "ae": "United Arab Emirates",
    "gb": "United Kingdom",
    "us": "United States",
    "um": "United States Minor Outlying Islands",
    "uy": "Uruguay",
    "uz": "Uzbekistan",
    "vu": "Vanuatu",
    "ve": "Venezuela",
    "vn": "Viet Nam",
    "vg": "Virgin Islands (British)",
    "vi": "Virgin Islands (U.S.)",
    "wf": "Wallis and Futuna Islands",
    "eh": "Western Sahara",
    "ye": "Yemen",
    "yu": "Yugoslavia",
    "zm": "Zambia",
    "zw": "Zimbabwe",
    }

waitText = {
    'de-DE': [u"Einen Moment bitte", u"OK"],
    'en-US': [u"One moment please", u"Let me check"]
}

errorText = {
    'de-DE': [u"Entschuldigung aber zur Zeit ist die Funktion nicht verfügbar."],
    'en-US': [u"Sorry this is not available right now."]
}

noDataForLocationText = {
    'de-DE': [u"Entschuldigung aber für ihren Standort finde ich keine Daten."],
    'en-US': [u"Sorry, I cannot find any data for your location."]
}

dailyForcast = {
    'de-DE': [u"Hier ist die Vorhersage für {0}, {1}."],
    'en-US': [u"Here is the visual forecast for {0}, {1}."]
}

yweather = "{http://xml.weather.yahoo.com/ns/rss/1.0}"
geo = "{http://www.w3.org/2003/01/geo/wgs84_pos#}"
place = "{http://where.yahooapis.com/v1/schema.rng}"

idFinder = re.compile("/(?P<locationID>[A-z0-9_]+).html")

class yahooWeather(Plugin):

    def showWait(self, language):
        textView = UIAssistantUtteranceView()
        textView.speakableText = textView.text = random.choice(localizations['search'][language])
        textView.dialogIdentifier = "Clock#getTime"

        rootAnchor = UIAddViews(self.refId)
        rootAnchor.dialogPhase = rootAnchor.DialogPhaseReflectionValue
        rootAnchor.scrollToTop = False
        rootAnchor.temporary = False
        rootAnchor.views = [textView]  
        
        self.sendRequestWithoutAnswer(rootAnchor)

    @register("de-DE", "(Wie ?viel Uhr.*)|(.*Uhrzeit.*)")     
    @register("en-US", "(What.*time.*)|(.*current time.*)")
    def currentTime(self, speech, language):
        #first tell that we look it up
        self.showWait(language)
        
        
        textView = UIAssistantUtteranceView()
        textView.text = textView.speakableText = random.choice(localizations["currentTime"][language]) + "."
        textView.dialogIdentifier = "Clock#showTimeInCurrentLocation"
        textView.listenAfterSpeaking = False
        
        clock = ClockObject()
        clock.timezoneId = self.connection.assistant.timeZoneId
        
        clockView = ClockSnippet()
        clockView.clocks = [clock]
        
        rootAnchor = UIAddViews(self.refId)
        rootAnchor.dialogPhase = rootAnchor.DialogPhaseSummaryValue
        rootAnchor.views = [textView, clockView]
        
        
        self.sendRequestWithoutAnswer(rootAnchor)
        self.complete_request()

    def getNameFromGoogle(request):
        try:
            result = getWebsite(request, timeout=5)
            root = json.loads(result)
            location = root["results"][0]["formatted_address"]
            return location
        except:
            return None
    
    @register("de-DE", "(Wieviel Uhr.*in|Uhrzeit.*in) (?P<loc>[\w ]+)")
    @register("en-US", "(What.*time.*|.*current time.*)(in|for) (?P<loc>[\w ]+)")
    def currentTimeIn(self, speech, language, matchedRegex):
        
        self.showWait(language)
        
        location = matchedRegex.group("loc")
        # ask google to enhance the request
        googleGuesser = "http://maps.googleapis.com/maps/api/geocode/json?address={0}&sensor=false&language={1}".format(urllib.quote(location.encode("utf-8")), language)
        googleLocation = getNameFromGoogle(googleGuesser)
        if googleLocation != None:
            location = googleLocation
        
        self.logger.debug(u"User requested time in: {0}".format(location))
        # ask yahoo for a timezoneID
        query = u"select name from geo.places.belongtos where member_woeid in (select woeid from geo.places where text=\"{0}\") and placetype=31".format(location.encode("utf-8"))
        request = u"http://query.yahooapis.com/v1/public/yql?q={0}&format=json&callback=".format(urllib.quote(query.encode("utf-8")))
        timeZoneId = None
        try:
            result = getWebsite(request, timeout=5)
            root = json.loads(result)
            place = root["query"]["results"]["place"]
            if type(place) == types.ListType:
                place = place[0]
            
            timeZoneId = place["name"]
        except:
            self.logger.exception("Error getting timezone")
        
        if timeZoneId == None:
            self.say(random.choice(localizations['failure'][language]))
            self.complete_request()
            return
        
        clock = ClockObject()
        clock.timezoneId = timeZoneId
        
        clockView = ClockSnippet()
        clockView.clocks = [clock]
        
        textView = UIAssistantUtteranceView()
        textView.listenAfterSpeaking = False
        textView.dialogIdentifier = "Clock#showTimeInOtherLocation"
        textView.text = textView.speakableText = random.choice(localizations["currentTimeIn"][language]).format(location, timeZoneId) + "."
        
        rootAnchor = UIAddViews(self.refId)
        rootAnchor.dialogPhase = rootAnchor.DialogPhaseSummaryValue
        rootAnchor.scrollToTop = False
        rootAnchor.temporary = False
        rootAnchor.views = [textView, clockView]
        
        self.sendRequestWithoutAnswer(rootAnchor)
        self.complete_request()

## we should implement such a command if we cannot get the location however some structures are not implemented yet
#{"class"=>"AddViews",
#    "properties"=>
#        {"temporary"=>false,
#            "dialogPhase"=>"Summary",
#            "scrollToTop"=>false,
#            "views"=>
#                [{"class"=>"AssistantUtteranceView",
#                 "properties"=>
#                 {"dialogIdentifier"=>"Common#unresolvedExplicitLocation",
#                 "speakableText"=>
#                 "Ich weiß leider nicht, wo das ist. Wenn du möchtest, kann ich im Internet danach suchen.",
#                 "text"=>
#                 "Ich weiß leider nicht, wo das ist. Wenn du möchtest, kann ich im Internet danach suchen."},
#                 "group"=>"com.apple.ace.assistant"},
#                 {"class"=>"Button",
#                 "properties"=>
#                 {"commands"=>
#                 [{"class"=>"SendCommands",
#                  "properties"=>
#                  {"commands"=>
#                  [{"class"=>"StartRequest",
#                   "properties"=>
#                   {"handsFree"=>false,
#                   "utterance"=>
#                   "^webSearchQuery^=^Amerika^^webSearchConfirmation^=^Ja^"},
#                   "group"=>"com.apple.ace.system"}]},
#                  "group"=>"com.apple.ace.system"}],
#                 "text"=>"Websuche"},
#                 "group"=>"com.apple.ace.assistant"}]},
#    "aceId"=>"fbec8e13-5781-4b27-8c36-e43ec922dda3",
#    "refId"=>"702C0671-DB6F-4914-AACD-30E84F7F7DF3",
#    "group"=>"com.apple.ace.assistant"}
    
    def __init__(self):
        super(yahooWeather, self).__init__()
        self.loopcounter = 0
    
    
    def showWaitPlease(self, language):
        rootAnchor = UIAddViews(self.refId)
        rootAnchor.dialogPhase = rootAnchor.DialogPhaseReflectionValue
        
        waitView = UIAssistantUtteranceView()
        waitView.text = waitView.speakableText = random.choice(waitText[language])
        waitView.listenAfterSpeaking = False
        waitView.dialogIdentifier = "Misc#ident" # <- what is the correct one for this?
        
        rootAnchor.views = [waitView]
        
        self.sendRequestWithoutAnswer(rootAnchor)
    
    
    def getWeatherLocation(self, locationId, xml):
        item = xml.find("channel/item")
        location = xml.find("channel/{0}location".format(yweather))
        
        weatherLocation = WeatherLocation()
        if location is None:
            return weatherLocation
        
        weatherLocation.city = location.get("city")
        weatherLocation.countryCode = location.get("country")
        weatherLocation.latitude = item.find("{0}lat".format(geo)).text
        weatherLocation.longitude = item.find("{0}long".format(geo)).text
        weatherLocation.locationId = locationId
        weatherLocation.stateCode = location.get("region")
        weatherLocation.accuracy = weatherLocation.AccuracyBestValue
        return weatherLocation
    
    def getWeatherUnits(self, xml):
        units = xml.find("channel/{0}units".format(yweather))
        
        weatherUnits = WeatherUnits()
        if units is None:
            return weatherUnits
        
        ydistance = units.get("distance")
        if ydistance == "mi":
            weatherUnits.distanceUnits = weatherUnits.DistanceUnitsMilesValue
        elif ydistance == "km":
            weatherUnits.distanceUnits = weatherUnits.DistanceUnitsKilometersValue
        elif ydistance == "m":
            weatherUnits.distanceUnits = weatherUnits.DistanceUnitsMetersValue
        elif ydistance == "ft":
            weatherUnits.distanceUnits = weatherUnits.DistanceUnitsFeetValue
            
        ypressure = units.get("pressure")
        if ypressure == "mb":
            weatherUnits.pressureUnits = weatherUnits.PressureUnitsMBValue
        elif ypressure == "in":
            weatherUnits.pressureUnits = weatherUnits.PressureUnitsINValue
            
        yspeed = units.get("speed")
        if yspeed == "km/h":
            weatherUnits.speedUnits = weatherUnits.SpeedUnitsKPHValue
        elif yspeed == "mph":
            weatherUnits.speedUnits = weatherUnits.SpeedUnitsMPHValue
            
        ytemp = units.get("temperature")
        if ytemp == "F":
            weatherUnits.temperatureUnits = weatherUnits.TemperatureUnitsFahrenheitValue
        elif ytemp == "C":
            weatherUnits.temperatureUnits = weatherUnits.TemperatureUnitsCelsiusValue
        
        return weatherUnits
    
    def getWeatherBarometrics(self, xml):
        barometric = xml.find("channel/{0}atmosphere".format(yweather))
        
        weatherBaro = WeatherBarometricPressure()
        if barometric is None:
            return weatherBaro
        
        yrising = barometric.get("rising")
        if yrising == "0":
            weatherBaro.trend = weatherBaro.TrendSteadyValue
        elif yrising == "1":
            weatherBaro.trend = weatherBaro.TrendRisingValue
        elif yrising == "2":
            weatherBaro.trend = weatherBaro.TrendFallingValue
        weatherBaro.value = barometric.get("pressure")
        
        return weatherBaro
    
    
    def getWeatherWind(self, xml):
        wind = xml.find("channel/{0}wind".format(yweather))
        weatherWind = WeatherWindSpeed()
        if wind is None:
            return weatherWind
        
        weatherWind.value = wind.get("speed")
        weatherWind.windDirectionDegree = int(wind.get("direction"))
        
        # north is 0 make intervals from -22.5,+22.5 results in 45 interval for each direction
        if weatherWind.windDirectionDegree >= 337.5 and weatherWind.windDirectionDegree <= 22.5:
            weatherWind.windDirection = weatherWind.DirectionNorthValue
        elif weatherWind.windDirectionDegree >= 22.5 and weatherWind.windDirectionDegree <= 67.5:
            weatherWind.windDirection = weatherWind.DirectionNorthEastValue
        elif weatherWind.windDirectionDegree >= 67.5 and weatherWind.windDirectionDegree <= 112.5:
            weatherWind.windDirection = weatherWind.DirectionEastValue
        elif weatherWind.windDirectionDegree >= 112.5 and weatherWind.windDirectionDegree <= 157.5:
            weatherWind.windDirection = weatherWind.DirectionSouthEastValue
        elif weatherWind.windDirectionDegree >= 157.5 and weatherWind.windDirectionDegree <= 202.5:
            weatherWind.windDirection = weatherWind.DirectionSouthValue
        elif weatherWind.windDirectionDegree >= 202.5 and weatherWind.windDirectionDegree <= 247.5:
            weatherWind.windDirection = weatherWind.DirectionSouthWestValue
        elif weatherWind.windDirectionDegree >= 247.5 and weatherWind.windDirectionDegree <= 292.5:
            weatherWind.windDirection = weatherWind.DirectionWestValue
        elif weatherWind.windDirectionDegree >= 292.5 and weatherWind.windDirectionDegree <= 337.5:
            weatherWind.windDirection = weatherWind.DirectionNorthWestValue
        return weatherWind
    
    def getWeatherCurrentConditions(self, xml):
        item = xml.find("channel/item")
        wind = xml.find("channel/{0}wind".format(yweather))
        barometric = xml.find("channel/{0}atmosphere".format(yweather))
        astronomy = xml.find("channel/{0}astronomy".format(yweather))
        currentCondition = item.find("{0}condition".format(yweather))
        
        if currentCondition is None:
            return None
        weatherCondition = WeatherCondition()
        weatherCondition.conditionCodeIndex = int(currentCondition.get("code"))
        weatherCondition.conditionCode = weatherCondition.ConditionCodeIndexTable[weatherCondition.conditionCodeIndex]
        
        current = WeatherCurrentConditions()
        current.dayOfWeek = currentCondition.get("date").split(",")[0]
        current.temperature = currentCondition.get("temp")
        current.barometricPressure = self.getWeatherBarometrics(xml)
        current.condition = weatherCondition
        current.percentHumidity = barometric.get("humidity")
        current.sunrise = astronomy.get("sunrise")
        current.sunset = astronomy.get("sunset")
        current.temperature = currentCondition.get("temp")
        current.timeOfObservation = xml.find("channel/lastBuildDate").text
        current.visibility = barometric.get("visibility")
        current.windChill = wind.get("chill")
        current.windSpeed = self.getWeatherWind(xml)
        return current
        

    def showCurrentWeatherWithWOEID(self, language, woeid, metric = True):
        # we can only get 2 day weather with woeid that suxx
        weatherLookup = "http://weather.yahooapis.com/forecastrss?w={0}&u={1}".format(woeid, "c" if metric else "f")
        result = getWebsite(weatherLookup, timeout=5)
        if result == None:
            self.say(random.choice(errorText[language]))
            self.complete_request()
            return
        
        result = ElementTree.XML(result)
        
        #get the item
        item = result.find("channel/item")
        if item is None:
            self.say(random.choice(noDataForLocationText[language]))
            self.complete_request()
            return
        
        # they change the language code using the other forecast link..
        weatherLocation = None
        
        match = idFinder.search(item.find("link").text)
        if match != None:
            loc = match.group('locationID')
            weatherLocation = self.getWeatherLocation(loc[:-2], result)
            fiveDayForecast = "http://xml.weather.yahoo.com/forecastrss/{0}_{1}.xml".format(loc, "c" if metric else "f")
            
            
            try:
                result = self.getWebsite(fiveDayForecast, timeout=5)
                result = ElementTree.XML(result)
                item = result.find("channel/item")
            except:
                pass
        
        if weatherLocation == None:
            weatherLocation = self.getWeatherLocation(woeid, result)
        
        if item is None:
            self.say(random.choice(noDataForLocationText[language]))
            self.complete_request()
            return
        
        forecast = WeatherObject()
        forecast.currentConditions = self.getWeatherCurrentConditions(result)
        if forecast.currentConditions == None:
            self.say(random.choice(noDataForLocationText[language]))
            self.complete_request()
            return
        
        forecast.extendedForecastUrl = item.find("link").text
        forecast.units = self.getWeatherUnits(result)
        forecast.view = forecast.ViewDAILYValue
        forecast.weatherLocation = weatherLocation
        forecast.hourlyForecasts = []
        
        dailyForecasts = []
        for dailyForecast in result.findall("channel/item/{0}forecast".format(yweather)):
            weatherDaily = WeatherDailyForecast()
            weatherDaily.timeIndex = appleWeek[dailyForecast.get("day")]
            weatherDaily.lowTemperature = int(dailyForecast.get("low"))
            weatherDaily.highTemperature = int(dailyForecast.get("high"))
            weatherDaily.isUserRequested = True
            dailyCondition = WeatherCondition()
            dailyCondition.conditionCodeIndex = int(dailyForecast.get("code"))
            dailyCondition.conditionCode = dailyCondition.ConditionCodeIndexTable[dailyCondition.conditionCodeIndex]
            weatherDaily.condition = dailyCondition
            dailyForecasts.append(weatherDaily)
    
        forecast.dailyForecasts = dailyForecasts
        snippet = WeatherForecastSnippet()
        snippet.aceWeathers = [forecast]
        
        showViewsCMD = UIAddViews(self.refId)
        showViewsCMD.dialogPhase = showViewsCMD.DialogPhaseSummaryValue
        displaySnippetTalk = UIAssistantUtteranceView()
        displaySnippetTalk.dialogIdentifier = "Weather#forecastCommentary"
        
        countryName = countries[forecast.weatherLocation.countryCode.lower()] if forecast.weatherLocation.countryCode.lower() in countries else forecast.weatherLocation.countryCode
        displaySnippetTalk.text = displaySnippetTalk.speakableText = random.choice(dailyForcast[language]).format(forecast.weatherLocation.city, countryName)
        self.say("It is currently {0} degrees {1} with a humidity of {2}%.".format(forecast.currentConditions.temperature, forecast.units.temperatureUnits, forecast.currentConditions.percentHumidity))
        
        showViewsCMD.views = [displaySnippetTalk, snippet]
        
        self.sendRequestWithoutAnswer(showViewsCMD)
        self.complete_request()
        
    def getNameFromGoogle(self, request):
        try:
            result = getWebsite(request, timeout=5)
            root = ElementTree.XML(result)
            location = root.find("result/formatted_address")
            location = location.text
            return location
        except:
            return None
    
    @register("en-US", "(what|how).*weather.*(in|around|near|for|at) (?P<location>[\w ]+?)$")
    @register('de-DE', "(wie ist das )?wetter in (?P<location>[\w ]+?)$")
    def forcastWeatherAtLocation(self, speech, language, regex):
        self.showWaitPlease(language)
        location = regex.group("location")
        # lets refine the location using google
        googleGuesser = "http://maps.googleapis.com/maps/api/geocode/xml?address={0}&sensor=false&language={1}".format(urllib.quote(location.encode("utf-8")), language)
        googleLocation = self.getNameFromGoogle(googleGuesser)
        if googleLocation != None:
            location = googleLocation
            
        query = u"select woeid, placeTypeName from geo.places where text=\"{0}\" limit 1".format(location)
        lookup = u"http://query.yahooapis.com/v1/public/yql?q={0}&format=xml".format(urllib.quote(query.encode("utf-8")))
        #lookup = "http://where.yahooapis.com/geocode?location={0}&appid={1}".format(urllib.quote(location.encode("utf-8")), yahooAPIkey)
        
        result = getWebsite(lookup, timeout=5)
        if result == None:
            self.say(random.choice(errorText[language]))
            self.complete_request()
            return
        
        root = ElementTree.XML(result)
        placeTypeCode = root.find("results/{0}place/{0}placeTypeName".format(place))
        woeidElem = root.find("results/{0}place/{0}woeid".format(place))
        
        if woeidElem is None or placeTypeCode is None:
            self.say(random.choice(noDataForLocationText[language]))
            self.complete_request()
            return
        
        if placeTypeCode.get("code") != "7": #damn is this not a city
            # lets ask google what it think
            googleCapitalResolver = "http://maps.googleapis.com/maps/api/geocode/xml?address=capital%20of%20{0}&sensor=false&language={1}".format(urllib.quote(location.encode("utf-8")), language)
            location = self.getNameFromGoogle(googleCapitalResolver)
            if location != None and self.loopcounter < 2:
                x = re.match("(?P<location>.*)", location)
                # ok we should now have more details, lets call our self
                self.loopcounter += 1
                self.forcastWeatherAtLocation(speech, language, x)
                return
            else:
                self.say(random.choice(errorText[language]))
                self.complete_request()
                return
        
        self.showCurrentWeatherWithWOEID(language, woeidElem.text)
        
    @register("en-US", "(what|how).*(weather|forecast).*")
    @register("de-DE", "wetter(vorhersage)?")
    def forcastWeatherAtCurrentLocation(self, speech, language):
        location = self.getCurrentLocation()
        self.showWaitPlease(language)
        
        lng = location.longitude
        lat = location.latitude
        
        # we need the corresponding WOEID to the location
        query = "select woeid from geo.places where text=\"{0},{1}\"".format(lat,lng)
        reverseLookup = "http://query.yahooapis.com/v1/public/yql?q={0}&format=xml".format(urllib.quote(query.encode("utf-8")))
        #reverseLookup = "http://where.yahooapis.com/geocode?location={0},{1}&gflags=R&appid={2}".format(lat, lng, yahooAPIkey)
        result = getWebsite(reverseLookup, timeout=5)
        if result == None:
            self.say(random.choice(errorText[language]))
            self.complete_request()
            return
        
        root = ElementTree.XML(result)
        woeidElem = root.find("results/{0}place/{0}woeid".format(place))
    
        
        if woeidElem is None:
            self.say(random.choice(noDataForLocationText[language]))
            self.complete_request()
            return
        
        self.showCurrentWeatherWithWOEID(language, woeidElem.text)

    def showCurrentWeatherWithTime(self, language, woeid, metric = True):
        # we can only get 2 day weather with woeid that suxx
        weatherLookup = "http://weather.yahooapis.com/forecastrss?w={0}&u={1}".format(woeid, "c" if metric else "f")
        result = getWebsite(weatherLookup, timeout=5)
        if result == None:
            self.say(random.choice(errorText[language]))
            self.complete_request()
            return
        
        result = ElementTree.XML(result)
        
        #get the item
        item = result.find("channel/item")
        if item is None:
            self.say(random.choice(noDataForLocationText[language]))
            self.complete_request()
            return
        
        # they change the language code using the other forecast link..
        weatherLocation = None
        
        match = idFinder.search(item.find("link").text)
        if match != None:
            loc = match.group('locationID')
            weatherLocation = self.getWeatherLocation(loc[:-2], result)
            fiveDayForecast = "http://xml.weather.yahoo.com/forecastrss/{0}_{1}.xml".format(loc, "c" if metric else "f")
            
            try:
                result = self.getWebsite(fiveDayForecast, timeout=5)
                result = ElementTree.XML(result)
                item = result.find("channel/item")
            except:
                pass
        
        if weatherLocation == None:
            weatherLocation = self.getWeatherLocation(woeid, result)
        
        if item is None:
            self.say(random.choice(noDataForLocationText[language]))
            self.complete_request()
            return
        
        forecast = WeatherObject()
        forecast.currentConditions = self.getWeatherCurrentConditions(result)
        if forecast.currentConditions == None:
            self.say(random.choice(noDataForLocationText[language]))
            self.complete_request()
            return
        
        forecast.extendedForecastUrl = item.find("link").text
        forecast.units = self.getWeatherUnits(result)
        forecast.view = forecast.ViewDAILYValue
        forecast.weatherLocation = weatherLocation
        forecast.hourlyForecasts = []
        
        dailyForecasts = []
        for dailyForecast in result.findall("channel/item/{0}forecast".format(yweather)):
            weatherDaily = WeatherDailyForecast()
            weatherDaily.timeIndex = appleWeek[dailyForecast.get("day")]
            weatherDaily.lowTemperature = int(dailyForecast.get("low"))
            weatherDaily.highTemperature = int(dailyForecast.get("high"))
            weatherDaily.isUserRequested = True
            dailyCondition = WeatherCondition()
            dailyCondition.conditionCodeIndex = int(dailyForecast.get("code"))
            dailyCondition.conditionCode = dailyCondition.ConditionCodeIndexTable[dailyCondition.conditionCodeIndex]
            weatherDaily.condition = dailyCondition
            dailyForecasts.append(weatherDaily)
    
        forecast.dailyForecasts = dailyForecasts
        
        countryName = countries[forecast.weatherLocation.countryCode.lower()] if forecast.weatherLocation.countryCode.lower() in countries else forecast.weatherLocation.countryCode

        suggestion = ""
        if "fahrenheit" in forecast.units.temperatureUnits.lower():
            if (int(forecast.currentConditions.temperature) <= 33.8):
                suggestion += "freezing"
            elif (int(forecast.currentConditions.temperature) > 33.8 and int(forecast.currentConditions.temperature) <= 59):
                suggestion += "cool"
            elif (int(forecast.currentConditions.temperature) > 59 and int(forecast.currentConditions.temperature) <= 95):
                if (int(forecast.currentConditions.percentHumidity) >= 75):
                    suggestion += "soggy"
                elif (int(forecast.currentConditions.percentHumidity) >= 50 and int(forecast.currentConditions.percentHumidity) < 75):
                    suggestion += "humid"
                elif (int(forecast.currentConditions.percentHumidity) >= 25 and int(forecast.currentConditions.percentHumidity) < 50):
                    suggestion += "moist"
                else:
                    suggestion += "warm"
            else:
                suggestion += "scorching"
        else:
            if (int(forecast.currentConditions.temperature) <= 1):
                suggestion += "freezing"
            elif (int(forecast.currentConditions.temperature) > 1 and int(forecast.currentConditions.temperature) <= 15):
                suggestion += "cool"
            elif (int(forecast.currentConditions.temperature) > 15 and int(forecast.currentConditions.temperature) <= 35):
                if (int(forecast.currentConditions.percentHumidity) >= 75):
                    suggestion += "soggy"
                elif (int(forecast.currentConditions.percentHumidity) >= 50 and int(forecast.currentConditions.percentHumidity) < 75):
                    suggestion += "humid"
                elif (int(forecast.currentConditions.percentHumidity) >= 25 and int(forecast.currentConditions.percentHumidity) < 50):
                    suggestion += "moist"
                else:
                    suggestion += "warm"
            else:
                suggestion += "scorching"
        
        self.say(random.choice(localizations["currentTime"][language]) + ".  The temperature in {0}, {1} is a {2} {3} degrees {4}.".format(forecast.weatherLocation.city, countryName, suggestion, forecast.currentConditions.temperature, forecast.units.temperatureUnits))

        clock = ClockObject()
        clock.timezoneId = self.connection.assistant.timeZoneId
        
        clockView = ClockSnippet()
        clockView.clocks = [clock]
        
        rootAnchor = UIAddViews(self.refId)
        rootAnchor.dialogPhase = rootAnchor.DialogPhaseSummaryValue
        rootAnchor.views = [clockView]

        self.sendRequestWithoutAnswer(rootAnchor)

        snippet = WeatherForecastSnippet()
        snippet.aceWeathers = [forecast]
        
        showViewsCMD = UIAddViews(self.refId)
        showViewsCMD.dialogPhase = showViewsCMD.DialogPhaseSummaryValue
        
        showViewsCMD.views = [snippet]
        
        self.sendRequestWithoutAnswer(showViewsCMD)

        self.complete_request()
        
    @register("en-US", "good (day|morning|afternoon|evening|night)")
    def timedweather(self, speech, language):
        recite = speech[0].capitalize() + speech[1:].lower()
        #first tell that we look it up
        self.say("{0}, {1}!".format(recite, self.user_name()))
        location = self.getCurrentLocation()
        
        lng = location.longitude
        lat = location.latitude
        
        # we need the corresponding WOEID to the location
        query = "select woeid from geo.places where text=\"{0},{1}\"".format(lat,lng)
        reverseLookup = "http://query.yahooapis.com/v1/public/yql?q={0}&format=xml".format(urllib.quote(query.encode("utf-8")))
        #reverseLookup = "http://where.yahooapis.com/geocode?location={0},{1}&gflags=R&appid={2}".format(lat, lng, yahooAPIkey)
        result = getWebsite(reverseLookup, timeout=5)
        if result == None:
            self.say(random.choice(errorText[language]))
            self.complete_request()
            return
        
        root = ElementTree.XML(result)
        woeidElem = root.find("results/{0}place/{0}woeid".format(place))
        
        if woeidElem is None:
            self.say(random.choice(noDataForLocationText[language]))
            self.complete_request()
            return
        
        self.showCurrentWeatherWithTime(language, woeidElem.text)
        
        self.complete_request()