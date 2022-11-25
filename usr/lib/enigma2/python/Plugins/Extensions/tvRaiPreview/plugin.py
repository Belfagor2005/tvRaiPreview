#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
****************************************
*        coded by Lululla              *
*                                      *
*             02/08/2022               *
*       Skin by MMark                  *
****************************************
Info http://t.me/tivustream
'''
from __future__ import print_function
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.MultiContent import MultiContentEntryPixmapAlphaTest
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.config import config
from Plugins.Plugin import PluginDescriptor
from Screens.InfoBar import MoviePlayer
from Screens.InfoBarGenerics import InfoBarSeek, InfoBarAudioSelection, InfoBarNotifications
from Screens.InfoBarGenerics import InfoBarSubtitleSupport, InfoBarMenu
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import SCOPE_PLUGINS
from Tools.Directories import resolveFilename
from enigma import RT_HALIGN_LEFT
from enigma import RT_VALIGN_CENTER
from enigma import eServiceReference, iPlayableService
from enigma import eTimer, eListboxPythonMultiContent, gFont
from enigma import loadPNG
import os
import re
import sys
import ssl
import six
from . import Utils
from . import html_conv
global skin_path, pluglogo, pngx, pngl, pngs

PY3 = sys.version_info.major >= 3
print('Py3: ', PY3)

if PY3:
    from urllib.request import urlopen
    from urllib.request import Request
else:
    from urllib2 import Request
    from urllib2 import urlopen

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


currversion = '1.2'
plugin_path = os.path.dirname(sys.modules[__name__].__file__)
pluglogo = resolveFilename(SCOPE_PLUGINS, "Extensions/tvRaiPreview/res/pics/{}".format('logo.png'))
pngx = resolveFilename(SCOPE_PLUGINS, "Extensions/tvRaiPreview/res/pics/{}".format('plugins.png'))
pngl = resolveFilename(SCOPE_PLUGINS, "Extensions/tvRaiPreview/res/pics/{}".format('plugin.png'))
pngs = resolveFilename(SCOPE_PLUGINS, "Extensions/tvRaiPreview/res/pics/{}".format('setting.png'))
desc_plugin = '..:: TiVu Rai Preview by Lululla %s ::.. ' % currversion
name_plugin = 'TiVu Rai Preview'

skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/skins/hd/".format('tvRaiPreview'))
if Utils.isFHD():
    skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/skins/fhd/".format('tvRaiPreview'))
if Utils.DreamOS():
    skin_path = skin_path + "dreamOs/"


class SetList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        if Utils.isFHD():
            self.l.setItemHeight(50)
            textfont = int(34)
            self.l.setFont(0, gFont('Regular', textfont))
        else:
            self.l.setItemHeight(50)
            textfont = int(24)
            self.l.setFont(0, gFont('Regular', textfont))


def OneSetListEntry(name):
    res = [name]
    if Utils.isFHD():
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(pngx)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1900, 50), font=0, text=name, color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 12), size=(34, 25), png=loadPNG(pngx)))
        res.append(MultiContentEntryText(pos=(60, 0), size=(1000, 50), font=0, text=name, color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res


def showlist(data, list):
    icount = 0
    plist = []
    for line in data:
        name = data[icount]
        plist.append(OneSetListEntry(name))
        icount = icount+1
        list.setList(plist)


def returnIMDB(text_clear):
    TMDB = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('TMDB'))
    IMDb = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('IMDb'))
    if TMDB:
        try:
            from Plugins.Extensions.TMBD.plugin import TMBD
            text = html_conv.html_unescape(text_clear)
            _session.open(TMBD.tmdbScreen, text, 0)
        except Exception as ex:
            print("[XCF] Tmdb: ", str(ex))
        return True
    elif IMDb:
        try:
            from Plugins.Extensions.IMDb.plugin import main as imdb
            text = html_conv.html_unescape(text_clear)
            imdb(_session, text)
        except Exception as ex:
            print("[XCF] imdb: ", str(ex))
        return True
    else:
        text_clear = html_conv.html_unescape(text_clear)
        _session.open(MessageBox, text_clear, MessageBox.TYPE_INFO)
        return True
    return


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
        self['text'] = SetList([])
        self['info'] = Label(_('Loading data... Please wait'))
        self['key_green'] = Button(_('Select'))
        self['key_red'] = Button(_('Back'))
        self['key_green'].hide()
        self.timer = eTimer()
        self.timer.start(1500, True)
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self['title'] = Label(name_plugin)
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'ButtonSetupActions',
                                     'DirectionActions'], {'ok': self.okRun,
                                                           'green': self.okRun,
                                                           'red': self.exit,
                                                           'cancel': self.exit}, -2)

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
        self['key_green'].show()

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

    def exit(self):
        Utils.deletetmp()
        self.close()


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
        self['text'] = SetList([])
        self['info'] = Label(_('Loading data... Please wait'))
        self['key_green'] = Button(_('Select'))
        self['key_red'] = Button(_('Back'))
        self['key_green'].hide()
        self.timer = eTimer()
        self.timer.start(1500, True)
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self['title'] = Label(desc_plugin)
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'ButtonSetupActions',
                                     'DirectionActions'], 'green': self.okRun,
                                                          'red': self.close,
                                                          'cancel': self.close}, -2)

    def _gotPageLoad(self):
        self.names = []
        self.urls = []
        self.pics = []
        name = self.name
        url = self.url
        content = Utils.getUrl(url)
        if PY3:
            content = six.ensure_str(content)
        content = content.replace("\r", "").replace("\t", "").replace("\n", "")
        try:
            if 'type="video">' in content:
                # print('content1 : ', content)
                regexcat = '<label>(.*?)</label>.*?type="video">(.*?)</url>'  # relinker
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
                    url1 = url
                else:
                    url1 = "http://www.tgr.rai.it" + url
                # pic = image
                url = url1
                name = html_conv.html_unescape(name)
                self.names.append(name)
                self.urls.append(url)
                # self.pics.append(pic)
            self['info'].setText(_('Please select ...'))
            self['key_green'].show()
            showlist(self.names, self['text'])
        except Exception as e:
            print('error: ', str(e))
            pass

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
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
        self['text'] = SetList([])
        self['info'] = Label(_('Loading data... Please wait'))
        self['key_green'] = Button(_('Select'))
        self['key_red'] = Button(_('Back'))
        self['key_green'].hide()
        self.timer = eTimer()
        self.timer.start(1500, True)
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self['title'] = Label(name_plugin)
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ButtonSetupActions',
                                     'ColorActions',
                                     'DirectionActions'], {'ok': self.okRun,
                                                           'green': self.okRun,
                                                           'red': self.close,
                                                           'cancel': self.close}, -2)

    def _gotPageLoad(self):
        self.names = []
        self.urls = []
        self.pics = []
        name = self.name
        url = self.url
        content = Utils.getUrl(url)
        if PY3:
            content = six.ensure_str(content)
        content = content.replace("\r", "").replace("\t", "").replace("\n", "")
        try:
            if 'type="video">' in content:
                # print('content10 : ', content)
                regexcat = '<label>(.*?)</label>.*?type="video">(.*?)</url>'  # relinker
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
                    url1 = url
                else:
                    url1 = "http://www.tgr.rai.it" + url
                # pic = image
                url = url1
                name = html_conv.html_unescape(name)
                self.names.append(name)
                self.urls.append(url)
                # self.pics.append(pic)
            self['info'].setText(_('Please select ...'))
            self['key_green'].show()
            showlist(self.names, self['text'])
        except Exception as e:
            print('error: ', str(e))
            pass

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
        self.session.open(Playstream4, name, url)


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
        self['text'] = SetList([])
        self['info'] = Label(_('Loading data... Please wait'))
        self['key_green'] = Button(_('Play'))
        self['key_red'] = Button(_('Back'))
        self['key_green'].hide()
        self.timer = eTimer()
        self.timer.start(1500, True)
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self['title'] = Label(name_plugin)
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'ButtonSetupActions',
                                     'DirectionActions'], {'ok': self.okRun,
                                                           'green': self.okRun,
                                                           'red': self.close,
                                                           'cancel': self.close}, -2)

    def _gotPageLoad(self):
        self.names = []
        self.urls = []
        url = self.url
        name = self.name
        content = Utils.getUrl(url)

        if PY3:
            content = six.ensure_str(content)
        print(content)
        items = []

        # i = 0
        # while i < 10:
        try:
            regexcat = 'data-video-json="(.*?).json".*?<img alt="(.*?)"'
            match = re.compile(regexcat, re.DOTALL).findall(content)
            # this = '/tmp/rai-play-'
            # filex = this + self.name.lower() + '.m3u'
            # f=open(filex,"w")
            # f.write("#EXTM3U\n")
            for url, name in match:
                print('name1 ', name)
                print('url1 ', url)

                url1 = "http://www.raiplay.it" + url + '.html'
                content2 = Utils.getUrl(url1)
                # if PY3:
                    # content2 = six.ensure_str(content2)
                print('content2 ', content2)
                # regexcat2 = '"/video/(.*?)",'
                # /video/info/014f4973-a60c-4d59-8dd4-fb104c0e3088.json
                # http://www.raiplay.it/video/info/014f4973-a60c-4d59-8dd4-fb104c0e3088.json

                regexcat2 = '"/video/(.*?)",'
                match2 = re.compile(regexcat2, re.DOTALL).findall(content2)
                url2 = match2[0].replace("json", "html")
                url3 = "http://www.raiplay.it/video/" + url2  # (url2.replace('json', 'html'))
                print('url3 ', url3)
                name = html_conv.html_unescape(name)
                name = name.replace('-', '').replace('RaiPlay', '')
                # item = name + "###" + url3
                # items.append(item)
            # items.sort()
            # for item in items:
                # if item not in items:
                    # name = item.split("###")[0]
                    # url3 = item.split("###")[1]
                print('name ', name)
                print('url3 ', url3)
                self.names.append(name)
                self.urls.append(url3)
                # i = i+1
                # # ################
                # txt1 = "#EXTINF:-1," + name + "\n"
                # f.write(txt1)
                # from Plugins.Extensions.tvRaiPreview.youtube_dl import YoutubeDL
                # ydl_opts = {'format': 'best'}
                # '''
                # ydl_opts = {'format': 'bestaudio/best'}
                # '''
                # ydl = YoutubeDL(ydl_opts)
                # ydl.add_default_info_extractors()
                # result = ydl.extract_info(url3, download=False)
                # print ("rai result =", result)
                # url = result["url"]
                # print ("rai final url =", url)
                # txt2 = url + "\n"
                # f.write(txt2)
                # # ################
        except Exception as e:
            print('error: ', str(e))
        showlist(self.names, self['text'])
        self['info'].setText(_('Please select ...'))
        self['key_green'].show()

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
        print('nameok : ', name)
        print('urlok:  ', url)
        try:
            from Plugins.Extensions.tvRaiPreview.youtube_dl import YoutubeDL
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
        except Exception as e:
            print('error tvr4 e  ', str(e))


class tvRai3(Screen):
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
        self['text'] = SetList([])
        self['info'] = Label(_('Loading data... Please wait'))
        self['key_green'] = Button(_('Play'))
        self['key_red'] = Button(_('Back'))
        self['key_green'].hide()
        self.timer = eTimer()
        self.timer.start(1500, True)
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self['title'] = Label(name_plugin)
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'ButtonSetupActions',
                                     'DirectionActions'], {'ok': self.okRun,
                                                           'green': self.okRun,
                                                           'red': self.close,
                                                           'cancel': self.close}, -2)

    def _gotPageLoad(self):
        self.names = []
        self.urls = []
        url = self.url
        name = self.name
        content = Utils.getUrl(url)
        if PY3:
            content = six.ensure_str(content)
        try:
            if content.find('behaviour="list">'):
                regexcat = '<label>(.*?)</label>.*?type="list">(.*?).html</url>'
                print('content2 : ', content)
                match = re.compile(regexcat, re.DOTALL).findall(content)
                print("showContent2 match =", match)
                for name, url in match:
                    url = "http://www.tgr.rai.it/" + url + '.html'
                    print("getVideos5 name =", name)
                    print("getVideos5 url =", url)
                    name = html_conv.html_unescape(name)
                    self.names.append(name)
                    self.urls.append(url)
        except Exception as e:
            print('error: ', str(e))
        self['info'].setText(_('Please select ...'))
        self['key_green'].show()
        showlist(self.names, self['text'])

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
        print('nameok : ', name)
        print('urlok:  ', url)
        try:
            if 'relinker' in url:
                from Plugins.Extensions.tvRaiPreview.youtube_dl import YoutubeDL
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
            else:
                self.session.open(tvRai4, name, url)
        except Exception as e:
            print('error: ', str(e))


class tvRai4(Screen):
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
        self['text'] = SetList([])
        self['info'] = Label(_('Loading data... Please wait'))
        self['key_green'] = Button(_('Play'))
        self['key_red'] = Button(_('Back'))
        self['key_green'].hide()
        self.timer = eTimer()
        self.timer.start(1500, True)
        if Utils.DreamOS():
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self['title'] = Label(name_plugin)
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'ButtonSetupActions',
                                     'DirectionActions'], {'ok': self.okRun,
                                                           'green': self.okRun,
                                                           'red': self.close,
                                                           'cancel': self.close}, -2)

    def _gotPageLoad(self):
        self.names = []
        self.urls = []
        url = self.url
        name = self.name
        content = Utils.getUrl(url)
        if PY3:
            content = six.ensure_str(content)
        regexcat = 'data-video-json="(.*?)".*?<img alt="(.*?)"'
        match = re.compile(regexcat, re.DOTALL).findall(content)
        try:
            for url, name in match:
                url1 = "http://www.raiplay.it" + url
                content2 = Utils.getUrl(url1)
                if PY3:
                    content2 = six.ensure_str(content2)
                regexcat2 = '"/video/(.*?)"'
                match2 = re.compile(regexcat2, re.DOTALL).findall(content2)
                url2 = match2[0].replace("json", "html")
                url3 = "http://www.raiplay.it/video/" + url2
                name = html_conv.html_unescape(name)
                url3 = url3
                self.names.append(name)
                self.urls.append(url3)

        except Exception as e:
            print('error: ', str(e))
        self['info'].setText(_('Please select ...'))
        self['key_green'].show()
        showlist(self.names, self['text'])

    def okRun(self):
        i = len(self.names)
        print('iiiiii= ', i)
        if i < 1:
            return
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
        print('nameok : ', name)
        print('urlok:  ', url)
        try:
            # try:
            from Plugins.Extensions.tvRaiPreview.youtube_dl import YoutubeDL
            # except:
                # from youtube_dl.Youtube_DL import *
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
        except Exception as e:
            print('error: ', str(e))


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
    skipToggleShow = False

    def __init__(self):
        self["ShowHideActions"] = ActionMap(["InfobarShowHideActions"], {"toggleShow": self.OkPressed, "hide": self.hide}, 0)
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.serviceStarted})
        self.__state = self.STATE_SHOWN
        self.__locked = 0
        self.hideTimer = eTimer()
        try:
            self.hideTimer_conn = self.hideTimer.timeout.connect(self.doTimerHide)
        except:
            self.hideTimer.callback.append(self.doTimerHide)
        self.hideTimer.start(5000, True)
        self.onShow.append(self.__onShow)
        self.onHide.append(self.__onHide)

    def OkPressed(self):
        self.toggleShow()

    def toggleShow(self):
        if self.skipToggleShow:
            self.skipToggleShow = False
            return
        if self.__state == self.STATE_HIDDEN:
            self.show()
            self.hideTimer.stop()
        else:
            self.hide()
            self.startHideTimer()

    def serviceStarted(self):
        if self.execing:
            if config.usage.show_infobar_on_zap.value:

                self.doShow()

    def __onShow(self):
        self.__state = self.STATE_SHOWN
        self.startHideTimer()

    def startHideTimer(self):
        if self.__state == self.STATE_SHOWN and not self.__locked:
            self.hideTimer.stop()
            idx = config.usage.infobar_timeout.index
            if idx:
                self.hideTimer.start(idx * 1500, True)

    def __onHide(self):
        self.__state = self.STATE_HIDDEN

    def doShow(self):
        self.hideTimer.stop()
        self.show()
        self.startHideTimer()

    def doTimerHide(self):
        self.hideTimer.stop()
        if self.__state == self.STATE_SHOWN:
            self.hide()

    def lockShow(self):
        try:
            self.__locked += 1
        except:
            self.__locked = 0
        if self.execing:
            self.show()
            self.hideTimer.stop()
            self.skipToggleShow = False

    def unlockShow(self):
        try:
            self.__locked -= 1
        except:
            self.__locked = 0
        if self.__locked < 0:
            self.__locked = 0
        if self.execing:
            self.startHideTimer()

    def debug(obj, text=""):
        print(text + " %s\n" % obj)


class Playstream4(
                  InfoBarBase,
                  InfoBarMenu,
                  InfoBarSeek,
                  InfoBarAudioSelection,
                  InfoBarSubtitleSupport,
                  InfoBarNotifications,
                  TvInfoBarShowHide,
                  Screen
                  ):
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    ENABLE_RESUME_SUPPORT = True
    ALLOW_SUSPEND = True
    screen_timeout = 5000

    def __init__(self, session, name, url):
        global streaml
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = 'MoviePlayer'
        streaml = False
        for x in InfoBarBase, \
                InfoBarMenu, \
                InfoBarSeek, \
                InfoBarAudioSelection, \
                InfoBarSubtitleSupport, \
                InfoBarNotifications, \
                TvInfoBarShowHide:
            x.__init__(self)
        try:
            self.init_aspect = int(self.getAspect())
        except:
            self.init_aspect = 0
        self.new_aspect = self.init_aspect
        self['actions'] = ActionMap(['MoviePlayerActions',
                                     'MovieSelectionActions',
                                     'MediaPlayerActions',
                                     'EPGSelectActions',
                                     'MediaPlayerSeekActions',
                                     'ColorActions',
                                     'ButtonSetupActions',
                                     'InfobarShowHideActions',
                                     'InfobarActions',
                                     'InfobarSeekActions'], {'stop': self.cancel,
                                                             'epg': self.showIMDB,
                                                             'info': self.showIMDB,
                                                             # 'info': self.cicleStreamType,
                                                             'tv': self.cicleStreamType,
                                                             # 'stop': self.leavePlayer,
                                                             'cancel': self.cancel,
                                                             'back': self.cancel}, -1)
        self.allowPiP = False
        self.service = None
        self.url = url
        self.pcip = 'None'
        self.name = html_conv.html_unescape(name)
        self.state = self.STATE_PLAYING
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        if '8088' in str(self.url):
            # self.onLayoutFinish.append(self.slinkPlay)
            self.onFirstExecBegin.append(self.slinkPlay)
        else:
            # self.onLayoutFinish.append(self.cicleStreamType)
            self.onFirstExecBegin.append(self.cicleStreamType)
        self.onClose.append(self.cancel)

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

    def showIMDB(self):
        text_clear = self.name
        if returnIMDB(text_clear):
            print('show imdb/tmdb')

    def slinkPlay(self, url):
        name = self.name
        ref = "{0}:{1}".format(url.replace(":", "%3a"), name.replace(":", "%3a"))
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def openTest(self, servicetype, url):
        name = self.name
        ref = "{0}:0:0:0:0:0:0:0:0:0:{1}:{2}".format(servicetype, url.replace(":", "%3a"), name.replace(":", "%3a"))
        print('reference:   ', ref)
        if streaml is True:
            url = 'http://127.0.0.1:8088/' + str(url)
            ref = "{0}:0:1:0:0:0:0:0:0:0:{1}:{2}".format(servicetype, url.replace(":", "%3a"), name.replace(":", "%3a"))
            print('streaml reference:   ', ref)
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def cicleStreamType(self):
        global streml
        streaml = False
        from itertools import cycle, islice
        self.servicetype = '4097'
        print('servicetype1: ', self.servicetype)
        url = str(self.url)
        if str(os.path.splitext(self.url)[-1]) == ".m3u8":
            if self.servicetype == "1":
                self.servicetype = "4097"
        currentindex = 0
        streamtypelist = ["4097"]
        # if "youtube" in str(self.url):
            # self.mbox = self.session.open(MessageBox, _('For Stream Youtube coming soon!'), MessageBox.TYPE_INFO, timeout=5)
            # return
        if Utils.isStreamlinkAvailable():
            streamtypelist.append("5002")
            streaml = True
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
        self.servicetype = str(next(nextStreamType))
        print('servicetype2: ', self.servicetype)
        self.openTest(self.servicetype, url)

    def up(self):
        pass

    def down(self):
        self.up()

    def doEofInternal(self, playing):
        self.close()

    def __evEOF(self):
        self.end = True

    def showVideoInfo(self):
        if self.shown:
            self.hideInfobar()
        if self.infoCallback is not None:
            self.infoCallback()
        return

    def showAfterSeek(self):
        if isinstance(self, TvInfoBarShowHide):
            self.doShow()

    def cancel(self):
        if os.path.isfile('/tmp/hls.avi'):
            os.remove('/tmp/hls.avi')
        self.session.nav.stopService()
        self.session.nav.playService(self.srefInit)
        if not self.new_aspect == self.init_aspect:
            try:
                self.setAspect(self.init_aspect)
            except:
                pass
        streaml = False
        self.close()

    def leavePlayer(self):
        self.close()


def main(session, **kwargs):
    try:
        if Utils.zCheckInternet(1):
            try:
                from . import Update
                Update.upd_done()
            except:
                import traceback
                traceback.print_exc()
            session.open(tgrRai)
        else:
            from Screens.MessageBox import MessageBox
            from Tools.Notifications import AddPopup
            AddPopup(_("Sorry but No Internet :("), MessageBox.TYPE_INFO, 10, 'Sorry')
    except:
        import traceback
        traceback.print_exc()


def Plugins(**kwargs):
    ico_path = 'logo.png'
    if not os.path.exists('/var/lib/dpkg/status'):
        ico_path = plugin_path + '/res/pics/logo.png'
    # main_menu = PluginDescriptor(name = name_plugin, description = desc_plugin, where = PluginDescriptor.WHERE_MENU, fnc = StartSetup, needsRestart = True)
    extensions_menu = PluginDescriptor(name=name_plugin, description=desc_plugin, where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main, needsRestart=True)
    result = [PluginDescriptor(name=name_plugin, description=desc_plugin, where=PluginDescriptor.WHERE_PLUGINMENU, icon=ico_path, fnc=main)]
    result.append(extensions_menu)
    # result.append(main_menu)
    return result
