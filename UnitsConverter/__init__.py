#!/usr/bin/python
# -*- coding: utf-8 -*-
# Plugins courtesy of Eichhoernchen and SilentSpark community
# Revisions and reconfigurations performed by Twisted


import re
import urllib2, urllib
import json

from plugin import *
from plugin import __criteria_key__

from siriObjects.uiObjects import AddViews
from siriObjects.answerObjects import AnswerSnippet, AnswerObject, AnswerObjectLine

class UnitsConverter(Plugin):
    
    @register("en-US", "(Convert|Calculate)* ([\w ]+)")
    @register("en-GB", "(Convert|Calculate)* ([\w ]+)")
    def defineword(self, speech, language, regex):
        Title = regex.group(regex.lastindex)
        Query = urllib.quote_plus(Title.encode("utf-8"))
        SearchURL = u'http://www.google.com/ig/calculator?q=' + str(Query)
        try:
            result = urllib2.urlopen(SearchURL).read().decode("utf-8", "ignore")
            result = re.sub("([a-z]+):", '"\\1" :', result)
            result = json.loads(result)
            ConvA = result['lhs']
            ConvB = result['rhs'] 
            self.say("Here is what I found..." '\n' +str(ConvA) + " equals, " +str(ConvB))
            self.complete_request()
        except (urllib2.URLError):
            self.say("Sorry, but a connection to the Google calculator could not be established.")
            self.complete_request()
