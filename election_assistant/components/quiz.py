"""Multiple-choice quiz component.

Renders questions one at a time with randomized option order,
immediate feedback, and score tracking.  Session state stores
only indices, not data dicts.  Fires GA4 ``quiz_completed``
when all questions are answered.
"""

from __future__ import annotations

import random

import streamlit as st

from config import ENABLE_ANALYTICS
from utils.google_services import track_event


def render_quiz(data: dict) -> None:
    """Render the MCQ quiz interface.

    Args:
        data: The loaded election data dictionary.
    """
    questions = data.get("quiz", [])
    total = len(questions)

    st.header("🧠 Quiz Mode")
    st.caption(
        f"Test your knowledge of {data['country']}'s election process"
    )

    if not questions:
        st.warning("No quiz questions available for this country.")
        return

    # --- Check if quiz is complete ---
    if st.session_state["quiz_index"] >= total:
        _render_final_score(total, data)
        return

    # --- Render current question ---
    idx = st.session_state["quiz_index"]
    question = questions[idx]
    _render_question(question, idx, total)


def _render_question(
    question: dict, idx: int, total: int
) -> None:
    """Render a single quiz question with shuffled options.

    Args:
        question: The quiz question dictionary.
        idx: The current question index (0-based).
        total: Total number of questions.
    """
    st.subheader(f"Question {idx + 1} of {total}")
    st.markdown(f"**{question['question']}**")

    # Get or create shuffled option order for this question
    shuffled = _get_shuffled_options(question, idx)
    display_options = [question["options"][i] for i in shuffled]

    # Radio selection
    selected = st.radio(
        "Choose your answer:",
        options=display_options,
        key=f"quiz_q_{idx}",
        index=None,
        label_visibility="collapsed",
    )

    if st.button("Submit Answer", key=f"quiz_submit_{idx}"):
        if selected is None:
            st.warning("⚠️ Please select an answer first.")
            return
        _check_answer(selected, question, shuffled, idx)


def _get_shuffled_options(
    question: dict, idx: int
) -> list[int]:
    """Retrieve or create a shuffled option index list.

    Args:
        question: The quiz question dictionary.
        idx: The current question index.

    Returns:
        A list of shuffled indices into ``question["options"]``.
    """
    key = str(idx)
    shuffled_map = st.session_state["quiz_shuffled_options"]

    if key not in shuffled_map:
        indices = list(range(len(question["options"])))
        random.shuffle(indices)
        shuffled_map[key] = indices

    return shuffled_map[key]


def _check_answer(
    selected: str,
    question: dict,
    shuffled: list[int],
    idx: int,
) -> None:
    """Check the answer and update score.

    Args:
        selected: The selected option text.
        question: The quiz question dictionary.
        shuffled: The shuffled index mapping.
        idx: The current question index.
    """
    # Find the original index of the selected option
    selected_original = question["options"].index(selected)
    correct_original = question["correct_index"]
    is_correct = selected_original == correct_original

    if is_correct:
        st.success("✅ Correct!")
        st.session_state["quiz_score"] += 1
    else:
        correct_text = question["options"][correct_original]
        st.error(f"❌ Incorrect. The answer is: **{correct_text}**")

    # Show explanation
    st.info(f"📖 {question['explanation']}")

    # Record and advance
    st.session_state["quiz_answers"].append(selected_original)
    st.session_state["quiz_index"] = idx + 1

    st.button("Next Question ➡️", key=f"quiz_next_{idx}")


def _render_final_score(total: int, data: dict) -> None:
    """Display the final quiz score with percentage.

    Args:
        total: Total number of questions.
        data: The election data dict (for GA4 context).
    """
    score = st.session_state["quiz_score"]
    percentage = (score / total * 100) if total else 0

    st.success(f"🎉 Quiz Complete!")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{score}/{total}")
    with col2:
        st.metric("Percentage", f"{percentage:.0f}%")
    with col3:
        grade = _get_grade(percentage)
        st.metric("Grade", grade)

    # Fire GA4 event (only once)
    if not st.session_state.get("quiz_ga4_fired"):
        st.session_state["quiz_ga4_fired"] = True
        if ENABLE_ANALYTICS:
            js = track_event(
                "quiz_completed",
                {
                    "score": score,
                    "total": total,
                    "country": data["country"],
                },
            )
            st.markdown(js, unsafe_allow_html=True)

    # Restart button
    if st.button("🔄 Retake Quiz", key="quiz_restart"):
        _reset_quiz()
        st.rerun()


def _get_grade(percentage: float) -> str:
    """Return a letter grade based on percentage.

    Args:
        percentage: The score as a percentage (0-100).

    Returns:
        A letter grade string.
    """
    if percentage >= 90:
        return "A+"
    if percentage >= 80:
        return "A"
    if percentage >= 70:
        return "B"
    if percentage >= 60:
        return "C"
    return "D"


def _reset_quiz() -> None:
    """Reset all quiz-related session state to initial values."""
    st.session_state["quiz_score"] = 0
    st.session_state["quiz_index"] = 0
    st.session_state["quiz_answers"] = []
    st.session_state["quiz_shuffled_options"] = {}
    st.session_state["quiz_ga4_fired"] = False
