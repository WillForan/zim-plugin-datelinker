
# Copyright 2009-2018 Jaap Karssenberg <jaap.karssenberg@gmail.com>


from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk

import re

from functools import partial

import logging

from zim.plugins import PluginClass
from zim.actions import action
from zim.signals import SignalHandler, ConnectorMixin
import zim.datetimetz as datetime
from zim.datetimetz import dates_for_week, weekcalendar
from zim.notebook import Path, NotebookExtension
from zim.notebook.index import IndexNotFoundError
from zim.templates.expression import ExpressionFunction

from zim.gui.pageview import PageViewExtension, FIND_REGEX, _is_heading_tag, ParseTree
from zim.gui.widgets import ScrolledWindow, \
    WindowSidePaneWidget, LEFT_PANE, PANE_POSITIONS

from zim.plugins.pageindex import PageTreeStore, PageTreeView
from zim.plugins.journal import JournalPlugin


logger = logging.getLogger('zim.plugins.date_linker')


# FUTURE: Use calendar.HTMLCalendar from core libs to render this plugin in www

# TODO: add extension
# - hook to the pageview end-of-word signal and link dates
#   add a preference for this
# - Overload the "Insert date" dialog by adding a 'link' option


date_path_re = re.compile(r'^(.*:)?\d{4}:\d{1,2}:\d{2}$')
week_path_re = re.compile(r'^(.*:)?\d{4}:Week \d{2}$')
month_path_re = re.compile(r'^(.*:)?\d{4}:\d{1,2}$')
year_path_re = re.compile(r'^(.*:)?\d{4}$')



class DateLinkerPlugin(PluginClass):
    """define plugin"""
    plugin_info = {
        'name': _('Date Linker'), # T: plugin name
        'description': _('Forward and back link pages to journal entries'),
        # T: plugin description
        'author': 'Will Foran',
    }

    plugin_preferences = (
        # key, type, label, default
        ('hours_past_midnight', 'int', _('Hours past Midnight'), 4, (0, 12)),
        ('date_fmt', 'string', _('date format for links to journal page'), '[d: %Y-%m-%d]'), # T: preferences option
    )


class DateLinkerPageViewExtension(PageViewExtension):
    '''Extension used to add hotkey'''

    def __init__(self, plugin, pageview):
        PageViewExtension.__init__(self, plugin, pageview)

        self.notebook = pageview.notebook
        self.hour_delta = datetime.timedelta(hours=self.plugin.preferences['hours_past_midnight'])
        self.journal = JournalPlugin()

        # TODO: fix this?
        # properties = self.plugin.notebook_properties(self.notebook)
        # self.connectto(properties, 'changed', self.on_properties_changed)
        # self.on_properties_changed(properties)

    @action(_('E_xplainNow'), accelerator='<Control><Shift>E', menuhints='go') # T: menu item
    def go_page_today(self):
        """ insert text on todays page
        modified from zim.plugins.journal.go_page_today """
        curpage = self.pageview.page.name

        # early morning same day as late night
        # by default: if it's 4am, pretend it's midnight
        now = datetime.datetime.today() - self.hour_delta
        path = self.journal.path_from_date(self.pageview.notebook, now.date())

        # what if page doesn't exist?
        self.navigation.open_page(path)

        # what to insert
        logger.warn(curpage)
        text = xml_link(curpage, curpage, ' - \n')

        # page = self.pageview.notebook.get_path(path)
        # self.pageview.notebook.store_page(page)
        buffer = self.pageview.textview.get_buffer()
        insert_text(buffer, text, end=find_date_heading(buffer))

        # # and finally... scroll the window all the way to the bottom.
        # self.pageview.scroll_cursor_on_screen()


def _is_heading(thisiter):
    """is what we are looking at a header?
    shamelessly copied from tableofcontents plugin"""
    return bool(filter(_is_heading_tag, thisiter.get_tags()))


def find_date_heading(buffer):
    '''Find a heading
    @param buffer: the C{gtk.TextBuffer}
    @returns: a C{gtk.TextIter} for cursor at end of header or C{None}
    '''
    # TODO: use journal plugin settings to get heading?
    today = datetime.strftime("%A %0d %B", datetime.datetime.today())
    regex = "^%s$" % re.escape(today)
    with buffer.tmp_cursor():
        if buffer.finder.find(regex, FIND_REGEX):
            myiter = buffer.get_insert_iter()
            start = myiter.get_offset()
        else:
            return None

        while not _is_heading(myiter):
            if buffer.finder.find_next():
                myiter = buffer.get_insert_iter()
                if myiter.get_offset() == start:
                    return None  # break infinite loop
            else:
                return None

        if _is_heading(myiter):
            start, end = buffer.get_line_bounds(myiter.get_line())
            return end

        else:
            return None


def insert_text(buffer, text, end=None):
    """ insert text onto page
    optionally insert after a matching search
    pulled from inlinecalculator.py
    @param buffer: the C{gtk.TextBuffer}
    @param text: string or xml to insert
    @param search_datehdr: bool flag to insert after (week journal view) date
    @returns: a C{gtk.TextIter} for cursor at end of header or C{None}
    """

    # buffer = self.pageview.textview.get_buffer()

    # end will either be where the search is matched
    # otherwise use current cursor location
    if not end:
        cursor = buffer.get_iter_at_mark(buffer.get_insert())
        start, end = buffer.get_line_bounds(cursor.get_line())
        # from now button plugin
        #  end = buffer.get_end_iter()
        #  end.backward_visible_cursor_positions(1)
        #  buffer.place_cursor(end)

    with buffer.user_action:
        logger.debug("%s is %s", text.__repr__(), type(text))
        if isinstance(text, str):
            buffer.insert(end, text)
        else:
            buffer.insert_parsetree(end, text)


def xml_link(path, linktxt, text=''):
    """
    build a partial zim tree with a link and some text
    @param path  what to link to
    @param linktxt what to show for link
    @param text extra text after link
    @return xml link
    """
    xml = """<?xml version='1.0' encoding='utf-8'?>""" + \
          """<zim-tree partial="True">""" + \
          '<link href=":%(path)s">%(disp)s</link>%(text)s </zim-tree>'
    dispdict = {'path': path, 'disp': linktxt, 'text': text}
    zimtree = ParseTree().fromstring(xml % dispdict)
    return(zimtree)
