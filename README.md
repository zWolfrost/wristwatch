# wristwatch
![PyPI version](https://img.shields.io/pypi/v/wristwatch)
![PyPI downloads](https://img.shields.io/pypi/dm/wristwatch)
![GitHub license](https://img.shields.io/github/license/zWolfrost/wristwatch)

Yet another Python watcher for website updates.

&nbsp;
## Features
- Selecting elements to watch with CSS selectors.
- Importing Cookies from any browser (to scrape webpages that require authentication).
- Emailing the changes to yourself.
- Other minor features...

You can safely quit watching at any time by pressing `Ctrl+C`.

&nbsp;
## Installation
After having installed [Python 3](https://www.python.org/downloads/) with pip, you can install wristwatch using the following command:
```bash
pip install wristwatch
```

&nbsp;
## Arguments
| Command     | Shorthand | Example                  | Description
|:-:          |:-:        | :-:                      |:-
|             |           | `https://example.com/`   | The URL of the webpage to scrape.
| --browser   | -b        | `-b chrome`              | Name of the browser to get cookies from (default: any).
| --frequency | -f        | `-f 60`                  | Frequency of fetches in seconds (default: 60).
| --selector  | -s        | `-s #minutes -s #hours`  | CSS selector of element(s) to scrape. Can be used multiple times.
| --email     | -e        | `-e example@gmail.com`   | Email address to self-send the changes to.
| --password  | -p        | `-p aaaa bbbb cccc dddd` | Email "app" password. Here's a guide on how to generate one: https://support.google.com/accounts/answer/185833
| --quiet     | -q        | `-q`                     | Decrease output verbosity.
| --loop      | -l        | `-l`                     | Keep watching for changes even after the first one.
| --output    | -o        | `-o output.txt`          | Save the last fetch to a file.
| --input     | -i        | `-i input.txt`           | Load the first fetch from a file.
| --alert     | -a        | `-a`                     | Play a sound when changes are detected.
| --version   | -v        | `-v`                     | Show the program's version.

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