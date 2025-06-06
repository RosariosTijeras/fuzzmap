# main.py

from Modulos.extraction.pdf_extractor import extract_text_from_pdf
from Modulos.nlp.text_classifier import split_qa
from Modulos.avltree.avl_tree import AVLTree
from Modulos.fuzzylogic.fuzzy_evaluator import evaluate_performance, recommendation
from Modulos.ui.app import run_ui

def build_example():
    raw = extract_text_from_pdf("data/Ciencia_Datos/example.pdf")
    qa_pairs = split_qa(raw)

    tree = AVLTree()
    for q,a in qa_pairs:
        tree.insert(q, a)

    # Preparar diccionario para UI
    materia = "Ciencia_Datos"
    questions = {materia: tree.inorder()}
    return questions

if __name__ == "__main__":
    qs = build_example()
    run_ui(qs)
