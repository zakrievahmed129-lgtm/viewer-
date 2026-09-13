import sys, os, subprocess, time

script = os.path.abspath(r"scratch\test_setdisplayconfig.py")
python_exe = sys.executable
output_file = os.path.abspath(r"scratch\elevated_output.txt")

# Run test_setdisplayconfig.py elevated and redirect output to output_file
ps_cmd = f"Start-Process '{python_exe}' -ArgumentList '\"{script}\"' -RedirectStandardOutput '\"{output_file}\"' -RedirectStandardError '\"{output_file}.err\"' -Verb RunAs -Wait"

print("Running elevated test via PowerShell...")
subprocess.run(["powershell", "-Command", ps_cmd])

if os.path.exists(output_file):
    with open(output_file, "r") as f:
        print("=== STDOUT ===")
        print(f.read())
if os.path.exists(output_file + ".err"):
    with open(output_file + ".err", "r") as f:
        print("=== STDERR ===")
        print(f.read())
