from cx_Freeze import setup, Executable
# setup.py build
# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable(script='PunchClockTimer.py', 
    base=base, 
    targetName="PunchClockTimer.exe",
    icon="digitalclock2.ico")
]
include_files = []

setup(name='PCT',
      version = '0.0.1.0',
      description = 'Punch Clock Timer',
      options = dict(build_exe = buildOptions),
      executables = executables)

  
