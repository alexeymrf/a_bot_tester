"""Tests for response validators."""

import pytest
from unittest.mock import MagicMock

from a_bot_tester.validator import (
    ContainsTextValidator,
    MatchesPatternValidator,
    HasButtonsValidator,
    ResponseCountValidator,
    NotEmptyValidator,
    create_validators_from_config,
)


class TestContainsTextValidator:
    """Tests for ContainsTextValidator."""

    def test_contains_text_found(self) -> None:
        """Test when text is found in response."""
        msg = MagicMock()
        msg.text = "Welcome to the bot!"
        
        validator = ContainsTextValidator("Welcome")
        result = validator.validate(msg)
        
        assert result.passed is True
        assert "Found text" in result.message

    def test_contains_text_not_found(self) -> None:
        """Test when text is not found in response."""
        msg = MagicMock()
        msg.text = "Hello world"
        
        validator = ContainsTextValidator("Welcome")
        result = validator.validate(msg)
        
        assert result.passed is False

    def test_contains_text_case_insensitive(self) -> None:
        """Test case insensitive search."""
        msg = MagicMock()
        msg.text = "WELCOME to the bot"
        
        validator = ContainsTextValidator("welcome", case_sensitive=False)
        result = validator.validate(msg)
        
        assert result.passed is True


class TestNotEmptyValidator:
    """Tests for NotEmptyValidator."""

    def test_not_empty_with_text(self) -> None:
        """Test response with text is not empty."""
        msg = MagicMock()
        msg.text = "Hello"
        msg.media = None
        msg.buttons = None
        
        validator = NotEmptyValidator()
        result = validator.validate(msg)
        
        assert result.passed is True

    def test_not_empty_with_buttons(self) -> None:
        """Test response with buttons is not empty."""
        msg = MagicMock()
        msg.text = None
        msg.media = None
        msg.buttons = [[MagicMock()]]
        
        validator = NotEmptyValidator()
        result = validator.validate(msg)
        
        assert result.passed is True

    def test_empty_response_list(self) -> None:
        """Test empty response list."""
        validator = NotEmptyValidator()
        result = validator.validate([])
        
        assert result.passed is False


class TestCreateValidatorsFromConfig:
    """Tests for validator factory function."""

    def test_create_contains_validator(self) -> None:
        """Test creating contains validator from config."""
        config = [{"contains": "Hello"}]
        validators = create_validators_from_config(config)
        
        assert len(validators) == 1
        assert isinstance(validators[0], ContainsTextValidator)

    def test_create_multiple_validators(self) -> None:
        """Test creating multiple validators from config."""
        config = [
            {"contains": "Hello"},
            {"not_empty": True},
        ]
        validators = create_validators_from_config(config)
        
        assert len(validators) == 2
