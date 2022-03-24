#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charmed flog."""

import logging

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus

logger = logging.getLogger(__name__)


class FlogCharm(CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.workload_pebble_ready, self._on_workload_pebble_ready)

    def _on_workload_pebble_ready(self, event):
        """Define and start a workload using the Pebble API.

        Learn more about Pebble layers at https://github.com/canonical/pebble
        """
        self.unit.status = ActiveStatus()


if __name__ == "__main__":
    main(FlogCharm)
