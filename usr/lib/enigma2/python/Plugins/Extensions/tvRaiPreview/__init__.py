#!/usr/bin/python
# -*- coding: utf-8 -*-

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext
from os import environ as os_environ
import os

PluginLanguageDomain = 'tvRaiPreview'
PluginLanguagePath = 'Extensions/tvRaiPreview/res/locale'


def localeInit():
    if os.path.exists('/var/lib/dpkg/status'):
        lang = language.getLanguage()[:2]
        os_environ['LANGUAGE'] = lang
    gettext.bindtextdomain(
        PluginLanguageDomain,
        resolveFilename(
            SCOPE_PLUGINS,
            PluginLanguagePath))


if os.path.exists('/var/lib/dpkg/status'):
    def _(txt): return gettext.dgettext(
        PluginLanguageDomain, txt) if txt else ""
    localeInit()
    language.addCallback(localeInit)
else:
    def _(txt):
        if gettext.dgettext(PluginLanguageDomain, txt):
            return gettext.dgettext(PluginLanguageDomain, txt)
        else:
            print(("[%s] fallback to default translation for %s" %
                  (PluginLanguageDomain, txt)))
            return gettext.gettext(txt)
    language.addCallback(localeInit)
