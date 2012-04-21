#!/usr/bin/env python
"""Notify about new releases on the CyanogenMod download site.

v3.0 by maedox, April 2012."""


try:
	from BeautifulSoup import BeautifulSoup

except ImportError:
	print("Failed to import BeautifulSoup.")
	print("Installation instructions: http://www.crummy.com/software/BeautifulSoup")
	exit(1)

import ConfigParser, getpass, os, re, smtplib, socket
from urllib2 import urlopen


### Configuration ###
config_file = os.path.join(os.path.expanduser("~"), ".cm_checker.conf")
config = ConfigParser.RawConfigParser()

if not os.path.isfile(config_file):
	config.add_section("CMC")

	config.set("CMC", "download_url", "http://get.cm")
	config.set("CMC", "changelog_url", "http://cm-nightlies.appspot.com/?device=")
	config.set("CMC", "google_apps_url", "http://goo.im/gapps")
	config.set("CMC", "log_dir", os.path.join(os.path.expanduser("~"), "var", "log"))

	notify_via_email = raw_input("Send email notifications? (Y/n): ")
	if re.match("[yY].*", notify_via_email) or not notify_via_email:
		config.set("CMC", "notify_via_email", True)
	else:
		config.set("CMC", "notify_via_email", False)

	send_via_gmail = raw_input("Send email via your Gmail account? (Y/n): ")
	if re.match("[yY].*", send_via_gmail) or not send_via_gmail:
		config.set("CMC", "send_via_gmail", True)

		gmail_username = raw_input("Your Gmail username: ")
		config.set("CMC", "gmail_username", gmail_username)

		gmail_password = getpass.getpass("Your Gmail password: ")
		config.set("CMC", "gmail_password", gmail_password)

	else:
		config.set("CMC", "send_via_gmail", False)
		config.set("CMC", "gmail_username", "")
		config.set("CMC", "gmail_password", "")

	email_to = raw_input("Recipient email for notifications?: ")
	if email_to:
		config.set("CMC", "email_to", email_to)

	config.set("CMC", "email_subject", "CyanogenMod")

	with open(config_file, "wb") as f:
		config.write(f)

config.read(config_file)

download_url = config.get("CMC", "download_url")
changelog_url = config.get("CMC", "changelog_url")
google_apps_url = config.get("CMC", "google_apps_url")
log_dir = config.get("CMC", "log_dir")
notify_via_email = config.getboolean("CMC", "notify_via_email")
send_via_gmail = config.getboolean("CMC", "send_via_gmail")
gmail_username = config.get("CMC", "gmail_username")
gmail_password = config.get("CMC", "gmail_password")
email_to = config.get("CMC", "email_to")
email_subject = config.get("CMC", "email_subject")
### /Configuration ###

if not email_to:
	print("Please check the email settings. No recipient set.")
	exit(1)

def send_mail(email_body, device):
	if send_via_gmail:

		if not gmail_username or not gmail_password:
			print("Please check the email settings. Missing Gmail username or password.")
			exit(1)

		msg = """\
From: "{hostname}" <{from_email}>
To: {email_to}
Subject: {subj} ({device})

{body}

Changelog: {changelog_url}{device}
Google Apps: {gapps_url}
""".format(hostname = socket.gethostname(),
			from_email = gmail_username,
			email_to = email_to, subj = email_subject,
			device = device, body = email_body,
			changelog_url = changelog_url,
			gapps_url = google_apps_url)

		server = smtplib.SMTP("smtp.gmail.com:587")
		server.starttls()
		server.login(gmail_username, gmail_password)
		server.sendmail(gmail_username, email_to, msg)
		server.close()

	else:
		os.system("echo '{2}' | mail -s '{0} ({1})' {3}".format(
			email_subject, device, email_body, email_to))


def get_releases(devices):
	for device in devices:
		device_url = "{}/?device={}".format(download_url, device)
		email_list = []

		log_file = os.path.join(log_dir, "cm_checker_{}.log".format(device))

		# Create log_file if it doesn't exist
		if not os.path.isdir(log_dir):
			os.makedirs(log_dir)
		if not os.path.isfile(log_file):
			open(log_file, "w").close()

		with open(log_file, "r") as f:
			log_list = f.read()

		# Find the actual releases and notify if applicable
		soup = BeautifulSoup(urlopen(device_url))
		releases = soup.fetch("a", {"href": re.compile("\.zip")})

		for release in releases:
			release = release["href"]

			if release not in log_list:
				with open(log_file, "a") as f:
					f.write(release + "\n")

				if release[0:4] == "http":
					email_list.append(release)
				elif release[0:4] == "/get":
					email_list.append(download_url + release)

		if email_list and notify_via_email:
			email_body = "\n".join(email_list)
			send_mail(email_body, device)


def main():
	import argparse

	parser = argparse.ArgumentParser(
			add_help = False,
			description = "Check for new releases of CyanogenMod for you device.")

	parser.add_argument("-d", dest="devices", metavar="device", nargs="+",
						help="Specify device name(s)")

	args = parser.parse_args()

	if args.devices:
		get_releases(args.devices)

	else:
		parser.print_help()

		exit(1)


if __name__ == "__main__":
	main()
