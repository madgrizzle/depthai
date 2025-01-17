import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

initEnv = os.environ.copy()


def quoted(val):
    return '"' + str(val) + '"'

class App:
    def __init__(self, appName, appPath=None, appRequirements=None, appEntrypoint=None):
        self.appName = appName
        self.appPath = appPath or Path(__file__).parent.parent / "apps" / self.appName
        self.venvPath = self.appPath / "venv"
        self.appPip = str(self.venvPath / "bin" / "pip") if os.name != 'nt' else (self.venvPath / "Scripts" / "pip.exe")
        self.appInterpreter = str(self.venvPath / "bin" / "python") if os.name != 'nt' else (self.venvPath / "Scripts" / "python.exe")
        self.appRequirements = appRequirements or self.appPath / "requirements.txt"
        self.appEntrypoint = appEntrypoint or self.appPath / "main.py"

    def createVenv(self, force=False):
        try:
            subprocess.check_call(' '.join([quoted(sys.executable), '-m', 'venv', '-h']), env=initEnv, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            print(f"Error accessing \"venv\" module! Please try to install \"python3.{sys.version_info[1]}-venv\" or see oficial docs here - https://docs.python.org/3/library/venv.html", file=sys.stderr)
            sys.exit(1)
        try:
            subprocess.check_call(' '.join([quoted(sys.executable), '-m', 'pip', '-h']), env=initEnv, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            print("Error accessing \"pip\" module! Please try to install \"python3-pip\" or see oficial docs here - https://pip.pypa.io/en/stable/installation/", file=sys.stderr)
            sys.exit(1)

        if not force and Path(self.appInterpreter).exists() and Path(self.appPip).exists():
            print("Existing venv found.")
        else:
            if self.venvPath.exists():
                print("Recreating venv...")
                shutil.rmtree(self.venvPath)
            else:
                print("Creating venv...")
            try:
                subprocess.check_call(' '.join([quoted(sys.executable), '-m', 'venv', str(self.venvPath)]), shell=True, env=initEnv, cwd=self.appPath)
            except:
                print(f"Error creating a new virtual environment using \"venv\" module! Please try to install \"python3.{sys.version_info[1]}-venv\" again", file=sys.stderr)
                sys.exit(1)
        print("Installing requirements...")
        subprocess.check_call(' '.join([quoted(self.appInterpreter), '-m', 'pip', 'install', '-U', 'pip']), env=initEnv, shell=True, cwd=self.appPath)
        subprocess.check_call(' '.join([quoted(self.appInterpreter), '-m', 'pip', 'install', '--prefer-binary', '-r', str(self.appRequirements)]), env=initEnv, shell=True, cwd=self.appPath)

    def runApp(self, shouldRun = lambda: True):
        pro = subprocess.Popen(' '.join([quoted(self.appInterpreter), str(self.appEntrypoint)]), env=initEnv, shell=True, cwd=self.appPath, preexec_fn=os.setsid)
        while shouldRun():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
        os.killpg(os.getpgid(pro.pid), signal.SIGTERM)

