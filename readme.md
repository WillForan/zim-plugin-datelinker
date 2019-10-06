# zim-plugin-DateLinker
## Overview
Quickly timestamp, link, and backlink [Zim wiki](http://zim-wiki.org/)(>= .7) pages and the journal with a hotkey. Also in emacs within [zw-mode](https://github.com/WillForan/zw-mode)

Heavily inspired by [now-button](https://github.com/Osndok/zim-plugin-nowbutton). 


## Install
```
git clone https://github.com/WillForan/zim-plugin-datelinker ~/.local/share/zim/plugins/datelinker
```

  1. Put this repo within the local zim plugin directory (`$XDG_DATA_HOME/zim/plugins/`).
Zim will find `__init__.py` in the datelinker directory within plugins
  1. You will need to restart zim and enable the plugin from the list under `Edit -> Preferences -> Plugins`

## Description
This plugin proves 3 keybindings for quickly linking and backlinking today's journal page.

![screenshot](screenshot.png?raw=True)

* <kbd>Ctrl+Shift+E</kbd> - link current page onto today's page
   1. The window is navigated to today's journal page.
   1. append e.g. `[[Page:IWas:Editting]] - ` to today's page.
      * if date page is week, text is placed after date header (e.g. line after `Friday 31 March` header)
* <kbd>Ctrl+Shift+D</kbd> - link today's page to current page
  * insert date link `[d: yyyy-mm-dd]` at current cursor position. Like <kbd>Ctrl+d</kbd> but without a dialog first and the linked path starts with `:`.
* <kbd>Ctrl+Shift+Y</kbd> - page's absolute path to clipboard
  * differs from <kbd>Ctrl+Shift+L</kbd> in only that the copied path is absolute (starts with `:`)


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
