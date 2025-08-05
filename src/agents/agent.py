from abc import ABC, abstractmethod

from src.common.message import Message
from src.common.logging import logger
from src.llm_adapter import LLMAdapter
from src.prompt.manage import TemplateManager


class Agent(ABC):
    """
    Abstract base class for agents that handle specific tasks in a coordinator-delegate pattern.
    Each agent must implement the 'process' method to handle incoming messages.
    """

    TEMPLATE_PATH = "./config/adventure_outfitters.yml"
    llm_adapter = LLMAdapter()

    def __init__(self, name: str, session_id: str) -> None:
        """
        Initializes the Agent with a name, TemplateManager, and LLMAdapter.
        """
        self.name = name
        self.template_manager = TemplateManager(self.TEMPLATE_PATH)
        self.session_id = session_id
        logger.info(f"Agent {self.name} initialized with shared resources for session {session_id}.")

    @abstractmethod
    def process(self, message: Message) -> Message:
        """
        Abstract method to process the incoming message. Must be implemented by subclasses.
        """
        raise NotImplementedError(f"{self.__class__.__name__} has not implemented the 'process' method.")
