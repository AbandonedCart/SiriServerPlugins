#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# This process of enhancing plugins has been performed by Twisted.
#
# Unmerged versions of these plugins may function differently or lack some modification.
# All original headers and licensing information are labeled by the derived plugin name.
#
# WhereAmI Plugin
#
# Yelp Plugin
#
# Traffic Plugin
#
# Created by Javik
# Edited and made better by Tristen Russ (Playfrog4u)
#

import re
import urllib2, urllib
import json
import random
 
from plugin import *

from siriObjects.baseObjects import AceObject, ClientBoundCommand, ObjectIsCommand, RequestCompleted
from siriObjects.systemObjects import *
from siriObjects.uiObjects import *
from siriObjects.localsearchObjects import Business, MapItem, MapItemSnippet, Rating, ShowMapPoints

geonames_user="test2"

yelp_api_key = APIKeyForAPI("yelp")
 
class whereAmI(Plugin):
    
    @register("de-DE", "(Wo bin ich.*)")
    @register("fr-FR", u'(Où suis-je.*)')    
    @register("en-US", "(Where am I.*)|(What is my location.*)")
    def whereAmI(self, speech, language):
        location = self.getCurrentLocation(force_reload=True,accuracy=GetRequestOrigin.desiredAccuracyBest)
        url = "http://maps.googleapis.com/maps/api/geocode/json?latlng={0},{1}&sensor=false&language={2}".format(str(location.latitude),str(location.longitude), language)
        try:
            jsonString = urllib2.urlopen(url, timeout=3).read()
        except:
            pass
        if jsonString != None:
            response = json.loads(jsonString)
            if response['status'] == 'OK':
                components = response['results'][0]['address_components']              
                street = filter(lambda x: True if "route" in x['types'] else False, components)[0]['long_name']
                stateLong= filter(lambda x: True if "administrative_area_level_1" in x['types'] or "country" in x['types'] else False, components)[0]['long_name']
                try:
                    postalCode= filter(lambda x: True if "postal_code" in x['types'] else False, components)[0]['long_name']
                except:
                    postalCode=""
                try:
                    city = filter(lambda x: True if "locality" in x['types'] or "administrative_area_level_1" in x['types'] else False, components)[0]['long_name']
                except:
                    city=""
                countryCode = filter(lambda x: True if "country" in x['types'] else False, components)[0]['short_name']
                view = AddViews(self.refId, dialogPhase="Completion")
                if language == "de-DE":
                    the_header="Dein Standort"
                elif language == 'fr-FR':
                    the_header="Votre position"
                else:
                    self.say("This is your location {0}".format(self.user_name()))
                    the_header="Your location"
        view = AddViews(self.refId, dialogPhase="Completion")
        mapsnippet = MapItemSnippet(items=[MapItem(label=postalCode+" "+city, street=street, city=city, postalCode=postalCode, latitude=location.latitude, longitude=location.longitude, detailType="CURRENT_LOCATION")])
        view.views = [AssistantUtteranceView(speakableText=the_header, dialogIdentifier="Map#whereAmI"), mapsnippet]
        self.sendRequestWithoutAnswer(view)
        self.complete_request()

class yelpSearch(Plugin):
     res = {
          'searchString': {
               'en-US': '(find|show|where)?.*( )?(nearest|nearby|closest) (.*)',
               'en-GB': '(find|show|where).* (nearest|nearby|closest) (.*)',
               'de-DE': '(finde|zeige|wo).* (n\xe4chste|nächstes|n\xe4chstes|nahe|in der n\xe4he|in der umgebung) (.*)'
          },
          'searching': {
               'en-US': 'Searching...',
               'en-GB': 'Searching...',
               'de-DE': 'Suche...'
          },
          'results': {
               'en-US': 'I found {0} {1} results... {2} of them are fairly close to you:',
               'en-GB': 'I found {0} {1} results... {2} of them are fairly close to you:',
               'de-DE': 'Ich habe {0} {1} Ergebnisse gefunden... {2} davon ganz in deiner N\xe4he:'
          },
          'no-results': {
               'en-US': 'I\'m sorry but I did not find any results for {0} near you!',
               'en-GB': 'I\'m sorry but I did not find any results for {0} near you!',
               'de-DE': 'Es tut mir leid aber ich konnte keine Ergebnisse f\xfcr {0} in deiner N\xe4he finden'
          }
     }

     @register('en-US', res['searchString']['en-US'])
     @register('en-GB', res['searchString']['en-GB'])
     @register('de-DE', res['searchString']['de-DE'])
     def yelp_search(self, speech, language, regex):
          self.say(yelpSearch.res['searching'][language],' ')
          mapGetLocation = self.getCurrentLocation()
          latitude = mapGetLocation.latitude
          longitude = mapGetLocation.longitude
          Title = regex.group(regex.lastindex).strip()
          Query = urllib.quote_plus(str(Title.encode("utf-8")))
          random_results = random.randint(2,15)
          yelpurl = "http://api.yelp.com/business_review_search?term={0}&lat={1}&long={2}&radius=5&limit=20&ywsid={3}".format(str(Query),latitude,longitude,str(yelp_api_key))
          try:
               jsonString = urllib2.urlopen(yelpurl, timeout=20).read()
          except:
               jsonString = None
          if jsonString != None:
               response = json.loads(jsonString)
               if (response['message']['text'] == 'OK') and (len(response['businesses'])):
                    response['businesses'] = sorted(response['businesses'], key=lambda business: float(business['distance']))
                    yelp_results = []
                    for result in response['businesses']:
                         rating = Rating(value=result['avg_rating'], providerId='YELP', count=result['review_count'])
                         details = Business(totalNumberOfReviews=result['review_count'],name=result['name'],rating=rating)
                         if (len(yelp_results) < random_results):
                              mapitem = MapItem(label=result['name'], street=result['address1'], stateCode=result['state_code'], postalCode=result['zip'],latitude=result['latitude'], longitude=result['longitude'])
                              mapitem.detail = details
                              yelp_results.append(mapitem)
                         else:
                              break
                    mapsnippet = MapItemSnippet(items=yelp_results)
                    count_min = min(len(response['businesses']),random_results)
                    count_max = max(len(response['businesses']),random_results)
                    view = AddViews(self.refId, dialogPhase="Completion")
                    responseText = yelpSearch.res['results'][language].format(str(count_max), str(Title), str(count_min))
                    view.views = [AssistantUtteranceView(speakableText=responseText, dialogIdentifier="yelpSearchMap"), mapsnippet]
                    self.sendRequestWithoutAnswer(view)
               else:
                    self.say(yelpSearch.res['no-results'][language].format(str(Title)))
          else:
               self.say(yelpSearch.res['no-results'][language].format(str(Title)))
          self.complete_request()

class basicDirections(Plugin):
    @register("en-US", ".*(directions|get) to (?P<location>[\w ]+?)$")
    @register("en-GB", ".*(directions|get) to (?P<location>[\w ]+?)$")
    def directions(self, speech, language, regex):
       searchlocation = regex.group('location')
       Title = searchlocation   
       Query = urllib.quote_plus(str(Title.encode("utf-8")))
       googleurl = "http://maps.googleapis.com/maps/api/geocode/json?address={0}&sensor=true&language=en".format(Query)
       jsonString = urllib2.urlopen(googleurl, timeout=20).read()
       response = json.loads(jsonString)
       if (response['status'] == 'OK') and (len(response['results'])):
         for result in response['results']:
             label = "{0}".format(Title.title())
             latitude=result['geometry']['location']['lat']
             longitude=result['geometry']['location']['lng']
             city=result['address_components'][0]['long_name']
             state=result['address_components'][2]['short_name']
             country=result['address_components'][3]['short_name']
       code = 0
       Loc = Location(self.refId)
       Loc.street = ""
       Loc.countryCode = country
       Loc.city = city
       Loc.latitude = latitude
       Loc.stateCode = state
       Loc.longitude = longitude
       Map = MapItem(self.refId)
       Map.detailType = "ADDRESS_ITEM"
       Map.label = label
       Map.location = Loc
       Source = MapItem(self.refId)
       Source.detailType = "CURRENT_LOCATION"
       ShowPoints = ShowMapPoints(self.refId)
       ShowPoints.showTraffic = False  
       ShowPoints.showDirections = True
       ShowPoints.regionOfInterestRadiusInMiles = "10.0"
       ShowPoints.itemDestination = Map
       ShowPoints.itemSource = Source
       AddViews = UIAddViews(self.refId)
       AddViews.dialogPhase = "Summary"
       AssistantUtteranceView = UIAssistantUtteranceView()
       AssistantUtteranceView.dialogIdentifier = "LocationSearch#foundLocationForDirections"
       AssistantUtteranceView.speakableText = "Here are directions to {0}:".format(label)
       AssistantUtteranceView.text = "Here are directions to {0}:".format(label)
       AddViews.views = [(AssistantUtteranceView)]
       AddViews.scrollToTop = False
       AddViews.callbacks = [ResultCallback([ShowPoints], code)]
       callback = [ResultCallback([AddViews])]
       self.complete_request(callbacks=[ResultCallback([AddViews], code)])

class Traffic(Plugin):
    
    @register("en-US", ".*traffic like (in|around|near) (?P<location>[\w ]+?)$")
    @register("en-GB", ".*traffic like (in|around|near) (?P<location>[\w ]+?)$")
    def traffic(self, speech, language, regex):
       searchlocation = regex.group('location')
       Title = searchlocation   
       Query = urllib.quote_plus(str(Title.encode("utf-8")))
       googleurl = "http://maps.googleapis.com/maps/api/geocode/json?address={0}&sensor=true&language=en".format(Query)
       jsonString = urllib2.urlopen(googleurl, timeout=20).read()
       response = json.loads(jsonString)
       if (response['status'] == 'OK') and (len(response['results'])):
         for result in response['results']:
             label = "{0}".format(Title.title())
             latitude=result['geometry']['location']['lat']
             longitude=result['geometry']['location']['lng']
             city=result['address_components'][0]['long_name']
             state=result['address_components'][2]['short_name']
             country=result['address_components'][3]['short_name']
       code = 0
       Loc = Location(self.refId)
       Loc.street = ""
       Loc.countryCode = country
       Loc.city = city
       Loc.latitude = latitude
       Loc.stateCode = state
       Loc.longitude = longitude
       Map = MapItem(self.refId)
       Map.detailType = "ADDRESS_ITEM"
       Map.label = label
       Map.location = Loc
       Source = MapItem(self.refId)
       Source.detailType = "CURRENT_LOCATION"
       ShowPoints = ShowMapPoints(self.refId)
       ShowPoints.showTraffic = True  
       ShowPoints.showDirections = False
       ShowPoints.regionOfInterestRadiusInMiles = "10.0"
       ShowPoints.itemDestination = Map
       ShowPoints.itemSource = Source
       AddViews = UIAddViews(self.refId)
       AddViews.dialogPhase = "Summary"
       AssistantUtteranceView = UIAssistantUtteranceView()
       AssistantUtteranceView.dialogIdentifier = "LocationSearch#foundLocationForTraffic"
       AssistantUtteranceView.speakableText = "Here\'s the traffic for " + Loc.city +":"
       AssistantUtteranceView.text = "Here\'s the traffic for " + Loc.city +":"
       AddViews.views = [(AssistantUtteranceView)]
       AddViews.scrollToTop = False
       AddViews.callbacks = [ResultCallback([ShowPoints], code)]
       callback = [ResultCallback([AddViews])]
       self.complete_request(callbacks=[ResultCallback([AddViews], code)])

    @register("en-US", ".*traffic like")
    @register("en-GB", ".*traffic like")
    def trafficSelf(self, speech, language, regex):
       mapGetLocation = self.getCurrentLocation(force_reload=True,accuracy=GetRequestOrigin.desiredAccuracyBest)
       latitude= mapGetLocation.latitude
       longitude= mapGetLocation.longitude
       label = "Your location"
       code = 0
       Loc = Location(self.refId)
       Loc.street = ""
       Loc.countryCode = "US"
       Loc.city = ""
       Loc.latitude = latitude
       Loc.stateCode = ""
       Loc.longitude = longitude
       Map = MapItem(self.refId)
       Map.detailType = "ADDRESS_ITEM"
       Map.label = label
       Map.location = Loc
       Source = MapItem(self.refId)
       Source.detailType = "CURRENT_LOCATION"
       ShowPoints = ShowMapPoints(self.refId)
       ShowPoints.showTraffic = True  
       ShowPoints.showDirections = False
       ShowPoints.regionOfInterestRadiusInMiles = "10.0"
       ShowPoints.itemDestination = Map
       ShowPoints.itemSource = Source
       AddViews = UIAddViews(self.refId)
       AddViews.dialogPhase = "Summary"
       AssistantUtteranceView = UIAssistantUtteranceView()
       AssistantUtteranceView.dialogIdentifier = "LocationSearch#foundLocationForTraffic"
       AssistantUtteranceView.speakableText = "Here\'s the current traffic:"
       AssistantUtteranceView.text = "Here\'s the current traffic:"
       AddViews.views = [(AssistantUtteranceView)]
       AddViews.scrollToTop = False
       AddViews.callbacks = [ResultCallback([ShowPoints], code)]
       callback = [ResultCallback([AddViews])]
       self.complete_request(callbacks=[ResultCallback([AddViews], code)])