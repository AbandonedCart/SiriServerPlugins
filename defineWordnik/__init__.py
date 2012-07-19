#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This process of enhancing plugins has been performed by Twisted.
#
# Unmerged versions of these plugins may function differently or lack some modification.
# All original headers and licensing information are labeled by the derived plugin name.
#
# Wordnik Plugin
#
# by Twisted, based on work by mrjf
#
# Wordnik functions can be found at
# http://developer.wordnik.com/docs/
# Original python API can be referenced at
# https://github.com/wordnik/wordnik-python
#
# Urban Dictionary Plugin
#
# No license included, courtesy of SNXRaven (Jonathon Nickols)
#
# Wikipedia Plugin
#
# Calculator Plugin
#
# by Mike Pissanos (gaVRos) 
#    Usage: simply say Convert or Calculate X to Y
#    Examples: 
#             Convert 70 ferinheight to celsius 
#             Convert 1 euro to dollars
#             Convert 1 tablespoon to teaspoons
#             Calculate 30 divided by 10
#
# Display Plugin
#
#request formatting information can be found at
#https://developers.google.com/image-search/v1/jsondevguide#request_format
#
# Search Plugin
#

import urllib2, nltk, json
import json, urllib
import re
from urllib import urlencode
from BeautifulSoup import BeautifulSoup
from plugin import *
from plugin import __criteria_key__
from plugins.defineWordnik.config import *

from siriObjects.baseObjects import AceObject, ClientBoundCommand
from siriObjects.uiObjects import AddViews, AssistantUtteranceView
from siriObjects.answerObjects import AnswerSnippet, AnswerObject, AnswerObjectLine
from siriObjects.websearchObjects import WebSearch

#you will need to install the Wordnik API to use this
#this can be done from the commandline by typing: easy_install Wordnik
try:
   from wordnik.api.WordAPI import WordAPI
   import wordnik.model
   # from wordnik import Wordnik
except ImportError:
   raise NecessaryModuleNotFound("Wordnik library not found. Please install wordnik library! e.g. sudo easy_install wordnik")

#You need a wordnik api key, you can get yours at http://developer.wordnik.com/ (first you sign up for a username with Wordnik, then submit it for an API key)
########################################################

wordnik_api_key = APIKeyForAPI("wordnik")

#########################################################

import sys
sys.path.append('../../wordnik/wordnik')

from wordnik.api.APIClient import APIClient
import wordnik.model

my_client = APIClient(wordnik_api_key, 'http://api.wordnik.com/v4')

from wordnik.api.WordAPI import WordAPI
wordAPI = WordAPI(my_client)

class defineWordnik(Plugin):
    
    @register("en-US", ".*define ([\w ]+)")
    def defineword(self, speech, language, regMatched):
        question = regMatched.group(1).lower()
        input = wordnik.model.WordDefinitionsInput.WordDefinitionsInput()
        input.word = question
        input.limit = 1
        output = wordAPI.getDefinitions(input)
        if len(output) == 1:
            for answer in output:
                worddef = answer.text
                if worddef:
                    self.say(worddef, "The definition of {0} is: {1}".format(question, worddef))
                else:
                    self.say("Sorry, I could not find " + question + " in the dictionary.")
        else:
            self.say("Sorry, I could not find " + question + " in the dictionary.")

        self.complete_request()

class images(Plugin):
    
    @register("de-DE", "(zeig mir|zeige|zeig).*(bild|zeichnung) (vo. ein..|vo.|aus)* ([\w ]+)")
    @register("en-US", "(display|show me|show).*(picture|image|drawing|illustration) (of|an|a)* ([\w ]+)")
    def imagedisplay(self, speech, language, regex):
        Title = regex.group(regex.lastindex)
        Query = urllib.quote_plus(Title.encode("utf-8"))
        SearchURL = u'https://ajax.googleapis.com/ajax/services/search/images?v=1.0&safe=off&q=' + str(Query)
        answer = self.ask("Would you like mobile size images only?")
        if ("Yes" or "Yeah" or "Yup") in answer:
            SearchURL = SearchURL + "&imgsz=small|medium|large|xlarge"
        try:
            jsonResponse = urllib2.urlopen(SearchURL).read()
            jsonDecoded = json.JSONDecoder().decode(jsonResponse)
            ImageURL = jsonDecoded['responseData']['results'][0]['unescapedUrl']
            view = AddViews(self.refId, dialogPhase="Completion")
            ImageAnswer = AnswerObject(title=str(Title),lines=[AnswerObjectLine(image=ImageURL)])
            view1 = AnswerSnippet(answers=[ImageAnswer])
            view.views = [view1]
            self.sendRequestWithoutAnswer(view)
            self.complete_request()
        except (urllib2.URLError):
            self.say("Sorry, a connection to Google Images could not be established.")
            self.complete_request()
    @register("en-US", ".*(Search|Google)( the)?( web| net| internet| google)?( for| about)? ([\w ]+)")
    def webSearch(self, speech, language, regex):
        if (language == "en-US"):
            speech = regex.group(regex.lastindex).lower()
            if speech == "":
                speech = self.ask("What is your query?")

        self.say("Searching Google for " + speech)
        search = WebSearch(refId=self.refId, query=speech)
        self.sendRequestWithoutAnswer(search)
        self.complete_request()

class urbandictionary(Plugin):

    # Dictionary for help phrases used by the helpPlugin
    helpPhrases = {
        "en-US": ["Urban dictionary <something>", "Example: Urban dictionary banana"]
                  }

    @register("en-US", ".*urban dictionary ([\w ]+)")
    def sn_dictionary(self, speech, language, regMatched):
        if language == 'en-US':
            terms = regMatched.group(1).lower()
            match = urllib.quote_plus(terms.encode("utf-8"))
            r = urllib2.urlopen('http://www.urbandictionary.com/iphone/search/define?term='+match)
            data = json.loads(r.read())
            if ( len(data['list']) > 1 ):
                data['list'] = data['list'][:1]  # only print 2 results
            for i in range(len(data['list'])):
                word = data['list'][i][u'word']
            definition = data['list'][i][u'definition']
            example = data['list'][i][u'example']
        if definition.startswith(word + ':'):
            self.say(definition).replace(word + ':', word + ': ')
        else:
            self.say(word + ': ' + definition)
        self.say('Example: ' + example)
        self.complete_request()

class wikipedia(Plugin):
    @register("en-US", "(.*wikipedia.*)")
    def wiki(self, speech, language):
	#Json search results (via MediaWiki API)
	def searchWiki(lang, query):
		file = urllib2.urlopen("http://%s.wikipedia.org/w/api.php?" % (lang)+
				      urlencode({'action':'opensearch',
						  'search':query,
						  'format':'json',
						  'limit': searchlimit}))
		data = json.load(file)
		return data

	#save results to array 
	def resultsArray(lang, query):
		error = 0
		number = 0
		results = []
		while(error != 1):
			try:
				results.append(searchWiki(lang, query)[1][number])
				number = number + 1
			except IndexError:
				error = 1
		return results
	query = ""
	#ask for user's query
	query = speech.replace('Wikipedia', '',1)
	if (query == ""):
		query = self.ask('What would you like to search ?')

	self.say("Searching ..")
	error = 0
	number = 0
	WikipediaResults = ""
	results = resultsArray(lang, query)
	while (error != 1):
		try:  
			results[number]
			WikipediaResults = WikipediaResults + str(number + 1) + " : " + unicode(results[number]) + "\n"
			number = number + 1
		except IndexError:
			error = 1
	
	if (number == 0):
	  self.say("I didn't find anything !")
	  self.complete_request()
	#show results
	view = AddViews(self.refId, dialogPhase="Completion")
	view1 = 0
	Wikipedia = AnswerObject(title='Results',lines=[AnswerObjectLine(text=WikipediaResults)])
	view1 = AnswerSnippet(answers=[Wikipedia])
	view.views = [view1]
	self.sendRequestWithoutAnswer(view) 
	#ask for article
	invalid = 1
	while(invalid != 0):
		self.say("Answer only number article (one, two, ...)", " ")
		id = self.ask('Which one ?')
		try:
			id = int(id)
		except:
			invalid = 1
			continue
		if(id > number):
			invalid = 1
			continue
		else:
			invalid = 0
	self.say("Checking ...")
	#parse article
	query = str(results[id-1])
	url = "http://%s.wikipedia.org/w/index.php?" % (lang) + urlencode({'action':'render','title':query})
	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	html = opener.open(url).read()
	html = str(html)
	paragraph = BeautifulSoup(''.join(html)).findAll('p')
	text = paragraph
	
	#show article
	error = 0
	number = 0
	while (error != 1):
		try:
			text[number]
			number = number + 1
		except IndexError :
			error = 1
	paragraphsCount = number - 1
	lastCount = 10

	WikipediaArticle = ""
	error = 0
	number = 0
	while (error != 1):
		if (number == lastCount):
			error = 1
		try:
			text[number]
			WikipediaArticle = WikipediaArticle + nltk.clean_html(unicode(text[number]))
			number = number + 1
		except IndexError :
			error = 1
	
	view = AddViews(self.refId, dialogPhase="Completion")
	view1 = 0
	Wikipedia = AnswerObject(title=query,lines=[AnswerObjectLine(text=WikipediaArticle)])
	view1 = AnswerSnippet(answers=[Wikipedia])
	view.views = [view1]
	self.sendRequestWithoutAnswer(view) 
	
	
	while (paragraphsCount-lastCount > 0):
		loadmore = self.ask('Would you like to load more ?')
		WikipediaArticle = ""
		if (loadmore == 'Yes'):
		  lastCount = lastCount + 10
		  error = 0
		  while (error != 1):
			  if (number == lastCount):
				  error = 1
			  try:
				  text[number]
				  WikipediaArticle = WikipediaArticle + nltk.clean_html(unicode(text[number]))
				  number = number + 1
			  except IndexError :
				  error = 1
		else:
			self.complete_request()
		view = AddViews(self.refId, dialogPhase="Completion")
		view1 = 0
		Wikipedia = AnswerObject(title=query,lines=[AnswerObjectLine(text=WikipediaArticle)])
		view1 = AnswerSnippet(answers=[Wikipedia])
		view.views = [view1]
		self.sendRequestWithoutAnswer(view)
		
	self.complete_request()

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
            response = json.loads(result)
            ConvA = response['lhs']
            ConvB = response['rhs'] 
            self.say("I was able to calculate the following results:")
            self.say(str(ConvA) + " equals " + str(Conv))
            self.complete_request()
        except (urllib2.URLError):
            self.say("Sorry, but a connection to the Google calculator could not be established.")
            self.complete_request()