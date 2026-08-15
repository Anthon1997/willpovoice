import traceback
try:
    import ui.modern_window
    print("MODERN OK")
except Exception:
    traceback.print_exc()
