#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Automatic Creation System
# Copyright (C) 2017 SiLeader. All rights reserved.
# License : Mozilla Public License 2.0 (see LICENSE)
#

import argparse
import settings
import compile

import subprocess
import os.path
import sys


def main():
    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers(title="build switch", description="Build, rebuild or clean", help="Build option")

    build_parser = sub.add_parser("build", help="Build source")
    rebuild_parser = sub.add_parser("rebuild", help="Rebuild source")
    clean_parser = sub.add_parser("clean", help="Clear objects")
    show_parser = sub.add_parser("show", help="Show settings")

    build_parser.add_argument("-r", "--release", help="Release build", action="store_true")
    build_parser.add_argument("-d", "--debug", help="Debug build", action="store_true")
    build_parser.add_argument("--setting", "--setting-file", help="Setting file")
    build_parser.add_argument("-R", "--recursive", help="Find file as recursive", action="store_true")
    build_parser.set_defaults(func=build)

    rebuild_parser.add_argument("-r", "--release", help="Release build", action="store_true")
    rebuild_parser.add_argument("-d", "--debug", help="Debug build", action="store_true")
    rebuild_parser.add_argument("--setting", "--setting-file", help="Setting file")
    rebuild_parser.add_argument("-R", "--recursive", help="Find file as recursive", action="store_true")
    rebuild_parser.set_defaults(func=rebuild)

    clean_parser.add_argument("--setting", "--setting-file", help="Setting file")
    clean_parser.set_defaults(func=clean)

    show_parser.add_argument("-r", "--release", help="Release build", action="store_true")
    show_parser.add_argument("-d", "--debug", help="Debug build", action="store_true")
    show_parser.add_argument("--setting", "--setting-file", help="Setting file")
    show_parser.set_defaults(func=show)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        print("Please set sub command")


def common(args, from_clean=False, from_show=False):
    ty = "release"
    rec = False
    if not from_clean:
        if args.debug:
            ty = "debug"
        if not from_show:
            rec = args.recursive
    else:
        ty = "clean"

    setting_file = "./setting.json"
    if args.setting:
        setting_file = args.setting

    working_dir = "."

    working_dir = os.path.abspath(working_dir)

    print("Build type   : {0}".format(ty))
    print("Setting file : {0}".format(setting_file))
    print("Working dir  : {0}".format(working_dir))
    print()

    stng = settings.Settings.load(setting_file)

    if stng is None:
        sys.stderr.write("Cannot find setting file\n")
        return None

    return {
        "recursive": rec,
        "working": working_dir,
        "build_type": ty,
        "settings": stng
    }


def build_impl(setting):
    if compile.compile_sequence(setting["settings"], setting["build_type"], setting["recursive"]):
        command = setting["settings"].run_command()
        if len(command) > 0:
            print("Running program...")
            subprocess.run(command, shell=True)


def build(args):
    setting = common(args)

    if setting is None:
        return

    build_impl(setting)


def clean(args):
    setting = common(args, from_clean=True)

    if setting is None:
        return

    compile.clean(setting["settings"])


def rebuild(args):
    setting = common(args)

    if setting is None:
        return

    compile.clean(setting["settings"])
    build_impl(setting)


def show(args):
    setting = common(args, from_show=True)

    if setting is None:
        return

    setting["settings"].show(setting["build_type"])


if __name__ == '__main__':
    print("Automatic Creation System")
    main()
