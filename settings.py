#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os.path
import sys


class Settings:
    """ setting """

    def __init__(self):
        self._rules = {"debug": {}, "release": {}, "link": {}}
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

            if "link" not in rules:
                sys.stderr.write("rules for link is not in setting file\n")
            else:
                link = rules["link"]
                self._rules["link"] = link

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

        include_dirs = ""
        for i in rule["includes"]:
            include_dirs += "-I" + i
            include_dirs += " "

        output = Settings.temporary_object_file(file, working_dir)
        cmdline = rule["compiler"] + " " + rule["options"] + " -o " + output + " -c " + file + " " + include_dirs

        return {"cmd": cmdline, "output": output}

    @staticmethod
    def temporary_object_file(source, working):
        file_name = source.translate(str.maketrans("\\/", "!!"))

        return working + "/build_output_dir/" + file_name + ".o"

    def exists(self, ty, file_name):
        _, ext = os.path.splitext(file_name)
        rule = self._rules[ty]
        return ext in rule

    def run_command(self):
        return self._run

    def link_command(self, working, file_list):
        
    
        files = ""
        for f in file_list:
            files += f
            files += " "
        link = self._rules["link"]

        library_dir = []
        library = []
        if "library" in link:
            if "directory" in link["library"]:
                library_dir = link["library"]["directory"]

            if "link" in link["library"]:
                library = link["library"]["link"]

        dirs = ""
        for d in library_dir:
            dirs += "-L" + working + "/" + d + " "

        libs = ""
        for l in library:
            libs += "-l" + l + " "

        return link["linker"]\
               + " -o " + working + "/" + link["output"] + " "\
               + link["options"] + " "\
               + dirs\
               + libs + " "\
               + files

    def output(self, working):
        return working + "/" + self._rules["link"]["output"]

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


if __name__ == '__main__':
    sys.stderr.write("This file is not startup script.\n")
