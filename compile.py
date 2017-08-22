#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Automatic Creation System
# Copyright (C) 2017 SiLeader. All rights reserved.
# License : Mozilla Public License 2.0 (see LICENSE)
#

import sys
import os
import subprocess
import multiprocessing
from concurrent import futures
import shutil

import settings


def compiler(setting, build_type, working_dir, file):
    res = ""
    try:
        cmd = setting.command_line(build_type, working_dir, file)

        res = subprocess.check_output(cmd["cmd"], shell=True)
        return {"status": True, "output": cmd["output"], "file": file}
    except:
        return {"status": False, "message": res}


def compile_(setting, build_type, d, r):
    """
    compile
    :param setting: setting object
    :param build_type: build type
    :param d: target directory
    :param r: run as recursive
    :return: compiled object file paths
    """
    processed = []

    time = 0.
    if os.path.exists(setting.output(d)):
        time = os.stat(setting.output(d)).st_mtime
    target = find_file(setting, build_type, d, r, time)

    with futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()+1) as pool:
        compiled = {pool.submit(compiler, setting, build_type, d, f): f for f in target}
        for future in futures.as_completed(compiled):
            res = future.result()
            if res["status"]:
                processed.append(res["output"])
                print("Compiled [{0}/{1}] {2}".format(len(processed), len(target), res["file"]))
            else:
                sys.stderr.write(res["message"])
                return None

    return processed


def find_file_impl(setting, ty, d, time, file):
    file = d + "/" + file
    if not os.path.isdir(file) and not os.path.islink(file) and setting.exists(ty, file):
        out = settings.Settings.temporary_object_file(file, d, ty)
        file_time = os.stat(file).st_mtime
        if file_time > time and (not os.path.exists(out) or os.stat(out).st_mtime < file_time):
            return {"status": True, "file": file}
    return {"status": False}


def find_all_files(directory):
    for root, dirs, files in os.walk(directory):
        yield root
        for file in files:
            yield os.path.join(root, file)


def find_file(setting, ty, d, r, time):
    """
    find to compile files
    :param setting: setting
    :param ty: build type
    :param d: target directory
    :param r: run as recursive
    :param time: Output file time
    :return: found file
    """
    found = []

    if r:
        target = find_all_files(d)
    else:
        target = os.listdir(d)

    with futures.ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() + 1) as pool:
        find = {pool.submit(find_file_impl, setting, ty, d, time, f): f for f in target}
        for future in futures.as_completed(find):
            res = future.result()
            if res["status"]:
                found.append(res["file"])

    return found
    

def get_temporary_object_files(setting, ty, d, r):
    found = []

    for file in os.listdir(d):
        file = d + "/" + file
        if r and os.path.isdir(file):
            p = get_temporary_object_files(setting, ty, d, r)
            if p is not None:
                found.extend(p)

        elif not os.path.islink(file):
            if setting.exists(ty, file):
                out = settings.Settings.temporary_object_file(file, d, ty)
                found.append(out)

    return found


def compile_sequence_impl(s, t, d, r):
    """
    compile and link
    :param s: setting object
    :param t: build type
    :param d: target directory
    :param r: run as recursive
    :return: is success
    """

    output_dir = d + "/build_output_dir/" + t
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    object_file = compile_(s, t, d, r)

    if object_file is None:
        sys.stderr.write("Error caused.\nStop.\n")
        return False

    if 0 < len(object_file) <= 1:
        print("{0} file is compiled.".format(len(object_file)))
    elif len(object_file) == 0:
        print("No file is updated")
        if os.path.exists(s.output(d)):
            print()
            return True
    else:
        print("{0} files are compiled.".format(len(object_file)))

    print()

    object_file = get_temporary_object_files(s, t, d, r)

    res = ""
    try:
        cmd = s.link_command(d, object_file)
        res = subprocess.check_output(cmd, shell=True)
        print("Linked output: {0}".format(s.output(d)))
        print()
        return True
    except:
        sys.stderr.write(res)
        return False


def clean_impl(setting, directory):
    path = directory + "/build_output_dir"
    if os.path.exists(path):
        shutil.rmtree(path)

    output = setting.output(directory)
    if os.path.exists(output):
        os.remove(output)


def clean(setting):
    for index in range(0, setting.working_directory_count()):
        clean_impl(setting, setting.working_directory(index))


def compile_sequence(setting, build_type, recursive):
    for index in range(0, setting.working_directory_count()):
        compile_sequence_impl(setting, build_type, setting.working_directory(index), recursive)


if __name__ == '__main__':
    sys.stderr.write("This file is not startup script.\n")
