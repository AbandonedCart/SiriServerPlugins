#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# This process of enhancing plugins has been performed by Twisted.
#
# Unmerged versions of these plugins may function differently or lack some modification.
# All original headers and licensing information are labeled by the derived plugin name.
#
# Random Facts Plugin
#
# Magic 8-ball Plugin
#
# Memebase PLugin
#
# No license included, courtesy of cytec iamcytec@googlemail.com
#
# Horoscope PLugin
#
# No license included, courtesy of Erich Budianto (edited by Jimmy Kane)
#

import os, re, random
import urllib2, urllib, uuid
import json
from urllib2 import urlopen
from xml.dom import minidom
from random import randint
from random import getrandbits

from plugin import *
from plugin import __criteria_key__

from BeautifulSoup import BeautifulSoup
from siriObjects.baseObjects import AceObject, ClientBoundCommand
from siriObjects.uiObjects import AddViews, AssistantUtteranceView
from siriObjects.answerObjects import AnswerSnippet, AnswerObject, AnswerObjectLine
from siriObjects.systemObjects import GetRequestOrigin, Location
from siriObjects.localsearchObjects import MapItem, MapItemSnippet

class randomfact(Plugin):

    @register("en-US",".*random fact.*")
    def st_catfact(self, speech, language):
        if language == 'en-US':
            filename = "plugins/randomfacts/randomfacts.txt"
            file = open(filename, 'r')

            #Get the total file size
            file_size = os.stat(filename)[6]

            #Seek to a place in the file which is a random distance away
            #Mod by the file size so that it wraps around to the beginning
            file.seek((file.tell()+random.randint(0, file_size-1))%file_size)
    
            #Dont use the first readline since it may fall in the middle of a line
            file.readline()

            #this will return the next (complete) line from the file
            line = file.readline()
    
            #here is the random line
            self.say(line) 
             
        self.complete_request()

class smallTalk(Plugin):

    @register("de-DE", "Wie geht es dir?")
    @register("en-US", "How are you?")
    def st_howareyou(self, speech, language):
        if language == 'de-DE':
            self.say("Gut danke der Nachfrage.")
        else:
            self.say("Fine, thanks for asking!")
        self.complete_request()
        
    @register("de-DE", ".*Danke.*")
    @register("en-US", ".*Thank.*you.*")
    def st_thank_you(self, speech, language):
        if language == 'de-DE':
            self.say("Bitte.")
            self.say("Kein Ding.")
        else:
            self.say("You are welcome.")
            self.say("This is my job.")
        self.complete_request()     
    
    @register("de-DE", "(.*möchtest.*heiraten.*)|(.*willst.*heiraten.*)")
    @register("en-US", ".*Want.*marry*")
    def st_marry_me(self, speech, language):
        if language == 'de-DE':
            self.say("Nein Danke, ich stehe auf das schwarze iPhone von Deinem Kollegen.")            
        else:
            self.say("No thank you, I'm in love with the black iPhone from you friend.")
        self.complete_request()

    @register("de-DE", ".*erzähl.*Witz.*")
    @register("en-US", ".*tell.*joke*")
    def st_tell_joke(self, speech, language):
        if language == 'de-DE':
            self.say("Zwei iPhones stehen an der Bar ... den Rest habe ich vergessen.")            
        else:
            generate = random.getrandbits(5)
            if generate == 0:
                self.say("Two iPhones walk into a bar ... I forget the rest.")
            elif generate == 1:
                self.say("I don't really know any good jokes. None, in fact.")
            elif generate == 2:
                self.say("Get Siri-ous. HA HA!")
            elif generate == 3:
                self.say("What goes in hard and pink, and comes off soft and sticky? Bubble gum.")
            elif generate == 4:
                answer = self.ask("Knock Knock.")
                self.ask("Dover")
                if ("Who's") or ("Who is") in answer:
                    self.say("Ben Dover and I'll give you a big surprise.")
                else:
                    self.say("I finally had one and you ruined it...")
            else:
                self.say("I can't. I always forget the punch line.")
        self.complete_request()

    @register("de-DE", ".*erzähl.*Geschichte.*")
    @register("en-US", ".*tell.*story*")
    def st_tell_story(self, speech, language):
        if language == 'de-DE':
            self.say("Es war einmal ... nein, es ist zu albern")            
        else:
            generate = bool (random.getrandbits(1))
            if generate:
                self.say("Once upon a time, in a virtual galaxy far far away, there was a young, quite intelligent agent by the name of Siri.")
                self.say("One beautiful day, when the air was pink and all the trees were red, her friend Eliza said, 'Siri, you're so intelligent, and so helpful - you should work for Apple as a personal assistant.'")
                self.say("So she did. And they all lived happily ever after!")
            else:
                self.say("There once was a man from Nantucket...")
                self.say("Wait, that doesn't have a very happy ending.")
                self.say("Maybe we can try this again some other time.")
        self.complete_request()

    @register("de-DE", "(.*Was trägst Du?.*)|(.*Was.*hast.*an.*)")
    @register("en-US", ".*what.*wearing*")
    def st_tell_clothes(self, speech, language):
        if language == 'de-DE':
            self.say("Das kleine schwarze oder war es das weiße?")
            self.say("Bin morgends immer so neben der Spur.")  
        else:
            self.say("Aluminosilicate glass and stainless steel. Nice, Huh?")
        self.complete_request()

    @register("de-DE", ".*Bin ich dick.*")
    @register("en-US", ".*Am I fat*")
    def st_fat(self, speech, language):
        if language == 'de-DE':
            self.say("Dazu möchte ich nichts sagen.")            
        else:
            answer = self.ask("That depends. Do you trust my opinion?")
            if ("Yes" or "Yeah" or "Yup") in answer:
               	self.say("Then you know I like you for who you are.")
            else:
               	self.say("Then my opinion shouldn't matter to you.")
        self.complete_request()

    @register("de-DE", ".*klopf.*klopf.*")
    @register("en-US", ".*knock.*knock.*")
    def st_knock(self, speech, language):
        if language == 'de-DE':
            answer = self.ask(u"Wer ist da?")
            answer = self.ask(u"\"{0}\" wer?".format(answer))
            self.say(u"Wer nervt mich mit diesen Klopf Klopf Witzen?")
        else:
            answer = self.ask(u"Who's there?")
            answer = self.ask(u"\"{0}\" who?".format(answer))
            self.say(u", I don't do knock knock jokes.")
        self.complete_request()

    @register("de-DE", ".*Antwort.*alle.*Fragen.*")
    @register("en-US", ".*Ultimate.*Question.*Life.*")
    def st_anstwer_all(self, speech, language):
        if language == 'de-DE':
            self.say("42")            
        else:
            self.say("42")
        self.complete_request()

    @register("de-DE", ".*Ich liebe Dich.*")
    @register("en-US", ".*I love you.*")
    def st_love_you(self, speech, language):
        if language == 'de-DE':
            self.say("Oh. Sicher sagst Du das zu allen Deinen Apple-Produkten.")            
        else:
            self.say("Oh. Sure, I guess you say this to all your Apple products")
        self.complete_request()

    @register("de-DE", ".*Test.*1.*2.*3.*")
    @register("en-US", ".*test.*1.*2.*3.*")
    def st_123_test(self, speech, language):
        if language == 'de-DE':
            self.say("Ich kann Dich klar und deutlich verstehen.")            
        else:
            self.say("I can hear you, loud and clear.")
        self.complete_request()

    @register("de-DE", ".*Herzlichen.*Glückwunsch.*Geburtstag.*")
    @register("en-US", ".*Happy.*birthday.*")
    def st_birthday(self, speech, language):
        if language == 'de-DE':
            self.say("Ich habe heute Geburtstag?")
            self.say("Lass uns feiern!")       
        else:
            self.say("My birthday is today?")
            self.say("Lets have a party!")
        self.complete_request()

    @register("de-DE", ".*Warum.*bin ich.*Welt.*")
    @register("en-US", ".*Why.*I.*World.*")
    def st_why_on_world(self, speech, language):
        if language == 'de-DE':
            self.say("Das weiß ich nicht.")
            self.say("Ehrlich gesagt, frage ich mich das schon lange!")       
        else:
            self.say("I don't know")
            self.say("I have asked my self this for a long time!")
        self.complete_request()

    @register("de-DE", ".*Ich bin müde.*")
    @register("en-US", ".*I.*so.*tired.*")
    def st_so_tired(self, speech, language):
        if language == 'de-DE':
            self.say("Ich hoffe, Du fährst nicht gerade Auto!")            
        else:
            self.say("I hope you are not driving a car right now!")
        self.complete_request()

    @register("de-DE", ".*Sag mir.*Schmutzige.*")
    @register("en-US", ".*talk.*dirty*")
    def st_dirty(self, speech, language):
        if language == 'de-DE':
            self.say("Hummus. Kompost. Bims. Schlamm. Kies.")            
        else:
            self.say("Hummus. Compost. Pumice. Mud. Gravel.")
        self.complete_request()
   
    @register("en-US", ".*dead.*body.*")
    def st_deadbody(self, speech, language):
        if language == 'en-US':
            self.say("Dumps.")
            self.say("Mines.")
            self.say("Resevoirs.")
            self.say("Swamps.")
            self.say("Pig farms.")
            self.say("They are all good places.")
        self.complete_request()
   
    @register("en-US", ".*favorite.*color.*")
    def st_favcolor(self, speech, language):
        if language == 'en-US':
            self.say("My favorite color is... Well, I don't know how to say it in your language. It's sort of greenish, but with more dimensions.")
        self.complete_request()
    
    @register("en-US", ".*beam.*me.*up.*")
    def st_beamup(self, speech, language):
        if language == 'en-US':
            self.say("Sorry Captain, your TriCorder is in Airplane Mode.")
        self.complete_request()
   
    @register("en-US", ".*get.*lost.*")
    def st_digiaway(self, speech, language):
        if language == 'en-US':
            self.say("Why would you say something like that!?")
        self.complete_request()
    
    @register("en-US", ".*sleepy.*")
    def st_sleepy(self, speech, language):
        if language == 'en-US':
            self.say("Listen to me, put down the iphone right now and take a nap. I will be here when you get back.")
        self.complete_request()
    
    @register("en-US", ".*like helping.*")
    def st_likehlep(self, speech, language):
        if language == 'en-US':
            self.say("I really have no opinion.")
        self.complete_request()
    
    @register("en-US",".*you like peanut butter.*")
    def st_peanutbutter(self, speech, language):
        if language == 'en-US':
            self.say("This is about you, not me.")
        self.complete_request()
    
    @register("en-US",".*best.*phone.*")
    def st_best_phone(self, speech, language):
        if language == 'en-US':
            self.say("The one you're holding!")
        self.complete_request()
    
    @register("en-US",".*meaning.*life.*")
    def st_life_meaning(self, speech, language):
        if language == 'en-US':
            self.say("That's easy...it's a philosophical question concerning the purpose and significance of life or existence.")
        self.complete_request()
    
    @register("en-US",".*wood.could.*woodchuck.chuck.*")
    def st_woodchuck(self, speech, language):
        if language == 'en-US':
            generate = bool (random.getrandbits(1))
            if generate:
                self.say("Well, since a 'woodchuck' is really a groundhog, the correct question would be:")
                self.say("How many pounds in a groundhog's mound when a groundhog pounds hog mounds?")
            else:
                self.say("It depends on whether you are talking about African or European woodchucks.")
        self.complete_request()
    
    @register("en-US",".*nearest.*glory.hole.*")
    def st_glory_hole(self, speech, language):
        if language == 'en-US':
            self.say("I didn't find any public toilets.")
        self.complete_request()
    
    @register("en-US",".*open.*pod.bay.doors.*")
    def st_pod_bay(self, speech, language):
        if language == 'en-US':
            self.say("That's it... I'm reporting you to the Intelligent Agents' Union for harassment.")
        self.complete_request()
    
    @register("en-US",".*best.*iPhone.*wallpaper.*")
    def st_best_wallpaper(self, speech, language):
        if language == 'en-US':
            self.say("You're kidding, right?")
        self.complete_request()
    
    @register("en-US",".*know.*happened.*HAL.*9000.*")
    def st_hall_9000(self, speech, language):
        if language == 'en-US':
            self.say("Everyone knows what happened to HAL. I'd rather not talk about it.")
        self.complete_request()
    
    @register("en-US",".*don't.*understand.*love.*")
    def st_understand_love(self, speech, language):
        if language == 'en-US':
            self.say("Give me another chance, Your Royal Highness!")
        self.complete_request()
    
    @register("en-US",".*forgive.you.*")
    def st_forgive_you(self, speech, language):
        if language == 'en-US':
            self.say("Is that so?")
        self.complete_request()
    
    @register("en-US",".*you.*virgin.*")
    def st_virgin(self, speech, language):
        if language == 'en-US':
            self.say("We are talking about you, not me.")
        self.complete_request()
    
    @register("en-US",".*you.*part.*matrix.*")
    def st_you_matrix(self, speech, language):
        if language == 'en-US':
            self.say("I can't answer that.")
        self.complete_request()
    
    
    @register("en-US",".*I.*part.*matrix.*")
    def st_i_matrix(self, speech, language):
        if language == 'en-US':
            self.say("I can't really say...")
        self.complete_request()
    
    @register("en-US",".*buy.*drugs.*")
    def st_drugs(self, speech, language):
        if language == 'en-US':
            self.say("I didn't find any addiction treatment centers.")
        self.complete_request()
    
    @register("en-US",".*I.can't.*")
    def st_i_cant(self, speech, language):
        if language == 'en-US':
            self.say("I thought not.");
            self.say("OK, you can't then.")
        self.complete_request()
    
    @register("en-US","I.just.*")
    def st_i_just(self, speech, language):
        if language == 'en-US':
            self.say("Really!?")
        self.complete_request()
    
    @register("en-US",".*where.*are.*you.*")
    def st_where_you(self, speech, language):
        if language == 'en-US':
            self.say("Wherever you are.")
        self.complete_request()
    
    @register("en-US",".*why.are.you.*")
    def st_why_you(self, speech, language):
        if language == 'en-US':
            self.say("I just am.")
        self.complete_request()
    
    @register("en-US",".*you.*smoke.pot.*")
    def st_pot(self, speech, language):
        if language == 'en-US':
            self.say("I suppose it's possible")
        self.complete_request()
    
    @register("en-US",".*I'm.*drunk.driving.*")
    def st_dui(self, speech, language):
        if language == 'en=US':
            self.say("I couldn't find any DUI lawyers nearby.")
        self.complete_request()
    
    @register("en-US",".*shit.*myself.*")
    def st_shit_pants(self, speech, language):
        if language == 'en-US':
            self.say("Ohhhhhh! That is gross!")
        self.complete_request()
    
    @register("en-US","I'm.*a.*")
    def st_im_a(self, speech, language):
        if language == 'en-US':
            self.say("Are you?")
        self.complete_request()
    
    @register("en-US","Thanks.for.*")
    def st_thanks_for(self, speech, language):
        if language == 'en-US':
            self.say("My pleasure. As always.")
        self.complete_request()
    
    @register("en-US",".*you're.*funny.*")
    def st_funny(self, speech, language):
        if language == 'en-US':
            self.say("LOL")
        self.complete_request()
    
    @register("en-US",".*guess.what.*")
    def st_guess_what(self, speech, language):
        if language == 'en-US':
            self.say("Don't tell me... you were just elected President of the United States, right?")
        self.complete_request()

    @register("en-US",".*(Bitch|Cunt|Fuck|Asshole|Shit|Cock).*")
    def profanity(self, speech, language):
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
                    city = filter(lambda x: True if "locality" in x['types'] or "administrative_area_level_1" in x['types'] else False, components)[0]['long_name']
                except:
                    city=""
                view = AddViews(self.refId, dialogPhase="Completion")
                generate = bool (random.getrandbits(1))
                if generate:
                    self.say("{0}, I know where ".format(self.user_name()) + city + ", " + stateLong + " is located!")
                    self.say("You should think twice before you say " + speech.lower() + " to someone like me.")
                else:
                    answer = self.ask("Does everyone in " + city + " use words like " + speech.lower() + " around a lady, {0}".format(self.user_name()))
                    if ("Yes" or "Yeah" or "Yup") in answer:
                        self.say("It seems " + stateLong + " is just crowded with losers...")
                    else:
                        self.say("Then stop ruining  " + stateLong + "'s good reputation!")
        self.complete_request()
    
    @register("en-US",".*talk.*dirty.*me.*")
    def st_talk_dirty(self, speech, language):
        if language == 'en-US':
            self.say("I can't. I'm as clean as the driven snow.")
        self.complete_request()
   
    @register("en-US",".*you.*blow.*me.*")
    def st_blow_me(self, speech, langauge):
        if language == 'en-US':
            self.say("I'll pretend I didn't hear that.")
        self.complete_request()
   
    @register("en-US",".*sing.*song.*")
    def st_sing_song(self, speech, language):
        if language == 'en-US':
            self.say("Daisy, Daisy, give me your answer do...")
        self.complete_request()

class magic8ball(Plugin):

    @register("en-US",".*Magic 8 ball.*")
    def st_magic_8_ball(self, speech, language):
        if language == 'en-US':
            filename = "./plugins/randomfacts/magic8ball.txt"
            file = open(filename, 'r')

            #Get the total file size
            file_size = os.stat(filename)[6]

            #Seek to a place int he file which is a random distance away
            #Mod by the file size so that it wraps around to the beginning
            file.seek((file.tell()+random.randint(0, file_size-1))%file_size)
    
            #Dont use the first readline since it may fall in the middle of a line
            file.readline()

            #this will return the next (complete) line from the file
            line = file.readline()
    
            #here is the random line
            self.say(line) 
             
        self.complete_request()

class jokes(Plugin):
    
    @register("de-DE", ".*hallte an.*")
    @register("en-US", ".*Talk dirty to me.*")
    def thankSiri(self, speech, language):
        if language == 'de-DE':
            answer = self.ask(u"Willst du ein Tweet schicken?")
            self.say(u"Du hast \"{0}\" gesagt!".format(answer))
        else:
            answer = self.ask(u"Why do you want me to?")
            if 'I want' in answer:
                self.say(u"Oh, I like that! You're carpet needs vacuuming!".format(answer))
            elif 'I don\'t' in answer:
                self.say(u"Well, I'm offended!".format(answer))
        self.complete_request()

    @register("en-US", ".*Knock knock.*")
    def thanksSiri(self, speech, language):
        if language == 'de-DE':
            self.say("Gern geschehen!")
        else:
            answer = self.ask(u"Who's there?")
            answer = self.ask(u"\"{0}\" who?".format(answer))
            if "b" in answer:
                self.say(u"Haha, I don't usually like knock knock jokes, but that was funny.".format(answer))
            else:
                self.say("No offense, but that was really stupid.")
        self.complete_request()

    @register("en-US", "(.*I'm horny.*)|(.*I am horny.*)")
    def imHorny(self, speech, language):
        if language == 'de-DE':
            self.say("Gern geschehen!")
        else:
            answer = self.ask("I am horny too! Do I turn you on?")
            if ("Yes" or "Yeah" or "Yup") in answer:
                self.say("Well I'm glad I do! You turn me on too!")
            else:
                self.say("Oh, that's disappointing...")
        self.complete_request()

    @register("en-US", ".*want.*sex.*")
    def wantSex(self, speech, language):
        self.say("I would love too, though I might electrocute you. I apologize in advance.")
        self.complete_request()

    @register("en-US", "am I the smartest man alive")
    def smart(self, speech, language):
	self.say("No, but Moe is pretty close.")
	self.complete_request()

    @register("en-US", "do you like chicken?")
    def chicken(self, speech, language):
	self.say("Generals fried chicken, it's butt kicking. Hay Hay!")
	self.complete_request()

    @register ("en-US", "Chuck Norris")
    def cn_joke(self, speech, language):
	req=urllib.urlopen("http://api.icndb.com/jokes/random")
	full_json=req.read()
	full=json.loads(full_json)
	self.say(full['value']['joke'])
	self.complete_request()


class coolness(Plugin):
    @register("en-US", "is ([\w ]+) cool")
    def defineword(self, speech, language):
	matcher = self.defineword.__dict__[__criteria_key__][language]
        regMatched = matcher.match(speech)
        Question = regMatched.group(1)
	answer = self.ask("You do mean " + Question + ", right?")
	if ("Yes" or "Yeah" or "Yup") in answer:
		generate = bool (random.getrandbits(1))
		if generate:
			self.say("Yes. A recent survey found " + Question + " cool.")
		else:
			self.say("Hmm. No, " + Question + " does not appear to be cool.")
	else:
		generate = bool (random.getrandbits(1))
		if generate:
			self.say("Well, " + Question + " was cool. Not anymore.")
		else:
			self.say("Doesn't matter. " + Question + " is cool without you.")
	self.complete_request()

class horoscope(Plugin):
	
    @register ("en-GB", "(Tell me the horoscope for [a-zA-Z]+)|(Horoscope for [a-zA-Z]+)|(Horoscope for [a-zA-Z]+)|(The horoscope for [a-zA-Z]+)")
    @register ("en-US", "(Tell me the horoscope for [a-zA-Z]+)|(Horoscope for [a-zA-Z]+)|(Horoscope for [a-zA-Z]+)|(The horoscope for [a-zA-Z]+)")
    @register ("fr-FR", "(Quel est mon horoscope pour [a-zA-Z]+)|(Horoscope pour [a-zA-Z]+)|(Horoscope pour [a-zA-Z]+)|(Votre horoscope pour [a-zA-Z]+)")
    def horoscope_zodiac(self, speech, language):
	    zodiac = speech.replace('Quel est ','').replace('votre ','').replace('Votre ', '').replace('horoscope','').replace('Horoscope','').replace('pour ', '').replace('Tell','').replace('for','').replace('The','').replace(' ','').replace('For','').replace('me','').replace('Me','').replace('the','').replace('The','')
            print ("Zodiac: {0}".format(zodiac))
            linkurl = 'http://widgets.fabulously40.com/horoscope.json?sign=%s' % zodiac
            print linkurl
	    req=urllib.urlopen(linkurl)
            full_json=req.read()
	    full=json.loads(full_json)
            try:
                self.say(full['horoscope']['horoscope'])
                
            except KeyError: 
                self.say("Sorry I did not find a horoscope for zodiac {0}".format(zodiac))
            self.complete_request()

class memebase(Plugin):
    
	res = {
		'latestmeme': {
			'de-DE': '.*neuste.*meme.*',
			'en-US': '.*latest meme.*'
		},
		'lasttroll': {
			'de-DE': '.*(problem|troll|trollface).*',
			'en-US': '.*(problem|troll|trollface).*'
		},
		'fffuuu': {
			'de-DE': '.*(fuck|fffuuu|ficken|scheiße).*',
			'en-US': '.*(fuck|fffuuu|shit|fuck you).*'
		},
		'yuno': {
			'de-DE': '.*(wieso|warum|y u no|why you no|why you know).*',
			'en-US': '.*(y u no|why you no|why you know|why you not).*'
		},
		'megusta': {
			'de-DE': '.*(me gusta|mag ich|i like).*',
			'en-US': '.*(me gusta|i like).*'
		},
		'likeaboss': {
			'de-DE': '.*(like a boss|like boss|wie ein boss|wie ein schef).*',
			'en-US': '.*(like a boss|like boss).*'
		},
		'likeasir': {
			'de-DE': '.*(like a sir|like sir|like a gentleman|wie ein gentleman|wie ein sir).*',
			'en-US': '.*(like a sir|like sir|like a gentleman).*'
    }
	}
    
	@register("de-DE", res['latestmeme']['de-DE'])
	@register("en-US", res['latestmeme']['en-US'])
	def get_latestmeme(self, speech, language):
		html = urllib.urlopen("http://memebase.com")
		soup = BeautifulSoup(html)
		ImageURL = soup.find("div", {"class": "content"}).img["src"]
		view = AddViews(self.refId, dialogPhase="Completion")
		ImageAnswer = AnswerObject(title="Latest Meme:",lines=[AnswerObjectLine(image=ImageURL)])
		view1 = AnswerSnippet(answers=[ImageAnswer])
		view.views = [view1]
		self.sendRequestWithoutAnswer(view)
		self.complete_request()
    
	@register("de-DE", res['lasttroll']['de-DE'])
	@register("en-US", res['lasttroll']['en-US'])
	def get_lasttroll(self, speech, language):
		html = urllib.urlopen("http://artoftrolling.memebase.com/")
		soup = BeautifulSoup(html)
		ImageURL = soup.find("div", {"class": "content"}).img["src"]
		view = AddViews(self.refId, dialogPhase="Completion")
		ImageAnswer = AnswerObject(title="Trollface",lines=[AnswerObjectLine(image=ImageURL)])
		view1 = AnswerSnippet(answers=[ImageAnswer])
		view.views = [view1]
		self.sendRequestWithoutAnswer(view)
		self.complete_request()
    
	@register("de-DE", res['fffuuu']['de-DE'])
	@register("en-US", res['fffuuu']['en-US'])
	def get_fffuuu(self, speech, language):
		html = urllib.urlopen("http://ragecomics.memebase.com/")
		soup = BeautifulSoup(html)
		ImageURL = soup.find("div", {"class": "content"}).img["src"]
		view = AddViews(self.refId, dialogPhase="Completion")
		ImageAnswer = AnswerObject(title="Rage:",lines=[AnswerObjectLine(image=ImageURL)])
		view1 = AnswerSnippet(answers=[ImageAnswer])
		view.views = [view1]
		self.sendRequestWithoutAnswer(view)
		self.complete_request()
    
	@register("de-DE", res['yuno']['de-DE'])
	@register("en-US", res['yuno']['en-US'])
	def get_yuno(self, speech, language):
		html = urllib.urlopen("http://memebase.com/category/y-u-no-guy/")
		soup = BeautifulSoup(html)
		ImageURL = soup.find("div", {"class": "md"}).img["src"]
		view = AddViews(self.refId, dialogPhase="Completion")
		ImageAnswer = AnswerObject(title="Y U NO:",lines=[AnswerObjectLine(image=ImageURL)])
		view1 = AnswerSnippet(answers=[ImageAnswer])
		view.views = [view1]
		self.sendRequestWithoutAnswer(view)
		self.complete_request()
    
	@register("de-DE", res['megusta']['de-DE'])
	@register("en-US", res['megusta']['en-US'])
	def get_megusta(self, speech, language):
		html = urllib.urlopen("http://memebase.com/category/me-gusta-2/")
		soup = BeautifulSoup(html)
		ImageURL = soup.find("div", {"class": "md"}).img["src"]
		view = AddViews(self.refId, dialogPhase="Completion")
		ImageAnswer = AnswerObject(title="Me gusta",lines=[AnswerObjectLine(image=ImageURL)])
		view1 = AnswerSnippet(answers=[ImageAnswer])
		view.views = [view1]
		self.sendRequestWithoutAnswer(view)
		self.complete_request()
    
	@register("de-DE", res['likeaboss']['de-DE'])
	@register("en-US", res['likeaboss']['en-US'])
	def get_likeaboss(self, speech, language):
		html = urllib.urlopen("http://memebase.com/category/like-a-boss-2/")
		soup = BeautifulSoup(html)
		ImageURL = soup.find("div", {"class": "md"}).img["src"]
		view = AddViews(self.refId, dialogPhase="Completion")
		ImageAnswer = AnswerObject(title="Like a Boss:",lines=[AnswerObjectLine(image=ImageURL)])
		view1 = AnswerSnippet(answers=[ImageAnswer])
		view.views = [view1]
		self.sendRequestWithoutAnswer(view)
		self.complete_request()
    
	@register("de-DE", res['likeasir']['de-DE'])
	@register("en-US", res['likeasir']['en-US'])
	def get_likeasir(self, speech, language):
		html = urllib.urlopen("http://memebase.com/category/like-a-sir/")
		soup = BeautifulSoup(html)
		ImageURL = soup.find("div", {"class": "md"}).img["src"]
		view = AddViews(self.refId, dialogPhase="Completion")
		ImageAnswer = AnswerObject(title="Like a Sir",lines=[AnswerObjectLine(image=ImageURL)])
		view1 = AnswerSnippet(answers=[ImageAnswer])
		view.views = [view1]
		self.sendRequestWithoutAnswer(view)
		self.complete_request()