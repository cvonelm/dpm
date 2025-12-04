#!/usr/bin/env python3

import argparse
import logging
import subprocess
import sys

import dpm.pkg_definition
import dpm.store
from dpm.types import Needs, Provides

parser = argparse.ArgumentParser(
    prog="DPM",
    description="The Package Manager of last Resort",
)

parser.add_argument("-v", "--verbose", action="store_true")


subparsers = parser.add_subparsers(dest="subparser_name")
parser_install = subparsers.add_parser("install")

parser_install.add_argument("-r", "--required", action="append")
parser_install.add_argument("-f", "--forbidden", action="append")
parser_install.add_argument("--repo", default="")
parser_install.add_argument("STORE")
parser_install.add_argument("PKG")

parser_uninstall = subparsers.add_parser("uninstall")
parser_uninstall.add_argument("STORE")
parser_uninstall.add_argument("PKG")
parser_uninstall.add_argument("--repo", default="")

parser_reinstall = subparsers.add_parser("reinstall")
parser_reinstall.add_argument("-r", "--required", action="append")
parser_reinstall.add_argument("-f", "--forbidden", action="append")
parser_reinstall.add_argument("--repo", default="")
parser_reinstall.add_argument("STORE")
parser_reinstall.add_argument("PKG")


parser_stored = subparsers.add_parser("stored")

parser_stored.add_argument("STORE")

parser_shell = subparsers.add_parser("shell")

parser_shell.add_argument("STORE")
parser_shell.add_argument("PKG", nargs="*", action="append")
args = parser.parse_args()

logger = logging.getLogger("dpm")
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
