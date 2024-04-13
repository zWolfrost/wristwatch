#! venv/bin/python 

import time, os, sys, argparse, difflib, rookiepy
from urllib.parse import urlparse

from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.common.exceptions import InvalidArgumentException

from bs4 import BeautifulSoup
from bs4.formatter import HTMLFormatter

import smtplib, ssl
from email.message import EmailMessage


def get_args():
	parser = argparse.ArgumentParser(description="Wristwatch is a simple tool to watch for changes on a webpage and notify you via email.", prog="wristwatch")

	parser.add_argument("webpage", type=str, help="The URL of the webpage to scrape.", metavar="URL")

	parser.add_argument("-b", "--browser", type=str, help="Name of the browser to get cookies from (default: any).", default="load", choices=["brave", "chrome", "chromium", "edge", "firefox", "internet_explorer", "librewolf", "octo_browser", "opera", "opera_gx", "safari", "vivaldi"])
	parser.add_argument("-f", "--frequency", type=int, help="Frequency of fetches in seconds (default: 60).", default=60, metavar="SECONDS")
	parser.add_argument("-s", "--selector", type=str, help="CSS selector of element(s) to scrape. Can be used multiple times.", action="extend", nargs="+")

	parser.add_argument("-e", "--email", type=str, help="Email address to self-send the changes to.", required=("-p" in sys.argv or "--password" in sys.argv))
	parser.add_argument("-p", "--password", type=str, help="Email \"app\" password. Here's a guide on how to generate one: https://support.google.com/accounts/answer/185833", required=("-e" in sys.argv or "--email" in sys.argv))

	parser.add_argument("-q", "--quiet", help="Decrease output verbosity.", action="store_true")
	parser.add_argument("-l", "--loop", help="Keep watching for changes even after the first one.", action="store_true")

	parser.add_argument("-o", "--output", type=str, help="Save the last fetch to a file.", metavar="FILE")
	parser.add_argument("-i", "--input", type=str, help="Load the first fetch from a file.", metavar="FILE")

	parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.2")

	return vars(parser.parse_args())


def init_driver():
	options = Options()

	options.add_argument("--headless=new")
	options.add_argument("--no-sandbox")
	options.add_argument("--disable-dev-shm-usage")
	options.add_argument("--disable-gpu")
	options.add_argument("--start-maximized")
	options.add_argument("--ignore-certificate-errors")

	# options.add_argument("--disable-infobars")
	# options.add_argument("--disable-notifications")

	# options.add_experimental_option("excludeSwitches", ["enable-logging"])

	driver = Chrome(options=options)

	return driver

def add_cookies(driver: Chrome, cookies: list = None):
	if (cookies is None):
		return None
	else:
		errorCookies = 0

		for cookie in cookies:
			try:
				driver.add_cookie(cookie)
			except Exception:
				errorCookies += 1

		return len(cookies) - errorCookies

def fetch_driver(driver: Chrome, selectors: str = None):
	formatter = HTMLFormatter(indent=3)
	soup = BeautifulSoup(driver.page_source, "html.parser")

	if (selectors is None):
		return str(soup.prettify(formatter=formatter))
	else:
		fetch = ""

		for selector in selectors:
			for i, element in enumerate(soup.select(selector)):
				fetch += str(element.prettify(formatter=formatter))
				if (i < len(soup.select(selector)) - 1):
					fetch += "\n"

		return fetch


def print_text(text: str, line_numbers: bool = False, prefix: str = ""):
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
	try:
		ARGS = get_args()
		DOMAIN = urlparse(ARGS["webpage"]).netloc

		driver = init_driver()



		####
		## Open webpage
		####

		try:
			driver.get(ARGS["webpage"])
		except InvalidArgumentException:
			print("Webpage URL is invalid. Please retry.")
			sys.exit()



		####
		## Get cookies and apply them
		####

		try:
			cookies = getattr(rookiepy, ARGS["browser"])([DOMAIN])

			if (cookies):
				addedCookies = add_cookies(driver, cookies)
				print(f"Successfully added {addedCookies} cookies of {len(cookies)} found for \"{DOMAIN}\"")
			else:
				print(f"No cookies found for \"{DOMAIN}\"")
		except:
			print(f"\"{ARGS['browser']}\" browser not found.")



		####
		## Make first Fetch
		####

		driver.refresh()
		time.sleep(ARGS["frequency"])

		if (ARGS["input"]):
			if (not ARGS["quiet"]):
				print(f"Reading first fetch from \"{ARGS['input']}\"...")
			with open(ARGS["input"], "r") as f:
				first_fetch = f.read()
		else:
			first_fetch = fetch_driver(driver, ARGS["selector"])

		if (ARGS["quiet"]):
			print("First fetch done. Waiting for changes...")
		else:
			print("\n#### First fetch: ####")
			print_text(first_fetch, line_numbers=True)
			print("")

		if (ARGS["output"]):
			if (not ARGS["quiet"]):
				print(f"Saving fetch to \"{ARGS['output']}\"...")
			with open(ARGS["output"], "w") as f:
				f.write(first_fetch)



		####
		## Start watching
		####

		fetches = 0

		while True:
			driver.refresh()
			time.sleep(ARGS["frequency"])

			current_fetch = fetch_driver(driver, ARGS["selector"])

			fetches += 1

			if (first_fetch != current_fetch):
				diff = "\n".join(difflib.unified_diff(first_fetch.splitlines(), current_fetch.splitlines(), lineterm=""))

				if (ARGS["quiet"]):
					print("\nChanges detected!")
				else:
					print("\n\n#### Changes detected! Diff: ####")
					print_text(diff)
					print("")

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
				else:
					break
			else:
				print(f"\rNo changes detected ({fetches} fetches).", end="")
	except KeyboardInterrupt:
		print(f"\nStopped watching.")



	####
	## Close drivers
	####

	print(f"Closing drivers...")
	driver.quit()