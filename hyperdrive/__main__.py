#!/usr/bin/env python
"""The main entry point. Invoke as `hyperdrive' or `python -m hyperdrive'.
"""
import sys
import argparse
import hyperdrive


def main():
    parser = argparse.ArgumentParser(
        description=hyperdrive.__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s {}'.format(hyperdrive.__version__))
    parser.add_argument(
        '-v', '--verbose', action='count', default=0, help='increase verbosity')
    args, _ = parser.parse_known_args()


if __name__ == '__main__':
    sys.exit(main())
