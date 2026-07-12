from subprocess import DEVNULL
from typing import Tuple

import os
import time
import subprocess
from pathlib import Path
import re
import tempfile
import configparser
import secrets
import argparse
import hashlib


class Tournament:
    def __init__(self, args):
        self.used_ports = set()
        self.next_port = 1200
        self.used_seeds = set()
        self.instances : dict[tuple[str,str,str], subprocess.Popen]= {}
        self.AIS_DIRECTORY = args.submissions
        self.ais = self.get_files(self.AIS_DIRECTORY)
        self.results = {
            ai:{
                ai2:[] for ai2 in self.ais if ai2 != ai
            } for ai in self.ais
        }
        self.config_directory = tempfile.TemporaryDirectory()
        self.N_SEEDS = args.seeds
        self.LOAD_FACTOR = args.load_factor


    @staticmethod
    def get_files(dir: str) -> list[str]:
        return [dir + "/" + p.name for p in Path(dir).iterdir() if p.is_file()]

    @staticmethod
    def write_log(content: str) -> Path:
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        path = log_dir / f"{digest}.log"

        path.write_text(content, encoding="utf-8")

        return path

    def process_result(self, config_location, ai1, ai2):
        process = self.instances[(config_location, ai1, ai2)]
        print(f"Processing {self.get_match_string(config_location,ai1,ai2)}")
        stdout, stderr = process.communicate()
        ma = re.findall(r'\|\s*(\d+)\s+P\.:\s+ai(\d)', stdout)
        if len(ma) < 2:
            stderr_log_path = self.write_log(stderr)
            stdout_log_path = self.write_log(stdout)
            print(f"Failed to process {self.get_match_string(config_location,ai1,ai2)}")
            print(f"Writing stdout log to {stdout_log_path} and stderr log to {stderr_log_path}")

            return
        ais = [ai1,ai2]
        small_results = {}
        for (score, index) in ma:
            me = ais[int(index)-1]
            small_results[me] = int(score)
        self.results[ai1][ai2].append((small_results[ai1],small_results[ai2]))
        self.results[ai2][ai1].append((small_results[ai2],small_results[ai1]))




    def get_and_inc_port(self) -> int:
        retval = self.next_port
        self.used_ports.add(self.next_port)
        self.next_port += 1
        if self.next_port > 64000:
            raise OverflowError("too many ports used")
        return retval

    @staticmethod
    def get_match_string(config_location: str, ai1: str, ai2: str) -> str:
        return f"match {ai1} vs {ai2} with config {config_location}"


    def start_once(self, config_location: str, ai1: str, ai2: str):
        port = self.get_and_inc_port()
        print(f"Starting {self.get_match_string(config_location,ai1,ai2)} on port {port}")
        env = os.environ.copy()
        env["PORT"] = f"{port}"
        env["CONFIG_LOCATION"] = config_location
        env["AI1_LOCATION"] = ai1
        env["AI2_LOCATION"] = ai2
        self.instances[(config_location, ai1, ai2)] = (subprocess.Popen([
        "docker", "compose",
        "-p", self.get_project_name(port),
        "up"
    ], env = env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        )
        )

    def collect_results(self):
        while len(self.instances):
            self.reap_finished()
            time.sleep(0.1)

    def run_tournament(self):
        self.start_all()
        self.collect_results()

    def start_all(self):
        [self.get_new_seed() for _ in range(self.N_SEEDS)]
        for seed in self.used_seeds:
            config = self.create_temp_config(seed)
            ticks = self.get_ticks(config)
            for ai1 in self.ais:
                for ai2 in self.ais:
                    while not self.should_spawn_another_match():
                        self.reap_finished()
                        time.sleep(0.1)
                    if ai1 != ai2:
                        self.start_once(
                            config,
                            ai1,
                            ai2
                        )


    def print_results(self):
        scores = [(ai, self.calculate_score(ai)) for ai in self.ais]

        scores.sort(
            key=lambda x: (x[1][0], x[1][1], -x[1][2]),
            reverse=True,
        )

        for ai, score in scores:
            print(f"{ai}: {score}")

    def calculate_score(self, ai: str) -> Tuple[int,int,int]:
        win = draw = loss = 0
        for subresults in self.results[ai].values():
            for my_score, other_score in subresults:
                if my_score > other_score:
                    win += 1
                if my_score == other_score:
                    draw += 1
                if my_score < other_score:
                    loss += 1
        return win,draw,loss

    def should_spawn_another_match(self):
        cpus = os.cpu_count()
        return len(self.instances)*self.LOAD_FACTOR < cpus

    def cleanup(self):
        for port in self.used_ports:
            subprocess.run([
                "docker", "compose",
                "-p", self.get_project_name(port),
                "down",
                "--remove-orphans",
            ],
            stdout=DEVNULL,
            stderr=DEVNULL)
        self.config_directory.cleanup()

    @staticmethod
    def get_project_name(port) -> str:
        return f"game_{port}"

    def create_temp_config(self, seed: int, original_path: str = "config.ini") -> str:
        config = configparser.ConfigParser()
        config.read(original_path)

        config["global"]["seed"] = str(seed)

        output_path = Path(f"{self.config_directory.name}/config_{seed}.ini")

        with output_path.open("w") as f:
            config.write(f)


        return str(output_path)

    @staticmethod
    def get_ticks(config_path: str) -> int:
        config = configparser.ConfigParser()
        config.read(config_path)
        return int(config["global"]["playtime"])

    def get_new_seed(self):
        seed = int.from_bytes(secrets.token_bytes(32), "little")
        self.used_seeds.add(seed)
        return seed

    def reap_finished(self):
        finished = []

        for key, proc in self.instances.items():
            if proc.poll() is not None:
                self.process_result(*key)
                finished.append(key)

        for key in finished:
            del self.instances[key]


def main():
    parser = argparse.ArgumentParser(description="Run python seekers AIs.")
    parser.add_argument("--submissions", type=str, default="submissions",
                        help="Path to submissions")
    parser.add_argument("--seeds", "-s", type=int, default=1,
                        help="Number of seeds to use")
    parser.add_argument("--load_factor",  type=float, default=2.5,
                        help="Number of cores to aim for for each game")
    args = parser.parse_args()
    t = Tournament(args)
    try:
        t.run_tournament()
        print(t.results)
        t.print_results()

    finally:
        t.cleanup()

if __name__ == "__main__":
    main()