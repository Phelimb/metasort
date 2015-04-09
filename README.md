# Metasort

A Digital Health Hack Weekend Project using OneCodex API.

Filter reads based on taxonomy assignment from OneCodex.

Upload a Fast(a/q) file and download individual files sorted by species. 

## CLI

set your OneCodex API key

export ONE_CODEX_API_KEY=f8##################78

usage: cli.py [-h] f [outdir]

./cli.py seq.fa /path/to/outdir


## Web

Usage:

    pip install -r requirements
    python webapp.py

Live demo here:

[https://genome-sort.herokuapp.com/](https://genome-sort.herokuapp.com/)
