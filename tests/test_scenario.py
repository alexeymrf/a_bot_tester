"""Tests for scenario loading."""

import tempfile
from pathlib import Path

import pytest

from a_bot_tester.scenario import load_scenario, TestCase, TestScenario


class TestLoadScenario:
    """Tests for scenario loading."""

    def test_load_basic_scenario(self, tmp_path: Path) -> None:
        """Test loading a basic scenario file."""
        scenario_content = """
name: Test Scenario
description: A test scenario

tests:
  - name: Test 1
    command: /start
    expected:
      - contains: "Welcome"
    timeout: 10
"""
        scenario_file = tmp_path / "test.yaml"
        scenario_file.write_text(scenario_content)
        
        scenario = load_scenario(scenario_file)
        
        assert scenario.name == "Test Scenario"
        assert scenario.description == "A test scenario"
        assert len(scenario.tests) == 1
        assert scenario.tests[0].name == "Test 1"
        assert scenario.tests[0].command == "/start"

    def test_load_scenario_with_setup(self, tmp_path: Path) -> None:
        """Test loading scenario with setup/teardown commands."""
        scenario_content = """
name: Setup Test
setup_commands:
  - /reset
teardown_commands:
  - /cleanup

tests:
  - name: Test 1
    command: /test
"""
        scenario_file = tmp_path / "setup_test.yaml"
        scenario_file.write_text(scenario_content)
        
        scenario = load_scenario(scenario_file)
        
        assert scenario.setup_commands == ["/reset"]
        assert scenario.teardown_commands == ["/cleanup"]

    def test_load_scenario_with_skip(self, tmp_path: Path) -> None:
        """Test loading scenario with skipped tests."""
        scenario_content = """
name: Skip Test

tests:
  - name: Skipped Test
    command: /skip
    skip: true
    skip_reason: Not implemented yet
"""
        scenario_file = tmp_path / "skip_test.yaml"
        scenario_file.write_text(scenario_content)
        
        scenario = load_scenario(scenario_file)
        
        assert scenario.tests[0].skip is True
        assert scenario.tests[0].skip_reason == "Not implemented yet"
