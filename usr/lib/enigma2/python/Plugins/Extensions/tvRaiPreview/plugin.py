#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
****************************************
*        coded by Lululla & PCD        *
*             skin by MMark            *
*             17/07/2021              *
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
from Components.AVSwitch import AVSwitch                                        
from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.InfoBarGenerics import *
from Screens.InfoBar import MoviePlayer, InfoBar
from Screens.InfoBarGenerics import InfoBarAudioSelection, InfoBarNotifications 
from Screens.InfoBarGenerics import InfoBarShowHide, InfoBarMenu, InfoBarSeek                                                                                 
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
import json
import six          
from Tools.LoadPixmap import LoadPixmap
global isDreamOS, vid
global skin_path, pluglogo, pngx, pngl, pngs
from sys import version_info
PY3 = sys.version_info.major >= 3
print('Py3: ',PY3)
from six.moves.urllib.request import urlopen
from six.moves.urllib.request import Request
from six.moves.urllib.error import HTTPError, URLError
from six.moves.urllib.parse import urlparse
from six.moves.urllib.parse import quote
from six.moves.urllib.parse import urlencode
from six.moves.urllib.request import urlretrieve
# import six.moves.urllib.request

isDreamOS = False
try:
    from enigma import eMediaDatabase
    isDreamOS = True
except:
    isDreamOS = False
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
    link = []
    print("Here in client2 getUrl url =", url)
    req = Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urlopen(req)
    link=response.read()
    response.close()
    print("Here in client2 link =", link)
    return link

DESKHEIGHT = getDesktop(0).size().height()
currversion = '1.1'
plugin_path = os.path.dirname(sys.modules[__name__].__file__)
skin_path = plugin_path
pluglogo = plugin_path + '/res/pics/logo.png'
pngx = plugin_path + '/res/pics/plugins.png'
pngl = plugin_path + '/res/pics/plugin.png'
pngs = plugin_path + '/res/pics/setting.png'
HD = getDesktop(0).size()
vid = plugin_path + '/vid.txt'
desc_plugin = '..:: TiVu Rai Preview by Lululla %s ::.. ' % currversion
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
        self.names.append("Film")
        self.urls.append("http://www.raiplay.it/film/")
        self.pics.append(pngx)
        self.names.append("Serietv")
        self.urls.append("http://www.raiplay.it/serietv/")
        self.pics.append(pngx)
        self.names.append("Fiction")
        self.urls.append("http://www.raiplay.it/fiction/")
        self.pics.append(pngx)
        self.names.append("Documentari")
        self.urls.append("http://www.raiplay.it/documentari/")
        self.pics.append(pngx)
        self.names.append("Bambini")
        self.urls.append("http://www.raiplay.it/bambini/")
        self.pics.append(pngx)
        self.names.append("Teen")
        self.urls.append("http://www.raiplay.it/teen/")
        self.pics.append(pngx)
        showlist(self.names, self['text'])
        self['info'].setText(_('Please select ...'))

    def okRun(self):
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
        # print('name : ', name)
        # print('url:  ', url)
        if 'tgr' in url.lower():
            self.session.open(tgrRai2, name, url)
        else:
            self.session.open(tvRai2, name, url)

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
        self['title'] = Label(desc_plugin)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okRun,
         'green': self.okRun,
         'red': self.close,
         'cancel': self.close}, -2)

    def _gotPageLoad(self):
        self.names = []
        self.urls = []
        self.pics = []  
        name = self.name        
        url = self.url
        content = getUrl(url)
        if PY3:
            content = six.ensure_str(content)  
        content = content.replace("\r", "").replace("\t", "").replace("\n", "")
        pic = " "
        try:
            if 'type="video">' in content:
                # print('content1 : ', content)
                regexcat = '<label>(.*?)</label>.*?type="video">(.*?)</url>' #relinker
                self["key_green"].setText('Play')
            elif 'type="list">' in content:
                # print('content2 : ', content)
                regexcat = '<label>(.*?)</label>.*?type="list">(.*?)</url>'
            else:
                print('passsss')
                pass
            match = re.compile(regexcat, re.DOTALL).findall(content)
            # print("showContent2 match =", match)
            # print('name : ', name)
            for name, url in match:
                if url.startswith('http'):
                    url1=url
                else:
                    url1 = "http://www.tgr.rai.it" + url
                # pic = image
                url = checkStr(url1)
                name = checkStr(name)
                
                self.names.append(name)
                self.urls.append(url)
                # self.pics.append(pic)
            self['info'].setText(_('Please select ...'))
            showlist(self.names, self['text'])
        except:
            pass

    def okRun(self):
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
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
        self.names = []
        self.urls = []
        self.pics = [] 
        name = self.name        
        url = self.url
        content = getUrl(url)
        if PY3:
            content = six.ensure_str(content)
        content = content.replace("\r", "").replace("\t", "").replace("\n", "")
        pic = " "
        try:
            if 'type="video">' in content:
                # print('content10 : ', content)
                regexcat = '<label>(.*?)</label>.*?type="video">(.*?)</url>' #relinker
                self["key_green"].setText('Play')

            elif 'type="list">' in content:
                # print('content20 : ', content)
                regexcat = '<label>(.*?)</label>.*?type="list">(.*?)</url>'
            else:
                print('passsss')
                pass
            match = re.compile(regexcat, re.DOTALL).findall(content)
            # print("showContent21 match =", match)
            for name, url in match:
                # print('name : ', name)
                # print('url : ', url)
                if url.startswith('http'):
                    url1=url
                else:
                    url1 = "http://www.tgr.rai.it" + url
                # pic = image
                
                url = checkStr(url1)
                name = checkStr(name)
                
                self.names.append(name)
                self.urls.append(url)
                # self.pics.append(pic)
            self['info'].setText(_('Please select ...'))
            showlist(self.names, self['text'])
        except:
            pass

    def okRun(self):
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
        print('name : ', name)
        print('url:  ', url)
        # try:
            # print("In playVideo2 url =", url)
        self.session.open(Playstream4, name, url)
        # except:
            # self['info'].setText(_('Nothing ...'))
            # pass

class tvRai2(Screen):
    def __init__(self, session, name, url):
        self.session = session
        skin = skin_path + 'settings.xml'
        with open(skin, 'r') as f:
            self.skin = f.read()
        self.setup_title = ('TiVuDream')
        Screen.__init__(self, session)
        self.setTitle(name_plugin)
        self.list = []
        self.name = name
        self.url = url
        self['text'] = OneSetList([])
        self['info'] = Label(_('Getting the list, please wait ...'))
        self['key_green'] = Button(_('Play'))
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
        url = self.url
        name = self.name
        content = getUrl(url)
        if PY3:
            content = six.ensure_str(content)
        # items = []
        pic = " "
        regexcat = 'data-video-json="(.*?)".*?<img alt="(.*?)"'
        match = re.compile(regexcat, re.DOTALL).findall(content)
        # print("showContent2 match =", match)
        # print('name : ', name)
        for url, name in match:
            try:
                    url1 = "http://www.raiplay.it" + url
                    content2 = getUrl(url1)
                    if PY3:
                        content2 = six.ensure_str(content2)
                    regexcat2 = '"/video/(.*?)"'
                    match2 = re.compile(regexcat2,re.DOTALL).findall(content2)
                    url2 = match2[0].replace("json", "html")
                    url3 = "http://www.raiplay.it/video/" + url2
                    name = decodeHtml(name)

                    url3 = checkStr(url3)
                    name = checkStr(name)

                    self.names.append(name)
                    self.urls.append(url3)
            except:
                continue
        self['info'].setText(_('Please select ...'))
        showlist(self.names, self['text'])

    def okRun(self):
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
        print('nameok : ', name)
        print('urlok:  ', url)
        try:
            # print("In playVideo2 url =", url)
            from Plugins.Extensions.tvDream.youtube_dl import YoutubeDL
            ydl_opts = {'format': 'best'}
            '''
            ydl_opts = {'format': 'bestaudio/best'}
            '''
            ydl = YoutubeDL(ydl_opts)
            ydl.add_default_info_extractors()
            result = ydl.extract_info(url, download=False)
            print ("rai result =", result)
            url = result["url"]
            print ("rai final url =", url)
            self.session.open(Playstream4, name, url)
        except:
            self['info'].setText(_('Nothing ...'))
            pass

'''
rai end
'''
class TvInfoBarShowHide():
    """ InfoBar show/hide control, accepts toggleShow and hide actions, might start
    fancy animations. """
    STATE_HIDDEN = 0
    STATE_HIDING = 1
    STATE_SHOWING = 2
    STATE_SHOWN = 3

    def __init__(self):
        self["ShowHideActions"] = ActionMap(["InfobarShowHideActions"], {"toggleShow": self.toggleShow,
         "hide": self.hide}, 0)
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.serviceStarted})
        self.__state = self.STATE_SHOWN
        self.__locked = 0
        self.hideTimer = eTimer()
        self.hideTimer.start(5000, True)
        try:
            self.hideTimer_conn = self.hideTimer.timeout.connect(self.doTimerHide)
            
        except:
            self.hideTimer.callback.append(self.doTimerHide)
        self.onShow.append(self.__onShow)
        self.onHide.append(self.__onHide)

    def serviceStarted(self):
        if self.execing:
            if config.usage.show_infobar_on_zap.value:
                self.doShow()

    def __onShow(self):
        self.__state = self.STATE_SHOWN
        self.startHideTimer()
                
    def startHideTimer(self):
        if self.__state == self.STATE_SHOWN and not self.__locked:
            idx = config.usage.infobar_timeout.index
            if idx:
                self.hideTimer.start(idx * 1500, True)

    def __onHide(self):
        self.__state = self.STATE_HIDDEN
                 
    def doShow(self):
        self.show()
        self.startHideTimer()

    def doTimerHide(self):
        self.hideTimer.stop()
        if self.__state == self.STATE_SHOWN:
            self.hide()

    def toggleShow(self):
        if self.__state == self.STATE_SHOWN:
            self.hide()
            self.hideTimer.stop()
        elif self.__state == self.STATE_HIDDEN:
            self.show()

    def lockShow(self):
        self.__locked = self.__locked + 1
        if self.execing:
            self.show()
            self.hideTimer.stop()

    def unlockShow(self):
        self.__locked = self.__locked - 1
        if self.execing:
            self.startHideTimer()

    def debug(obj, text = ""):
        print(text + " %s\n" % obj)
                                           
class Playstream4(Screen, InfoBarMenu, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarAudioSelection, TvInfoBarShowHide): #,InfoBarSubtitleSupport
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    ENABLE_RESUME_SUPPORT = True
    ALLOW_SUSPEND = True
    screen_timeout = 5000                          

    def __init__(self, session, name, url):
        Screen.__init__(self, session)
        self.skinName = 'MoviePlayer'
        title = 'Play'
        # InfoBarBase.__init__(self)
        # InfoBarShowHide.__init__(self)
        InfoBarMenu.__init__(self)
        InfoBarNotifications.__init__(self)
        InfoBarBase.__init__(self, steal_current_service=True)
        TvInfoBarShowHide.__init__(self)
        InfoBarAudioSelection.__init__(self)
        try:
            self.init_aspect = int(self.getAspect())
        except:
            self.init_aspect = 0     
        self.new_aspect = self.init_aspect
        self['actions'] = ActionMap(['WizardActions',
         'MoviePlayerActions',
         'MovieSelectionActions',
         'MediaPlayerActions',
         'EPGSelectActions',
         'MediaPlayerSeekActions',
         'SetupActions',
         'ColorActions',
         'InfobarShowHideActions',
         'InfobarActions',
         'InfobarSeekActions'], {'leavePlayer': self.cancel,
         'epg': self.showIMDB,
         'info': self.showinfo,
         'tv': self.cicleStreamType,
         'stop': self.leavePlayer,
         'cancel': self.cancel,
         'back': self.cancel}, -1)
        self.allowPiP = False
        InfoBarSeek.__init__(self, actionmap='InfobarSeekActions')                      
        self.service = None
        service = None                      
        # InfoBarSeek.__init__(self, actionmap='MediaPlayerSeekActions')
        url = url.replace(':', '%3a')
        url = url.replace(' ','%20')
        self.url = url
        self.pcip = 'None'
        self.name = decodeHtml(name)
        self.state = self.STATE_PLAYING                                 
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        # self.onLayoutFinish.append(self.openTest)
        self.onLayoutFinish.append(self.cicleStreamType)
        self.onClose.append(self.cancel)
        return
        
    def getAspect(self):
        return AVSwitch().getAspectRatioSetting()

    def getAspectString(self, aspectnum):
        return {0: _('4:3 Letterbox'),
         1: _('4:3 PanScan'),
         2: _('16:9'),
         3: _('16:9 always'),
         4: _('16:10 Letterbox'),
         5: _('16:10 PanScan'),
         6: _('16:9 Letterbox')}[aspectnum]

    def setAspect(self, aspect):
        map = {0: '4_3_letterbox',
         1: '4_3_panscan',
         2: '16_9',
         3: '16_9_always',
         4: '16_10_letterbox',
         5: '16_10_panscan',
         6: '16_9_letterbox'}
        config.av.aspectratio.setValue(map[aspect])
        try:
            AVSwitch().setAspectRatio(aspect)
        except:
            pass

    def av(self):
        temp = int(self.getAspect())
        temp = temp + 1
        if temp > 6:
            temp = 0
        self.new_aspect = temp
        self.setAspect(temp)        
        
    def showinfo(self):
        sTitle = ''
        sServiceref = ''
        try:
            servicename, serviceurl = getserviceinfo(sref)
            if servicename is not None:
                sTitle = servicename
            else:
                sTitle = ''
            if serviceurl is not None:
                sServiceref = serviceurl
            else:
                sServiceref = ''
            currPlay = self.session.nav.getCurrentService()
            sTagCodec = currPlay.info().getInfoString(iServiceInformation.sTagCodec)
            sTagVideoCodec = currPlay.info().getInfoString(iServiceInformation.sTagVideoCodec)
            sTagAudioCodec = currPlay.info().getInfoString(iServiceInformation.sTagAudioCodec)
            message = 'stitle:' + str(sTitle) + '\n' + 'sServiceref:' + str(sServiceref) + '\n' + 'sTagCodec:' + str(sTagCodec) + '\n' + 'sTagVideoCodec:' + str(sTagVideoCodec) + '\n' + 'sTagAudioCodec :' + str(sTagAudioCodec)
            self.mbox = self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        except:
            pass

        return
        
    def showIMDB(self):
        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/TMBD/plugin.pyo"):
            from Plugins.Extensions.TMBD.plugin import TMBD
            text_clear = self.name
            text = charRemove(text_clear)
            self.session.open(TMBD, text, False)
        elif os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/IMDb/plugin.pyo"):
            from Plugins.Extensions.IMDb.plugin import IMDB
            text_clear = self.name
            text = charRemove(text_clear)
            HHHHH = text
            self.session.open(IMDB, HHHHH)
        else:
            text_clear = self.name
            self.session.open(MessageBox, text_clear, MessageBox.TYPE_INFO)  
            
    def openTest(self, servicetype, url):
        url = url
        if url.endswith('m3u8'):
            servicetype = '4097'        
        ref = servicetype +':0:1:0:0:0:0:0:0:0:' + str(url)
        print('final reference :   ', ref)
        sref = eServiceReference(ref)
        sref.setName(self.name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)
        
    def cicleStreamType(self):
        from itertools import cycle, islice
        self.servicetype ='4097'#str(config.plugins.exodus.services.value)# 
        print('servicetype1: ', self.servicetype)
        url = str(self.url)
        # if url.endswith('m3u8'):
            # self.servicetype = '4097'
        
        currentindex = 0
        streamtypelist = ["4097"]
        if os.path.exists("/usr/bin/gstplayer"):
            streamtypelist.append("5001")
        if os.path.exists("/usr/bin/exteplayer3"):
            streamtypelist.append("5002")
        if os.path.exists("/usr/bin/apt-get"):
            streamtypelist.append("8193")
        for index, item in enumerate(streamtypelist, start=0):
            if str(item) == str(self.servicetype):
                currentindex = index
                break
        nextStreamType = islice(cycle(streamtypelist), currentindex + 1, None)
        self.servicetype = int(next(nextStreamType))
        print('servicetype2: ', self.servicetype)
        self.openTest(self.servicetype, url)

    def keyNumberGlobal(self, number):
        self['text'].number(number)     
        
    def cancel(self):
        if os.path.exists('/tmp/hls.avi'):
            os.remove('/tmp/hls.avi')
        self.session.nav.stopService()
        self.session.nav.playService(self.srefOld)
        if self.pcip != 'None':
            url2 = 'http://' + self.pcip + ':8080/requests/status.xml?command=pl_stop'
            resp = urlopen(url2)
        if not self.new_aspect == self.init_aspect:
            try:
                self.setAspect(self.init_aspect)
            except:
                pass
        self.close()

    def showVideoInfo(self):
        if self.shown:
            self.hideInfobar()
        if self.infoCallback is not None:
            self.infoCallback()
        return

    def leavePlayer(self):
        self.close() 

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

def decodeUrl(text):
	text = text.replace('%20',' ')
	text = text.replace('%21','!')
	text = text.replace('%22','"')
	text = text.replace('%23','&')
	text = text.replace('%24','$')
	text = text.replace('%25','%')
	text = text.replace('%26','&')
	text = text.replace('%2B','+')
	text = text.replace('%2F','/')
	text = text.replace('%3A',':')
	text = text.replace('%3B',';')
	text = text.replace('%3D','=')
	text = text.replace('&#x3D;','=')
	text = text.replace('%3F','?')
	text = text.replace('%40','@')
	return text

def decodeHtml(text):
	text = text.replace('&auml;','ä')
	text = text.replace('\u00e4','ä')
	text = text.replace('&#228;','ä')
	text = text.replace('&oacute;','ó')
	text = text.replace('&eacute;','e')
	text = text.replace('&aacute;','a')
	text = text.replace('&ntilde;','n')

	text = text.replace('&Auml;','Ä')
	text = text.replace('\u00c4','Ä')
	text = text.replace('&#196;','Ä')
	
	text = text.replace('&ouml;','ö')
	text = text.replace('\u00f6','ö')
	text = text.replace('&#246;','ö')
	
	text = text.replace('&ouml;','Ö')
	text = text.replace('\u00d6','Ö')
	text = text.replace('&#214;','Ö')
	
	text = text.replace('&uuml;','ü')
	text = text.replace('\u00fc','ü')
	text = text.replace('&#252;','ü')
	
	text = text.replace('&Uuml;','Ü')
	text = text.replace('\u00dc','Ü')
	text = text.replace('&#220;','Ü')
	
	text = text.replace('&szlig;','ß')
	text = text.replace('\u00df','ß')
	text = text.replace('&#223;','ß')
	
	text = text.replace('&amp;','&')
	text = text.replace('&quot;','\"')
	text = text.replace('&quot_','\"')

	text = text.replace('&gt;','>')
	text = text.replace('&apos;',"'")
	text = text.replace('&acute;','\'')
	text = text.replace('&ndash;','-')
	text = text.replace('&bdquo;','"')
	text = text.replace('&rdquo;','"')
	text = text.replace('&ldquo;','"')
	text = text.replace('&lsquo;','\'')
	text = text.replace('&rsquo;','\'')
	text = text.replace('&#034;','\'')
	text = text.replace('&#038;','&')
	text = text.replace('&#039;','\'')
	text = text.replace('&#39;','\'')
	text = text.replace('&#160;',' ')
	text = text.replace('\u00a0',' ')
	text = text.replace('&#174;','')
	text = text.replace('&#225;','a')
	text = text.replace('&#233;','e')
	text = text.replace('&#243;','o')
	text = text.replace('&#8211;',"-")
	text = text.replace('\u2013',"-")
	text = text.replace('&#8216;',"'")
	text = text.replace('&#8217;',"'")
	text = text.replace('#8217;',"'")
	text = text.replace('&#8220;',"'")
	text = text.replace('&#8221;','"')
	text = text.replace('&#8222;',',')
	text = text.replace('&#x27;',"'")
	text = text.replace('&#8230;','...')
	text = text.replace('\u2026','...')
	text = text.replace('&#41;',')')
	text = text.replace('&lowbar;','_')
	text = text.replace('&rsquo;','\'')
	text = text.replace('&lpar;','(')
	text = text.replace('&rpar;',')')
	text = text.replace('&comma;',',')
	text = text.replace('&period;','.')
	text = text.replace('&plus;','+')
	text = text.replace('&num;','#')
	text = text.replace('&excl;','!')
	text = text.replace('&#039','\'')
	text = text.replace('&semi;','')
	text = text.replace('&lbrack;','[')
	text = text.replace('&rsqb;',']')
	text = text.replace('&nbsp;','')
	text = text.replace('&#133;','')
	text = text.replace('&#4','')
	text = text.replace('&#40;','')

	text = text.replace('&atilde;',"'")
	text = text.replace('&colon;',':')
	text = text.replace('&sol;','/')
	text = text.replace('&percnt;','%')
	text = text.replace('&commmat;',' ')
	text = text.replace('&#58;',':')

	return text	
