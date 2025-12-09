# This is a script to keep track of the word count in a set of text files
# determined by a file glob, and to send the cumulative increase of the
# word counts to a beeminder goal only if the word count is higher.
#
# This script is intended to be run as a cron task:
# */5 * * * * cd /home/tom/code/beeminder-wc; /home/tom/.local/bin/uv run -m beeminder_wc >> beeminder-wc.log 2>&1
# Or with syslog logging:
# */5 * * * * cd /home/tom/code/beeminder-wc; /home/tom/.local/bin/uv run -m beeminder_wc --syslog

import argparse
import glob
import logging
import logging.handlers
import os
import re
from datetime import datetime

import requests
import yaml

# Set up logger
logger = logging.getLogger("beeminder_wc")
logger.setLevel(logging.INFO)


def get_curval_from_beeminder(username: str, auth_token: str, goal: str) -> int:
    # Get the value of the most recent datapoint from the Beeminder API
    url = f"https://www.beeminder.com/api/v1/users/{username}/goals/{goal}.json?auth_token={auth_token}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["curval"]
    return 0


def count_words_in_markdown(markdown: str) -> int:
    # taken from https://github.com/gandreadis/markdown-word-count/blob/master/mwc/counter.py
    text = markdown

    # Comments
    text = re.sub(r"<!--(.*?)-->", "", text, flags=re.MULTILINE)
    # Tabs to spaces
    text = text.replace("\t", "    ")
    # More than 1 space to 4 spaces
    text = re.sub(r"[ ]{2,}", "    ", text)
    # Footnotes
    text = re.sub(r"^\[[^]]*\][^(].*", "", text, flags=re.MULTILINE)
    # Indented blocks of code
    text = re.sub(r"^( {4,}[^-*]).*", "", text, flags=re.MULTILINE)
    # Custom header IDs
    text = re.sub(r"{#.*}", "", text)
    # Replace newlines with spaces for uniform handling
    text = text.replace("\n", " ")
    # Remove images
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    # Remove HTML tags
    text = re.sub(r"</?[^>]*>", "", text)
    # Remove special characters
    text = re.sub(r"[#*`~\-–^=<>+|/:]", "", text)
    # Remove footnote references
    text = re.sub(r"\[[0-9]*\]", "", text)
    # Remove enumerations
    text = re.sub(r"[0-9#]*\.", "", text)

    return len(text.split())


def get_wordcount_from_files(base_dir: str, my_glob: str) -> int:
    # Get the word count of all files matching the glob pattern
    word_count = 0
    full_path = os.path.join(base_dir, my_glob)
    for file_path in glob.glob(full_path, recursive=True):
        logger.debug(f"Processing file: {file_path}")
        with open(file_path, "r") as file:
            word_count += count_words_in_markdown(file.read())
    logger.info(f"Word count for {my_glob}: {word_count}")
    return word_count


def post_to_beeminder(
    username: str,
    auth_token: str,
    goal: str,
    difference: int,
    comment: str = "Updated from beeminder-wc script",
):
    try:
        # Send the difference to the Beeminder API
        url = f"https://www.beeminder.com/api/v1/users/{username}/goals/{goal}/datapoints.json"
        data = {"auth_token": auth_token, "value": difference, "comment": comment}
        requests.post(url, data=data)
    except Exception as e:
        logger.error(f"Failed to post to Beeminder: {e}")


def main(config_path: str):
    config = yaml.safe_load(open(config_path))
    BASE_DIR = config["base_dir"]
    USERNAME = config["beeminder"]["username"]
    AUTH_TOKEN = config["beeminder"]["auth_token"]
    GOALS = config["beeminder"]["goals"]

    goal_curval = 0
    difference = 0

    logger.info(f"Starting beeminder-wc at {datetime.now()}")
    for goal in GOALS:
        goal_name = goal["name"]
        glob = goal["glob"]
        logger.info(f"Processing {glob} for {goal_name}")
        goal_curval = get_curval_from_beeminder(USERNAME, AUTH_TOKEN, goal_name)
        logger.info(f"Current word count value from Beeminder: {goal_curval}")
        difference = get_wordcount_from_files(BASE_DIR, glob) - goal_curval
        if difference > 0:
            logger.info(f"Posting {difference} words to {goal_name}")
            post_to_beeminder(USERNAME, AUTH_TOKEN, goal_name, difference)
            print(f"Posted {difference} words to {goal_name}")
        else:
            logger.info(f"No new words to post for {goal_name}")


def setup_syslog_logging():
    """Set up syslog logging handler"""
    try:
        # Try different syslog addresses based on the platform
        syslog_addresses = ["/dev/log", "/var/run/syslog", ("localhost", 514)]
        syslog_handler = None

        for address in syslog_addresses:
            try:
                syslog_handler = logging.handlers.SysLogHandler(address=address)
                break
            except Exception:
                continue

        if syslog_handler is None:
            logger.error("Failed to connect to syslog")
            return

        formatter = logging.Formatter("%(name)s: %(levelname)s - %(message)s")
        syslog_handler.setFormatter(formatter)
        logger.addHandler(syslog_handler)
        logger.info("Syslog logging initialized")
    except Exception as e:
        logger.error(f"Failed to set up syslog logging: {e}")


def setup_stdout_logging():
    """Set up stdout logging handler"""
    # Only add stdout handler if no handlers exist
    if not logger.handlers:
        stdout_handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Beeminder word count tracker")
    parser.add_argument("--syslog", action="store_true", help="Enable syslog logging")
    parser.add_argument(
        "--config", default="config.yml", help="Path to configuration file"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.syslog:
        setup_syslog_logging()
    else:
        setup_stdout_logging()

    main(args.config)
