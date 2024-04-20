#! venv/bin/python 

import time, os, sys, argparse, difflib
from urllib.parse import urlparse

from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome

from bs4 import BeautifulSoup
from bs4.formatter import HTMLFormatter
from soupsieve.util import SelectorSyntaxError

import browser_cookie3, chime

import smtplib, ssl
from email.message import EmailMessage


debug_mode = False



def get_args() -> dict:
	parser = argparse.ArgumentParser(prog="wristwatch", description="Yet another Python watcher for website updates.")

	parser.add_argument("webpage", type=str, help="The URL of the webpage to scrape.", metavar="URL")

	parser.add_argument("-b", "--browser", type=str, help="Name of the browser to get cookies from (by default, any browser possible).", default="load", choices=["brave", "chrome", "chromium", "edge", "firefox", "librewolf", "opera", "opera_gx", "safari", "vivaldi"])
	parser.add_argument("-f", "--frequency", type=int, help="Frequency of fetches in seconds (default: 60).", default=60, metavar="SECONDS")
	parser.add_argument("-s", "--selector", type=str, help="CSS selector of element(s) to scrape. Can be used multiple times.", action="extend", nargs="+")
	parser.add_argument("-a", "--attribute", type=str, help="Attribute of the element(s) to scrape. Can be used multiple times. Can also be \"text\" to scrape the text content.", action="extend", nargs="+")

	parser.add_argument("-e", "--email", type=str, help="Email address to self-send the changes to.", required=("-p" in sys.argv or "--password" in sys.argv))
	parser.add_argument("-p", "--password", type=str, help="Email \"app\" password. Here's a guide on how to generate one: https://support.google.com/accounts/answer/185833", required=("-e" in sys.argv or "--email" in sys.argv))

	parser.add_argument("-i", "--input", type=str, help="Load the first fetch from a file.", metavar="FILE")
	parser.add_argument("-o", "--output", type=str, help="Save the last fetch to a file.", metavar="FILE")

	parser.add_argument("-q", "--quiet", help="Decrease output verbosity.", action="store_true")
	parser.add_argument("-l", "--loop", help="Keep watching for changes even after the first one.", action="store_true")
	parser.add_argument("-c", "--chime", help="Play a sound when changes are detected.", action="store_true")

	parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.3.0")
	parser.add_argument("-d", "--debug", help="Enable debug mode.", action="store_true")

	return vars(parser.parse_args())


def cookie_to_dict(cookie) -> dict:
	cookie_dict = {
		"name": getattr(cookie, "name", None),
		"value": getattr(cookie, "value", None),
		"path": getattr(cookie, "path", None),
		"domain": getattr(cookie, "domain", None),

		"secure": getattr(cookie, "secure", None) is True,
		"httpOnly": "HTTPOnly" in getattr(cookie, "_rest", None),
		"expiry": getattr(cookie, "expires", None),

		# "sameSite" value not available in browser_cookie3
	}

	if (debug_mode):
		print(vars(cookie), "\n------------\n", cookie_dict, "\n")

	return cookie_dict

def add_cookies(driver: Chrome, cookies: list = None) -> int:
	if (cookies is None):
		return None
	else:
		errorCookies = 0

		for (i, cookie) in enumerate(cookies):
			try:
				driver.add_cookie(cookie)
			except BaseException as e:
				if (debug_mode):
					print(f"COOKIE NO. {i + 1}")
					print(e)
				errorCookies += 1

		return len(cookies) - errorCookies

def fetch_driver(driver: Chrome, selectors: list = None, attributes: list = None) -> str:
	formatter = HTMLFormatter(indent=3)
	soup = BeautifulSoup(driver.page_source, "html.parser")

	if (selectors is None):
		return str(soup.prettify(formatter=formatter))
	else:
		fetch = ""

		for selector in selectors:

			elements = soup.select(selector)

			for i, el in enumerate(elements):
				if (attributes):
					for attributeName in attributes:
						if (attributeName == "text"):
							fetch += el.get_text() + "\n"
						else:
							attributeValue = el.get(attributeName, None)
							if (attributeValue is not None):
								if (isinstance(attributeValue, list)):
									attributeValue = " ".join(attributeValue)
								fetch += attributeValue + "\n"
				else:
					fetch += str(el.prettify(formatter=formatter))
					if (i < len(elements) - 1):
						fetch += "\n"

		fetch = fetch.strip()

		return fetch


def print_text(text: str, line_numbers: bool = False, prefix: str = ""):
	if (text == ""):
		print("<empty>")
		return

	try:
		max_length = os.get_terminal_size().columns
	except:
		max_length = None

	break_line = "..."
	padding = len(str(len(text.splitlines())))
	for i, line in enumerate(text.splitlines()):
		full_line = prefix
		if (line_numbers): full_line += f"{str(i + 1).rjust(padding)}: "
		full_line += line

		if (max_length and len(full_line) > max_length):
			full_line = full_line[:max_length - len(break_line)] + break_line

		print(full_line)

def print_sleep(string: str, seconds: int = 0):
	try:
		padding = len(string.format(seconds))
		for i in range(seconds, 0, -1):
			print("\r" + (string.format(i)).ljust(padding), end="")
			time.sleep(1)
		print("\r" + " " * padding + "\r", end="")
	except KeyboardInterrupt:
		print("\b\b  ")
		sys.exit()


def send_email(from_email: str, to_email: str, password: str, subject="", body="", attachments=[]):
	msg = EmailMessage()
	msg["From"] = from_email
	msg["To"] = to_email
	msg["Subject"] = subject
	msg.set_content(body)

	for attachment in attachments:
		with open(attachment, "rb") as f:
			attachment_data = f.read()
			attachment_name = os.path.basename(attachment)

		msg.add_attachment(attachment_data, maintype="application", subtype="octet-stream", filename=attachment_name)

	context = ssl.create_default_context()

	with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
		smtp.login(from_email, password)
		smtp.sendmail(from_email, to_email, msg.as_string())



def main():
	####
	## Parse arguments and initialize driver
	####

	chime.theme("material")

	ARGS = get_args()
	DOMAIN = urlparse(ARGS["webpage"]).netloc

	if (ARGS["debug"]):
		global debug_mode
		debug_mode = True
		print("Debug mode enabled.")

	if (debug_mode):
		print(ARGS)

	options = Options()
	options.add_argument("--headless=new")
	options.add_argument("--no-sandbox")
	options.add_argument("--disable-dev-shm-usage")
	options.add_argument("--disable-gpu")
	options.add_argument("--ignore-certificate-errors")

	driver = Chrome(options=options)

	try:
		####
		## Load the webpage
		####

		try:
			driver.get(ARGS["webpage"])
		except Exception:
			print("Failed to load the webpage. Please check the URL and ensure that your internet connection is working.")
			sys.exit()



		####
		## Get cookies and apply them
		####

		try:
			cookies = getattr(browser_cookie3, ARGS["browser"])(domain_name=DOMAIN)
			cookies = [cookie_to_dict(cookie) for cookie in cookies]

			if (cookies):
				addedCookies = add_cookies(driver, cookies)
				print(f"Successfully added {addedCookies} cookies of {len(cookies)} found for \"{DOMAIN}\"")
			else:
				print(f"No cookies found for \"{DOMAIN}\"")
		except browser_cookie3.BrowserCookieError:
			print(f"\"{ARGS['browser'].capitalize()}\" browser not found. No cookies were loaded.")



		####
		## Make first Fetch
		####

		if (ARGS["input"]):
			if (not os.path.exists(ARGS["input"])):
				print(f"File \"{ARGS['input']}\" not found.")
				sys.exit()
			else:
				with open(ARGS["input"], "r") as f:
					first_fetch = f.read()
				print(f"First fetch loaded from \"{ARGS['input']}\".")
		else:
			driver.refresh()
			print_sleep("Waiting before the first fetch. {} seconds remaining...", ARGS["frequency"])

			try:
				first_fetch = fetch_driver(driver, ARGS["selector"], ARGS["attribute"])
			except SelectorSyntaxError as e:
				print(f"\n{e.__class__.__name__}: {e}")
				sys.exit()

			if (ARGS["quiet"]):
				print("First fetch done. Waiting for changes...")
			else:
				print("\n#### First fetch: ####")
				print_text(first_fetch, line_numbers=True)
				print()

		if (ARGS["output"] and ARGS["input"] != ARGS["output"]):
			with open(ARGS["output"], "w") as f:
				f.write(first_fetch)
			print(f"Saved fetch to \"{ARGS['output']}\"")



		####
		## Start watching
		####

		if (not ARGS["quiet"]):
			print("Starting to watch. You can safely quit at any time by pressing \"Ctrl+C\".\n")

		fetches = 0

		while True:
			driver.refresh()
			print_sleep(f"No changes detected ({fetches} fetches). Waiting {{}} seconds before the next fetch...", ARGS["frequency"])
			print("\rFetching...", end="")

			current_fetch = fetch_driver(driver, ARGS["selector"], ARGS["attribute"])

			fetches += 1

			if (first_fetch != current_fetch):
				diff = "\n".join(difflib.unified_diff(first_fetch.splitlines(), current_fetch.splitlines(), lineterm=""))

				if (ARGS["chime"]):
					chime.info()

				print("\r", end="")
				if (ARGS["quiet"]):
					print(f"Changes detected after {fetches} fetches!")
				else:
					print(f"#### Changes detected after {fetches} fetches! Diff: ####")
					print_text(diff)
					print()

				if (ARGS["output"]):
					if (not ARGS["quiet"]):
						print(f"Saving fetch to \"{ARGS['output']}\"...")
					with open(ARGS["output"], "w") as f:
						f.write(current_fetch)

				if (ARGS["email"]):
					print(f"Sending email to {ARGS['email']}...")
					send_email(ARGS["email"], ARGS["email"], ARGS["password"], subject=f"Changes detected on {ARGS['webpage']}", body=diff)

				if (ARGS["loop"]):
					first_fetch = current_fetch
					fetches = 0
				else:
					break

	except () if debug_mode else BaseException as e:
		if (e.__class__ in (KeyboardInterrupt, SystemExit)):
			print(f"Stopped watching.")
		else:
			print(f"\"{e.__class__.__name__}\" Exception")

	finally:
		print(f"Closing drivers...")
		driver.quit()