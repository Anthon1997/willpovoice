import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.text_normalizer import normalize_for_tts as n

tests = [
    '"We finally pushed to production!"',
    '"Do not refactor this loop; it breaks gravity".',
    'Dijo "hello my friend" y sigue en espanol',
    'Espanol puro entre "comillas" queda intacto',
]

for t in tests:
    print("INPUT :", t)
    print("OUTPUT:", n(t, guard=True))
    print()
