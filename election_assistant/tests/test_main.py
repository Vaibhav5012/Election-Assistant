"""Tests for the main application entry point using AppTest."""

from streamlit.testing.v1 import AppTest
from config import DEFAULT_COUNTRY, DEFAULT_MODE, MODE_OPTIONS

def test_app_loads_default_state():
    """Test that the app initializes with default state."""
    at = AppTest.from_file("main.py").run()
    assert not at.exception
    assert at.session_state["country"] == DEFAULT_COUNTRY
    assert at.session_state["mode"] == DEFAULT_MODE

def test_app_syncs_query_params_valid():
    """Test that valid query params update the state."""
    at = AppTest.from_file("main.py")
    at.query_params["country"] = "usa"
    at.query_params["mode"] = "Quiz Mode"
    at.run()
    
    assert not at.exception
    assert at.session_state["country"] == "usa"
    assert at.session_state["mode"] == "Quiz Mode"

def test_app_rejects_invalid_country_query_param():
    """Test that an invalid country query param falls back to default."""
    at = AppTest.from_file("main.py")
    at.query_params["country"] = "invalid_country"
    at.run()
    
    assert not at.exception
    assert at.session_state["country"] == DEFAULT_COUNTRY

def test_app_rejects_invalid_mode_query_param():
    """Test that an invalid mode query param falls back to default."""
    at = AppTest.from_file("main.py")
    at.query_params["mode"] = "Invalid Mode"
    at.run()
    
    assert not at.exception
    assert at.session_state["mode"] == DEFAULT_MODE

def test_sidebar_country_change():
    """Test changing country via sidebar selectbox updates state and rerun."""
    at = AppTest.from_file("main.py").run()
    
    # Simulate selecting 'usa' in the sidebar selectbox
    at.selectbox(key="sidebar_country").set_value("usa").run()
    
    assert not at.exception
    assert at.session_state["country"] == "usa"

def test_sidebar_mode_change():
    """Test changing mode via sidebar radio updates state and rerun."""
    at = AppTest.from_file("main.py").run()
    
    # Simulate selecting 'Ask Questions' in the sidebar radio
    at.radio(key="sidebar_mode").set_value("Ask Questions").run()
    
    assert not at.exception
    assert at.session_state["mode"] == "Ask Questions"
