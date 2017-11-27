#!/usr/bin/python
#
# nowbutton.py
# 
# A Zim plugin that jumps to today's journal entry, and appends the current *time* to the end of the file.
# This makes it nearly trivial to keep a log with tighter-than-one-day granularity.
#
# Skeleton and basic operation of this script was DERIVED from zim 'quicknote' and 'tasklist' plugins.
#

# If you tend to make log entries past midnight, this is the number of hours past midnight that
# will be considered "the same day" (for purposes of selecting the journal page). To be most
# effective, it should be the time that you are "most surely asleep". Small for early risers, larger
# for night-owls. For example, a value of '4' would imply that the new day/page starts at '4am'.
hours_past_midnight = 4

# ----------------------

from time import strftime
import gtk


from datetime import datetime, timedelta
from datetime import date as dateclass

# used for inserting buffer, instead of parse(append=True)
from zim.formats import ParseTree

# finding header (copied from plugins/tableofcontents.py)
import re
from zim.gui.pageview import FIND_REGEX, _is_heading_tag

# TODO: kern out unneccesary imports
from zim.plugins import PluginClass, WindowExtension, extends
from zim.actions import action
from zim.config import data_file, ConfigManager
from zim.notebook import Notebook,  NotebookInfo, \
	resolve_notebook, build_notebook
from zim.gui.widgets import Dialog, ScrolledTextView, IconButton, \
	InputForm, gtk_window_set_default_icon, QuestionDialog
from zim.gui.clipboard import Clipboard, SelectionClipboard
from zim.gui.notebookdialog import NotebookComboBox
from zim.templates import get_template

# get current page
#from zim.history import get_current
import zim.history
import logging

logger = logging.getLogger('zim.plugins.nowbutton')

class NowButtonPlugin(PluginClass):

	plugin_info = {
		'name': _('Now Button'), # T: plugin name
		'description': _('''\
This plugin provides an easy toolbar option to append the current time to today's journal entry and
focus that page. Note that it is easy to get back to where you were due to Zim\'s built-in back-tracking
buttons.
'''), # T: plugin description
		'author': 'Robert Hailey',
		'help': 'Plugins:NowButton',
	}

@extends('MainWindow')
class MainWindowExtension(WindowExtension):

	uimanager_xml = '''
		<ui>
			<menubar name='menubar'>
				<menu action='tools_menu'>
					<placeholder name='plugin_items'>
						<menuitem action='now_button_clicked'/>
					        <menuitem action='path_to_clip'/>
					        <menuitem action='quick_date_insert'/>
					</placeholder>
				</menu>
			</menubar>
			<toolbar name='toolbar'>
				<placeholder name='tools'>
					<toolitem action='now_button_clicked'/>
				</placeholder>
			</toolbar>
		</ui>
	'''

	def __init__(self, plugin, window):
		WindowExtension.__init__(self, plugin, window)
                self._preferences = plugin.preferences
		#self.notebookcombobox = NotebookComboBox(current='file:///home/robert/Notebooks/Primary')
		#self.notebookcombobox.connect('changed', self.on_notebook_changed)

        def get_cur_path(self, aslink=True):
            pathname = ':' + self.window.ui.history.get_current().name
            if aslink:
                pathname = '[[' + pathname + ']]'
            return(pathname)

        def get_current_day_page(self):
            ui = self.window.ui
            offset_time = datetime.today()-timedelta(hours=hours_past_midnight)

            # find the calendar/jounal plugin
            plugins = self.window.ui.plugins._connected_signals.values()
            calplug = [
                    x[0] for x in plugins
                    if "CalendarPlugin" in str(type(x[0]()))
                    ]

            # if we didn't find the plugin, it's not loaded
            # we could default to some deafult path template 
            # (coded but never reached)
            if(len(calplug) <= 0):
                raise Exception("enable Journal plugin")
                # or we could just make up a date path
                name = offset_time.strftime(':Calendar:%Y:Week %W')
                path = ui.notebook.resolve_path(name)
            else:
                # get the actual plugin
                # assume there is only one plugin matching 'CalendarPlugin'
                calplug = calplug[0]()
                # use calendar plugin to get the path
                path = calplug.path_from_date(offset_time)

            return(path)



        @action(('QuickDateInsert'), accelerator='<Control><Shift>D')  # T: menu item
        def quick_date_insert(self):
            """
            insert link to date as [yyyy-mm-dd]
            without gui popup of Control+D
            also adds ':' to front of link
            """
            # xml for linked date
            # like [d: yyyy-mm-dd]
            #datelink_xml = """<?xml version='1.0' encoding='utf-8'?><zim-tree partial="True"><link href=":%(path)s">[d: %(disp)s]</link></zim-tree>"""
            #dispdict = {
            #        'path': self.get_current_day_page(),
            #        'disp': strftime('%Y-%m-%d')}
            #datelink = ParseTree().fromstring(datelink_xml % dispdict)
            datelink = get_link_and_text(self.get_current_day_page(), strftime('[d: %Y-%m-%d]'))

            # insert it
            # cribbed from plugins/linesorter.py
            buffer = self.window.pageview.view.get_buffer()
            buffer.insert_parsetree_at_cursor(datelink)

            # quicknote method
            # ui = self.window.ui
            # page = ui.notebook.get_page(self.window.ui.history.get_current())
            # page.parse('wiki', text, append=True)

        @action(('PathToClipboard'), accelerator='<Control><Shift>Y')  # T: menu item
        def path_to_clip(self):
                """
                this is the same as Control-Shit-L
                but it wont auto link on paste
                """
                curpagelink = self.get_cur_path(False)
                gtk.Clipboard().set_text(curpagelink)

	@action(
		('Log Entry'),
		stock=gtk.STOCK_JUMP_TO,
		readonly=True,
		accelerator='<Control><Shift>E'
	)  # T: menu item
	def now_button_clicked(self):
		ui = self.window.ui

                # get page from path
                calpath = self.get_current_day_page()
                page = ui.notebook.get_page(calpath)

                # find the calendar plugin instantiated by zim
                # make the text to add to the current date page
                # includes where we came from and the current time

                # TODO: dont hardcode
		#text = '\n' + strftime('%I:%M%p - ').lower();
		curpagelink = self.get_cur_path()
		curtime     = strftime('%I:%M%p - ').lower()
                text = '\n' + curpagelink + ' - ' + curtime
                # no link version for xml insert
		curpagelink = self.get_cur_path(aslink=False)


		#ui.append_text_to_page(path, text)

                # create the current date page if we dont already have it
		if not page.exists():
			parsetree = ui.notebook.get_template(page)
			page.set_parsetree(parsetree)
		
                # # go to date page and insert
                # either right after the date heading
                # or at the end of the page if we cannot find date
                ui.present(calpath)
                textBuffer = self.window.pageview.view.get_buffer()
                itr = find_date_heading(textBuffer)
                if itr is not None:
                    el = get_link_and_text(curpagelink, curpagelink, ' - @\n')
                    textBuffer.insert_parsetree(itr, el)
                    textBuffer.place_cursor(itr)
                else:
                    page.parse('wiki', text, append=True)
                    ui.notebook.store_page(page)

                    # Move the cursor to the end of the line that was just appended...
                    i = textBuffer.get_end_iter()
                    i.backward_visible_cursor_positions(1)
                    textBuffer.place_cursor(i)

                    # and finally... scroll the window all the way to the bottom.
                    self.window.pageview.scroll_cursor_on_screen()


	def on_notebook_changed(self):
		return None
		

def get_link_and_text(path, linktxt, text=''):
    """
    build a partial zim tree with a link and some text
    @param path  what to link to
    @param linktxt what to show for link
    @param text extra text after link
    """
    xml = """<?xml version='1.0' encoding='utf-8'?>""" + \
          """<zim-tree partial="True">""" + \
          '<link href=":%(path)s">%(disp)s</link>%(text)s </zim-tree>'
    dispdict = {'path': path, 'disp': linktxt, 'text': text}
    zimtree = ParseTree().fromstring(xml % dispdict)
    return(zimtree)


# shamelessly copied from tableofcontents plugin
_is_heading = lambda iter: bool(filter(_is_heading_tag, iter.get_tags()))


def find_date_heading(buffer):
    '''Find a heading
    @param buffer: the C{gtk.TextBuffer}
    @returns: a C{gtk.TextIter} for cursor at end of header or C{None}
    '''
    today = strftime("%A %0d %B")
    regex = "^%s$" % re.escape(today)
    with buffer.tmp_cursor():
        if buffer.finder.find(regex, FIND_REGEX):
            iter = buffer.get_insert_iter()
            start = iter.get_offset()
        else:
            return None

        while not _is_heading(iter):
            if buffer.finder.find_next():
                iter = buffer.get_insert_iter()
                if iter.get_offset() == start:
                    return None  # break infinite loop
            else:
                return None

        if _is_heading(iter):
            start, end = buffer.get_line_bounds(iter.get_line())
            return end

        else:
            return None

