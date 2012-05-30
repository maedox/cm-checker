#!/usr/bin/env python
"""Notify about new releases on the CyanogenMod download site.

v3.0 by maedox, April 2012."""


try:
	from BeautifulSoup import BeautifulSoup

except ImportError:
	print("Failed to import BeautifulSoup.")
	print("Installation instructions: http://www.crummy.com/software/BeautifulSoup")
	exit(1)

import ConfigParser, getpass, logging, logging.handlers, os, re, smtplib, socket
from urllib2 import urlopen


### Configuration ###
config_file = os.path.join(os.path.expanduser("~"), ".cm_checker.conf")
config = ConfigParser.RawConfigParser()

if not os.path.isfile(config_file):
	config.add_section("CMC")

	config.set("CMC", "download_url", "http://get.cm")
	config.set("CMC", "changelog_url", "http://cm9log.appspot.com/?device=")
	config.set("CMC", "google_apps_url", "http://goo.im/gapps")
	config.set("CMC", "exclude_pattern", "rommanager|cm-7")
	config.set("CMC", "log_dir", os.path.join(os.path.expanduser("~"), "var", "log"))
	config.set("CMC", "log_level", "INFO")

	notify_via_email = raw_input("Send email notifications? (Y/n): ")
	if re.match("[yY].*", notify_via_email) or not notify_via_email:
		config.set("CMC", "notify_via_email", True)

		send_with_gmail = raw_input("Send email via your Gmail account? (Y/n) (If no, will use local SMTP): ")
		if re.match("[yY].*", send_with_gmail) or not send_with_gmail:
			config.set("CMC", "send_with_gmail", True)

			gmail_username = raw_input("Gmail username: ")
			config.set("CMC", "gmail_username", gmail_username)

			gmail_password = getpass.getpass("Gmail password: ")
			config.set("CMC", "gmail_password", gmail_password)

		else:
			config.set("CMC", "send_with_gmail", False)
			config.set("CMC", "gmail_username", "")
			config.set("CMC", "gmail_password", "")

		email_to = raw_input("Recipient email for notifications?: ")
		if email_to:
			config.set("CMC", "email_to", email_to)

	else:
		config.set("CMC", "notify_via_email", False)
		config.set("CMC", "send_with_gmail", False)
		config.set("CMC", "gmail_username", "")
		config.set("CMC", "gmail_password", "")
		config.set("CMC", "email_to", "")

	config.set("CMC", "email_subject", "CyanogenMod")

	with open(config_file, "wb") as f:
		config.write(f)

	print("Configuration was written to {0}".format(config_file))


config.read(config_file)

download_url = config.get("CMC", "download_url")
changelog_url = config.get("CMC", "changelog_url")
google_apps_url = config.get("CMC", "google_apps_url")

exclude_pattern = config.get("CMC", "exclude_pattern")
if exclude_pattern is "": exclude_pattern = ".\A"

log_dir = config.get("CMC", "log_dir")
log_level = config.get("CMC", "log_level")

notify_via_email = config.getboolean("CMC", "notify_via_email")
send_with_gmail = config.getboolean("CMC", "send_with_gmail")

gmail_username = config.get("CMC", "gmail_username")
gmail_password = config.get("CMC", "gmail_password")

email_to = config.get("CMC", "email_to")
email_subject = config.get("CMC", "email_subject")
### /Configuration ###


### Logging setup ###
log = logging.getLogger(__name__)
log.setLevel(log_level)

log_handler = logging.handlers.RotatingFileHandler(
		filename=os.path.join(log_dir, "cm_checker.log"),
		maxBytes=1000000, backupCount=1, encoding="utf-8")
log_format = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
log_handler.setFormatter(log_format)

log.addHandler(log_handler)
### /Logging setup ###

def send_mail(email_body, device):
	if send_with_gmail:

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
		log.info("Email sent using Gmail")

	else:
		os.system("echo '{2}' | mail -s '{0} ({1})' {3}".format(
			email_subject, device, email_body, email_to))
		log.info("Email sent using local SMTP daemon")

	log.debug("Email message sent:\n{0}".format(msg))

def get_releases(devices):
	for device in devices:
		device_url = "{0}/?device={1}".format(download_url, device)
		email_list = []
		log_list = []

		release_log_file = os.path.join(log_dir, "cm_checker_{0}.log".format(device))

		# Create release_log_file if it doesn't exist
		if not os.path.isdir(log_dir):
			os.makedirs(log_dir)
			log.info("Created log directory: {0}".format(log_dir))
		if not os.path.isfile(release_log_file):
			open(release_log_file, "w").close()
			log.info("Created log file: {0}".format(release_log_file))

		with open(release_log_file, "r") as f:
			for line in f.readlines():
				log_list.append(line)
			log.debug("Read {0} previous release(s) from the log file into log_list".format(len(log_list)))

		# Find the actual releases and notify if applicable
		soup = BeautifulSoup(urlopen(device_url))
		releases = soup.fetch("a", {"href": re.compile("\.zip|\.torrent")})
		log.debug("Found {0} release(s) on the website".format(len(releases)))

		for release in releases:
			release = release["href"]

			if any(release in s for s in log_list) or re.search(exclude_pattern, release):
				continue

			else:
				if release[:4] == "http":
					email_list.append(release)
					log.debug("Added '{0}' to the email list".format(release))

				elif re.match("/get|/torrents", release):
					email_list.append(download_url + release)
					log.debug("Added '{0}' to the email list".format(download_url + release))

		# Log any new releases
		if email_list:
			with open(release_log_file, "a") as f:
				for e in email_list:
					f.write(e + "\n")
				log.info("Logged {0} new release(s) in log file: {1}".format(len(email_list), release_log_file))

			# Send email alert if enabled
			if notify_via_email:
				email_body = "\n".join(email_list)
				log.info("Attempting to send email notification to {0}".format(email_to))
				send_mail(email_body, device)


def main():
	import argparse

	parser = argparse.ArgumentParser(
			add_help = False,
			description = "Check for new releases of CyanogenMod for you device.")

	parser.add_argument("-d", dest="devices", metavar="device", nargs="+",
						help="Specify device name(s)", required=True)

	args = parser.parse_args()

	get_releases(args.devices)


if __name__ == "__main__":
	main()
