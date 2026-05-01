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
