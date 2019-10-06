"""
DateLinker plugin cribbed from other plugins
namly
  nowbutton - intial starting point
  journal - get the current page
  inlinecalculator, linesort - inserting text
  tableofcontents - finding headers
also see
  https://developer.gnome.org/pygtk/stable/class-gtktextiter.html
  https://developer.gnome.org/pygtk/stable/class-gtktextbuffer.html
"""
import re
import logging
import gettext
import gtk

from zim.plugins import PluginClass
from zim.actions import action
import zim.datetimetz as datetime
from zim.gui.clipboard import Clipboard
# from zim.datetimetz import dates_for_week, weekcalendar
# from zim.notebook import Path
# from zim.notebook.index import IndexNotFoundError

from zim.gui.pageview import PageViewExtension, FIND_REGEX,\
    _is_heading_tag, ParseTree
from zim.plugins.journal import JournalPlugin

# ## setup
LOGGER = logging.getLogger('zim.plugins.date_linker')
_ = gettext.gettext  # avoid lint issues


class DateLinkerPlugin(PluginClass):
    """define plugin"""
    plugin_info = {
        'name': _('Date Linker'),
        'description': _('Forward and back link pages to journal entries'),
        'author': 'Will Foran',
    }

    plugin_preferences = (
        # key, type, label, default
        ('hours_past_midnight', 'int', _('Hours past Midnight'), 4, (0, 12)),
        ('explain_fmt', 'string', _('Template for journal insert'), "$L - "),
        ('date_fmt', 'string', _('date format for links to journal page'),
         '[d: %Y-%m-%d] - '),
    )


class DateLinkerPageViewExtension(PageViewExtension):
    """Extension used to add hotkey"""

    def __init__(self, plugin, pageview):
        PageViewExtension.__init__(self, plugin, pageview)

        self.notebook = pageview.notebook
        hpm = self.plugin.preferences['hours_past_midnight']
        self.hour_delta = datetime.timedelta(hours=hpm)
        self.journal = JournalPlugin()

        # TODO: fix this?
        # properties = self.plugin.notebook_properties(self.notebook)
        # self.connectto(properties, 'changed', self.on_properties_changed)
        # self.on_properties_changed(properties)
    def current_date_page(self):
        """get the path to current date's journal page"""
        # early morning same day as late night
        # by default: if it's 4am, pretend it's midnight
        now = datetime.datetime.today() - self.hour_delta
        path = self.journal.path_from_date(self.pageview.notebook, now.date())
        return path

    @action(_('AbsY_ank'), accelerator='<Control><Shift>Y', menuhints='go')
    def yank_current_path(self):
        """copy the absolute path of the current page to the clipboard"""
        curpage = ":" + self.pageview.page.name
        Clipboard.set_text(curpage)

    @action(_('AbsD_ateLink'), accelerator='<Control><Shift>D', menuhints='go')
    def insert_abs_date(self):
        """insert link to abs date where we are editing"""
        path = self.current_date_page().name
        buffer = self.pageview.textview.get_buffer()
        datefmt = self.plugin.preferences['date_fmt']

        today = datetime.strftime(datefmt, datetime.datetime.today())
        datelink = zim_xml(xml_link(path, today))

        buffer.insert_parsetree_at_cursor(datelink)

    @action(_('E_xplainNow'), accelerator='<Control><Shift>E', menuhints='go')
    def go_page_today(self):
        """ insert text on todays page
        modified from zim.plugins.journal.go_page_today """
        curpage = ":" + self.pageview.page.name

        path = self.current_date_page()

        # what if page doesn't exist?
        self.navigation.open_page(path)

        # what to insert
        fmt = self.plugin.preferences['explain_fmt']
        fmt = re.sub('\$L', xml_link(curpage), fmt)
        # TODO: run fmt through strftime?
        text = zim_xml(fmt)

        # page = self.pageview.notebook.get_path(path)
        # self.pageview.notebook.store_page(page)
        buffer = self.pageview.textview.get_buffer()
        heading = find_date_heading(buffer)  # None if no match
        insert_text(buffer, text, insert_at=heading)

        # # and finally... scroll the window all the way to the bottom.
        # self.pageview.scroll_cursor_on_screen()


def _is_heading(thisiter):
    """is what we are looking at a header?
    shamelessly copied from tableofcontents plugin"""
    return bool(filter(_is_heading_tag, thisiter.get_tags()))


def find_date_heading(buffer):
    """Find a heading
    @param buffer: the C{gtk.TextBuffer}
    @returns: a C{gtk.TextIter} for cursor at end of header or C{None}
    """
    # TODO: use journal plugin settings to get heading?
    today = datetime.strftime("%A %0d %B", datetime.datetime.today())
    regex = "^%s$" % re.escape(today)  # "^%A %0d %B$"
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

        # haven't returned None, current line should be a header
        if _is_heading(myiter):
            start, end = buffer.get_line_bounds(myiter.get_line())
            return end


def insert_text(buffer, text, insert_at=None):
    """ insert text onto page
    optionally insert after a matching search
    pulled from inlinecalculator.py, linesorter.py
    @param buffer: the C{gtk.TextBuffer}
    @param text: string or xml to insert
    @param insert_at:  C{gtk.TextIter} insert position. EOF if None (default)
    @returns: a C{gtk.TextIter} end of line where inserted
    """

    # buffer = self.pageview.textview.get_buffer()

    # end will either be where the search is matched
    # otherwise use current cursor location
    if not insert_at:
        # from nowbutton plugin - end of page
        insert_at = buffer.get_end_iter()

    # after insert, insert_at is invalidated (buffer changed)
    # so get line now
    insert_line = insert_at.get_line()

    with buffer.user_action:
        if isinstance(text, str):
            buffer.insert(insert_at, text)
        else:
            buffer.place_cursor(insert_at)
            buffer.insert_parsetree_at_cursor(text)

    # from inlinecalculator, linesorter
    start, end_at = buffer.get_line_bounds(insert_line)
    # wrong for muliline insert. TODO: count "\n" and add to get_line?
    return end_at


def xml_link(path, linktxt=None):
    """gtk xml for a link
    @param path  what to link to
    @param linktxt what to show for link, default to same as path
    @return xml link text
    """
    if not linktxt:
        linktxt = path
    return """<link href="%s">%s</link>""" % (path, linktxt)


def zim_xml(text):
    """
    build a partial zim tree with a link and some text
    @param text what to wrap in xml
    @return xml zim-tree xml ready for insert
    """
    xml = """<?xml version='1.0' encoding='utf-8'?>""" + \
          """<zim-tree partial="True">""" + \
          '%s</zim-tree>'
    zimtree = ParseTree().fromstring(xml % text)
    return zimtree
