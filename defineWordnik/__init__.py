#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This process of enhancing plugins has been performed by Twisted.
#
# Unmerged versions of these plugins may function differently or lack some functionality.
# All original headers and licensing information is labeled by the derived plugin name.
#
# Wordnik Plugin
#
#additional Wordnik functions to add can be found at:
#http://developer.wordnik.com/docs/
#
# Urban Dictionary Plugin
#
# Wikipedia Plugin
#
# Unit Converter Plugin
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

#you will need to install the Wordnik API to use this
#this can be done from the commandline by typing: easy_install Wordnik
try:
   from wordnik import Wordnik
except ImportError:
   raise NecessaryModuleNotFound("Wordnik library not found. Please install wordnik library! e.g. sudo easy_install wordnik")

#You need a wordnik api key, you can get yours at http://developer.wordnik.com/ (first you sign up for a username in the upp$
########################################################

wordnik_api_key = APIKeyForAPI("wordnik")

#########################################################

w = Wordnik(api_key=wordnik_api_key)

class defineWordnik(Plugin):
    
    @register("en-US", "define ([\w ]+)")
    def defineword(self, speech, language, regMatched):
        Question = regMatched.group(1).lower()
        output = w.word_get_definitions(Question, limit=1)
        if len(output) == 1:
            answer = dict(output[0])
            if u'text' in answer:
                worddef = answer[u'text']
                if worddef:
                    self.say(worddef, "The definition of {0} is: {1}".format(Question, worddef))
                else:
                    self.say("Sorry, I could not find " + Question + " in the dictionary.")
        else:
            self.say("Sorry, I could not find " + Question + " in the dictionary.")

        self.complete_request()

class urbandictionary(Plugin):

    # Dictionary for help phrases used by the helpPlugin
    helpPhrases = {
        "en-US": ["Urban dictionary <something>", "Example: Urban dictionary banana"]
                  }

    @register("en-US", ".*Urban.*dictionary ([\w ]+)")
    def sn_dictionary(self, speech, language, regMatched):
        if language == 'en-US':
            match = regMatched.group(1).lower()
            r = urllib2.urlopen('http://www.urbandictionary.com/iphone/search/define?term='+match.group(1))
            data = json.loads(r.read())
            if ( len(data['list']) > 1 ):
                data['list'] = data['list'][:1]  # only print 2 results
            for i in range(len(data['list'])):
                word = data['list'][i][u'word']
            definition = data['list'][i][u'definition']
            example = data['list'][i][u'example']
            print(word + ': ' + definition),
            print('example: ' + example),
        self.say(word + ': ' + definition)
        self.say('For example: ' + example)
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
            result = json.loads(result)
            ConvA = result['lhs']
            ConvB = result['rhs'] 
            self.say("Here is what I found..." '\n' +str(ConvA) + " equals, " +str(ConvB))
            self.complete_request()
        except (urllib2.URLError):
            self.say("Sorry, but a connection to the Google calculator could not be established.")
            self.complete_request()