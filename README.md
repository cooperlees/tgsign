# tgsign
Sign SSH Keys for Terragraph Access

## What is `tgsign`

Small Python tool that can resign SSH Key pair for Terragraph access.

## How to use `tgsign`

- Optional / Reccomended - Make a venv
  - `python3 -m venv /some/path`
- pip install tgsign
  - `/some/path/bin/pip install git+git://github.com/cooperlees/tgsign`
- Initalize tgsign (store API token + ID and point at your SSH Keys)
  - `/some/path/bin/tgsign --init`
- Then every ~30 days obtain a new certificate
  - `/some/path/bin/tgsign`

Now enjoy access to a Terragraph Development image.
