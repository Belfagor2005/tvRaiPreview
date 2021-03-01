#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
****************************************
*        coded by Lululla & PCD        *
*             skin by MMark            *
*             30/01/2021              *
*       Skin by MMark                  *
****************************************
'''
# from __future__ import print_function
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Button import Button
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap
from Components.PluginComponent import plugins
from Components.PluginList import *
from Components.ScrollLabel import ScrollLabel
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.InfoBarGenerics import *
from Screens.InfoBar import MoviePlayer, InfoBar
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Tools.Directories import *
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, fileExists
from enigma import *
from enigma import RT_HALIGN_LEFT, getDesktop, RT_HALIGN_RIGHT, RT_HALIGN_CENTER
from enigma import eTimer, eListboxPythonMultiContent, eListbox, eConsoleAppContainer, gFont
from os import path, listdir, remove, mkdir, chmod
from twisted.web.client import downloadPage, getPage
from xml.dom import Node, minidom
import base64
import os
import re
import sys
import shutil
import ssl
import glob
from Tools.LoadPixmap import LoadPixmap
global isDreamOS, vid
global skin_path, pluglogo, pngx, pngl, pngs

isDreamOS = False
try:
    from enigma import eMediaDatabase
    isDreamOS = True
except:
    isDreamOS = False

'''
PY3 = sys.version_info.major >= 3
'''
PY3 = sys.version_info[0] == 3

if PY3:
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError
    from urllib.parse import urlparse
    from urllib.parse import urlencode, quote
    from urllib.request import urlretrieve
else:
    from urllib2 import urlopen, Request
    from urllib2 import URLError, HTTPError
    from urlparse import urlparse
    from urllib import urlencode, quote
    from urllib import urlretrieve


if sys.version_info >= (2, 7, 9):
    try:
        import ssl
        sslContext = ssl._create_unverified_context()
    except:
        sslContext = None

def ssl_urlopen(url):
    if sslContext:
        return urlopen(url, context=sslContext)
    else:
        return urlopen(url)

try:
    from enigma import eDVBDB
except ImportError:
    eDVBDB = None

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def checkStr(txt):
    if PY3:
        if type(txt) == type(bytes()):
            txt = txt.decode('utf-8')
    else:
        if type(txt) == type(unicode()):
            txt = txt.encode('utf-8')
    return txt

def checkInternet():
    try:
        response = checkStr(urlopen("http://google.com", None, 5))
        response.close()
    except HTTPError:
        return False
    except URLError:
        return False
    except socket.timeout:
        return False
    else:
        return True

def checkUrl(url):
    try:
        response = checkStr(urlopen(url, None, 5))
        response.close()
    except HTTPError:
        return False
    except URLError:
        return False
    except socket.timeout:
        return False
    else:
        return True

def getUrl(url):
    print(" Here in getUrl url =", url)
    req = Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = checkStr(urlopen(req))
    link = response.read()
    response.close()
    return link

DESKHEIGHT = getDesktop(0).size().height()
currversion = '1.0'

plugin_path = os.path.dirname(sys.modules[__name__].__file__)
skin_path = plugin_path
pluglogo = plugin_path + '/res/pics/logo.png'
pngx = plugin_path + '/res/pics/plugins.png'
pngl = plugin_path + '/res/pics/plugin.png'
pngs = plugin_path + '/res/pics/setting.png'
HD = getDesktop(0).size()
vid = plugin_path + '/vid.txt'
desc_plugin = '..:: TiVu Rai Preview by Lululla %s ::.. ' % currversion)
name_plugin = 'TiVuRaiPreview'
    
if HD.width() > 1280:
    if isDreamOS:
        skin_path = plugin_path + '/res/skins/fhd/dreamOs/'
    else:
        skin_path = plugin_path + '/res/skins/fhd/'
else:
    if isDreamOS:
        skin_path = plugin_path + '/res/skins/hd/dreamOs/'
    else:
        skin_path = plugin_path + '/res/skins/hd/'


class SetList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setFont(0, gFont('Regular', 20))
        self.l.setFont(1, gFont('Regular', 22))
        self.l.setFont(2, gFont('Regular', 24))
        self.l.setFont(3, gFont('Regular', 26))
        self.l.setFont(4, gFont('Regular', 28))
        self.l.setFont(5, gFont('Regular', 30))
        self.l.setFont(6, gFont('Regular', 32))
        self.l.setFont(7, gFont('Regular', 34))
        self.l.setFont(8, gFont('Regular', 36))
        self.l.setFont(9, gFont('Regular', 40))
        if HD.width() > 1280:
            self.l.setItemHeight(50)
        else:
            self.l.setItemHeight(50)


class OneSetList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        if HD.width() > 1280:
            self.l.setItemHeight(50)
            textfont = int(34)
            self.l.setFont(0, gFont('Regular', textfont))
        else:
            self.l.setItemHeight(50)
            textfont = int(22)
            self.l.setFont(0, gFont('Regular', textfont))

def OneSetListEntry(name):

    res = [name]
    if HD.width() > 1280:
        res.append(MultiContentEntryPixmapAlphaTest(pos = (10, 12), size = (34, 25), png = loadPNG(pngx)))
        res.append(MultiContentEntryText(pos = (60, 0), size = (1200, 50), font = 0, text = name, color = 0xa6d1fe, flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos = (10, 6), size = (34, 25), png = loadPNG(pngx)))
        res.append(MultiContentEntryText(pos = (60, 2), size = (1000, 50), font = 0, text = name, color = 0xa6d1fe, flags = RT_HALIGN_LEFT))
    return res

def showlist(data, list):
    icount = 0
    plist = []
    for line in data:
        name = data[icount]
        plist.append(OneSetListEntry(name))
        icount = icount+1
        list.setList(plist)

'''
tgrRai start
'''
class tgrRai(Screen):

    def __init__(self, session):
        self.session = session
        skin = skin_path + 'settings.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('tvRaiPreview')
        Screen.__init__(self, session)
        self.setTitle(name_plugin)
        self.list = []
        self['text'] = OneSetList([])
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['key_green'] = Button(_('Select'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button(_(''))
        self["key_blue"] = Button(_(''))
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.timer = eTimer()
        self.timer.start(1500, True)
        if isDreamOS:
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self['title'] = Label(name_plugin)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def _gotPageLoad(self):
        self.names = []
        self.urls = []
        self.pics = []
        # self.urls.append("http://www.tgr.rai.it/dl/tgr/mhp/home.xml")        
        self.names.append("TG")
        self.urls.append("http://www.tgr.rai.it/dl/tgr/mhp/regioni/Page-0789394e-ddde-47da-a267-e826b6a73c4b.html?tgr")   
        self.pics.append("http://www.tgr.rai.it/dl/tgr/mhp/immagini/tgr.png")
        self.names.append("METEO")
        self.urls.append("http://www.tgr.rai.it/dl/tgr/mhp/regioni/Page-0789394e-ddde-47da-a267-e826b6a73c4b.html?meteo")        
        self.pics.append("http://www.tgr.rai.it/dl/tgr/mhp/immagini/meteo.png")
        self.names.append("BUONGIORNO ITALIA")
        self.urls.append("http://www.tgr.rai.it/dl/rai24/tgr/rubriche/mhp/ContentSet-88d248b5-6815-4bed-92a3-60e22ab92df4.html")  
        self.pics.append("http://www.tgr.rai.it/dl/tgr/mhp/immagini/buongiorno%20italia.png")        
        self.names.append("BUONGIORNO REGIONE")
        self.urls.append("http://www.tgr.rai.it/dl/tgr/mhp/regioni/Page-0789394e-ddde-47da-a267-e826b6a73c4b.html?buongiorno")         
        self.pics.append("http://www.tgr.rai.it/dl/tgr/mhp/immagini/buongiorno%20regione.png")         
        self.names.append("IL SETTIMANALE")
        self.urls.append("http://www.tgr.rai.it/dl/rai24/tgr/rubriche/mhp/ContentSet-b7213694-9b55-4677-b78b-6904e9720719.html")   
        self.pics.append("http://www.tgr.rai.it/dl/tgr/mhp/immagini/il%20settimanale.png")         
        self.names.append("RUBRICHE")
        self.urls.append("http://www.tgr.rai.it/dl/rai24/tgr/rubriche/mhp/list.xml")  
        self.pics.append("http://www.tgr.rai.it/dl/tgr/mhp/immagini/rubriche.png")         
        showlist(self.names, self['text'])
        self['info'].setText(_('Please select ...'))
    
    def okRun(self):
        selection = str(self['text'].getCurrent())
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
        print('name : ', name)
        print('url:  ', url)
        self.session.open(tgrRai2, name, url)

class tgrRai2(Screen):

    def __init__(self, session, name, url):
        self.session = session
        skin = skin_path + 'settings.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('tvRaiPreview')
        Screen.__init__(self, session)
        self.setTitle(name_plugin)
        self.list = []
        self.name = name
        self.url = url
        self['text'] = OneSetList([])
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['key_green'] = Button(_('Select'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button(_(''))
        self["key_blue"] = Button(_(''))
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.timer = eTimer()
        self.timer.start(1500, True)
        if isDreamOS:
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self['title'] = Label(name_plugin)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def _gotPageLoad(self):
        url = self.url
        getPage(url).addCallback(self._gotPageLoad2).addErrback(self.errorLoad)

    def errorLoad(self, error):
        print(str(error))
        self['info'].setText(_('Try again later ...'))

    def _gotPageLoad2(self, data):
        content = data.replace("\r", "").replace("\t", "").replace("\n", "")
        name = self.name
        self.names = []
        self.urls = []
        self.pics = []
        pic = " "
        try:
            if 'type="video">' in content:
                print('content1 : ', content)
                regexcat = '<label>(.*?)</label>.*?type="video">(.*?)</url>' #relinker
                self["key_green"].setText('Play')
                
            elif 'type="list">' in content: 
                print('content2 : ', content)
                regexcat = '<label>(.*?)</label>.*?type="list">(.*?)</url>'
            else:
                print('passsss')
                pass
            match = re.compile(regexcat, re.DOTALL).findall(content)
            print("showContent2 match =", match)
            print('name : ', name)
            for name, url in match:
                if url.startswith('http'):
                    url1=url
                else:
                    url1 = "http://www.tgr.rai.it" + url
                # pic = image
                self.names.append(name)
                self.urls.append(url1)
                # self.pics.append(pic)
            self['info'].setText(_('Please select ...'))
            showlist(self.names, self['text'])            
        except:
            pass

        
    def okRun(self):
        selection = str(self['text'].getCurrent())
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
        print('name : ', name)
        print('url:  ', url)
        
        if 'relinker' in url:
            self.session.open(Playstream4, name, url)
        else:
            self.session.open(tgrRai3, name, url)

            
class tgrRai3(Screen):

    def __init__(self, session, name, url):
        self.session = session
        skin = skin_path + 'settings.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('tvRaiPreview')
        Screen.__init__(self, session)
        self.setTitle(name_plugin)
        self.list = []
        self.name = name
        self.url = url
        self['text'] = OneSetList([])
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['key_green'] = Button(_('Select'))
        self['key_red'] = Button(_('Back'))
        self['key_yellow'] = Button(_(''))
        self["key_blue"] = Button(_(''))
        self['key_yellow'].hide()
        self['key_blue'].hide()
        self.timer = eTimer()
        self.timer.start(1500, True)
        if isDreamOS:
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self['title'] = Label(name_plugin)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def _gotPageLoad(self):
        url = self.url
        
        getPage(url).addCallback(self._gotPageLoad2).addErrback(self.errorLoad)

    def errorLoad(self, error):
        print(str(error))
        self['info'].setText(_('Try again later ...'))
        
    def _gotPageLoad2(self, data):
        content = data.replace("\r", "").replace("\t", "").replace("\n", "")
        name = self.name        
        self.names = []
        self.urls = []
        self.pics = []
        pic = " "
        try:
            if 'type="video">' in content:
                print('content10 : ', content)
                regexcat = '<label>(.*?)</label>.*?type="video">(.*?)</url>' #relinker
                self["key_green"].setText('Play')
                    
            elif 'type="list">' in content: 
                print('content20 : ', content)
                regexcat = '<label>(.*?)</label>.*?type="list">(.*?)</url>'
            else:
                print('passsss')
                pass
            match = re.compile(regexcat, re.DOTALL).findall(content)
            print("showContent21 match =", match)
            for name, url in match:
                print('name : ', name)
                print('url : ', url)
                if url.startswith('http'):
                    url1=url
                else:
                    url1 = "http://www.tgr.rai.it" + url
                # pic = image 
                self.names.append(name)
                self.urls.append(url1)
                # self.pics.append(pic)
            self['info'].setText(_('Please select ...'))
            showlist(self.names, self['text'])
          
        except:
            pass            
            

    def okRun(self):
        selection = str(self['text'].getCurrent())
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
        print('name : ', name)
        print('url:  ', url)
        try:
            print("In playVideo2 url =", url)
            self.session.open(Playstream4, name, url)
        except:
            self['info'].setText(_('Nothing ...'))
            pass

'''
rai end
'''
class Playstream4(Screen, InfoBarMenu, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarShowHide):

    def __init__(self, session, name, url):
        Screen.__init__(self, session)
        self.skinName = 'MoviePlayer'
        title = 'Play'
        InfoBarMenu.__init__(self)
        InfoBarNotifications.__init__(self)
        InfoBarBase.__init__(self)
        InfoBarShowHide.__init__(self)
        self['actions'] = ActionMap(['WizardActions',
         'MoviePlayerActions',
         'EPGSelectActions',
         'MediaPlayerSeekActions',
         'ColorActions',
         'InfobarShowHideActions',
         'InfobarActions'], {'leavePlayer': self.cancel,
         'back': self.cancel}, -1)
        self.allowPiP = False
        InfoBarSeek.__init__(self, actionmap='MediaPlayerSeekActions')
        url = url.replace(':', '%3a')
        self.url = url
        self.name = name
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        url = self.url
        name = self.name
        print("Here in Playvid name A =", name)
        name = name.replace(":", "-")
        name = name.replace("&", "-")
        name = name.replace(" ", "-")
        name = name.replace("/", "-")
        name = name.replace("›", "-")
        name = name.replace(",", "-")
        print("Here in Playvid name B2 =", name)

        if url is not None:
            url = str(url)
            url = url.replace(":", "%3a")
            url = url.replace("\\", "/")
            print("url final= ", url)
            ref = "4097:0:1:0:0:0:0:0:0:0:" + url
            print("ref= ", ref)
            sref = eServiceReference(ref)
            sref.setName(self.name)
            self.session.nav.stopService()
            self.session.nav.playService(sref)
        else:
           return

    def openTestX(self):
        ref = '4097:0:1:0:0:0:0:0:0:0:' + self.url
        sref = eServiceReference(ref)
        sref.setName(self.name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def cancel(self):
        if os.path.exists('/tmp/hls.avi'):
            os.remove('/tmp/hls.avi')
        self.session.nav.stopService()
        self.session.nav.playService(self.srefOld)
        self.close()

    def keyLeft(self):
        self['text'].left()

    def keyRight(self):
        self['text'].right()

    def keyNumberGlobal(self, number):
        self['text'].number(number)

def main(session, **kwargs):
    if checkInternet():
        session.open(tgrRai)
    else:
        session.open(MessageBox, "No Internet", MessageBox.TYPE_INFO)

def StartSetup(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(_('tvRaiPreview'), main, 'tvRaiPreview', 15)]
    else:
        return []

def Plugins(**kwargs):
    ico_path = 'logo.png'
    if not isDreamOS:
        ico_path = plugin_path + '/res/pics/logo.png'
    main_menu = PluginDescriptor(name = name_plugin, description = desc_plugin, where = PluginDescriptor.WHERE_MENU, fnc = StartSetup, needsRestart = True)
    extensions_menu = PluginDescriptor(name = name_plugin, description = desc_plugin, where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc = main, needsRestart = True)
    result = [PluginDescriptor(name = name_plugin, description = desc_plugin, where = PluginDescriptor.WHERE_PLUGINMENU, icon = ico_path, fnc = main)]
    result.append(extensions_menu)
    result.append(main_menu)
    return result
