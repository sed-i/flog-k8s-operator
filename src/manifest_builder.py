# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Manifest builder."""

from ops import pebble
from workload import Manifest


def _flog_layer(config) -> pebble.Layer:
    """Returns Pebble configuration layer for flog."""

    def command():
        cmd = (
            "/bin/flog --loop --type log --output /bin/fake.log --overwrite "
            f"--format {config['format']} "
            f"--rate {config['rate']} "
        )

        if rotate := config.get("rotate"):
            cmd += f"--rotate {rotate} "

        return cmd

    return pebble.Layer(
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


def flog_manifest(config) -> Manifest:
    return {}, _flog_layer(config)
