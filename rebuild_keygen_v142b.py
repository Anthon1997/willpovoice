import subprocess, sys, pathlib
priv = pathlib.Path("scripts/private.pem").resolve()
cmd = [sys.executable, "-m", "PyInstaller", "--onefile", "--noconsole",
       "--name", "WillpoVoiceKeygen", "--paths", ".",
       f"--add-data={priv};scripts",
       "--distpath", "dist", "--workpath", "build_kg",
       "--specpath", "build_kg", "scripts/keygen_gui.py"]
r = subprocess.run(cmd)
print("exit:", r.returncode)
p = pathlib.Path("dist/WillpoVoiceKeygen.exe")
print("keygen exe:", p.exists(), (p.stat().st_size // 1024), "KB")
