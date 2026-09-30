#!/usr/bin/env python3
"""Count red, green, and timed-out runs of a safe, repeatable check."""

import argparse
import json
import math
import os
import signal
import subprocess
import sys
import time


def stop_check(process: subprocess.Popen[bytes]) -> None:
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        elif process.poll() is None:
            process.kill()
    except ProcessLookupError:
        pass
    process.wait()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, required=True)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if args.runs < 1 or not math.isfinite(args.timeout) or args.timeout <= 0 or not command:
        parser.error("provide --runs >= 1, a finite --timeout > 0, and a command after --")

    results = {"green": 0, "red": 0, "timeout": 0}
    return_codes: dict[str, int] = {}
    started = time.monotonic()
    interrupted_by: int | None = None

    def request_stop(signum: int, _frame: object) -> None:
        nonlocal interrupted_by
        if interrupted_by is None:
            interrupted_by = signum

    previous_handlers = {
        signum: signal.signal(signum, request_stop)
        for signum in (signal.SIGINT, signal.SIGTERM)
    }
    try:
        for _ in range(args.runs):
            if interrupted_by is not None:
                print("sampling interrupted; check stopped", file=sys.stderr)
                return 128 + interrupted_by
            try:
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=os.name == "posix",
                )
            except OSError as exc:
                parser.exit(2, f"cannot start check: {exc.strerror}\n")

            deadline = time.monotonic() + args.timeout
            while True:
                if interrupted_by is not None:
                    stop_check(process)
                    print("sampling interrupted; check stopped", file=sys.stderr)
                    return 128 + interrupted_by
                code = process.poll()
                if code is not None:
                    results["green" if code == 0 else "red"] += 1
                    key = str(code)
                    return_codes[key] = return_codes.get(key, 0) + 1
                    break
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    stop_check(process)
                    results["timeout"] += 1
                    break
                try:
                    process.wait(timeout=min(remaining, 0.1))
                except subprocess.TimeoutExpired:
                    continue
        if interrupted_by is not None:
            print("sampling interrupted; check stopped", file=sys.stderr)
            return 128 + interrupted_by
    finally:
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)
    print(json.dumps({"runs": args.runs, **results, "return_codes": return_codes, "seconds": round(time.monotonic() - started, 3)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
