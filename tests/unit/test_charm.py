# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

import unittest

from ops.model import ActiveStatus
from ops.testing import Harness

from charm import FlogCharm


class TestCharm(unittest.TestCase):
    def setUp(self):
        self.harness = Harness(FlogCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin_with_initial_hooks()
        self.harness.container_pebble_ready("workload")

    def test_charm_goes_into_active_status(self):
        # Ensure we set an ActiveStatus with no message
        self.assertEqual(self.harness.model.unit.status, ActiveStatus())
