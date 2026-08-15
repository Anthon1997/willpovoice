from pathlib import Path
import ast

p = Path("core/text_normalizer.py")
t = p.read_text(encoding="utf-8")

# ---- 1. Lista de deteccion amplia (sin solapamiento con espanol) ----
if "ENGLISH_DETECT = " not in t:
    bloque = '''ENGLISH_DETECT = ENGLISH_TRIGGERS + [
    "a", "an", "and", "but", "if", "then", "than", "because", "while",
    "during", "before", "after", "above", "below", "between", "into",
    "through", "about", "against", "again", "once", "just", "now",
    "such", "very", "too", "also", "only", "even", "still", "already",
    "yet", "ever", "never", "always", "often", "sometimes", "usually",
    "finally", "really", "actually", "basically", "probably", "maybe",
    "perhaps", "almost", "enough", "quite", "rather", "soon", "there",
    "here", "we", "they", "them", "him", "his", "its", "our", "your",
    "their", "mine", "yours", "ours", "theirs", "myself", "yourself",
    "himself", "herself", "itself", "ourselves", "themselves", "to",
    "of", "in", "on", "at", "by", "for", "with", "from", "up", "down",
    "out", "off", "over", "under", "away", "back", "forward", "is",
    "am", "are", "was", "were", "be", "been", "being", "do", "does",
    "did", "done", "doing", "have", "has", "had", "having", "will",
    "would", "can", "could", "shall", "should", "must", "might",
    "need", "let", "get", "got", "gets", "getting", "go", "goes",
    "went", "gone", "going", "make", "makes", "made", "making",
    "take", "takes", "took", "taken", "taking", "know", "knows",
    "knew", "known", "think", "thinks", "thought", "see", "sees",
    "saw", "seen", "come", "comes", "came", "coming", "want",
    "wants", "wanted", "like", "likes", "liked", "say", "says",
    "said", "tell", "tells", "told", "ask", "asks", "asked",
    "answer", "answers", "give", "gives", "gave", "given", "find",
    "finds", "found", "help", "helps", "helped", "try", "tries",
    "tried", "call", "calls", "called", "keep", "keeps", "kept",
    "leave", "leaves", "left", "live", "lives", "lived", "move",
    "moves", "moved", "run", "runs", "ran", "running", "stop",
    "stops", "stopped", "start", "starts", "started", "turn",
    "turns", "turned", "open", "opens", "opened", "close",
    "closes", "closed", "read", "reads", "write", "writes",
    "wrote", "written", "speak", "speaks", "spoke", "listen",
    "listens", "push", "pushed", "pull", "pulled", "deploy",
    "deployed", "build", "built", "release", "released",
    "refactor", "loop", "loops", "break", "breaks", "broke",
    "broken", "it", "as", "or", "us",
]


'''
    anchor = t.find("] + list(HOMOGRAFOS)")
    if anchor != -1:
        anchor = t.find("\n", anchor) + 1
        t = t[:anchor] + "\n" + bloque + t[anchor:]
        print("1. ENGLISH_DETECT amplia agregada.")

# ---- 2. Usarla en las dos capas ----
n = t.count("for w in ENGLISH_TRIGGERS")
t = t.replace("for w in ENGLISH_TRIGGERS", "for w in ENGLISH_DETECT")
print(f"2. Deteccion ampliada aplicada en {n} capa(s).")

p.write_text(t, encoding="utf-8")

try:
    ast.parse(t)
    print("SINTAXIS OK")
except SyntaxError as e:
    print("ERROR:", e.lineno, e.msg)
