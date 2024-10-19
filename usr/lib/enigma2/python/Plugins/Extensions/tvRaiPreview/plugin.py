#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
****************************************
*        coded by Lululla              *
*             01/10/2023               *
*       Skin by MMark                  *
****************************************
#--------------------#
Info http://t.me/tivustream
'''
from __future__ import print_function
from . import _
from . import Utils
from . import html_conv
from .Console import Console as xConsole

from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import (MultiContentEntryPixmapAlphaTest, MultiContentEntryText)
from Components.ServiceEventTracker import (ServiceEventTracker, InfoBarBase)
from Components.config import config
from Plugins.Plugin import PluginDescriptor
from Screens.InfoBarGenerics import (
    InfoBarSubtitleSupport,
    InfoBarSeek,
    InfoBarAudioSelection,
    InfoBarMenu,
    InfoBarNotifications,
)
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import (SCOPE_PLUGINS, resolveFilename)
from enigma import (
    RT_VALIGN_CENTER,
    RT_HALIGN_LEFT,
    eTimer,
    eListboxPythonMultiContent,
    eServiceReference,
    iPlayableService,
    gFont,
    loadPNG,
    getDesktop,
)
from datetime import datetime
import codecs
import json           
import os
import re
import six
import ssl
import sys

global skin_path, pngx, pngl, pngs

PY3 = False
PY3 = sys.version_info.major >= 3
print('Py3: ', PY3)

if PY3:
    from urllib.request import urlopen
    PY3 = True
else:
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


currversion = '1.4'
plugin_path = '/usr/lib/enigma2/python/Plugins/Extensions/tvRaiPreview'
pluglogo = os.path.join(plugin_path, "res/pics/logo.png")
pngx = os.path.join(plugin_path, "res/pics/plugins.png")
pngl = os.path.join(plugin_path, "res/pics/plugin.png")
pngs = os.path.join(plugin_path, "res/pics/setting.png")
desc_plugin = '..:: TiVu Rai Preview by Lululla %s ::.. ' % currversion
name_plugin = 'TiVu Rai Preview'
skin_path = os.path.join(plugin_path, "res/skins/hd/")
screenwidth = getDesktop(0).size()
if screenwidth.width() == 1920:
    skin_path = plugin_path + '/res/skins/fhd/'
if screenwidth.width() == 2560:
    skin_path = plugin_path + '/res/skins/uhd/'
if os.path.exists('/var/lib/dpkg/info'):
    skin_path = skin_path + 'dreamOs/'
installer_url = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL0JlbGZhZ29yMjAwNS90dlJhaVByZXZpZXcvbWFpbi9pbnN0YWxsZXIuc2g='
developer_url = 'aHR0cHM6Ly9hcGkuZ2l0aHViLmNvbS9yZXBvcy9CZWxmYWdvcjIwMDUvdHZSYWlQcmV2aWV3'


class SetList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        if screenwidth.width() == 2560:
            self.l.setFont(0, gFont('Regular', 48))
            self.l.setItemHeight(56)
        elif screenwidth.width() == 1920:
            self.l.setFont(0, gFont('Regular', 30))
            self.l.setItemHeight(50)
        else:
            self.l.setFont(0, gFont('Regular', 24))
            self.l.setItemHeight(45)


def OneSetListEntry(name):
    res = [name]
    pngx = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/setting.png".format('tvRaiPreview'))  # ico1_path
    if screenwidth.width() == 2560:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 15), size=(40, 40), png=loadPNG(pngx)))
        res.append(MultiContentEntryText(pos=(80, 0), size=(2000, 60), font=0, text=name, color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    elif screenwidth.width() == 1920:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(40, 40), png=loadPNG(pngx)))
        res.append(MultiContentEntryText(pos=(70, 0), size=(1000, 50), font=0, text=name, color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(3, 10), size=(40, 40), png=loadPNG(pngx)))
        res.append(MultiContentEntryText(pos=(50, 0), size=(500, 50), font=0, text=name, color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res


def showlist(data, list):
    icount = 0
    plist = []
    for line in data:
        name = data[icount]
        plist.append(OneSetListEntry(name))
        icount += 1
        list.setList(plist)


def returnIMDB(text_clear):
    TMDB = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('TMDB'))
    tmdb = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('tmdb'))
    IMDb = resolveFilename(SCOPE_PLUGINS, "Extensions/{}".format('IMDb'))
    text = html_conv.html_unescape(text_clear)
    if os.path.exists(TMDB):
        try:
            from Plugins.Extensions.TMBD.plugin import TMBD
            _session.open(TMBD.tmdbScreen, text, 0)
        except Exception as e:
            print("[XCF] Tmdb: ", str(e))
        return True

    elif os.path.exists(tmdb):
        try:
            from Plugins.Extensions.tmdb.plugin import tmdb
            _session.open(tmdb.tmdbScreen, text, 0)
        except Exception as e:
            print("[XCF] Tmdb: ", str(e))
        return True

    elif os.path.exists(IMDb):
        try:
            from Plugins.Extensions.IMDb.plugin import main as imdb
            imdb(_session, text)
        except Exception as e:
            print("[XCF] imdb: ", str(e))
        return True
    else:
        _session.open(MessageBox, text, MessageBox.TYPE_INFO)
        return True
    return False


class tgrRai(Screen):
    def __init__(self, session):
        self.session = session
        skin = os.path.join(skin_path, 'settings.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
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
        self['key_yellow'] = Button(_('Update'))
        # self['key_yellow'].hide()
        self['title'] = Label(name_plugin)
        self.Update = False
        self['actions'] = ActionMap(['OkCancelActions',
                                     'HotkeyActions',
                                     'InfobarEPGActions',
                                     'ChannelSelectBaseActions',
                                     'DirectionActions'], {'ok': self.okRun,
                                                           'yellow': self.update_me,  # update_me,
                                                           'yellow_long': self.update_dev,
                                                           'info_long': self.update_dev,
                                                           'infolong': self.update_dev,
                                                           'showEventInfoPlugin': self.update_dev,
                                                           'green': self.okRun,
                                                           'cancel': self.closerm,
                                                           'red': self.closerm}, -1)
        self.timer = eTimer()
        if os.path.exists('/var/lib/dpkg/status'):
            self.timer_conn = self.timer.timeout.connect(self.check_vers)
        else:
            self.timer.callback.append(self.check_vers)
        self.timer.start(500, 1)
        self.onLayoutFinish.append(self._gotPageLoad)

    def check_vers(self):
        remote_version = '0.0'
        remote_changelog = ''
        req = Utils.Request(Utils.b64decoder(installer_url), headers={'User-Agent': 'Mozilla/5.0'})
        page = Utils.urlopen(req).read()
        if PY3:
            data = page.decode("utf-8")
        else:
            data = page.encode("utf-8")
        if data:
            lines = data.split("\n")
            for line in lines:
                if line.startswith("version"):
                    remote_version = line.split("=")
                    remote_version = line.split("'")[1]
                if line.startswith("changelog"):
                    remote_changelog = line.split("=")
                    remote_changelog = line.split("'")[1]
                    break
        self.new_version = remote_version
        self.new_changelog = remote_changelog
        # if currversion < remote_version:
        if float(currversion) < float(remote_version):
            self.Update = True
            # self['key_yellow'].show()
            # self['key_green'].show()
            self.session.open(MessageBox, _('New version %s is available\n\nChangelog: %s\n\nPress info_long or yellow_long button to start force updating.') % (self.new_version, self.new_changelog), MessageBox.TYPE_INFO, timeout=5)
        # self.update_me()

    def update_me(self):
        if self.Update is True:
            self.session.openWithCallback(self.install_update, MessageBox, _("New version %s is available.\n\nChangelog: %s \n\nDo you want to install it now?") % (self.new_version, self.new_changelog), MessageBox.TYPE_YESNO)
        else:
            self.session.open(MessageBox, _("Congrats! You already have the latest version..."),  MessageBox.TYPE_INFO, timeout=4)

    def update_dev(self):
        try:
            req = Utils.Request(Utils.b64decoder(developer_url), headers={'User-Agent': 'Mozilla/5.0'})
            page = Utils.urlopen(req).read()
            data = json.loads(page)
            remote_date = data['pushed_at']
            strp_remote_date = datetime.strptime(remote_date, '%Y-%m-%dT%H:%M:%SZ')
            remote_date = strp_remote_date.strftime('%Y-%m-%d')
            self.session.openWithCallback(self.install_update, MessageBox, _("Do you want to install update ( %s ) now?") % (remote_date), MessageBox.TYPE_YESNO)
        except Exception as e:
            print('error xcons:', e)

    def install_update(self, answer=False):
        if answer:
            cmd1 = 'wget -q "--no-check-certificate" ' + Utils.b64decoder(installer_url) + ' -O - | /bin/sh'
            self.session.open(xConsole, 'Upgrading...', cmdlist=[cmd1], finishedCallback=self.myCallback, closeOnSuccess=False)
        else:
            self.session.open(MessageBox, _("Update Aborted!"),  MessageBox.TYPE_INFO, timeout=3)

    def myCallback(self, result=None):
        print('result:', result)
        return

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
        # self.names.append("Film")
        # self.urls.append("http://www.raiplay.it/film/")
        # self.pics.append(pngx)
        # self.names.append("Serietv")
        # self.urls.append("http://www.raiplay.it/serietv/")
        # self.pics.append(pngx)
        # self.names.append("Fiction")
        # self.urls.append("http://www.raiplay.it/fiction/")
        # self.pics.append(pngx)
        # self.names.append("Documentari")
        # self.urls.append("http://www.raiplay.it/documentari/")
        # self.pics.append(pngx)
        # self.names.append("Bambini")
        # self.urls.append("http://www.raiplay.it/bambini/")
        # self.pics.append(pngx)
        # self.names.append("Teen")
        # self.urls.append("http://www.raiplay.it/teen/")
        # self.pics.append(pngx)
        showlist(self.names, self['text'])
        self['info'].setText(_('Please select ...'))
        self['key_green'].show()

    def okRun(self):
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
        if 'tgr' in url.lower():
            self.session.open(tgrRai2, name, url)
        else:
            self.session.open(tvRai2, name, url)

    def closerm(self):
        Utils.deletetmp()
        self.close()


class tgrRai2(Screen):
    def __init__(self, session, name, url):
        self.session = session
        skin = os.path.join(skin_path, 'settings.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
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
        self['key_yellow'] = Button()
        self['key_yellow'].hide()
        self.timer = eTimer()
        self.timer.start(1500, True)
        if os.path.exists('/var/lib/dpkg/info'):
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self['title'] = Label(desc_plugin)
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'DirectionActions'], {'green': self.okRun,
                                                           'red': self.close,
                                                           'ok': self.okRun,
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
                self.names.append(str(name))
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
        if i < 1:
            return
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
        if 'relinker' in url:
            self.session.open(Playstream1, name, url)
        else:
            self.session.open(tgrRai3, name, url)


class tgrRai3(Screen):
    def __init__(self, session, name, url):
        self.session = session
        skin = os.path.join(skin_path, 'settings.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
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
        self['key_yellow'] = Button()
        self['key_yellow'].hide()
        self.timer = eTimer()
        if os.path.exists('/var/lib/dpkg/info'):
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self.timer.start(1500, True)
        self['title'] = Label(name_plugin)
        self['actions'] = ActionMap(['OkCancelActions',
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
                self.names.append(str(name))
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
        if i < 1:
            return
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
        self.session.open(Playstream1, name, url)


class tvRai2(Screen):
    def __init__(self, session, name, url):
        self.session = session
        skin = os.path.join(skin_path, 'settings.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = ('tvRaiPreview')
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
        self['key_yellow'] = Button()
        self['key_yellow'].hide()
        self.timer = eTimer()
        if os.path.exists('/var/lib/dpkg/info'):
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self.timer.start(1500, True)
        self['title'] = Label(name_plugin)
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
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
        # items = []
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
                name = html_conv.html_unescape(name)
                name = name.replace('-', '').replace('RaiPlay', '')
                # item = name + "###" + url3
                # items.append(item)
            # items.sort()
            # for item in items:
                # if item not in items:
                    # name = item.split("###")[0]
                    # url3 = item.split("###")[1]
                self.names.append(str(name))
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
        if i < 1:
            return
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
        try:
            from Plugins.Extensions.tvRaiPreview.youtube_dl import YoutubeDL
            ydl_opts = {'format': 'best'}
            '''
            ydl_opts = {'format': 'bestaudio/best'}
            '''
            ydl = YoutubeDL(ydl_opts)
            ydl.add_default_info_extractors()
            result = ydl.extract_info(url, download=False)
            url = result["url"]
            self.session.open(Playstream1, name, url)
        except Exception as e:
            print('error tvr4 e  ', str(e))


class tvRai3(Screen):
    def __init__(self, session, name, url):
        self.session = session
        skin = os.path.join(skin_path, 'settings.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = ('tvRaiPreview')
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
        self['key_yellow'] = Button()
        self['key_yellow'].hide()
        self.timer = eTimer()
        if os.path.exists('/var/lib/dpkg/info'):
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self.timer.start(1500, True)
        self['title'] = Label(name_plugin)
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'DirectionActions'], {'ok': self.okRun,
                                                           'green': self.okRun,
                                                           'red': self.close,
                                                           'cancel': self.close}, -2)

    def _gotPageLoad(self):
        self.names = []
        self.urls = []
        name = self.name
        url = self.url
        content = Utils.getUrl(url)
        if PY3:
            content = six.ensure_str(content)
        try:
            if content.find('behaviour="list">'):
                regexcat = '<label>(.*?)</label>.*?type="list">(.*?).html</url>'
                match = re.compile(regexcat, re.DOTALL).findall(content)
                for name, url in match:
                    url = "http://www.tgr.rai.it/" + url + '.html'
                    name = html_conv.html_unescape(name)
                    self.names.append(str(name))
                    self.urls.append(url)
        except Exception as e:
            print('error: ', str(e))
        self['info'].setText(_('Please select ...'))
        self['key_green'].show()
        showlist(self.names, self['text'])

    def okRun(self):
        i = len(self.names)
        if i < 1:
            return
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
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
                url = result["url"]
                self.session.open(Playstream1, name, url)
            else:
                self.session.open(tvRai4, name, url)
        except Exception as e:
            print('error: ', str(e))


class tvRai4(Screen):
    def __init__(self, session, name, url):
        self.session = session
        skin = os.path.join(skin_path, 'settings.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()
        self.setup_title = ('tvRaiPreview')
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
        self['key_yellow'] = Button()
        self['key_yellow'].hide()
        self.timer = eTimer()
        if os.path.exists('/var/lib/dpkg/info'):
            self.timer_conn = self.timer.timeout.connect(self._gotPageLoad)
        else:
            self.timer.callback.append(self._gotPageLoad)
        self.timer.start(1500, True)
        self['title'] = Label(name_plugin)
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
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
                self.names.append(str(name))
                self.urls.append(url3)
        except Exception as e:
            print('error: ', str(e))
        self['info'].setText(_('Please select ...'))
        self['key_green'].show()
        showlist(self.names, self['text'])

    def okRun(self):
        i = len(self.names)
        if i < 1:
            return
        idx = self["text"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
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
            url = result["url"]
            self.session.open(Playstream1, name, url)
        except Exception as e:
            print('error: ', str(e))


class TvInfoBarShowHide():
    """ InfoBar show/hide control, accepts toggleShow and hide actions, might start
    fancy animations. """
    STATE_HIDDEN = 0
    STATE_HIDING = 1
    STATE_SHOWING = 2
    STATE_SHOWN = 3
    skipToggleShow = False

    def __init__(self):
        self["ShowHideActions"] = ActionMap(["InfobarShowHideActions"], {
            "toggleShow": self.OkPressed,
            "hide": self.hide
        }, 0)

        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
            iPlayableService.evStart: self.serviceStarted
        })
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


class Playstream1(Screen):
    def __init__(self, session, name, url):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session

        skin = os.path.join(skin_path, 'Playstream1.xml')
        with codecs.open(skin, "r", encoding="utf-8") as f:
            self.skin = f.read()

        self.setup_title = ('Select Player Stream')
        self.setTitle(desc_plugin)
        self.list = []
        self['list'] = SetList([])
        self['info'] = Label('Select Player Stream')
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(_('Select'))
        self['actions'] = ActionMap(['MoviePlayerActions',
                                     'MovieSelectionActions',
                                     'MediaPlayerActions',
                                     'EPGSelectActions',
                                     'MediaPlayerSeekActions',
                                     'DirectionActions',
                                     'ButtonSetupActions',
                                     'OkCancelActions',
                                     'InfobarShowHideActions',
                                     'InfobarActions',
                                     'InfobarSeekActions'], {'red': self.cancel,
                                                             'green': self.okClicked,
                                                             'back': self.cancel,
                                                             'cancel': self.cancel,
                                                             'leavePlayer': self.cancel,
                                                             # 'yellow': self.taskManager,
                                                             # 'rec': self.runRec,
                                                             # 'instantRecord': self.runRec,
                                                             # 'ShortRecord': self.runRec,
                                                             'ok': self.okClicked}, -2)
        self.name = Utils.cleanName(name)
        self.url = url
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        url = self.url
        self.names = []
        self.urls = []
        self.names.append('Play Direct')
        self.urls.append(url)
        self.names.append('Play Hls')
        self.urls.append(url)
        self.names.append('Play Ts')
        self.urls.append(url)
        showlist(self.names, self['list'])

    def okClicked(self):
        idx = self['list'].getSelectionIndex()
        if idx is not None or idx != -1:
            self.name = self.name
            self.url = self.urls[idx]
            if idx == 0:
                self.play()
            elif idx == 1:
                try:
                    os.remove('/tmp/hls.avi')
                except:
                    pass
                header = ''
                cmd = 'python "/usr/lib/enigma2/python/Plugins/Extensions/tvRaiPreview/lib/hlsclient.py" "' + self.url + '" "1" "' + header + '" + &'
                os.system(cmd)
                os.system('sleep 3')
                self.url = '/tmp/hls.avi'
                self.play()
            elif idx == 2:
                url = self.url
                try:
                    os.remove('/tmp/hls.avi')
                except:
                    pass
                cmd = 'python "/usr/lib/enigma2/python/Plugins/Extensions/tvRaiPreview/lib/tsclient.py" "' + url + '" "1" + &'
                os.system(cmd)
                os.system('sleep 3')
                self.url = '/tmp/hls.avi'
                self.play()
            # preview
            elif idx == 3:
                print('In playVideo url D=', self.url)
                self.play2()
            else:
                print('In playVideo url D=', self.url)
                self.play()
            return

    def playfile(self, serverint):
        self.serverList[serverint].play(self.session, self.url, self.name)

    def play(self):
        url = self.url
        name = self.name
        self.session.open(Playstream2, name, url)

    def play2(self):
        self['info'].setText(self.name)
        url = self.url.replace(':', '%3a')
        print('In url =', url)
        ref = '4097:0:1:0:0:0:0:0:0:0:' + url
        sref = eServiceReference(ref)
        print('SREF: ', sref)
        sref.setName(self.name)
        self.session.nav.playService(sref)

    def cancel(self):
        try:
            self.session.nav.stopService()
            self.session.nav.playService(self.srefInit)
            self.close()
        except:
            pass


class Playstream2(Screen, InfoBarMenu, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarAudioSelection, TvInfoBarShowHide, InfoBarSubtitleSupport):
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    ENABLE_RESUME_SUPPORT = True
    ALLOW_SUSPEND = True
    screen_timeout = 5000

    def __init__(self, session, name, url):
        global streaml, _session
        Screen.__init__(self, session)
        self.session = session
        _session = session
        self.skinName = 'MoviePlayer'
        streaml = False
        InfoBarMenu.__init__(self)
        InfoBarNotifications.__init__(self)
        InfoBarBase.__init__(self, steal_current_service=True)
        TvInfoBarShowHide.__init__(self)
        InfoBarAudioSelection.__init__(self)
        InfoBarSubtitleSupport.__init__(self)
        try:
            self.init_aspect = int(self.getAspect())
        except:
            self.init_aspect = 0
        self.new_aspect = self.init_aspect
        self['actions'] = ActionMap(['WizardActions', 'MoviePlayerActions', 'MovieSelectionActions', 'MediaPlayerActions', 'EPGSelectActions', 'MediaPlayerSeekActions', 'ColorActions',
                                     'ButtonSetupActions', 'InfobarShowHideActions', 'InfobarActions', 'InfobarSeekActions'], {
            'leavePlayer': self.cancel,
            'epg': self.showIMDB,
            'info': self.showIMDB,
            # 'info': self.cicleStreamType,
            'tv': self.cicleStreamType,
            'stop': self.leavePlayer,
            'cancel': self.cancel,
            'back': self.cancel
        }, -1)
        self.allowPiP = False
        self.service = None
        InfoBarSeek.__init__(self, actionmap='InfobarSeekActions')
        self.url = url
        self.name = html_conv.html_unescape(name)
        self.state = self.STATE_PLAYING
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        if '8088' in str(self.url):
            self.onFirstExecBegin.append(self.slinkPlay)
        else:
            self.onFirstExecBegin.append(self.cicleStreamType)
        return

    def getAspect(self):
        return AVSwitch().getAspectRatioSetting()

    def getAspectString(self, aspectnum):
        return {0: '4:3 Letterbox',
                1: '4:3 PanScan',
                2: '16:9',
                3: '16:9 always',
                4: '16:10 Letterbox',
                5: '16:10 PanScan',
                6: '16:9 Letterbox'}[aspectnum]

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
        temp += 1
        if temp > 6:
            temp = 0
        self.new_aspect = temp
        self.setAspect(temp)

    def showIMDB(self):
        text_clear = self.name
        if returnIMDB(text_clear):
            print('show imdb/tmdb')

    def slinkPlay(self):
        ref = str(self.url)
        ref = ref.replace(':', '%3a').replace(' ', '%20')
        print('final reference: 1', ref)
        sref = eServiceReference(ref)
        sref.setName(self.name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def openTest(self, servicetype, url):
        url = url.replace(':', '%3a').replace(' ', '%20')
        ref = str(servicetype) + ':0:1:0:0:0:0:0:0:0:' + str(url)
        if streaml is True:
            ref = str(servicetype) + ':0:1:0:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/' + str(url)
        print('final reference 2:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(self.name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def cicleStreamType(self):
        global streaml
        from itertools import cycle, islice
        self.servicetype = '4097'
        print('servicetype1: ', self.servicetype)
        url = str(self.url)
        if str(os.path.splitext(url)[-1]) == ".m3u8":
            if self.servicetype == "1":
                self.servicetype = "4097"
        currentindex = 0
        streamtypelist = ["4097"]
        # if "youtube" in str(self.url):
            # self.mbox = self.session.open(MessageBox, _('For Stream Youtube coming soon!'), MessageBox.TYPE_INFO, timeout=5)
            # return
        # if Utils.isStreamlinkAvailable():
            # streamtypelist.append("5002")
            # streaml = True
        # if os.path.exists("/usr/bin/gstplayer"):
            # streamtypelist.append("5001")
        # if os.path.exists("/usr/bin/exteplayer3"):
            # streamtypelist.append("5002")
        # if os.path.exists("/usr/bin/apt-get"):
            # streamtypelist.append("8193")
        for index, item in enumerate(streamtypelist, start=0):
            if str(item) == str(self.servicetype):
                currentindex = index
                break
        nextStreamType = islice(cycle(streamtypelist), currentindex + 1, None)
        self.servicetype = str(next(nextStreamType))
        print('servicetype2: ', self.servicetype)
        self.openTest(self.servicetype, url)

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
        if os.path.exists('/tmp/hls.avi'):
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
        self.session.nav.stopService()
        self.session.nav.playService(self.srefInit)
        self.close()


def main(session, **kwargs):
    try:
        from . import Update
        Update.upd_done()
    except:
        import traceback
        traceback.print_exc()
    session.open(tgrRai)


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
