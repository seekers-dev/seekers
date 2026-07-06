import subprocess
import argparse
import time

def main():
    parser = argparse.ArgumentParser(description="Run python seekers AIs.")
    parser.add_argument("ai_files", type=str, nargs="*", help="Paths to the AIs.")
    args = parser.parse_args()
    server = subprocess.Popen(["python3", "seekers.py"],
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
        clients.append(subprocess.Popen(["python3", "client.py", script]))
        time.sleep(0.1)
    server.wait()


if __name__ == "__main__":
    main()
