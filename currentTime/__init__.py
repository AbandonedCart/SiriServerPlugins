#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This process of enhancing plugins has been performed by Twisted.
#
# Unmerged versions of these plugins may function differently or lack some modification.
# All original headers and licensing information are labeled by the derived plugin name.
#
# Current Time Plugin
#
# Alarm Plugin
#
# Notes Plugin
#

from plugin import *

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

from siriObjects.clockObjects import ClockSnippet, ClockObject
from siriObjects.baseObjects import AceObject, ClientBoundCommand
from siriObjects.uiObjects import AddViews, AssistantUtteranceView
from siriObjects.systemObjects import DomainObject
from siriObjects.alarmObjects import *
from siriObjects.timerObjects import *


localizations = {
    "search":
    {
      "de-DE": [u"Es wird gesucht ..."], 
      "en-US": [u"Looking up ..."]
    },                  
    "currentTime": 
    {
     "de-DE": [u"Es ist @{fn#currentTime}"], 
     "en-US": [u"It is @{fn#currentTime}"]
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
    },
    'Alarm': {
        "settingAlarm": {
            "en-US": u"Setting the Alarm\u2026"
        }, "alarmWasSet": {
            "en-US": "Your alarm is set for {0}:{1} {2}."
        }, "alarmSetWithLabel": {
            "en-US": "Your alarm {0} {1} is set for {2}:{3} {4}."
        }
    },
    'Timer': {
        'durationTooBig': {
            'en-US': 'Sorry, I can only set timers up to 24 hours.'
        }, "settingTimer": {
            "en-US": u"Setting the timer\u2026"
        }, 'showTheTimer': {
            'en-US': u'Here\u2019s the timer:'
        }, 'timerIsAlreadyPaused': {
            'en-US': u'It\u2019s already paused.'
        }, "timerIsAlreadyRunning": {
            "en-US": u"Your timer\u2019s already running:"
        }, 'timerIsAlreadyStopped': {
            'en-US': u'It\u2019s already stopped.'
        }, 'timerWasPaused': {
            'en-US': u'It\u2019s paused.'
        }, 'timerWasReset': {
            'en-US': u'I\u2019ve canceled the timer.'
        }, 'timerWasResumed': {
            'en-US': u'It\u2019s resumed.'
        }, "timerWasSet": {
            "en-US": "Your timer is set for {0}."
        }, "wontSetTimer": {
            "en-US": "OK."
        }
    },
    "noteDefaults": {
        "searching": {
            "en-US": "Creating your note ..."
        }, 
        "result": {
            "en-US": "Here is your note:"
        },
        "nothing": {
            "en-US": "What should I note?"
        }, 
        "failure": {
            "en-US": "I cannot type your note right now."
        }
    }
}
res = {
        'setAlarm': {
            'en-US': '.*(wake up|alarm).*(at|for).* (0?[1-9]|1[012])([0-5]\d)?\s?([APap][mM])\s?(\bcalled|named|labeled\b)?\s?(([a-z0-9]{1,7}\s)?([a-z0-9]{1,7})\s?([a-z0-9]{1,7}))?'
        },
        'articles': {
            'en-US': 'a|an|the'
        }, 'pauseTimer': {
            'en-US': '.*(pause|freeze|hold).*timer'
        }, 'resetTimer': {
            'en-US': '.*(cancel|reset|stop).*timer'
        }, 'resumeTimer': {
            'en-US': '.*(resume|thaw|continue).*timer'
        }, 'setTimer': {
            # 'en-US': '.*timer[^0-9]*(((([0-9/ ]*|a|an|the)\s+(seconds?|secs?|minutes?|mins?|hours?|hrs?))\s*(and)?)+)'
            'en-US': '.*timer[^0-9]*(?P<length>([0-9/ ]|seconds?|secs?|minutes?|mins?|hours?|hrs?|and|the|an|a){2,})'
        }, 'showTimer': {
            'en-US': '.*(show|display|see).*timer'
        }, 'timerLength': {
            'en-US': '([0-9][0-9 /]*|an|a|the)\s+(seconds?|secs?|minutes?|mins?|hours?|hrs?)'
        }
    }


class currentTime(Plugin):

    @register("en-US", res['setAlarm']['en-US'])
    def setAlarm(self, speech, language):
        alarmString = re.match(res['setAlarm'][language], speech, re.IGNORECASE)
        
        alarmHour = int(alarmString.group(3))
        alarm24Hour = alarmHour
        alarmMinutes = alarmString.group(4)
        alarmAMPM = alarmString.group(5)
        alarmLabelExists = alarmString.group(6)
        
        #check if we are naming the alarm
        if alarmLabelExists == None:
            alarmLabel = None
        else:
            alarmLabel = alarmString.group(5)
        
        #the siri alarm object requires 24 hour clock
        if (alarmAMPM == "pm" and alarmHour != 12):
            alarm24Hour += 12

        if alarmMinutes == None:
            alarmMinutes = "00"
        else:
            alarmMinutes = int(alarmMinutes.strip())

        view = AddViews(self.refId, dialogPhase="Reflection")
        view.views = [
            AssistantUtteranceView(
                speakableText=localizations['Alarm']['settingAlarm'][language],
                dialogIdentifier="Alarm#settingAlarm")]
        self.sendRequestWithoutAnswer(view)

        #create the alarm
        alarm = AlarmObject(alarmLabel, int(alarmMinutes), alarm24Hour, None, 1)
        response = self.getResponseForRequest(AlarmCreate(self.refId, alarm))
        
        print(localizations['Alarm']['alarmWasSet'][language].format(alarmHour, alarmMinutes, alarmAMPM))
        view = AddViews(self.refId, dialogPhase="Completion")
        
        if alarmLabel == None:
            view1 = AssistantUtteranceView(speakableText=localizations['Alarm']['alarmWasSet'][language].format(alarmHour, alarmMinutes, alarmAMPM), dialogIdentifier="Alarm#alarmWasSet")
        else:
            view1 = AssistantUtteranceView(speakableText=localizations['Alarm']['alarmSetWithLabel'][language].format(alarmLabelExists, alarmLabel, alarmHour, alarmMinutes, alarmAMPM), dialogIdentifier="Alarm#alarmSetWithLabel")
        
        view2 = AlarmSnippet(alarms=[alarm])
        view.views = [view1, view2]
        self.sendRequestWithoutAnswer(view)
        self.complete_request()

    @register("en-US",u".*wake.* up (within|in).* ([0-5][0-9]|[0-9]) (hour|hours|minutes)")
    def Nap(self, speech, language):
        global time
        currenttime = time.time()
        hour = time.strftime('%H', time.localtime(currenttime))

        if hour >= 12:
            alarmAMPM = 'PM'
            alarmAMPM2 = u'hour'
            alarmAMPM3 = u'hours'
            alarmAMPM4 = u'minutes'
        else:
            alarmAMPM = 'AM'

        c = re.search(u"hour|hours|minutes", speech)
        d = c.group() 
        a = re.search('([0-5][0-9]|[0-9])', speech)
        b = a.group()

        if d == (u"minutes"):
            currenttime = time.time()
            alarmHour = time.strftime('%H', time.localtime(currenttime + int(b) * 60))
            alarmMinutes = time.strftime('%M', time.localtime(currenttime + int(b) * 60))

        if d == (u"hour"):
            currenttime = time.time()
            alarmHour = time.strftime('%H', time.localtime(currenttime + int(b) * 60 * 60))
            alarmMinutes = time.strftime('%M', time.localtime(currenttime + int(b) * 60 * 60))

        if d ==(u"hours"):
            currenttime = time.time()
            alarmHour = time.strftime('%H', time.localtime(currenttime + int(b) * 60 * 60))
            alarmMinutes = time.strftime('%M', time.localtime(currenttime + int(b) * 60 * 60))

        if int(alarmHour) >= 13:
            alarmHour12 = (int(alarmHour) - 12)
        else:
            alarmHour12 = alarmHour

        view = AddViews(self.refId, dialogPhase="Reflection")
        view.views = [
            AssistantUtteranceView(
                speakableText=Nap.localizations['Alarm']['settingAlarm'][language],
                dialogIdentifier="Alarm#settingAlarm")]
        self.sendRequestWithoutAnswer(view)

        #create the alarm
        alarmLabel = None
        alarm = AlarmObject(alarmLabel, int(alarmMinutes), int(alarmHour), None, 1)
        response = self.getResponseForRequest(AlarmCreate(self.refId, alarm))

        print(Nap.localizations['Alarm']['alarmWasSet'][language].format(alarmHour12, alarmMinutes, alarmAMPM))
        view = AddViews(self.refId, dialogPhase="Completion")

        if alarmLabel == None:
            view1 = AssistantUtteranceView(speakableText=Nap.localizations['Alarm']['alarmWasSet'][language].format(alarmHour12, alarmMinutes, alarmAMPM), dialogIdentifier="Alarm#alarmWasSet")
        else:
            view1 = AssistantUtteranceView(speakableText=Nap.localizations['Alarm']['alarmSetWithLabel'][language].format(alarmLabelExists, alarmLabel, alarmHour12, alarmMinutes, alarmAMPM), dialogIdentifier="Alarm#alarmSetWithLabel")

        view2 = AlarmSnippet(alarms=[alarm])
        view.views = [view1, view2]
        self.sendRequestWithoutAnswer(view)
        self.complete_request()

    @register("en-US", res['setTimer']['en-US'])
    def setTimer(self, speech, language):
        m = re.match(res['setTimer'][language], speech, re.IGNORECASE)
        timer_length = m.group('length')
        duration = parse_timer_length(timer_length, language)
        
        view = AddViews(self.refId, dialogPhase="Reflection")
        view.views = [
                      AssistantUtteranceView(
                                             speakableText=localizations['Timer']['settingTimer'][language],
                                             dialogIdentifier="Timer#settingTimer")]
        self.sendRequestWithoutAnswer(view)
        
        # check the current state of the timer
        response = self.getResponseForRequest(TimerGet(self.refId))
        if response['class'] == 'CancelRequest':
            self.complete_request()
            return
        timer_properties = response['properties']['timer']['properties']
        timer = TimerObject(timerValue=timer_properties['timerValue'],
                            state=timer_properties['state'])
        
        if timer.state == "Running":
            # timer is already running!
            view = AddViews(self.refId, dialogPhase="Completion")
            view1 = AssistantUtteranceView(speakableText=localizations['Timer']['timerIsAlreadyRunning'][language], dialogIdentifier="Timer#timerIsAlreadyRunning")
            view2 = TimerSnippet(timers=[timer], confirm=True)
            view.views = [view1, view2]
            utterance = self.getResponseForRequest(view)
            #if response['class'] == 'StartRequest':
            view = AddViews(self.refId, dialogPhase="Reflection")
            view.views = [AssistantUtteranceView(speakableText=localizations['Timer']['settingTimer'][language], dialogIdentifier="Timer#settingTimer")]
            self.sendRequestWithoutAnswer(view)
            
            if re.match('\^timerConfirmation\^=\^no\^', utterance):
                # user canceled
                view = AddViews(self.refId, dialogPhase="Completion")
                view.views = [AssistantUtteranceView(speakableText=localizations['Timer']['wontSetTimer'][language], dialogIdentifier="Timer#wontSetTimer")]
                self.sendRequestWithoutAnswer(view)
                self.complete_request()
                return
            else:
                # user wants to set the timer still - continue on
                pass
        
        if duration > 24 * 60 * 60:
            view = AddViews(self.refId, dialogPhase='Clarification')
            view.views = [AssistantUtteranceView(speakableText=localizations['Timer']['durationTooBig'][language], dialogIdentifier='Timer#durationTooBig')]
            self.sendRequestWithoutAnswer(view)
            self.complete_request()
            return
        
        # start a new timer
        timer = TimerObject(timerValue = duration, state = "Running")
        response = self.getResponseForRequest(TimerSet(self.refId, timer=timer))
        
        print(localizations['Timer']['timerWasSet'][language].format(timer_length))
        view = AddViews(self.refId, dialogPhase="Completion")
        view1 = AssistantUtteranceView(speakableText=localizations['Timer']['timerWasSet'][language].format(timer_length), dialogIdentifier="Timer#timerWasSet")
        view2 = TimerSnippet(timers=[timer])
        view.views = [view1, view2]
        self.sendRequestWithoutAnswer(view)
        self.complete_request()
    
    @register("en-US", res['resetTimer']['en-US'])
    def resetTimer(self, speech, language):
        response = self.getResponseForRequest(TimerGet(self.refId))
        timer_properties = response['properties']['timer']['properties']
        timer = TimerObject(timerValue = timer_properties['timerValue'], state = timer_properties['state'])
        
        if timer.state == "Running" or timer.state == 'Paused':
            response = self.getResponseForRequest(TimerCancel(self.refId))
            if response['class'] == "CancelCompleted":
                view = AddViews(self.refId, dialogPhase="Completion")
                view.views = [AssistantUtteranceView(speakableText=localizations['Timer']['timerWasReset'][language], dialogIdentifier="Timer#timerWasReset")]
                self.sendRequestWithoutAnswer(view)
            self.complete_request()
        else:
            view = AddViews(self.refId, dialogPhase="Completion")
            view1 = AssistantUtteranceView(speakableText=localizations['Timer']['timerIsAlreadyStopped'][language], dialogIdentifier="Timer#timerIsAlreadyStopped")
            view2 = TimerSnippet(timers=[timer])
            view.views = [view1, view2]
            
            self.sendRequestWithoutAnswer(view)
            self.complete_request()
    
    @register("en-US", res['resumeTimer']['en-US'])
    def resumeTimer(self, speech, language):
        response = self.getResponseForRequest(TimerGet(self.refId))
        timer_properties = response['properties']['timer']['properties']
        timer = TimerObject(timerValue = timer_properties['timerValue'], state = timer_properties['state'])
        
        if timer.state == "Paused":
            response = self.getResponseForRequest(TimerResume(self.refId))
            if response['class'] == "ResumeCompleted":
                view = AddViews(self.refId, dialogPhase="Completion")
                view1 = AssistantUtteranceView(speakableText=localizations['Timer']['timerWasResumed'][language], dialogIdentifier="Timer#timerWasResumed")
                view2 = TimerSnippet(timers=[timer])
                view.views = [view1, view2]
                self.sendRequestWithoutAnswer(view)
            self.complete_request()
        else:
            view = AddViews(self.refId, dialogPhase="Completion")
            view1 = AssistantUtteranceView(speakableText=localizations['Timer']['timerIsAlreadyStopped'][language], dialogIdentifier="Timer#timerIsAlreadyStopped")
            view2 = TimerSnippet(timers=[timer])
            view.views = [view1, view2]
            
            self.sendRequestWithoutAnswer(view)
            self.complete_request()
    
    @register("en-US", res['pauseTimer']['en-US'])
    def pauseTimer(self, speech, language):
        response = self.getResponseForRequest(TimerGet(self.refId))
        timer_properties = response['properties']['timer']['properties']
        timer = TimerObject(timerValue = timer_properties['timerValue'], state = timer_properties['state'])
        
        if timer.state == "Running":
            response = self.getResponseForRequest(TimerPause(self.refId))
            if response['class'] == "PauseCompleted":
                view = AddViews(self.refId, dialogPhase="Completion")
                view.views = [AssistantUtteranceView(speakableText=localizations['Timer']['timerWasPaused'][language], dialogIdentifier="Timer#timerWasPaused")]
                self.sendRequestWithoutAnswer(view)
            self.complete_request()
        elif timer.state == "Paused":
            view = AddViews(self.refId, dialogPhase="Completion")
            view1 = AssistantUtteranceView(speakableText=localizations['Timer']['timerIsAlreadyPaused'][language], dialogIdentifier="Timer#timerIsAlreadyPaused")
            view2 = TimerSnippet(timers=[timer])
            view.views = [view1, view2]
            
            self.sendRequestWithoutAnswer(view)
            self.complete_request()
        else:
            view = AddViews(self.refId, dialogPhase="Completion")
            view1 = AssistantUtteranceView(speakableText=localizations['Timer']['timerIsAlreadyStopped'][language], dialogIdentifier="Timer#timerIsAlreadyStopped")
            view2 = TimerSnippet(timers=[timer])
            view.views = [view1, view2]
            
            self.sendRequestWithoutAnswer(view)
            self.complete_request()
    
    @register("en-US", res['showTimer']['en-US'])
    def showTimer(self, speech, language):
        response = self.getResponseForRequest(TimerGet(self.refId))
        timer_properties = response['properties']['timer']['properties']
        timer = TimerObject(timerValue = timer_properties['timerValue'], state = timer_properties['state'])
        
        view = AddViews(self.refId, dialogPhase="Summary")
        view1 = AssistantUtteranceView(speakableText=localizations['Timer']['showTheTimer'][language], dialogIdentifier="Timer#showTheTimer")
        view2 = TimerSnippet(timers=[timer])
        view.views = [view1, view2]
        self.sendRequestWithoutAnswer(view)
        self.complete_request()


    @register("de-DE", "(Welcher Tag.*)|(Welches Datum.*)")
    @register("en-US", "(What Day.*)|(What.*Date.*)")
    @register("en-GB", "(What Day.*)|(What.*Date.*)")
    @register("fr-FR", u"(Quel jour.*)|(Quel.*date.*)")
    def ttm_say_date(self, speech, language):
        now = date.today()
        if language == 'de-DE':
            locale.setlocale(locale.LC_ALL, 'de_DE')
            result=now.strftime("Heute ist %A, der %d.%m.%Y (Kalenderwoche: %W)")
            self.say(result)
        elif language == 'fr-FR':
            # I have only belgian locale with utf-8... so let Python find the most appropriate for us
            locale.setlocale(locale.LC_ALL, '')
            result=now.strftime(u"Aujourd'hui, nous sommes le %A, %d %m %Y.")
            self.say(result)
        else:
            locale.setlocale(locale.LC_ALL, 'en_US')
            result=now.strftime("Today is %A the %d.%m.%Y (Week: %W)")
            self.say(result)
        self.complete_request()

class NoteSnippet(AceObject):

    def __init__(self, notes=None):
        super(NoteSnippet, self).__init__("Snippet", "com.apple.ace.note")
        self.notes = notes if notes != None else []
    
    def to_plist(self):
        self.add_property('notes')
        return super(NoteSnippet, self).to_plist()


class NoteObject(AceObject):
    def __init__(self, contents="", identifier=""):
        super(NoteObject, self).__init__("Object", "com.apple.ace.note")
        self.contents = contents
        self.identifier = identifier
    def to_plist(self):
        self.add_property('contents')
        self.add_property('identifier')
        return super(NoteObject, self).to_plist()

class Create(ClientBoundCommand):
    def __init__(self, refId=None, aceId=None, contents=""):
        super(Create, self).__init__("Create", "com.apple.ace.note", None, None)
        self.contents = contents
        self.aceId= aceId if aceId != None else str.upper(str(uuid4()))
        self.refId = refId if refId != None else str.upper(str(uuid4()))
    
    def to_plist(self):
    	self.add_item('aceId')
        self.add_item('refId')
        self.add_property('contents')
        return super(Create, self).to_plist()

class note(Plugin):

    @register("en-US", "(Create|Write|Save|Take|New).*note [a-zA-Z0-9]+")
    def writeNote(self, speech, language):
        content_raw = re.match(".*note ([a-zA-Z0-9, ]+)$", speech, re.IGNORECASE)
        if content_raw == None:
            view_initial = AddViews(self.refId, dialogPhase="Reflection")
            view_initial.views = [AssistantUtteranceView(text=note.localizations['noteDefaults']['nothing'][language], speakableText=note.localizations['noteDefaults']['nothing'][language], dialogIdentifier="Note#failed")]
            self.sendRequestWithoutAnswer(view_initial)
        else:
            view_initial = AddViews(self.refId, dialogPhase="Reflection")
            view_initial.views = [AssistantUtteranceView(text=note.localizations['noteDefaults']['searching'][language], speakableText=note.localizations['noteDefaults']['searching'][language], dialogIdentifier="Note#creating")]
            self.sendRequestWithoutAnswer(view_initial)
            
            content_raw = content_raw.group(1).strip()
            if "saying" in content_raw:
                split = content_raw.split(' ')
                if split[0] == "saying":
                    split.pop(0)
                    content_raw = ' '.join(map(str, split))
            if "that" in content_raw:
                split = content_raw.split(' ')
                if split[0] == "that":
                    split.pop(0)
                    content_raw = ' '.join(map(str, split))
            if "for" in content_raw:
                split = content_raw.split(' ')
                if split[0] == "for":
                    split.pop(0)
                    content_raw = ' '.join(map(str, split))
            
            note_create = Create()
            note_create.contents = content_raw
            note_return = self.getResponseForRequest(note_create)
            
            view = AddViews(self.refId, dialogPhase="Summary")
            view1 = AssistantUtteranceView(text=note.localizations['noteDefaults']['result'][language], speakableText=note.localizations['noteDefaults']['result'][language], dialogIdentifier="Note#created")
            
            note_ = NoteObject()
            note_.contents = content_raw
            note_.identifier = note_return["properties"]["identifier"]
            
            view2 = NoteSnippet(notes=[note_])
            view.views = [view1, view2]
            self.sendRequestWithoutAnswer(view)
            self.complete_request()

    def parse_number(s, language):
        # check for simple article usage (a, an, the)
        if re.match(res['articles'][language], s, re.IGNORECASE):
            return 1
        f = 0
        for part in s.split(' '):
            f += float(Fraction(part))
        return f
    
    
    def parse_timer_length(t, language):
        seconds = None
        for m in re.finditer(res['timerLength'][language], t, re.IGNORECASE):
            print(m.groups())
            seconds = seconds or 0
            unit = m.group(2)[0]
            count = parse_number(m.group(1), language)
            if unit == 'h':
                seconds += count * 3600
            elif unit == 'm':
                seconds += count * 60
            elif unit == 's':
                seconds += count
            else:
                seconds += count * 60
        
        return seconds
