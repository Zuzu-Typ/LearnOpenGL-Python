import sys, os, subprocess

print("Some requirements were missing. Satisfying them now.")

install_command = "{} -m pip install -r {}".format(
    sys.executable,
    os.path.realpath("requirements.txt")
)

popen = subprocess.Popen(install_command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         universal_newlines=True,
                         shell=True)

for stdout_line in iter(popen.stdout.readline, ""):
    print(stdout_line, end="")

for stdout_line in iter(popen.stderr.readline, ""):
    print(stdout_line, end="", file=sys.stderr)
    
popen.stdout.close()

popen.wait()
