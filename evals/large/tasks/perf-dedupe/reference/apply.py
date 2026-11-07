#!/usr/bin/env python3
"""Copy the reference solution into a workspace: python3 reference/apply.py <workspace>"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ws = sys.argv[1]
    src = os.path.join(HERE, "files")
    for root, _dirs, files in os.walk(src):
        for name in files:
            rel = os.path.relpath(os.path.join(root, name), src)
            dst = os.path.join(ws, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join(root, name), dst)


if __name__ == "__main__":
    main()
