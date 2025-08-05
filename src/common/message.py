from typing import Dict, Optional


class Message:
    """
    Represents a message with content, sender, recipient, and optional metadata.
    """

    def __init__(self, content: str, sender: str, recipient: str, metadata: Optional[Dict[str, str]] = None) -> None:
        """
        Initializes the Message object.

        Args:
            content (str): The content of the message.
            sender (str): The sender of the message.
            recipient (str): The recipient of the message.
            metadata (Optional[Dict[str, str]]): Optional dictionary for storing additional information.
        """
        self.content: str = content
        self.sender: str = sender
        self.recipient: str = recipient
        self.metadata: Dict[str, str] = metadata or {}

    def __repr__(self) -> str:
        """
        Returns a string representation of the Message object.
        """
        return (
            f"Message(content={self.content}, sender={self.sender}, "
            f"recipient={self.recipient}, metadata={self.metadata})"
        )
