# beeminder-wc
This script is used to count the number of words in a set of markdown files and post the result to a [Beeminder](https://www.beeminder.com) goal. This script supports using the Python [glob](https://docs.python.org/3/library/glob.html) module to find files.

This script can be run using `uv`:
```bash
uv run main.py
```

Or it can be run on a schedule using `cron` on *NIX systems by adding to your crontab file:
```bash
# running once every 5 minutes
*/5 * * * * cd /path/to/beeminder-wc; /path/to/uv run main.py >> beeminder-wc.log 2>&1
```

The configuration for the script is sourced from the `config.yml` file. This contains the Beeminder API credentials and the globs used to find the files for processing. The `config.example.yml` file is a placeholder, copy it to `config.yml` and fill in your credentials and goal configuration.
