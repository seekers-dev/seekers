#!/bin/bash

echo "Hello from the Seekers Community! cx_Freeze helper 24.3.6"

usage() {
  echo "Usage: $0 [-b] [-s]" 1>&2
}

build() {
  echo "Building projekt ..."
  pip install -r requirements.txt
  pip install cx_Freeze
  cxfreeze -c run_seekers.py --target-dir dist --include-files default_config.ini
}

start() {
  echo "Starting game ..."
  dist/run_seekers examples/ai-decide.py examples/ai-simple.py
}

[ $# -eq 0 ] && usage
while getopts ":bs" arg; do
    case $arg in
        b)
            build
            ;;
        s)
            start
            ;;
        *)
            usage
            ;;
    esac
done
