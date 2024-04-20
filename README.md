# wristwatch
[![PyPI version](https://img.shields.io/pypi/v/wristwatch)](https://pypi.org/project/wristwatch/)
[![PyPI downloads](https://img.shields.io/pypi/dm/wristwatch)](https://pypi.org/project/wristwatch/)
[![GitHub license](https://img.shields.io/github/license/zWolfrost/wristwatch)](LICENSE)

Yet another Python watcher for website updates.

&nbsp;
## Features
- Selecting elements to watch with CSS selectors.
- Automatic importing of cookies from many browsers.
- Emailing the changes to yourself.
- Other features...

You can safely quit watching at any time by pressing `Ctrl+C`.

&nbsp;
## Installation
After having installed [Python 3](https://www.python.org/downloads/) with pip, you can install wristwatch using the following command:
```bash
pip install wristwatch
```

&nbsp;
## Arguments
| Command            | Example                     | Description
|:-:                 | :-:                         |:-
|                    | `"https://example.com/"`    | The URL of the webpage to scrape.
| `-b` `--browser`   | `-b "chrome"`               | Name of the browser to get cookies from (by default, any<br>browser possible). See `--help` for supported browsers.
| `-f` `--frequency` | `-f 60`                     | Frequency of fetches in seconds (default: 60).
| `-s` `--selector`  | `-s "#minutes" -s "#hours"` | CSS selector of element(s) to scrape. Can be used multiple times.
| `-a` `--attribute` | `-a "href" -a "title"`      | Attribute of the element(s) to scrape. Can be used multiple times.<br>Can also be "text" to scrape the text content.
| `-e` `--email`     | `-e "example@gmail.com"`    | Email address to self-send the changes to.
| `-p` `--password`  | `-p "aaaa bbbb cccc dddd"`  | Email "app" password. [Here's a guide on how to generate one](https://support.google.com/accounts/answer/185833#app-passwords).
| `-i` `--input`     | `-i "input.txt"`            | Load the first fetch from a file.
| `-o` `--output`    | `-o "output.txt"`           | Save the last fetch to a file.
| `-q` `--quiet`     | `-q`                        | Decrease output verbosity.
| `-l` `--loop`      | `-l`                        | Keep watching for changes even after the first one.
| `-c` `--chime`     | `-c`                        | Play a sound when changes are detected.
| `-v` `--version`   | `-v`                        | Show the program's version.
| `-h` `--help`      | `-h`                        | Show the help message on how to use the program.

&nbsp;
## Examples
```bash
wristwatch "https://relaxingclock.com" -s "#minutes" -f 5 -a -l
```

&nbsp;
## Screenshots

![Enter commands](screenshots/1.png)

&nbsp;
## Changelog
*This changelog only includes changes that are worth mentioning.*

- **1.0.0**:
<br>- Initial release.
	- 1.0.1
	<br>-Specified dependencies version requirements
	- 1.0.2
	<br>-Fixed `--loop` argument not working
- **1.1.0**:
<br>- Added `--alert` argument to play a sound when changes are detected.
- **1.2.0**:
<br>- Added `--debug` argument to show debug info & error messages.
<br>- Changed "rookiepy" dependency for "browser-cookie3"
<br>- Better error handling.
- **1.3.0**:
<br>- Added `--attribute` argument to scrape attributes and text content.
<br>- Changed `--alert` argument name to `--chime`
<br>- Better error handling.