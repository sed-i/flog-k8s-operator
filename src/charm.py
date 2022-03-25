#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charmed flog."""

import logging

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus, ModelError
from ops.pebble import ChangeError, Layer

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
        try:
            self._update_layer()
        except (ModelError, TypeError, ChangeError) as e:
            self.unit.status = BlockedStatus("Layer update failed: {}".format(str(e)))
        else:
            self.unit.status = ActiveStatus()

    def _flog_layer(self) -> Layer:
        """Returns Pebble configuration layer for flog."""

        def command():
            return "/bin/flog --format rfc5424 --loop --delay 1s --type log --output /bin/fake.log"

        return Layer(
            {
                "summary": "flog layer",
                "description": "pebble config layer for flog",
                "services": {
                    "flog": {
                        "override": "replace",
                        "summary": "flog service",
                        "command": command(),
                        "startup": "enabled",
                    }
                },
            }
        )

    def _update_layer(self):
        container = self.unit.get_container("workload")  # container name from metadata.yaml
        plan = container.get_plan()
        overlay = self._flog_layer()

        if overlay.services != plan.services:
            container.add_layer("flog layer", overlay, combine=True)
            container.replan()


if __name__ == "__main__":
    main(FlogCharm)
