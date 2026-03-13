import streamlit as st
from questions import generate_question, parse_question, get_topics_for_level
from database import create_progress, create_assignments
from styles import GLOBAL_CSS, render_sidebar, render_topnav

def get_starting_level(grade, score_percent):
    base = max(1, (grade - 1) // 2)
    if score_percent >= 80:
        return min(12, base + 1)
    elif score_percent >= 50:
        return base
    else:
        return max(1, base - 1)

def show_baseline():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    render_sidebar(None)
    render_topnav(st.session_state.get("username",""))

    if st.button("← Back to Dashboard"):
        st.session_state.show_baseline = False
        st.rerun()

    st.title("🧮 Placement Test")
    st.subheader("Let's find your starting level!")

    if "baseline_stage" not in st.session_state:
        st.session_state.baseline_stage    = "grade"
        st.session_state.baseline_index    = 0
        st.session_state.baseline_score    = 0
        st.session_state.baseline_grade    = None
        st.session_state.answered          = False
        st.session_state.current_question  = None

    if st.session_state.baseline_stage == "grade":
        st.write("First, tell us what grade you're in:")
        grade = st.selectbox("Select your grade", list(range(1, 13)))
        if st.button("Start Test", use_container_width=True):
            st.session_state.baseline_grade = grade
            st.session_state.baseline_stage = "test"
            st.rerun()

    elif st.session_state.baseline_stage == "test":
        grade   = st.session_state.baseline_grade
        total   = 10
        current = st.session_state.baseline_index

        st.progress(current / total)
        st.write(f"Question {current + 1} of {total}")

        if st.session_state.current_question is None:
            with st.spinner("Generating question..."):
                topics = get_topics_for_level(max(1, (grade - 1) // 2))
                topic  = topics[current % len(topics)]
                while True:
                    raw = generate_question(topic, grade)
                    question, options, answer = parse_question(raw)
                    if question and options and len(options) == 4 and answer:
                        break
                st.session_state.current_question = (question, options, answer)

        question, options, correct = st.session_state.current_question
        st.subheader(question)
        selected = st.radio("Choose your answer:", list(options.keys()),
                            format_func=lambda x: f"{x}) {options[x]}",
                            key=f"q_{current}")

        if not st.session_state.answered:
            if st.button("Submit Answer", use_container_width=True):
                st.session_state.answered = True
                if selected == correct:
                    st.session_state.baseline_score += 1
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Wrong! The answer was {correct}) {options[correct]}")
                st.rerun()
        else:
            if selected == correct:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Wrong! The answer was {correct}) {options.get(correct, '')}")
            if st.button("Next Question", use_container_width=True):
                st.session_state.baseline_index += 1
                st.session_state.answered        = False
                st.session_state.current_question = None
                if st.session_state.baseline_index >= total:
                    st.session_state.baseline_stage = "results"
                st.rerun()

    elif st.session_state.baseline_stage == "results":
        score   = st.session_state.baseline_score
        grade   = st.session_state.baseline_grade
        percent = (score / 10) * 100
        level   = get_starting_level(grade, percent)

        st.balloons()
        st.subheader(f"You scored {score}/10 ({percent:.0f}%)")
        st.write(f"Based on your results, you're starting at **Level {level}**.")

        if st.button("Go to Dashboard", use_container_width=True):
            topics = get_topics_for_level(level)
            create_progress(st.session_state.username, grade, level)
            create_assignments(st.session_state.username, level, topics)
            for key in ["baseline_stage", "baseline_index", "baseline_score",
                        "baseline_grade", "answered", "current_question"]:
                st.session_state.pop(key, None)
            st.session_state.show_baseline = False
            st.rerun()
