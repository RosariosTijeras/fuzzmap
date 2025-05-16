import unicodedata
import string
import streamlit as st
from Modulos.fuzzylogic.fuzzy_evaluator import evaluate_performance, recommendation

def normalize(s: str) -> str:
    # 1) Unicode NFD, 2) quitar diacríticos, 3) quitar puntuación, 4) lowercase, 5) strip
    s = unicodedata.normalize('NFD', s)
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    s = s.translate(str.maketrans('', '', string.punctuation))
    return s.lower().strip()

def run_ui(questions):
    st.title("FuzzMap Ejemplo")
    materia = st.selectbox("Elige materia", list(questions.keys()))

    if "test_started" not in st.session_state:
        st.session_state.test_started = False
        st.session_state.user_answers = []

    if st.button("Comenzar Test"):
        st.session_state.test_started = True
        st.session_state.user_answers = [""] * len(questions[materia])

    if st.session_state.test_started:
        for idx, (q, _) in enumerate(questions[materia]):
            st.session_state.user_answers[idx] = st.text_input(
                q,
                value=st.session_state.user_answers[idx],
                key=f"q{idx}"
            )

        if st.button("Finalizar Test"):
            correct = 0
            total = len(questions[materia])
            for idx, (_, a) in enumerate(questions[materia]):
                user_resp = normalize(st.session_state.user_answers[idx])
                good_ans = normalize(a)
                if user_resp == good_ans:
                    correct += 1

            score = evaluate_performance(correct, total)
            rec = recommendation(score)

            st.markdown("### Resultados")
            st.write(f"- Aciertos: **{correct}** de **{total}**")
            st.write(f"- Puntuación (0–1): **{score:.2f}**")
            st.write(f"- Recomendación: **{rec}**")

            st.session_state.test_started = False
