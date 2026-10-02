#!/usr/bin/env python3
"""Build/check an isolated executor root; default self-checks current cases."""
import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(command, cwd):
    result = subprocess.run(['rtk', 'proxy', *command], cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout


def verify(root):
    print(run(['pnpm', 'dlx', '--package', 'typescript@5.6.3', 'tsc', '-p', 'tsconfig.json'], root / 'library').strip())
    print(run(['node', str(HERE / 'verify_cases.cjs'), str(root)], root).strip())
    print(run(['node', str(root / 'state-transitions/consumer.cjs')], root).strip())
    print(run(['node', str(HERE / 'verify_state_transition.cjs'), str(root / 'state-transitions')], root).strip())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', nargs='?', type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='coder-refactor-cases-') as directory:
        root = Path(directory) / 'cases'
        source = args.root.resolve() if args.root else HERE.parent / 'cases'
        shutil.copytree(source, root)
        verify(root)
        if not args.root:
            # Prove cancellation-before-delivery is observable by this harness.
            bus = root / 'async/index.cjs'
            original = bus.read_text()
            bus.write_text(original.replace('if (listeners.has(fn)) fn(value)', 'fn(value)'))
            result = subprocess.run(['rtk', 'proxy', 'node', str(HERE / 'verify_cases.cjs'), str(root)], capture_output=True, text=True)
            if result.returncode == 0 or 'AssertionError' not in result.stderr:
                raise RuntimeError('Cancellation mutation was not rejected as expected')
            print('PASS harness rejects cancellation regression (negative control)')


if __name__ == '__main__':
    main()
