import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.text_normalizer import normalize_for_tts as n

texto = ("la tarea parecia un callejon sin salida. El codigo base "
         "combinaba sutilmente varias tecnologias: Python clasico, "
         "scripts de Bash oxidados y fragmentos en C++ [un lenguaje "
         "que ella no dominaba por completo")

print("OUTPUT:", n(texto, guard=True))
