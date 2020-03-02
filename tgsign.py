#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import argparse
import logging
import sys
from configparser import ConfigParser
from pathlib import Path
from typing import Optional

import httpx


CONF_FILE_NAME = ".tgsign.conf"
LOG = logging.getLogger(__name__)
WINDOWS = sys.platform == "win32"


def _config_read(config_path: Path) -> Optional[ConfigParser]:
    if not config_path.exists():
        LOG.info(
            f"No config @ {config_path}. Please run with `{sys.argv[0]} --init` "
            f"or manully create {config_path}"
        )
        return None

    LOG.debug(f"Loading found config @ {config_path} ... Loading ...")
    cp = ConfigParser()
    cp.read(str(config_path))
    return cp


def _handle_debug(debug: bool) -> bool:
    """Turn on debugging if asked otherwise INFO default"""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)s: %(message)s (%(filename)s:%(lineno)d)",
        level=log_level,
    )
    return debug


def _load_public_key(public_key_path: Path) -> str:
    if not public_key_path.exists():
        LOG.error(f"Public Key file {public_key_path} does not exist ...")
        return ""

    with public_key_path.open("r") as pkfp:
        return pkfp.read().strip()


def get_signed_cert(
    api_id: str,
    api_secret: str,
    public_key: str,
    username: str = "",
    sign_url: str = "https://sw.terragraph.link/sign",
) -> str:
    post_data = {
        "api_id": api_id,
        "api_secret": api_secret,
        "public_key": public_key,
    }
    if username:
        post_data["username"] = username
    r = httpx.post(sign_url, data=post_data)
    resp_json = r.json()
    if "error" in resp_json[0]:
        LOG.error(
            f"Problem signing key for {api_id} / ({username}): {resp_json[0]['error']}"
        )
        return ""

    return resp_json[0]["public_cert"]


def init_config(config_path: Path) -> int:
    api_id = input("API ID: ")
    api_secret = input("API Secret: ")
    public_key_path = input("Public Key File path: ")
    username = input("Username (different to app_id? hit enter if not): ")

    LOG.info("Generating a .tgsign.conf")
    cp = ConfigParser()
    cp["tgsign"] = {}
    cp["tgsign"]["api_id"] = api_id
    cp["tgsign"]["api_secret"] = api_secret
    cp["tgsign"]["public_key_file"] = str(public_key_path)
    if username:
        cp["tgsign"]["username"] = username

    with config_path.open("w") as cfp:
        cp.write(cfp)

    LOG.info(f"Wrote config to {config_path}")
    return 0


def write_public_cert(config: ConfigParser, public_key: str) -> int:
    public_key_path = Path(config["tgsign"]["public_key_file"]).expanduser()
    public_cert_file_name = public_key_path.name.replace(".pub", "-cert.pub")
    public_cert_path = public_key_path.parent / public_cert_file_name
    temp_public_cert_path = public_key_path.parent / f".{public_cert_file_name}"

    with temp_public_cert_path.open("w") as tpcfp:
        tpcfp.write(f"{public_key}\n")

    temp_public_cert_path.rename(public_cert_path)
    public_cert_path.chmod(0o600)
    LOG.info(f"Successfully wrote out a new {public_cert_path} signed SSH Cert")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Verbose debug output"
    )
    parser.add_argument(
        "-i",
        "--init",
        action="store_true",
        help=f"Interactively populate ~/{CONF_FILE_NAME}",
    )
    parser.add_argument(
        "-u", "--url", default="https://sw.terragraph.link/sign", help="Sign API URL"
    )
    args = parser.parse_args()
    _handle_debug(args.debug)

    LOG.debug(f"Starting {sys.argv[0]}")

    # TODO: Make path more Windows standard / friendly
    config_file_path = Path(f"~/{CONF_FILE_NAME}").expanduser()
    LOG.debug(f"Using {config_file_path} config")

    if args.init:
        return init_config(config_file_path)

    config = _config_read(config_file_path)
    if not config or not config["tgsign"]:
        LOG.error(f"{config_file_path} has no tgsign section")
        return 1

    public_key = _load_public_key(
        Path(str(config["tgsign"]["public_key_file"])).expanduser()
    )
    if not public_key:
        LOG.error("No public key loaded. Exiting.")
        return 2

    public_cert = get_signed_cert(
        str(config["tgsign"]["api_id"]),
        str(config["tgsign"]["api_secret"]),
        public_key,
        str(config["tgsign"]["username"]) if "username" in config else "",
        args.url,
    )
    if not public_cert:
        return 3

    return write_public_cert(config, public_cert)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
