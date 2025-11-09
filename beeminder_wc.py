import glob
import os
import re
from datetime import datetime

import requests
import yaml


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
    for file_path in glob.glob(full_path):
        print(f"Processing file: {file_path}")
        with open(file_path, "r") as file:
            word_count += count_words_in_markdown(file.read())
    print(f"Word count for {my_glob}: {word_count}")
    return word_count


def post_to_beeminder(
    username: str,
    auth_token: str,
    goal: str,
    difference: int,
    comment: str = "Updated from beeminder-wc script",
):
    # Send the difference to the Beeminder API
    url = f"https://www.beeminder.com/api/v1/users/{username}/goals/{goal}/datapoints.json"
    data = {"auth_token": auth_token, "value": difference, "comment": comment}
    requests.post(url, data=data)


def main(config_path: str):
    config = yaml.safe_load(open(config_path))
    BASE_DIR = config["base_dir"]
    USERNAME = config["beeminder"]["username"]
    AUTH_TOKEN = config["beeminder"]["auth_token"]
    GOALS = config["beeminder"]["goals"]

    goal_curval = 0
    difference = 0

    print(f"Starting beeminder-wc at {datetime.now()}")
    for goal in GOALS:
        goal_name = goal["name"]
        glob = goal["glob"]
        print(f"Processing {glob} for {goal_name}")
        goal_curval = get_curval_from_beeminder(USERNAME, AUTH_TOKEN, goal_name)
        print(f"Current word count value from Beeminder: {goal_curval}")
        difference = get_wordcount_from_files(BASE_DIR, glob) - goal_curval
        if difference > 0:
            print(f"Posting {difference} words to {goal_name}")
            post_to_beeminder(USERNAME, AUTH_TOKEN, goal_name, difference)
        else:
            print(f"No new words to post for {goal_name}")
