#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# This process of enhancing plugins has been performed by Twisted.
#
# Unmerged versions of these plugins may function differently or lack some modification.
# All original headers and licensing information are labeled by the derived plugin name.
#
# Facebook Plugin
# Par Cédric Boverie (cedbv)

# This plugin requires a web server (like Apache) with SiriServer-WebAddons (a php script) installed.
# https://github.com/cedbv/SiriServer-WebAddons
# TODO: Use a db instead of facebook.conf
# TODO: documentation

# Twitter Plugin
# Par Cédric Boverie (cedbv)

# This plugin requires a web server (like Apache) with SiriServer-WebAddons (a php script) installed.
# https://github.com/cedbv/SiriServer-WebAddons
# TODO: Use a db instead of twitter.conf
# TODO: documentation

import re
from plugin import *
import ConfigParser
import urllib, urllib2

from siriObjects.uiObjects import *
from siriObjects.systemObjects import *

configFile = APIKeyForAPI("webaddons_path")+"/facebook.conf"
twitterConfigFile = APIKeyForAPI("webaddons_path")+"/twitter.conf"
webaddons_url = APIKeyForAPI("webaddons_url")

class Facebook(Plugin):

    res = {
        'facebook': {
            'en-US': u".*(Facebook)(.*)",
            'fr-FR': u".*(Facebook)(.*)",
        },
        'what_to_post': {
            'en-US': u"What do you want to post to Facebook?",
            'fr-FR': u"Que voulez-vous envoyer sur Facebook ?",
        },
        'success': {
            'en-US': u"I just posted \"{0}\" on Facebook.",
            'fr-FR': u"J'ai envoyé \"{0}\" sur Facebook.",
        },
        'failure': {
            'en-US': u"Something doesn't work as expected. Try again later.",
            'fr-FR': u"Quelque chose s'est mal passé. Veuillez réessayer plus tard.",
        },
        'not_ready': {
            'en-US': u"Your Facebook account is not configured. Please click the button below to allow me to access your account.",
            'fr-FR': u"Votre compte Facebook n'est pas configuré. Vous pouvez vous connecter avec ce bouton :",
        },
    }

    @register("fr-FR", res["facebook"]["fr-FR"])
    @register("en-US", res["facebook"]["en-US"])
    def post(self, speech, language, regex):

        if regex.group(2) != None:
            msg = regex.group(2).strip()
        else:
            msg = ""

        config = ConfigParser.RawConfigParser()
        config.read(configFile)
        try:
            access_token = config.get(self.assistant.assistantId,"access_token")
        except:
            access_token = ""

        if access_token != "":
            if msg == "":
                msg = self. ask(self.res["what_to_post"][language])
            try:
                url = 'https://graph.facebook.com/me/feed'
                data = urllib.urlencode({'access_token' : access_token,'message' : msg})
                req = urllib2.Request(url, data)
                response = urllib2.urlopen(req).read()
                self.say(self.res["success"][language].format(msg))
            except:
                self.say(self.res["failure"][language])
        else:
            self.say(self.res["not_ready"][language])
            url = webaddons_url+"/facebook.php?id=" + self.assistant.assistantId

            view = UIAddViews(self.refId)
            button = UIButton()
            if language == 'en-US':
                button.text = u"Connect to Facebook"
            if language == 'fr-FR':
                button.text = u"Connectez-vous sur Facebook"
            link = UIOpenLink("")
            link.ref = url.replace("//","")
            button.commands = [link]
            view.views = [button]
            self.send_object(view)
            
        self.complete_request()

try:
    import tweepy
except ImportError:
    raise NecessaryModuleNotFound("Tweepy library not found. Please install Tweepy library! e.g. sudo easy_install tweepy")

class Twitter(Plugin):
    
    res = {
        'twitter': {
            'en-US': u".*(Twitter|tweet|twit)(.*)",
            'fr-FR': u".*(Twitter|tweeter|tweet|twit|tuiteur)(.*)",
        },
        'what_to_tweet': {
            'en-US': u"What do you want to tweet?",
            'fr-FR': u"Que voulez-vous tweeter ?",
        },
        'what_to_tweet_say': {
            'en-US': u"What do you want to tweet?",
            'fr-FR': u"Que voulez-vous twiter ?",
        },
        'success': {
            'en-US': u"I just posted \"{0}\" on Twitter.",
            'fr-FR': u"J'ai envoyé \"{0}\" sur Twitter.",
        },
        'success_say': {
            'en-US': u"I just posted \"{0}\" on Twitter.",
            'fr-FR': u"J'ai envoyé \"{0}\" sur Twitteur.",
        },
        'failure': {
            'en-US': u"Something doesn't work as expected. Try again later.",
            'fr-FR': u"Quelque chose s'est mal passé. Veuillez réessayer plus tard.",
        },
        'not_ready': {
            'en-US': u"Your Twitter account is not configured. Please click the button below to allow me to access your account.",
            'fr-FR': u"Votre compte Twitter n'est pas configuré. Vous pouvez vous connecter avec ce bouton :",
        },
    }
    
    @register("fr-FR", res["twitter"]["fr-FR"])
    @register("en-US", res["twitter"]["en-US"])
    def tweet(self, speech, language, regex):
        
        if regex.group(2) != None:
            twitterMsg = regex.group(2).strip()
        else:
            twitterMsg = ""
        
        config = ConfigParser.RawConfigParser()
        config.read(twitterConfigFile)
        try:
            consumer_key = config.get("consumer","consumer_key")
            consumer_secret = config.get("consumer","consumer_secret")
            access_token = config.get(self.assistant.assistantId,"access_token")
            access_token_secret = config.get(self.assistant.assistantId,"access_token_secret")
        except:
            access_token = ""
            access_token_secret = ""
        
        if access_token != "" and access_token_secret != "":
            if twitterMsg == "":
                twitterMsg = self. ask(self.res["what_to_tweet"][language],self.res["what_to_tweet_say"][language])
            
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth)
            try:
                api.update_status(twitterMsg)
                self.say(self.res["success"][language].format(twitterMsg),self.res["success_say"][language].format(twitterMsg))
            except:
                self.say(self.res["failure"][language])
        else:
            self.say(self.res["not_ready"][language])
            url = webaddons_url+"/twitter.php?id=" + self.assistant.assistantId
            
            view = UIAddViews(self.refId)
            button = UIButton()
            if language == 'en-US':
                button.text = u"Connect to Twitter"
            if language == 'fr-FR':
                button.text = u"Connectez-vous sur Twitter"
            link = UIOpenLink("")
            link.ref = url.replace("//","")
            button.commands = [link]
            view.views = [button]
            self.send_object(view)
        
        self.complete_request()
