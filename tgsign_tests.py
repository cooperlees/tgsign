#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from configparser import ConfigParser
from os import environ, getpid
from pathlib import Path
from tempfile import gettempdir
from typing import Dict, List
from unittest.mock import patch

import tgsign


# Commnet to see logging
# tgsign.LOG = Mock()
UNITTEST_TGSIGN_CONF = """\
[tgsign]
api_id = unittest
api_secret = unittest_secret
public_key_file = ~/.ssh/unittest_id_ed2519.pub
username = unittest_username

"""


class FakeHttpx:
    ERROR_JSON = [{"code": 69, "error": "It went real real bad"}]
    GOOD_JSON = [{"public_cert": "SSH cert of auth win"}]

    def __init__(self, url: str, data: Dict) -> None:
        self.data = data
        self.url = url

    def json(self, *args, **kwargs) -> List[Dict]:
        if "fail" in self.data["username"]:
            return self.ERROR_JSON
        return self.GOOD_JSON


class TgSignTests(unittest.TestCase):
    def _make_fake_home(self) -> Path:
        environ["HOME"] = gettempdir()
        ssh_dir = Path(gettempdir()) / ".ssh"
        ssh_dir.mkdir(exist_ok=True)
        return ssh_dir

    def test_config_read(self) -> None:
        fake_config_path = Path(gettempdir()) / f"tgsign.{getpid()}.conf"
        self.assertIsNone(tgsign._config_read(fake_config_path))

        with fake_config_path.open("w") as fcfp:
            fcfp.write(UNITTEST_TGSIGN_CONF)

        cp = tgsign._config_read(fake_config_path)
        self.assertTrue(isinstance(cp, ConfigParser))
        self.assertTrue("public_key_file" in cp["tgsign"])

    def test_get_signed_cert(self) -> None:
        with patch("tgsign.httpx.post", FakeHttpx):
            self.assertEqual(
                "SSH cert of auth win",
                tgsign.get_signed_cert("api_id", "api_secret", "PublicKey", "username"),
            )

        with patch("tgsign.httpx.post", FakeHttpx):
            self.assertEqual(
                "", tgsign.get_signed_cert("api_id", "api_secret", "PublicKey", "fail"),
            )

    def test_handle_debug(self) -> None:
        self.assertTrue(tgsign._handle_debug(True))

    def test_init_config(self) -> None:
        user_input = (
            "unittest",
            "unittest_secret",
            "~/.ssh/unittest_id_ed2519.pub",
            "unittest_username",
        )
        with patch("builtins.input", side_effect=user_input):
            fake_config_path = Path(gettempdir()) / f"tgsign.{getpid()}.conf"
            try:
                self.assertEqual(0, tgsign.init_config(fake_config_path))
                with fake_config_path.open("r") as fcfp:
                    ini_conf = fcfp.read()
                    self.assertEqual(UNITTEST_TGSIGN_CONF, ini_conf)
            finally:
                if fake_config_path.exists():
                    fake_config_path.unlink()

    def test_load_public_key(self) -> None:
        fake_key_path = Path(gettempdir()) / f"public_key.{getpid()}.pub"
        fake_key = "l33tKey69"

        # No key exists
        self.assertEqual("", tgsign._load_public_key(fake_key_path))
        try:
            with fake_key_path.open("w") as fkfp:
                fkfp.write(fake_key)
            self.assertEqual(fake_key, tgsign._load_public_key(fake_key_path))
        finally:
            if fake_key_path.exists():
                fake_key_path.unlink()

    def test_main(self) -> None:
        ssh_dir = self._make_fake_home()
        conf_file = ssh_dir.parent / f"{tgsign.CONF_FILE_NAME}"
        with conf_file.open("w") as cffp:
            cffp.write(UNITTEST_TGSIGN_CONF)

        with patch("tgsign._load_public_key") as mocked_pub_key:
            mocked_pub_key.return_value = True
            with patch("tgsign.get_signed_cert") as mocked_signed_cert:
                mocked_signed_cert.return_value = True
                with patch("tgsign.write_public_cert") as mocked_write_cert:
                    mocked_write_cert.return_value = 0
                    self.assertEqual(0, tgsign.main())

    def test_write_public_cert(self) -> None:
        cp = ConfigParser()
        cp.read_string(UNITTEST_TGSIGN_CONF)
        fake_public_key = "Unittest Public Key"

        self._make_fake_home()
        public_key_path = Path(cp["tgsign"]["public_key_file"]).expanduser()
        expected_public_cert = public_key_path.parent / "unittest_id_ed2519-cert.pub"
        try:
            self.assertEqual(0, tgsign.write_public_cert(cp, fake_public_key))

            self.assertTrue(expected_public_cert.exists())
            expected_st_mode = 33206 if tgsign.WINDOWS else 33152
            self.assertEqual(expected_st_mode, expected_public_cert.stat().st_mode)

            with expected_public_cert.open("r") as epcfp:
                loaded_key = epcfp.read()
            self.assertEqual(fake_public_key, loaded_key.strip())
        finally:
            if expected_public_cert.exists():
                expected_public_cert.unlink()


if __name__ == "__main__":
    unittest.main()
