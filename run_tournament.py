from __future__ import annotations

import argparse
import concurrent.futures
import logging
import sys
import traceback
from pathlib import Path

from seekers import *
from seekers.game import SeekersGame

from concurrent.futures import ProcessPoolExecutor


def run_game(ai1, ai2, config, args):
    print(ai1, ai2)

    try:
        seekers_game = SeekersGame(
            local_ai_locations=(ai1, ai2),
            config=config,
            debug=args.debug,
            scale=args.scale
        )
        res = seekers_game.start()
    except Exception as e:

        return f"{ai1}\t{ai2}\tError\n{traceback.format_exc()}\n"
    else:
        return f"{ai1}\t{ai2}\t{res}\t{seekers_game.ticks}\n"


def main():
    parser = argparse.ArgumentParser(description="Run python seekers AIs.")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode. This will enable debug drawing.")
    parser.add_argument("--scale", "-s", type=float, default=1.0,
                        help="Skaliert die Ausgabe, sodass auch auf Bildschirmen mit niedriger Auflösung das ganze Spielfeld eingesehen werden kann.")
    parser.add_argument("--config", "-c", type=str, default="config.ini",
                        help="Path to the config file. (default: config.ini)")
    parser.add_argument("ai_files", type=str, nargs="*", help="Paths to the AIs.")

    args = parser.parse_args()

    config = Config.from_filepath(args.config)

    logging.basicConfig(level=logging.DEBUG, style="{", format=f"[{{name}}] {{levelname}}: {{message}}",
                        stream=sys.stdout)

    lines = Path("results.txt").read_text().splitlines()

    with open("results.txt", "a") as f:
        f.write("---\n")
        f.flush()

        with ProcessPoolExecutor(4) as executor:
            futures = []

            for ai1 in args.ai_files:
                for ai2 in args.ai_files:
                    if ai1 == ai2:
                        continue

                    for line in lines:
                        if line.startswith(f"{ai1}\t{ai2}"):
                            print(f"{ai1}\t{ai2} ALREADY")
                            break
                    else:
                        futures.append(executor.submit(run_game, ai1, ai2, config, args))


            try:
                for res in concurrent.futures.as_completed(futures):
                    f.write(res.result())
                    f.flush()
            except:
                executor.shutdown(cancel_futures=True, wait=True)
                for future in futures:
                    future.cancel()
                sys.exit()
                exit()


if __name__ == "__main__":
    main()
