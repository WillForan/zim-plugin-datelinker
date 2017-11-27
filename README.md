# zim-plugin-nowbutton
## Overview
Super-easy way to make a timestamped log entries in the [Zim wiki](http://zim-wiki.org/)'s Journal with the click of a button or hotkey.

This is a plugin only. This is not zim.

## Plugin
When this new button is clicked or the hotkey (Ctrl+Shift+E) pressed, the following happens:
* If the current day's journal page does not exist, it is created. **The Journal plugin must be enabled.**
* The window is navigated to today's journal page.
* The page's text has the a link to previous page and current time appended to it (e.g. "\n[[Page:IWas:Editting]] - 04:52pm - ")
   * if date page is week, text is placed after date header (e.g. line after "Friday 31 March" header)
* The cursor is placed at the end of that new line, ready to type "what's happening now".

This plugin also provides two additional hotkeys
 * Ctrl+Shift+D: insert date link `[d: yyyy-mm-dd]` at current cursor postion. Like `Ctrl+d` but without a dialog first and the linked path starts with `:`.
 * Ctrl+Shift+Y: copy (yank) the path of the current page to the clipboard. nearly identical to the built in Ctrl+Shift+L, but does not paste as a relative link


## Install
To install this plugin, place the "py" file at "$HOME/.local/share/zim/plugins", and [re]start Zim.

```
svn export https://github.com/WillForan/zim-plugin-nowbutton/trunk/nowbutton.py ~/.local/share/zim/plugins/ 
```

## ToDo
* use preferences
  * insert text string format: $L for previouslink; time formates
  * specify path pattern instead of using journal plugin
* unit tests
* zim style plugin documentation
