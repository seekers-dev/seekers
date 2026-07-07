from time import sleep

import subprocess
import argparse
import time

def main():
    parser = argparse.ArgumentParser(description="Run python seekers AIs.")
    parser.add_argument("--address", "-a", type=str, default=None,
                        help="Address of the server. (default: localhost:(unix-time in centiseconds mod 60000 + 2000)")
    parser.add_argument("ai_files", type=str, nargs="*", help="Paths to the AIs.")
    args = parser.parse_args()

    if args.address is None:
        args.address = f"localhost:{(int(time.time()*100)) % 60000 + 2000}"

    server = subprocess.Popen(["python3", "seekers.py", "--address", args.address],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              text=True,
                              bufsize=1)
    for l in server.stdout:
        if """[SeekersGame] INFO: Waiting for players to connect:""" in l:
            break

    clients = []
    print(args.ai_files)
    for script in args.ai_files:
        clients.append(subprocess.Popen(["python3", "client.py", script, "--address", args.address]))
        time.sleep(0.1)

    while server.poll() is None:
        try:
            time.sleep(0.2)
        except KeyboardInterrupt:
            server.kill()
            for client in clients:
                client.kill()


if __name__ == "__main__":
    main()
