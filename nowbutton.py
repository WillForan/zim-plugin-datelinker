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
hours_past_midnight=4

# ----------------------

from time import strftime
import gtk


from datetime import datetime, timedelta
from datetime import date as dateclass

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


	def get_cur_path(self,aslink=True):
                pathname = self.window.ui.history.get_current().name 
                if aslink:  pathname = '[[' + pathname + ']]'
                return(pathname)

	@action(_('PathToClipboard'),accelerator = '<Control><Shift>Y') # T: menu item
	def path_to_clip(self):
		curpagelink =  self.get_cur_path(False)
                gtk.Clipboard().set_text(curpagelink)

	@action(
		_('Log Entry'),
		stock=gtk.STOCK_JUMP_TO,
		readonly=True,
		accelerator = '<Control><Shift>E'
	) # T: menu item
	def now_button_clicked(self):
		ui = self.window.ui

		offset_time=datetime.today()-timedelta(hours=hours_past_midnight)

                # find the calendar plugin instantiated by zim
                calplug = [  
                  x[0] for x in self.window.ui.plugins._connected_signals.values() 
                  if "CalendarPlugin" in str(type(x[0]()))
                ]

                # if we didn't find the plugin, it's not loaded
                # we could default to some deafult path template (coded but never reached)
                if(len(calplug)<=0):
                    raise Exception("enable Journal plugin")
                    # or we could just make up a date path
		    name=offset_time.strftime(':Calendar:%Y:Week %W');
		    path=ui.notebook.resolve_path(name);
                else:
                    # get the actual plugin (assume there is only one plugin matching the string 'CalendarPlugin')
                    calplug = calplug[0]()
                    # use calendar plugin to get the path
                    path = calplug.path_from_date(offset_time)


                # get page from path
		page=ui.notebook.get_page(path);

                # make the text to add to the current date page
                # includes where we came from and the current time

		#text = '\n' + strftime('%I:%M%p - ').lower();
		curpagelink = self.get_cur_path()
		curtime     = strftime('%I:%M%p - ').lower();
		text = '\n' + curpagelink + ' - ' + curtime;


		#ui.append_text_to_page(path, text)

                # create the current date page if we dont already have it
		if not page.exists():
			parsetree = ui.notebook.get_template(page)
			page.set_parsetree(parsetree)
		
                # go to that page
                # FIXME format hard coded ??? (this FIXME was copied from gui.__init__)
		page.parse('wiki', text, append=True)
		ui.present(path)
		ui.notebook.store_page(page);

		# Move the cursor to the end of the line that was just appended...
		textBuffer = self.window.pageview.view.get_buffer();
                print(type(textBuffer))
		i = textBuffer.get_end_iter();
		i.backward_visible_cursor_positions(1);
		textBuffer.place_cursor(i);

		# and finally... scroll the window all the way to the bottom.
		self.window.pageview.scroll_cursor_on_screen();


	def on_notebook_changed(self):
		return None
		


