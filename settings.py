#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Automatic Creation System
# Copyright (C) 2017 SiLeader. All rights reserved.
# License : Mozilla Public License 2.0 (see LICENSE)
#

import json
import os.path
import sys


class Settings:
    """ setting """

    def __init__(self):
        self._rules = {"debug": {}, "release": {}}
        self._target = []
        self._run = ""

    @staticmethod
    def load(setting_file):
        if not os.path.exists(setting_file):
            return None
        self = Settings()

        file = open(setting_file, "r")
        js = json.load(file)
        data = dict(js)

        if "rules" not in data:
            sys.stderr.write("rules is not in setting file.\n")
        else:
            rules = dict(data["rules"])
            if "debug" not in rules:
                sys.stderr.write("rules for debug is not in setting file.\n")
            else:
                Settings._setup_rules_impl(self, "debug", rules["debug"])

            if "release" not in rules:
                sys.stderr.write("rules for release is not in setting file\n")
            else:
                Settings._setup_rules_impl(self, "release", rules["release"])

        if "target" not in data:
            sys.stderr.write("target directory is not in setting file.\n")
        else:
            self._target = sorted(data["target"], key=lambda tt: int(-tt["priority"]))
            for t in self._target:
                t["directory"] = os.path.abspath(t["directory"])

        self._run = ""
        if "run" in data:
            run = data["run"]
            self._run = run
        return self

    @staticmethod
    def _setup_rules_impl(self, ty, rules):
        type_rules = self._rules[ty]
        for rule in rules:
            r = dict(rule)
            options = ""
            includes = []

            if "compiler" not in r:
                sys.stderr.write("compiler is not in rules\n")
                exit(-1)

            if "options" in r:
                options = r["options"]

            if "includes" in r:
                includes = r["includes"]

            type_rules[r["suffix"]] = {
                "compiler": r["compiler"],
                "options": options,
                "includes": includes
            }

    def command_line(self, ty, working_dir, file):
        _, ext = os.path.splitext(file)
        rule = self._rules[ty]
        rule = rule[ext]

        include_dirs = []
        for i in rule["includes"]:
            include_dirs.append("-I" + i)

        output = Settings.temporary_object_file(file, working_dir, ty)

        cmdline = [rule["compiler"], rule["options"], "-o", output, "-c", file]
        cmdline.extend(include_dirs)

        return {"cmd": " ".join(cmdline), "output": output}

    @staticmethod
    def temporary_object_file(source, working, build_type):
        file_name = source.translate(str.maketrans("\\/", "!!"))

        return working + "/build_output_dir/" + build_type + "/" + file_name + ".o"

    def exists(self, ty, file_name):
        _, ext = os.path.splitext(file_name)
        rule = self._rules[ty]
        return ext in rule

    def run_command(self):
        return self._run

    def link_command(self, working, file_list):
        files = []
        for f in file_list:
            files.append(f)

        t = self._get_link_object(working)
        if t is None:
            return None
        link = t["link"]

        if "manually" in link and link["manually"]:
            cmd = [link["linker"], link["options"].replace("$@", link["output"]).replace("$<", " ".join(files))]
            return " ".join(cmd)

        library_dir = []
        library = []
        if "library" in link:
            if "directory" in link["library"]:
                library_dir = "-L" + link["library"]["directory"]

            if "link" in link["library"]:
                library = "-l" + link["library"]["link"]

        cmd = [link["linker"], "-o", link["output"], link["options"]]
        cmd.extend(files)
        cmd.extend(library_dir)
        cmd.extend(library)

        return " ".join(cmd)

    def _get_link_object(self, working):
        for t in self._target:
            if "directory" in t and t["directory"] == working:
                return t
        return None

    def output(self, working):
        t = self._get_link_object(working)
        if t is None:
            return None
        return t["link"]["output"]

    def show(self, build_type):
        print("--- Setting ---")
        print("Build type   : {0}".format(build_type))

        for compiler in self._rules[build_type].values():
            print("Compiler rules")
            print("    Compiler : {0}".format(compiler["compiler"]))
            print("    Options  : {0}".format(compiler["options"]))
            if "includes" in compiler and len(compiler["includes"]) > 0:
                print("    Include directories:")
                for i in compiler["includes"]:
                    print("        {0}".format(i))

        link = self._rules["link"]
        print("Link rules")
        print("    Linker   : {0}".format(link["linker"]))
        print("    Output   : {0}".format(link["output"]))
        print("    Options  : {0}".format(link["options"]))
        if "library" in link:
            print("    Library:")
            if "directory" in link["library"]:
                print("        Directories:")
                for d in link["library"]["directory"]:
                    print("            {0}".format(d))
            if "link" in link["link"]:
                print("        Library:")
                for l in link["library"]["link"]:
                    print("            {0}".format(l))

    def working_directory(self, index):
        return self._target[index]["directory"]

    def working_directory_count(self):
        return len(self._target)


if __name__ == '__main__':
    sys.stderr.write("This file is not startup script.\n")
