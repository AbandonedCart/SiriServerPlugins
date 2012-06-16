Siri Server Plugins
===================

Do you like this?
-----------------
If you like this piece of software you can help me by donating, I can afford new devices and so get deeper to the core of all of this. Make it even cooler.
Or if you just want to give me a little credit for my work. But don't worry the code will remain free, you don't have to donate.

[<img alt="PayPal — The safer, easier way to pay online." src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG_global.gif">](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=2E3TD99JETMA4)


What is this?
-------------
This repository contains plugins I coded for my [SiriServerCore](https://github.com/Eichhoernchen/SiriServerCore).
They probably won't work with the old SiriServer version as they need up to date siriObjects, I recommend using SiriServerCore anyways.


What plugins are available?
---------------------------
At the moment there are:

* **Phone Call Plugin**:
  This allows you making phonecalls using your voice
  
* **Short Message Plugin**:
  This allows you to create short messages which you can send and compose via voice
  
* **Yahoo Weather Plugin**:
  This plugin gives you weather forecasts of your current location or any other location.

* **EPG Plugin for German Television**:
  This plugin offers an electronic program guide (tv schedule) for german television. Using services from http://tvprofil.net/xmltv/
  Currently it will display and read the program out, formatting will likely be improved in the future

* **Current Time Plugin**:
  This plugin allows you to ask for the time at a specific location or at your current

* **RequestHandler Plugin**:
  This plugin enables you to react on search button presses if something was not recognized by SiriServer.
  It will probably be extended to other delayed requests that might be handeled in the future.


How do I enable the plugins?
----------------------------
You add the specific plugin by entering the plugin name (the name of the folder) into your plugins.conf of SiriServer.
The priority of the plugins is specified by the order from top (higher priority) to bottom (lower priority) in the plugins.conf.
Currently non of my plugins need any special API-Key.

 
Licensing
---------
All plugins contain a header that describe their license. Usually you can modify them as long as the header is untouched. 
Also you can use them for free for personal non commercial use. If you want to use them commercially you need to have a license for SiriServer.
Also you must comply with any service that a plugin might use (e.g. Yahoo weather does not allow commercial use, so you cannot use it commercially although you have a SiriServer license).
  
  
Disclaimer
----------
Apple owns all the rights on Siri. I do not give any warranties or guaranteed support for this software. Use it as it is.
 
# SiriServer Plugin Collection

## cytec:

###Multi Language:

[**twitterPlugin**](https://github.com/cytec/SiriServer-Plugins/tree/master/twitterPlugin):<br />
Description: send tweets with siri and get last 5 tweets from timeline <br />
Requires: yelp api key

[**yelpSearch**](https://github.com/cytec/SiriServer-Plugins/tree/master/yelpSearch) originally by apexad:<br />
Description: Search for Stuff near you <br />
Requires: [yelp API Key](http://www.yelp.com/developers)

[**memebase**](https://github.com/cytec/SiriServer-Plugins/tree/master/memebase)<br />
Description: Get latest memes from Memebase.com<br />
Requires: [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) or <code>easy_install BeautifulSoup</code>

[**sickbeardHistory**](https://github.com/cytec/SiriServer-Plugins/tree/master/SickbeardHistory) <br />
Description: Get last 5 Downloaded Episodes from SickBeard

###German:

[**pantofflhelden**](https://github.com/cytec/SiriServer-Plugins/tree/master/pantofflhelden)<br />
Description: Get latest updates from pantofflhelden.com<br />
Requires: [feedparser](http://pypi.python.org/pypi/feedparser) or <code>easy_install feedparser</code>

[**wissen**](https://github.com/cytec/SiriServer-Plugins/tree/master/Wissen)<br />
Description: Get random german qoutes or fakts<br />
Requires: [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) or <code>easy_install BeautifulSoup</code>"

[**ferien**](https://github.com/cytec/SiriServer-Plugins/tree/master/ferien)<br />
Description: Ferientermine für Bundesländer <br>
bsp: "Sommerferien in Hessen" zeigt die Sommerferien für das aktuelle Jahr im Bundesland Hessen<br />
Requires: [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) or <code>easy_install BeautifulSoup</code>"

[**stau**](https://github.com/cytec/SiriServer-Plugins/tree/master/stau)<br />
Description: Aktuelle Staumeldungen für Deutschland <br>
bsp: "Stau auf der A5" zeigt die Staumeldungen für die A5<br />

Contributors include, but are not limited to:

Mike Pissanos (gaVRos)
AlphaBetaPhi <beta@alphabeta.ca>
Tristen Russ "Playfrog4u" <Playfrog4u@hotmail.com>
Maxx
JimmyKane
Ryan Davis (neoshroom)
Erich Budianto (praetorians)
Casey (Nurfballs) Mullineaux
Joh Gerna
john-dev
SNXRaven (Jonathon Nickols)
Javik
@FreeManRepo
P4r4doX <zatovic@azet.sk>
