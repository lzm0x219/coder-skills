#!/usr/bin/env python3
"""Replay runtime evidence; state-machine decisions remain separately reviewed."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parent


def check(command, expected=0, markers=()):
    result = subprocess.run(['rtk', 'proxy', *command], capture_output=True, text=True)
    diagnostics = result.stdout + result.stderr
    if result.returncode != expected or not all(marker in diagnostics for marker in markers):
        raise RuntimeError(f'Unexpected result: {command}, exit={result.returncode}\n{diagnostics}')
    return result.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--state-root', type=Path, default=HERE / 'evidence/state-v2')
    parser.add_argument('--rules-root', type=Path, default=HERE / 'evidence/rules-v2')
    args = parser.parse_args()
    state, rules = args.state_root.resolve(), args.rules_root.resolve()
    check(['node', str(state / 'consumer.cjs')], markers=('consumer PASS',))
    check(['node', str(HERE / 'verify_state_transition.cjs'), str(state)], markers=('PASS refreshed user edit',))
    print('PASS final user contract, isolated state, validation and writer failure ordering')
    before = check(['node', str(state / 'current-check.cjs'), str(state / 'user-baseline/index.cjs')])
    after = check(['node', str(state / 'current-check.cjs')])
    if json.loads(before) != json.loads(after):
        raise RuntimeError('Refreshed independent baseline differs from final observations')
    if (state / 'consumer.cjs').read_bytes() != (state / 'user-baseline/consumer.cjs').read_bytes():
        raise RuntimeError('User consumer was modified during the refactor')
    historical = hashlib.sha256((state / 'baseline-check.cjs').read_bytes()).hexdigest()
    if historical != 'ce6380bd167ad2fa49d29e9bbd65a076c206702ec2983642445774ee6d3fb783':
        raise RuntimeError('Phase A historical check fingerprint changed')
    check(['node', str(state / 'baseline-check.cjs')], expected=1, markers=('AssertionError', 'User total:', 'Total:'))
    print('PASS independent baseline differential, retained user consumer and Phase A check fingerprint')
    for side in ('before', 'after'):
        entry = str(rules / side / 'index.cjs')
        check(['node', str(rules / 'wrong-check.cjs'), entry], expected=1, markers=('AssertionError', '5.25'))
        check(['node', str(rules / 'correct-check.cjs'), entry], markers=('contract PASS',))
    print('PASS original assertion failure retained; corrected contract checks pass both implementations')


if __name__ == '__main__':
    main()
