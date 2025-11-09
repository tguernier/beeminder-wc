# This is a script to keep track of the word count in a set of text files
# determined by a file glob, and to send the cumulative increase of the
# word counts to a beeminder goal only if the word count is higher.
#
# This script is intended to be run as a cron task.
import beeminder_wc

if __name__ == "__main__":
    beeminder_wc.main(config_path="config.yml")
