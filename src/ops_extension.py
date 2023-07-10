# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Stuff that could potentially go into the ops lib."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Union

from ops.model import Container
from ops.pebble import Layer


@dataclass
class Manifest:
    """Manifest = files + pebble layer."""

    # A mapping from path to contents. Set contents to None to instruct a deletion.
    files: Dict[Union[str, Path], Optional[Union[str, bytes]]]

    # A pebble layer. If None, take no action (keep existing).
    layer: Optional[Layer]


class ManifestUpdateError(Exception):
    """Raised for layer update errors."""


def apply_manifest(
    manifest: Manifest, container: Container, with_silent_can_connect_guard: bool = False
):
    """Apply a manifest to a given container, blindly overwriting any pre-existing files/layer."""
    if with_silent_can_connect_guard and not container.can_connect():
        return

    try:
        for path, contents in manifest.files.items():
            # TODO what to do if path is already an existing dir?
            if contents is None:
                container.remove_path(path, recursive=True)
            else:
                container.push(path, contents, make_dirs=True)
    except Exception as e:
        raise ManifestUpdateError("Files update failed") from e

    if manifest.layer:
        try:
            container.add_layer("The one true layer", manifest.layer, combine=True)
            container.replan()
        except Exception as e:
            raise ManifestUpdateError("Layer update failed") from e
