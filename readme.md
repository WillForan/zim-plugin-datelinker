# zim-plugin-DateLinker
## Overview
Quickly timestamp, link, and backlink [Zim wiki](http://zim-wiki.org/) pages and the journal with a hotkey.

Heavily inspired by [now-button](https://github.com/Osndok/zim-plugin-nowbutton).

## Install
```
git clone https://github.com/WillForan/zim-plugin-datelinker ~/.local/share/zim/plugins/datelinker
```

  - Put this repo within the local zim plugin directory (`$XDG_DATA_HOME/zim/plugins/`).
Zim will find `__init__.py` in the datelinker directory within plugins
  - You will need to restart zim and enable the plugin from the list under `Edit -> Preferences -> Plugins`

## Description
This plugin proves 3 keybindings for quickly linking and backlinking today's journal page.

* <kbd>Ctrl+Shift+E</kbd> - link current page onto today's page
   1. If the current day's journal page does not exist, it is created. **The Journal plugin must be enabled.**
   1. The window is navigated to today's journal page.
   1. The page's text has a link to previous page and current time appended to it (e.g. `\n[[Page:IWas:Editting]] - @ `)
      * if date page is week, text is placed after date header (e.g. line after `Friday 31 March` header)
   1. The cursor is placed at the end of that new line, ready to type "what's happening now".
* <kbd>Ctrl+Shift+D</kbd> - link today's page to current page
  * insert date link `[d: yyyy-mm-dd]` at current cursor position. Like <kbd>Ctrl+d</kbd> but without a dialog first and the linked path starts with `:`.
* <kbd>Ctrl+Shift+Y</kbd> - absolute path to clipboard
  * differs from <kbd>Ctrl+L</kbd> in only that the copied path is absolute (starts with `:`)
  * copy (yank) the path of the current page to the clipboard. nearly identical to the built in <kbd>Ctrl+Shift+L</kbd>, but does not paste as a relative link


## Work Flow
### date backlinking
1. <kbd>Ctrl+J</kbd> jump to title or  <kbd>Ctrl+Shift+F</kbd> search all pages for some text
1. jump to and edit edit page
1. <kbd>Ctrl+Shift+E</kbd> to link current page back to the current day + jump to current date

### date forward linking
1. <kbd>Alt+d</kbd> to go to date page
1. <kbd>Ctl+L</kbd> to insert link to page to edit
1. go to page
1. <kbd>Ctrl+Shift+D</kbd> to insert link to date and keep editing

## ToDo
* unit tests
* zim style plugin documentation
