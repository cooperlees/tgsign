#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest

import tgsign


class TgSignTests(unittest.TestCase):
    def test_handle_debug(self) -> None:
        self.assertTrue(tgsign._handle_debug(True))


if __name__ == "__main__":
    unittest.main()
