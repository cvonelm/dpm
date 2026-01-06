import argparse
import logging
import subprocess
import sys

import dpm.pkg_definition
import dpm.store
from dpm.types import Needs, Provides


def parser_add_install(subparsers):
    parser = subparsers.add_parser("install")
    parser.add_argument("-r", "--required", action="append")
    parser.add_argument("-f", "--forbidden", action="append")
    parser.add_argument("--repo", default="")
    parser.add_argument("STORE")
    parser.add_argument("PKG")


def parser_add_uninstall(subparsers):
    parser = subparsers.add_parser("uninstall")
    parser.add_argument("STORE")
    parser.add_argument("PKG")
    parser.add_argument("--repo", default="")


def parser_add_reinstall(subparsers):
    parser = subparsers.add_parser("reinstall")
    parser.add_argument("-r", "--required", action="append")
    parser.add_argument("-f", "--forbidden", action="append")
    parser.add_argument("--repo", default="")
    parser.add_argument("STORE")
    parser.add_argument("PKG")


def parser_add_stored(subparsers):
    parser = subparsers.add_parser("stored")
    parser.add_argument("STORE")


def parser_add_shell(subparsers):
    parser = subparsers.add_parser("shell")
    parser.add_argument("STORE")
    parser.add_argument("PKG", nargs="*", action="append")


def main():
    parser = argparse.ArgumentParser(
        prog="DPM",
        description="The Package Manager of last Resort",
    )

    parser.add_argument("-v", "--verbose", action="store_true")

    subparsers = parser.add_subparsers(dest="subparser_name")
    parser_add_install(subparsers)
    parser_add_uninstall(subparsers)
    parser_add_reinstall(subparsers)
    parser_add_stored(subparsers)
    parser_add_shell(subparsers)

    args = parser.parse_args()

    if args.verbose:
        print("Setting verbose!")
        logging.basicConfig(level=logging.INFO)
    if args.subparser_name == "install":
        required_variants = args.required
        forbidden_variants = args.forbidden
        store = dpm.store.Store(args.STORE, args.repo)
        store.install(Needs(args.PKG, required_variants, forbidden_variants))
        sys.exit(0)

    if args.subparser_name == "uninstall":
        store = dpm.store.Store(args.STORE, args.repo)
        store.uninstall(Provides(args.PKG))
        sys.exit(1)

    if args.subparser_name == "reinstall":
        required_variants = args.required
        forbidden_variants = args.forbidden
        store = dpm.store.Store(args.STORE, args.repo)
        store.uninstall(Provides(args.PKG))
        store.install(Needs(args.PKG, required_variants, forbidden_variants))
        sys.exit(0)

    if args.subparser_name == "stored":
        store = dpm.store.Store(args.STORE)
        store.stored()
        sys.exit(0)

    if args.subparser_name == "shell":
        store = dpm.store.Store(args.STORE)
        env = dpm.pkg_definition.Environment(store)

        for pkg in args.PKG[0]:
            print(f"Registering {pkg}")
            env.register_package(Needs(pkg))
        print(env.to_dict())
        subprocess.run(["bash"], env=env.to_dict(), check=False)


if __name__ == "__main__":
    main()
