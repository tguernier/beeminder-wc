# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-file Python script (`beeminder_wc.py`) that counts words in markdown files matching glob patterns and posts incremental word count increases to [Beeminder](https://www.beeminder.com) goals via the Beeminder API. It only posts when the current word count exceeds the last value Beeminder has recorded.

## Running the script

```bash
# Run normally (requires config.yml)
uv run -m beeminder_wc

# Count words in a single file (no Beeminder posting)
uv run -m beeminder_wc --count-file path/to/file.md

# Log to syslog instead of stdout
uv run -m beeminder_wc --syslog

# Use a custom config file
uv run -m beeminder_wc --config /path/to/config.yml
```

## Configuration

Copy `config.example.yml` to `config.yml` and fill in credentials. Alternatively, set environment variables (`BEEMINDER_USERNAME`, `BEEMINDER_AUTH_TOKEN`, `BEEMINDER_GOALS` as JSON array, `BASE_DIR`). Environment variables take precedence over `config.yml`.

## Dependencies

Managed via `uv` (see `pyproject.toml`). Requires Python >=3.14. Dependencies: `pyyaml`, `requests`.

```bash
uv sync  # install dependencies
```

## Architecture

Everything lives in `beeminder_wc.py`. The flow is:

1. `load_config()` — reads from env vars or `config.yml`
2. For each goal: fetch current value from Beeminder API (`get_curval_from_beeminder`), count local files (`get_wordcount_from_files`), post difference if positive (`post_to_beeminder`)
3. Word counting (`count_words_in_markdown`) strips markdown syntax, HTML, and special characters before splitting on whitespace — intentionally aligned with the Obsidian Novel Word Count plugin behavior

The script is designed to be deployed as a cron job or GitHub Actions workflow. `beeminder-wc.yml` is a ready-made workflow file to copy into a markdown files repository.
