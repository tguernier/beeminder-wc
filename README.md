# beeminder-wc
This script is used to count the number of words in a set of markdown files and post the result to a [Beeminder](https://www.beeminder.com) goal. This script supports using the Python [glob](https://docs.python.org/3/library/glob.html) module to find files.

This script can be run using `uv`:
```bash
uv run -m beeminder_wc
```

Or it can be run on a schedule using `cron` on *NIX systems by adding to your crontab file:
```bash
# running once every 5 minutes
*/5 * * * * cd /path/to/beeminder-wc; /path/to/uv run -m beeminder_wc >> beeminder-wc.log 2>&1
```

The script now logs to stdout by default and also supports logging to syslog with the `--syslog` flag:
```bash
# Log to stdout (default)
uv run -m beeminder_wc

# Log to syslog instead
uv run -m beeminder_wc --syslog
```

The configuration for the script is sourced from the `config.yml` file. This contains the Beeminder API credentials and the globs used to find the files for processing. The `config.example.yml` file is a placeholder, copy it to `config.yml` and fill in your credentials and goal configuration.

Command line options:
- `--syslog`: Enable logging to syslog
- `--config PATH`: Specify a custom configuration file path (default: config.yml)
- `--count-file FILE`: Just count the words in a single file and print the result to stdout (without posting to Beeminder)

## Environment variables

As an alternative to `config.yml`, you can configure the script using environment variables. This is useful for CI/CD environments like GitHub Actions. If the environment variables are set, they take precedence over `config.yml`.

- `BEEMINDER_USERNAME` - Your Beeminder username
- `BEEMINDER_AUTH_TOKEN` - Your Beeminder API auth token
- `BEEMINDER_GOALS` - JSON array of goals, e.g. `[{"name": "my_goal", "glob": "**/*.md"}]`
- `BASE_DIR` - Base directory for file globs (default: `.`)

## Deploying with GitHub Actions

You can also run beeminder-wc automatically on every push to a repository of markdown files using GitHub Actions. This is free for both public and private repositories as long as you stay within the free-tier minutes.

### Setup

1. Copy two files from this repo into your **markdown files repository**:
   - `beeminder_wc.py` → root of your markdown repo
   - `beeminder-wc.yml` → `.github/workflows/beeminder-wc.yml`

2. Edit the `BEEMINDER_GOALS` line in the workflow file with your goal names and glob patterns.

3. In your markdown repo on GitHub, go to **Settings > Secrets and variables > Actions** and add these repository secrets:
   - `BEEMINDER_USERNAME` - Your Beeminder username
   - `BEEMINDER_AUTH_TOKEN` - Your Beeminder API auth token

4. Push a commit to the `main` branch — the workflow will run automatically and post any word count increases to Beeminder.
