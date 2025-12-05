"""Response validators for bot testing."""

import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from telethon.tl.types import Message

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation check."""
    
    passed: bool
    message: str
    details: dict[str, Any] | None = None


class Validator(ABC):
    """Base class for response validators."""
    
    @abstractmethod
    def validate(self, response: Message | list[Message]) -> ValidationResult:
        """Validate the response.
        
        Args:
            response: Bot response message(s)
            
        Returns:
            Validation result
        """
        pass


class ContainsTextValidator(Validator):
    """Validator that checks if response contains specific text."""
    
    def __init__(self, text: str, case_sensitive: bool = False) -> None:
        """Initialize validator.
        
        Args:
            text: Text to search for
            case_sensitive: Whether to do case-sensitive search
        """
        self.text = text
        self.case_sensitive = case_sensitive
    
    def validate(self, response: Message | list[Message]) -> ValidationResult:
        """Check if response contains the expected text."""
        messages = [response] if isinstance(response, Message) else response
        
        search_text = self.text if self.case_sensitive else self.text.lower()
        
        for msg in messages:
            if msg.text:
                msg_text = msg.text if self.case_sensitive else msg.text.lower()
                if search_text in msg_text:
                    return ValidationResult(
                        passed=True,
                        message=f"Found text '{self.text}' in response",
                    )
        
        return ValidationResult(
            passed=False,
            message=f"Text '{self.text}' not found in response",
            details={"expected": self.text, "got": [m.text for m in messages if m.text]},
        )


class MatchesPatternValidator(Validator):
    """Validator that checks if response matches a regex pattern."""
    
    def __init__(self, pattern: str, flags: int = 0) -> None:
        """Initialize validator.
        
        Args:
            pattern: Regex pattern to match
            flags: Regex flags
        """
        self.pattern = re.compile(pattern, flags)
    
    def validate(self, response: Message | list[Message]) -> ValidationResult:
        """Check if response matches the pattern."""
        messages = [response] if isinstance(response, Message) else response
        
        for msg in messages:
            if msg.text and self.pattern.search(msg.text):
                return ValidationResult(
                    passed=True,
                    message=f"Response matches pattern '{self.pattern.pattern}'",
                )
        
        return ValidationResult(
            passed=False,
            message=f"Response doesn't match pattern '{self.pattern.pattern}'",
            details={"pattern": self.pattern.pattern, "got": [m.text for m in messages if m.text]},
        )


class HasButtonsValidator(Validator):
    """Validator that checks if response has inline buttons."""
    
    def __init__(
        self,
        button_texts: list[str] | None = None,
        min_buttons: int | None = None,
    ) -> None:
        """Initialize validator.
        
        Args:
            button_texts: Expected button texts (optional)
            min_buttons: Minimum number of buttons expected (optional)
        """
        self.button_texts = button_texts
        self.min_buttons = min_buttons
    
    def validate(self, response: Message | list[Message]) -> ValidationResult:
        """Check if response has expected buttons."""
        messages = [response] if isinstance(response, Message) else response
        
        for msg in messages:
            if msg.buttons:
                # Flatten button list
                all_buttons = [btn for row in msg.buttons for btn in row]
                button_texts = [btn.text for btn in all_buttons]
                
                # Check minimum buttons
                if self.min_buttons and len(all_buttons) < self.min_buttons:
                    return ValidationResult(
                        passed=False,
                        message=f"Expected at least {self.min_buttons} buttons, got {len(all_buttons)}",
                        details={"expected_min": self.min_buttons, "got": len(all_buttons)},
                    )
                
                # Check specific button texts
                if self.button_texts:
                    missing = [t for t in self.button_texts if t not in button_texts]
                    if missing:
                        return ValidationResult(
                            passed=False,
                            message=f"Missing expected buttons: {missing}",
                            details={"expected": self.button_texts, "found": button_texts},
                        )
                
                return ValidationResult(
                    passed=True,
                    message=f"Found {len(all_buttons)} button(s)",
                    details={"buttons": button_texts},
                )
        
        return ValidationResult(
            passed=False,
            message="Response has no inline buttons",
        )


class ResponseCountValidator(Validator):
    """Validator that checks the number of response messages."""
    
    def __init__(
        self,
        min_count: int | None = None,
        max_count: int | None = None,
        exact_count: int | None = None,
    ) -> None:
        """Initialize validator.
        
        Args:
            min_count: Minimum number of responses
            max_count: Maximum number of responses
            exact_count: Exact number of responses expected
        """
        self.min_count = min_count
        self.max_count = max_count
        self.exact_count = exact_count
    
    def validate(self, response: Message | list[Message]) -> ValidationResult:
        """Check response count."""
        messages = [response] if isinstance(response, Message) else response
        count = len(messages)
        
        if self.exact_count is not None and count != self.exact_count:
            return ValidationResult(
                passed=False,
                message=f"Expected exactly {self.exact_count} response(s), got {count}",
            )
        
        if self.min_count is not None and count < self.min_count:
            return ValidationResult(
                passed=False,
                message=f"Expected at least {self.min_count} response(s), got {count}",
            )
        
        if self.max_count is not None and count > self.max_count:
            return ValidationResult(
                passed=False,
                message=f"Expected at most {self.max_count} response(s), got {count}",
            )
        
        return ValidationResult(
            passed=True,
            message=f"Response count ({count}) is valid",
        )


class NotEmptyValidator(Validator):
    """Validator that checks if response is not empty."""
    
    def validate(self, response: Message | list[Message]) -> ValidationResult:
        """Check if response has content."""
        messages = [response] if isinstance(response, Message) else response
        
        if not messages:
            return ValidationResult(
                passed=False,
                message="No response received",
            )
        
        for msg in messages:
            if msg.text or msg.media or msg.buttons:
                return ValidationResult(
                    passed=True,
                    message="Response has content",
                )
        
        return ValidationResult(
            passed=False,
            message="Response is empty",
        )


def create_validators_from_config(config: list[dict[str, Any]]) -> list[Validator]:
    """Create validator instances from configuration.
    
    Args:
        config: List of validator configurations
        
    Returns:
        List of Validator instances
    """
    validators: list[Validator] = []
    
    for item in config:
        if "contains" in item:
            validators.append(ContainsTextValidator(
                item["contains"],
                item.get("case_sensitive", False),
            ))
        elif "matches" in item:
            validators.append(MatchesPatternValidator(
                item["matches"],
                item.get("flags", 0),
            ))
        elif "has_buttons" in item:
            validators.append(HasButtonsValidator(
                button_texts=item.get("button_texts"),
                min_buttons=item.get("min_buttons"),
            ))
        elif "response_count" in item:
            validators.append(ResponseCountValidator(
                min_count=item.get("min"),
                max_count=item.get("max"),
                exact_count=item.get("exact"),
            ))
        elif "not_empty" in item:
            validators.append(NotEmptyValidator())
    
    return validators
