# zim-plugin-nowbutton
## Overview
Super-easy way to make a timestamped log entries in the [Zim wiki](http://zim-wiki.org/)'s Journal with the click of a button or hotkey.

This is a plugin only. This is not zim.

## Install
Install this plugin like any zim plugin: place the `py` file in `$HOME/.local/share/zim/plugins` and [re]start Zim.

```
svn export https://github.com/WillForan/zim-plugin-nowbutton/trunk/nowbutton.py ~/.local/share/zim/plugins/ 
```


## Plugin

* <kbd>Ctrl+Shift+E</kbd>
   1. If the current day's journal page does not exist, it is created. **The Journal plugin must be enabled.**
   1. The window is navigated to today's journal page.
   1. The page's text has the a link to previous page and current time appended to it (e.g. `\n[[Page:IWas:Editting]] - @ `)
      * if date page is week, text is placed after date header (e.g. line after `Friday 31 March` header)
   1. The cursor is placed at the end of that new line, ready to type "what's happening now".

* <kbd>Ctrl+Shift+D</kbd>
  * insert date link `[d: yyyy-mm-dd]` at current cursor postion. Like <kbd>Ctrl+d</kbd> but without a dialog first and the linked path starts with `:`.
* <kbd>Ctrl+Shift+Y</kbd>
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
* use preferences
  * insert text string format: $L for previouslink; time formates
  * specify path pattern instead of using journal plugin
* unit tests
* zim style plugin documentation
