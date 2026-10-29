from pathlib import Path
spec = Path("WillpoVoice_final.spec")
bak = spec.with_name(spec.name + ".bak_console_true")
if bak.exists():
    bak.replace(spec)
    print("✅ Spec restaurado a console=False")
run = Path("run.py")
bak2 = run.with_name(run.name + ".bak_faulthandler_diag")
if bak2.exists():
    bak2.replace(run)
    print("✅ run.py restaurado (sin faulthandler)")
mw = Path("ui/modern_window.py")
bak3 = mw.with_name(mw.name + ".bak_worker_diag")
if bak3.exists():
    bak3.replace(mw)
    print("✅ modern_window.py restaurado (sin prints de diagnóstico)")
