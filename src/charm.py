#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.


"""Charmed flog."""

import logging

from charms.loki_k8s.v0.loki_push_api import LogProxyConsumer
from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus

from manifest_builder import flog_manifest
from ops_extension import apply_manifest

logger = logging.getLogger(__name__)


class FlogCharm(CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        super().__init__(*args)

        # Relation managers
        # NOTE: these are expected to be fully initialized here, i.e. in this approach, relation
        # managers do not observe any events - they are fully initialized after their constructor
        # is done.
        self._log_proxy = LogProxyConsumer(
            charm=self, log_files=["/bin/fake.log"], container_name="workload"
        )
        # TODO refactor LogProxyConsumer so it has a `.manifest()` getter we could apply it using
        #  the workload instance.

        manifest = flog_manifest(self.config)

        # Flog's manifest may change only due to config-changed.
        # However, if pebble-ready is emitted after config-changed, then we won't be able to apply
        # the manifest just yet.
        # Also need to apply the manifest on log-proxy events (push promtail, update promtail
        # config).
        # Might as well call `apply_manifest` every time.
        # Note: Not wrapping in try-except because failing to push/add_layer after we already
        # did the due-diligence of `can_connect` should indeed put the charm in error state
        # and let juju/admin retry/resolve. I.e. no need to catch and manually put in blocked
        # status.
        # TODO: rename container to "flog"
        container = self.unit.get_container("workload")
        apply_manifest(manifest, container, with_silent_can_connect_guard=True)

        # Note: if LogProxyConsumer is refactored to have a "manifest" method, we may no longer
        # need this `observe`.
        self.framework.observe(
            self._log_proxy.on.promtail_digest_error,
            self._promtail_error,
        )

        self.unit.status = ActiveStatus()

    def _promtail_error(self, event):
        logger.error(event.message)
        self.unit.status = BlockedStatus(event.message)


if __name__ == "__main__":
    main(FlogCharm)
