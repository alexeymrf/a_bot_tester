"""Test scenario loading and management."""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


@dataclass
class TestCase:
    """A single test case."""
    
    name: str
    command: str
    expected: list[dict[str, Any]] = field(default_factory=list)
    timeout: int = 10
    description: str = ""
    skip: bool = False
    skip_reason: str = ""


@dataclass
class TestScenario:
    """A test scenario containing multiple test cases."""
    
    name: str
    description: str = ""
    setup_commands: list[str] = field(default_factory=list)
    teardown_commands: list[str] = field(default_factory=list)
    tests: list[TestCase] = field(default_factory=list)


def load_scenario(path: Path) -> TestScenario:
    """Load a test scenario from a YAML file.
    
    Args:
        path: Path to the YAML file
        
    Returns:
        TestScenario instance
    """
    with open(path) as f:
        data = yaml.safe_load(f)
    
    tests = []
    for test_data in data.get("tests", []):
        tests.append(TestCase(
            name=test_data["name"],
            command=test_data["command"],
            expected=test_data.get("expected", []),
            timeout=test_data.get("timeout", 10),
            description=test_data.get("description", ""),
            skip=test_data.get("skip", False),
            skip_reason=test_data.get("skip_reason", ""),
        ))
    
    return TestScenario(
        name=data.get("name", path.stem),
        description=data.get("description", ""),
        setup_commands=data.get("setup_commands", []),
        teardown_commands=data.get("teardown_commands", []),
        tests=tests,
    )


def load_all_scenarios(directory: Path) -> list[TestScenario]:
    """Load all test scenarios from a directory.
    
    Args:
        directory: Path to the scenarios directory
        
    Returns:
        List of TestScenario instances
    """
    scenarios = []
    
    for yaml_file in directory.glob("*.yaml"):
        try:
            scenario = load_scenario(yaml_file)
            scenarios.append(scenario)
            logger.info(f"Loaded scenario: {scenario.name} ({len(scenario.tests)} tests)")
        except Exception as e:
            logger.error(f"Failed to load scenario from {yaml_file}: {e}")
    
    for yml_file in directory.glob("*.yml"):
        try:
            scenario = load_scenario(yml_file)
            scenarios.append(scenario)
            logger.info(f"Loaded scenario: {scenario.name} ({len(scenario.tests)} tests)")
        except Exception as e:
            logger.error(f"Failed to load scenario from {yml_file}: {e}")
    
    return scenarios
