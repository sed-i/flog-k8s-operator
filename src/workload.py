# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Workload manager."""

from typing import Dict, Optional, Tuple
from ops import pebble


# A manifest is a 2-tuple of (files, layer), where "files" is a mapping from path to contents.
# If contents is None, it means deletion.
# TODO: contents could also be bytes
Manifest = Tuple[Optional[Dict[str, Optional[str]]], Optional[pebble.Layer]]


class ManifestUpdateError(Exception):
    """Raised for layer update errors."""


class Workload:
    """Partial amalgamation of ops.Container and pebble."""
    def __init__(self, container_name: str):
        self._name = container_name
        self._socket_path = f"/charm/containers/{self._name}/pebble.socket"
        self.pebble = pebble.Client(socket_path=self._socket_path)

    def can_connect(self) -> bool:
        try:
            self.pebble.get_system_info()
        except:  # Yeah, bare except; the full list is in ops.model.Container.can_connect
            return False
        return True

    def apply_manifest(
        self,
        manifest: Manifest,
        with_silent_can_connect_guard: bool = True
    ):
        if with_silent_can_connect_guard and not self.can_connect():
            return

        files, new_layer = manifest
        try:
            for path, contents in files.items():
                # TODO what to do if path is already an existing dir?
                if contents is None:
                    self.pebble.remove_path(path, recursive=True)
                else:
                    self.pebble.push(path, contents, make_dirs=True)
        except Exception as e:
            raise ManifestUpdateError("Files update failed: {}".format(str(e)))

        if new_layer:
            try:
                workload = Workload("workload")
                plan = workload.pebble.get_plan()
                if new_layer.services != plan.services:
                    workload.pebble.add_layer("The one true layer", new_layer, combine=True)
                    workload.pebble.replan_services()
            except Exception as e:
                raise ManifestUpdateError("Layer update failed: {}".format(str(e)))
