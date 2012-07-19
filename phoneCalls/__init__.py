#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# This process of enhancing plugins has been performed by Twisted.
#
# Unmerged versions of these plugins may function differently or lack some modification.
# All original headers and licensing information are labeled by the derived plugin name.
#
# Phone Call Plugin
#
# No header included, courtesy of Eichhoernchen
#
# Contacts Plugin
#
# Modded By Sebeqwerty <sebeqwerty@live.ru>
# 

import re

from plugin import *
from siriObjects.baseObjects import ObjectIsCommand, RequestCompleted
from siriObjects.contactObjects import PersonSearch, PersonSearchCompleted
from siriObjects.phoneObjects import PhoneCall
from siriObjects.systemObjects import SendCommands, StartRequest, ResultCallback, \
    Person, PersonAttribute, DomainObjectRetrieve, DomainObjectRetrieveCompleted, \
    DomainObjectUpdate, DomainObjectUpdateCompleted, DomainObjectCommit, \
    DomainObjectCommitCompleted
from siriObjects.uiObjects import AddViews, DisambiguationList, ListItem, \
    AssistantUtteranceView

responses = {
'notFound': 
    {'de-DE': u"Entschuldigung, ich konnte niemanden in deinem Telefonbuch finden der so heißt",
     'en-US': u"Sorry, I did not find a match in your phone book"
    },
'devel':
    {'de-DE': u"Entschuldigung, aber diese Funktion befindet sich noch in der Entwicklungsphase",
     'en-US': u"Sorry this feature is still under development"
    },
 'select':
    {'de-DE': u"Wen genau?", 
     'en-US': u"Which one?"
    },
'selectNumber':
    {'de-DE': u"Welche Telefonnummer für {0}",
     'en-US': u"Which phone one for {0}"
    },
'callPersonSpeak':
    {'de-DE': u"Rufe {0}, {1} an.",
     'en-US': u"Calling {0}, {1}."
    },
'callPerson': 
    {'de-DE': u"Rufe {0}, {1} an: {2}",
     'en-US': u"Calling {0}, {1}: {2}"
    }
}

numberTypesLocalized= {
'_$!<Mobile>!$_': {'en-US': u"mobile", 'de-DE': u"Handynummer"},
'iPhone': {'en-US': u"iPhone", 'de-DE': u"iPhone-Nummer"},
'_$!<Home>!$_': {'en-US': u"home", 'de-DE': u"Privatnummer"},
'_$!<Work>!$_': {'en-US': u"work", 'de-DE': u"Geschäftsnummer"},
'_$!<Main>!$_': {'en-US': u"main", 'de-DE': u"Hauptnummer"},
'_$!<HomeFAX>!$_': {'en-US': u"home fax", 'de-DE': u'private Faxnummer'},
'_$!<WorkFAX>!$_': {'en-US': u"work fax", 'de-DE': u"geschäftliche Faxnummer"},
'_$!<OtherFAX>!$_': {'en-US': u"_$!<OtherFAX>!$_", 'de-DE': u"_$!<OtherFAX>!$_"},
'_$!<Pager>!$_': {'en-US': u"pager", 'de-DE': u"Pagernummer"},
'_$!<Other>!$_':{'en-US': u"other phone", 'de-DE': u"anderes Telefon"}
}

namesToNumberTypes = {
'de-DE': {'mobile': "_$!<Mobile>!$_", 'handy': "_$!<Mobile>!$_", 'zuhause': "_$!<Home>!$_", 'privat': "_$!<Home>!$_", 'arbeit': "_$!<Work>!$_"},
'en-US': {'work': "_$!<Work>!$_",'home': "_$!<Home>!$_", 'mobile': "_$!<Mobile>!$_"}
}

speakableDemitter={
'en-US': u", or ",
'de-DE': u', oder '}

errorNumberTypes= {
'de-DE': u"Ich habe dich nicht verstanden, versuch es bitte noch einmal.",
'en-US': u"Sorry, I did not understand, please try again."
}

errorNumberNotPresent= {
'de-DE': u"Ich habe diese {0} von {1} nicht, aber eine andere.",
'en-US': u"Sorry, I don't have a {0} number from {1}, but another."
}

errorOnCallResponse={'en-US':
                     [{'dialogIdentifier':u"PhoneCall#airplaneMode",
                       'text': u"Your phone is in airplane mode.",
                       'code': 1201},
                      {'dialogIdentifier': u"PhoneCall#networkUnavailable",
                       'text': u"Uh, I can't seem to find a good connection. Please try your phone call again when you have cellular access.",
                       'code': 1202},
                      {'dialogIdentifier': u"PhoneCall#invalidNumber",
                       'text': u"Sorry, I can't call this number.",
                       'code': 1203},
                      {'dialogIdentifier': u"PhoneCall#fatalResponse",
                       'text': u"Oh oh, I can't make your phone call.",
                       'code': -1}],
                     'de-DE':
                     [{'dialogIdentifier':u"PhoneCall#airplaneMode",
                       'text': u"Dein Telefon ist im Flugmodus.",
                       'code': 1201},
                      {'dialogIdentifier': u"PhoneCall#networkUnavailable",
                       'text': u"Oh je! Ich kann im Moment keine gute Verbindung bekommen. Versuch es noch einmal, wenn du wieder Funkempfang hast.",
                       'code': 1202},
                      {'dialogIdentifier': u"PhoneCall#invalidNumber",
                       'text': u"Ich kann diese Nummer leider nicht anrufen.",
                       'code': 1203},
                      {'dialogIdentifier': u"PhoneCall#fatalResponse",
                       'text': u"Tut mir leid, Ich, ich kann momentan keine Anrufe t�tigen.",
                       'code': -1}]
}

class phonecallPlugin(Plugin):

    def searchUserByName(self, personToLookup):
        search = PersonSearch(self.refId)
        search.scope = PersonSearch.ScopeLocalValue
        search.name = personToLookup
        answerObj = self.getResponseForRequest(search)
        if ObjectIsCommand(answerObj, PersonSearchCompleted):
            answer = PersonSearchCompleted(answerObj)
            return answer.results if answer.results != None else []
        else:
            raise StopPluginExecution("Unknown response: {0}".format(answerObj))
        return []
           
    def getNumberTypeForName(self, name, language):
        # q&d
        if name != None:
            if name.lower() in namesToNumberTypes[language]:
                return namesToNumberTypes[language][name.lower()]
            else:
                for key in numberTypesLocalized.keys():
                    if numberTypesLocalized[key][language].lower() == name.lower():
                        return numberTypesLocalized[key][language]
        return name
    
    def findPhoneForNumberType(self, person, numberType, language):         
        # first check if a specific number was already requested
        phoneToCall = None
        if numberType != None:
            # try to find the phone that fits the numberType
            phoneToCall = filter(lambda x: x.label == numberType, person.phones)
        else:
            favPhones = filter(lambda y: y.favoriteVoice if hasattr(y, "favoriteVoice") else False, person.phones)
            if len(favPhones) == 1:
                phoneToCall = favPhones[0]
        if phoneToCall == None:
            # lets check if there is more than one number
            if len(person.phones) == 1:
                if numberType != None:
                    self.say(errorNumberNotPresent.format(numberTypesLocalized[numberType][language], person.fullName))
                phoneToCall = person.phones[0]
            else:
                # damn we need to ask the user which one he wants...
                while(phoneToCall == None):
                    rootView = AddViews(self.refId, temporary=False, dialogPhase="Clarification", scrollToTop=False, views=[])
                    sayit = responses['selectNumber'][language].format(person.fullName)
                    rootView.views.append(AssistantUtteranceView(text=sayit, speakableText=sayit, listenAfterSpeaking=True,dialogIdentifier="ContactDataResolutionDucs#foundAmbiguousPhoneNumberForContact"))
                    lst = DisambiguationList(items=[], speakableSelectionResponse="OK...", listenAfterSpeaking=True, speakableText="", speakableFinalDemitter=speakableDemitter[language], speakableDemitter=", ",selectionResponse="OK...")
                    rootView.views.append(lst)
                    for phone in person.phones:
                        numberType = numberTypesLocalized[phone.label][language] if phone.label in numberTypesLocalized else phone.label
                        item = ListItem()
                        item.title = ""
                        item.text = u"{0}: {1}".format(numberType, phone.number)
                        item.selectionText = item.text
                        item.speakableText = u"{0}  ".format(numberType)
                        item.object = phone
                        item.commands.append(SendCommands(commands=[StartRequest(handsFree=False, utterance=numberType)]))
                        lst.items.append(item)
                    answer = self.getResponseForRequest(rootView)
                    numberType = self.getNumberTypeForName(answer, language)
                    if numberType != None:
                        matches = filter(lambda x: x.label == numberType, person.phones)
                        if len(matches) == 1:
                            phoneToCall = matches[0]
                        else:
                            self.say(errorNumberTypes[language])
                    else:
                        self.say(errorNumberTypes[language])
        return phoneToCall
             
    
    def call(self, phone, person, language):
        root = ResultCallback(commands=[])
        rootView = AddViews("", temporary=False, dialogPhase="Completion", views=[])
        root.commands.append(rootView)
        rootView.views.append(AssistantUtteranceView(text=responses['callPerson'][language].format(person.fullName, numberTypesLocalized[phone.label][language], phone.number), speakableText=responses['callPersonSpeak'][language].format(person.fullName, numberTypesLocalized[phone.label][language]), dialogIdentifier="PhoneCall#initiatePhoneCall", listenAfterSpeaking=False))
        rootView.callbacks = []
        
        # create some infos of the target
        personAttribute=PersonAttribute(data=phone.number, displayText=person.fullName, obj=Person())
        personAttribute.object.identifer = person.identifier
        call = PhoneCall("", recipient=phone.number, faceTime=False, callRecipient=personAttribute)
        
        rootView.callbacks.append(ResultCallback(commands=[call]))
        
        call.callbacks = []
        # now fill in error messages (airplanemode, no service, invalidNumber, fatal)
        for i in range(4):
            errorRoot = AddViews(None, temporary=False, dialogPhase="Completion", scrollToTop=False, views=[])
            errorRoot.views.append(AssistantUtteranceView(text=errorOnCallResponse[language][i]['text'], speakableText=errorOnCallResponse[language][i]['text'], dialogIdentifier=errorOnCallResponse[language][i]['dialogIdentifier'], listenAfterSpeaking=False))
            call.callbacks.append(ResultCallback(commands=[errorRoot], code=errorOnCallResponse[language][i]['code']))
            
        self.complete_request([root])

    def presentPossibleUsers(self, persons, language):
        root = AddViews(self.refId, False, False, "Clarification", [], [])
        root.views.append(AssistantUtteranceView(responses['select'][language], responses['select'][language], "ContactDataResolutionDucs#disambiguateContact", True))
        lst = DisambiguationList([], "OK!", True, "OK!", speakableDemitter[language], ", ", "OK!")
        root.views.append(lst)
        for person in persons:
            item = ListItem(person.fullName, person.fullName, [], person.fullName, person)
            item.commands.append(SendCommands([StartRequest(False, "^phoneCallContactId^=^urn:ace:{0}".format(person.identifier))]))
            lst.items.append(item)
        return root
    
    @register("de-DE", "ruf. (?P<name>[\w ]+?)( (?P<type>arbeit|zuhause|privat|mobil|handy.*|iPhone.*|pager))? an$")
    @register("en-US", "(make a )?call (to )?(?P<name>[\w ]+?)( (?P<type>work|home|mobile|main|iPhone|pager))?$")
    def makeCall(self, speech, language, regex):
        personToCall = regex.group('name')
        numberType = str.lower(regex.group('type')) if type in regex.groupdict() else None
        numberType = self.getNumberTypeForName(numberType, language)
        persons = self.searchUserByName(personToCall)
        personToCall = None
        if len(persons) > 0:
            if len(persons) == 1:
                personToCall = persons[0]
            else:
                identifierRegex = re.compile("\^phoneCallContactId\^=\^urn:ace:(?P<identifier>.*)")
                #  multiple users, ask user to select
                while(personToCall == None):
                    strUserToCall = self.getResponseForRequest(self.presentPossibleUsers(persons, language))
                    self.logger.debug(strUserToCall)
                    # maybe the user clicked...
                    identifier = identifierRegex.match(strUserToCall)
                    if identifier:
                        strUserToCall = identifier.group('identifier')
                        self.logger.debug(strUserToCall)
                    for person in persons:
                        if person.fullName == strUserToCall or person.identifier == strUserToCall:
                            personToCall = person
                    if personToCall == None:
                        # we obviously did not understand him.. but probably he refined his request... call again...
                        self.say(errorNumberTypes[language])
                    
            if personToCall != None:
                self.call(self.findPhoneForNumberType(personToCall, numberType, language), personToCall, language)
                return # complete_request is done there
        self.say(responses['notFound'][language])                         
        self.complete_request()

    @register("en-US", "(What's|Whats) ?(?P<contact>[\w |']*) ?(?P<attribute>name|telephone|telephone number|phone number|email|email address|address|birthday)(\s|$)")
    def myContactName(self, speech, language, regex):
      
      attributeToFind = regex.group('attribute')	
      if attributeToFind.count('number') > 0:
        attributeToFind = 'telephone'	  
		
      contact = regex.group('contact')	
      if contact.count('tele') > 0:
        contact = contact.replace('tele','')
      if contact.count('email') > 0:
        contact = contact.replace('email','')
        attributeToFind = 'email'	  

      personToFind = contact
      if personToFind.count('\'s') > 0:
        personToFind = personToFind.replace('\'s','')
      else:
        personToFind = personToFind.rstrip(' s')

      if len(personToFind) < 3:
          personToFind = 'None'
    
#      self.logger.debug('Person & Attribute: ')	
#      self.logger.debug(personToFind)	
#      self.logger.debug(attributeToFind)	
	
      contactSearch = ABPersonSearch(self.refId)
      contactSearch.scope = "Local"
	  
      if personToFind == 'None':
        contactSearch.me = True
        personToFind = 'my  '
      else:
        contactSearch.name = personToFind
            
      names = 'Contact Not Found'	  

      answer = self.getResponseForRequest(contactSearch)
      if ObjectIsCommand(answer, ABPersonSearchCompleted):
          results = ABPersonSearchCompleted(answer)
          if results.results != None:
            persons = results.results
            identfind = results.results[0]
            contactIdentifier = identfind.identifier 
            personToFind = personToFind.rstrip(' ')
            if len(persons) > 1:
              personGT1 = 'True'
              names = personToFind.replace('my ','Your ')
              names = names + 's\' ' + attributeToFind
            else:
              personGT1 = 'False'
              names = personToFind.replace('my ','Your ')
              if len(personToFind) > 3:
                names = names + '\'s ' + attributeToFind
              else:
                names = 'Your ' + attributeToFind

            if attributeToFind == 'name':
              if len(persons) > 1:
                names = names + 's are:\n\n'
              else:
                names = names + ' is:\n'			  
            else:			
              if len(persons) > 1:
                names = ''

            for indexPerson in range (len(persons)):
              Person = persons[indexPerson]
              if attributeToFind == 'name':
                if contact.count('my') > 0:
                  if personGT1 == 'True':
                    names = names + Person.fullName + '\n(' + Person.nickName + ')' + '\n\n'
                  else:
                    names = names + Person.fullName + '\n'
				
              if attributeToFind == 'telephone':
                try:
                  if personGT1 == 'False':
                    if indexPerson == 0:
                      if len(Person.phones) > 1:
                        names = names + 's are:\n\n'
                      else:
                        names = names + ' is:\n\n' 			  				  				  
                  if personGT1 == 'True':
                    if contact.count('my') > 0:
                      names = names + '\n' + Person.fullName + '\n(' + Person.nickName + ')' + '\n'                    
                    else:
                      names = names + '\n' + Person.fullName + ':\n'                    
                  for indexTelephone in range (len(Person.phones)):
                    numberToCall = Person.phones[indexTelephone]
                    typeToCall = self.getNameFromNumberType(numberToCall.label, language)
                    names = names + typeToCall + ': ' + numberToCall.number + '\n'
                except:
                  if personGT1 == 'True':
                    names = names + 'No Telephone found.\n'		
                  else:
                    names = 'No Telephone found.'		
				  
              if attributeToFind == 'email':
                try:
                  if personGT1 == 'False':
                    if indexPerson == 0:
                      if len(Person.emails) > 1:
                        names = names + 's are:\n\n'
                      else:
                        names = names + ' is:\n\n' 			  				  				  
                  if personGT1 == 'True':
                    if contact.count('my') > 0:
                      names = names + '\n' + Person.fullName + '\n(' + Person.nickName + ')'  + '\n'                    
                    else:
                      names = names + '\n' + Person.fullName + ':\n'                    
                  for indexEmail in range (len(Person.emails)):
                    email = Person.emails[indexEmail]
                    names = names + email.emailAddress + '\n'
                except:
                  if personGT1 == 'True':
                    names = names + 'No Email Address found.\n'		
                  else:
                    names = 'No Email Address found.'		
				  
              if attributeToFind == 'address':
                try:
                  if personGT1 == 'False':
                    if indexPerson == 0:
                      if len(Person.addresses) > 1:
                        names = names + 'es are:\n\n'
                      else:
                        names = names + ' is:\n\n' 			  				  				  
                  if personGT1 == 'True':
                    if contact.count('my') > 0:
                      names = names + '\n' + Person.fullName + '\n(' + Person.nickName + ')' +'\n'                    
                    else:
                      names = names + '\n' + Person.fullName + ':\n'                    
                  for indexAddress in range (len(Person.addresses)):
                    address = Person.addresses[indexAddress]
                    typeToCall = self.getNameFromNumberType(address.label, language)
                    names = names + typeToCall + ':\n' + address.street + '\n' + address.city + ', ' + address.stateCode + ' ' + address.postalCode + '\n\n'
                except:
                  if personGT1 == 'True':
                    names = names + 'No Address found.\n'		
                  else:
                    names = 'No Address found.'		
				  
              if attributeToFind == 'birthday':                			  
                try:			  
                  if personGT1 == 'False':
                    names = names + ' is:\n' + Person.birthday.strftime("%b %d, %Y") + '\n'
                  else:
                    if contact.count('my') > 0:
                      names = names + Person.fullName + '\n(' + Person.nickName + ')' + '\n' + Person.birthday.strftime("%b %d, %Y") + '\n\n'
                    else:
                      names = names + Person.fullName + ':\n' + Person.birthday.strftime("%b %d, %Y") + '\n\n'					
                except:
                  if personGT1 == 'True':
                    names = names + Person.fullName + ':\n' + 'No Birthday found.\n\n'		
                  else:
                    names = 'No Birthday found.'								

      self.say(names)
      self.complete_request()
