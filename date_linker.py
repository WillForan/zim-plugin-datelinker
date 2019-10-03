
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

from zim.gui.pageview import PageViewExtension
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

    plugin_notebook_preferences = (
        # key, type, label, default
        ('datefmt', 'string', _('date format for links to journal page'), '[d: %Y-%m-%d]'), # T: preferences option
    )


class DateLinkerPageViewExtension(PageViewExtension):
    '''Extension used to add hotkey'''

    def __init__(self, plugin, pageview):
        PageViewExtension.__init__(self, plugin, pageview)

        self.notebook = pageview.notebook
        self.previous_page = None
        self.connectto(pageview, 'page-changed', lambda o, p: self.set_prev(p))
        self.journal = JournalPlugin()
        raise(self.journal)

        # TODO: fix this?
        # properties = self.plugin.notebook_properties(self.notebook)
        # self.connectto(properties, 'changed', self.on_properties_changed)
        # self.on_properties_changed(properties)

    def set_prev(self, p):
        self.previous_page = p
        print(p)

    @action(_('_ExplainNow'), accelerator='<Control><Shift>E', menuhints='go') # T: menu item
    def go_page_today(self):
        today = datetime.date.today()
        path = self.journal.path_from_date(self.pageview.notebook, today)
        self.navigation.open_page(path)
        # ui.notebook.store_page(page);
        # 
        # # Move the cursor to the end of the line that was just appended...
        # textBuffer = self.pageview.textview.get_buffer();
        # i = textBuffer.get_end_iter();
        # i.backward_visible_cursor_positions(1);
        # textBuffer.place_cursor(i);
        # 
        # # and finally... scroll the window all the way to the bottom.
        # self.pageview.scroll_cursor_on_screen()
