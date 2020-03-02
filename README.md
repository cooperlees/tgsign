# tgsign

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Actions Status](https://github.com/cooperlees/tgsign/workflows/tgsign_ci/badge.svg)](https://github.com/cooperlees/tgsign/actions)

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

## Sample .tgsign.conf

```ini
[tgsign]
api_id = foo
api_token = bar
public_key_file = /home/cooper/.ssh/id_25519.pub
username = cooper
```
