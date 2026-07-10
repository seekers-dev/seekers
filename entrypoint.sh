#!/bin/sh
exec nix-shell -p netcat-gnu --run "$*"
