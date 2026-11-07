#!/usr/bin/env python3
"""Copy the reference report.py into <workspace> and generate answers.json there.

Usage: python3 reference/apply.py <workspace>
"""
import os
import shutil
import subprocess
import sys

ws = os.path.abspath(sys.argv[1])
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), "report.py"), os.path.join(ws, "report.py"))
subprocess.run([sys.executable, "report.py"], cwd=ws, check=True)
