# Módulos/nlp/text_classifier.py

from typing import List, Tuple

def split_qa(raw_text: str) -> List[Tuple[str,str]]:
    """
    Separa el texto en pares (pregunta, respuesta).
    """
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    qa = []
    for i in range(0, len(lines), 2):
        try:
            question = lines[i]
            answer = lines[i+1].lstrip('- ').strip()
            qa.append((question, answer))
        except IndexError:
            pass
    return qa
