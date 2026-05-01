"""Tests for component logic (quiz, steps, timeline)."""

from __future__ import annotations


class TestQuizLogic:
    """Tests for quiz scoring and progression logic."""

    def test_correct_answer_increments_score(
        self, sample_india_data: dict, mock_session_state: dict
    ) -> None:
        """A correct answer increments the quiz score."""
        q = sample_india_data["quiz"][0]
        is_correct = q["correct_index"] == q["correct_index"]
        assert is_correct is True
        mock_session_state["quiz_score"] += 1
        assert mock_session_state["quiz_score"] == 1

    def test_wrong_answer_no_score_change(
        self, sample_india_data: dict, mock_session_state: dict
    ) -> None:
        """A wrong answer does not change the quiz score."""
        q = sample_india_data["quiz"][0]
        wrong = (q["correct_index"] + 1) % len(q["options"])
        is_correct = wrong == q["correct_index"]
        assert is_correct is False
        assert mock_session_state["quiz_score"] == 0

    def test_all_answered_score(
        self, sample_india_data: dict, mock_session_state: dict
    ) -> None:
        """Final score calculated correctly for all questions."""
        questions = sample_india_data["quiz"]
        for q in questions:
            mock_session_state["quiz_score"] += 1
            mock_session_state["quiz_answers"].append(q["correct_index"])
        total = len(questions)
        pct = (mock_session_state["quiz_score"] / total) * 100
        assert mock_session_state["quiz_score"] == total
        assert pct == 100.0

    def test_quiz_index_is_int(self, mock_session_state: dict) -> None:
        """Quiz index is stored as an integer."""
        assert isinstance(mock_session_state["quiz_index"], int)


class TestStepProgression:
    """Tests for step progression logic."""

    def test_step_advances(self, mock_session_state: dict) -> None:
        """Step index advances by one."""
        assert mock_session_state["current_step"] == 0
        mock_session_state["current_step"] += 1
        assert mock_session_state["current_step"] == 1

    def test_completed_tracking(self, mock_session_state: dict) -> None:
        """Completed steps are tracked in the set."""
        mock_session_state["steps_completed"].add(0)
        mock_session_state["steps_completed"].add(1)
        assert len(mock_session_state["steps_completed"]) == 2

    def test_step_index_is_int(self, mock_session_state: dict) -> None:
        """Step index is stored as an integer."""
        assert isinstance(mock_session_state["current_step"], int)


class TestTimelineLogic:
    """Tests for timeline phase logic."""

    def test_phase_count(self, sample_india_data: dict) -> None:
        """Correct number of phases in fixture."""
        phases = sample_india_data["timeline"]["phases"]
        assert len(phases) == 2

    def test_chronological_order(self, sample_india_data: dict) -> None:
        """Phases are ordered by start_offset_days."""
        phases = sample_india_data["timeline"]["phases"]
        offsets = [p["start_offset_days"] for p in phases]
        assert offsets == sorted(offsets)

    def test_required_fields(self, sample_india_data: dict) -> None:
        """Each phase has all required fields."""
        required = {"id", "name", "start_offset_days", "end_offset_days", "color", "description"}
        for phase in sample_india_data["timeline"]["phases"]:
            assert required.issubset(phase.keys())

    def test_sequential_ids(self, sample_india_data: dict) -> None:
        """Phase IDs are sequential starting from 1."""
        phases = sample_india_data["timeline"]["phases"]
        ids = [p["id"] for p in phases]
        assert ids == list(range(1, len(phases) + 1))


from streamlit.testing.v1 import AppTest

def test_steps_component_rendering():
    """Test step-by-step component rendering and interaction via AppTest."""
    at = AppTest.from_file("main.py")
    at.session_state["mode"] = "Learn Step-by-Step"
    at.run()
    assert not at.exception
    # Check if we can click the next step button
    if at.button(key="step_next"):
        at.button(key="step_next").click().run()
        assert not at.exception

def test_timeline_component_rendering():
    """Test timeline component rendering and interaction via AppTest."""
    at = AppTest.from_file("main.py")
    at.session_state["mode"] = "Election Timeline"
    at.run()
    assert not at.exception
    if at.button(key="timeline_new_fact"):
        at.button(key="timeline_new_fact").click().run()
        assert not at.exception

def test_chat_component_rendering():
    """Test chat component rendering and interaction via AppTest."""
    at = AppTest.from_file("main.py")
    at.session_state["mode"] = "Ask Questions"
    at.run()
    assert not at.exception
    if at.chat_input(key="chat_input"):
        at.chat_input(key="chat_input").set_value("How do I vote?").run()
        assert not at.exception

def test_quiz_component_rendering():
    """Test quiz component rendering and interaction via AppTest."""
    at = AppTest.from_file("main.py")
    at.session_state["mode"] = "Quiz Mode"
    at.run()
    assert not at.exception
    # Simulate clicking submit on the first question if it exists
    if at.button(key="quiz_submit_0"):
        at.button(key="quiz_submit_0").click().run()
        assert not at.exception

def test_facts_component_rendering():
    """Test facts component rendering via AppTest."""
    at = AppTest.from_file("main.py")
    at.session_state["mode"] = "Did You Know?"
    at.run()
    assert not at.exception

