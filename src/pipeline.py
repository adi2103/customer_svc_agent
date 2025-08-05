from typing import List, Union

from src.agents.coordinator import AdventureOutfittersAgent
from src.agents.delegates.early_risers_promotion import EarlyRisersPromotionAgent
from src.agents.delegates.order_status import OrderStatusAgent
from src.agents.delegates.product_recommendation import ProductRecommendationAgent
from src.common.message import Message
from src.common.logging import logger


class AdventureOutfittersPipeline:
    """
    Main pipeline for Adventure Outfitters customer service agent system.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        # Initialize specialized agents
        self.order_status_agent = OrderStatusAgent(name="OrderStatusAgent", session_id=session_id)
        self.product_recommendation_agent = ProductRecommendationAgent(name="ProductRecommendationAgent", session_id=session_id)
        self.early_risers_promotion_agent = EarlyRisersPromotionAgent(name="EarlyRisersPromotionAgent", session_id=session_id)

        # Initialize the main coordinator agent
        self.adventure_outfitters_agent = AdventureOutfittersAgent(
            name="AdventureOutfittersAgent",
            sub_agents=[
                self.order_status_agent,
                self.product_recommendation_agent,
                self.early_risers_promotion_agent,
            ],
            session_id=session_id,
        )

        logger.info(f"Adventure Outfitters Pipeline initialized successfully for session {session_id}")

    @property
    def coordinator(self):
        """Access to the main coordinator agent."""
        return self.adventure_outfitters_agent

    def process_query(self, query: str) -> str:
        """
        Process a single customer query and return the response.
        """
        try:
            message = Message(content=query, sender="Customer", recipient="AdventureOutfittersAgent")
            response_message = self.adventure_outfitters_agent.process(message)

            logger.info(f"Query processed: '{query}' -> Response: '{response_message.content[:100]}...'")
            return response_message.content

        except Exception as e:
            logger.error(f"Error processing query '{query}': {e}")
            unexpected_error_msg = (
                "🏔️ I encountered an unexpected error. Please try again or contact "
                "our support team. Onward into the unknown! 🌟"
            )
            return unexpected_error_msg

    def execute(self, queries: Union[str, List[str]]) -> None:
        """
        Execute the pipeline with one or more queries (for testing/demo purposes).
        """
        if isinstance(queries, str):
            queries = [queries]

        for query in queries:
            try:
                response = self.process_query(query)

                print(f"\n{'=' * 60}")
                print(f"Customer: {query}")
                print(f"{'=' * 60}")
                print(f"Adventure Outfitters: {response}")
                print(f"{'=' * 60}")

            except Exception as e:
                logger.error(f"Error processing query '{query}': {e}")


def run_demo(queries: Union[str, List[str]]) -> None:
    """
    Run the pipeline with demo queries.
    """
    pipeline = AdventureOutfittersPipeline()
    pipeline.execute(queries)


if __name__ == "__main__":
    # Demo queries to test different intents
    demo_queries = [
        "Check my order #W001 for john.doe@example.com",
        "I'm looking for a good backpack for hiking",
        "Can I get an Early Risers discount code?",
        "Hello, how are you?",
        "What can you help me with?",
    ]

    print("🏔️ Welcome to Adventure Outfitters Customer Service Demo! 🌟")
    print("Testing various customer queries...")

    run_demo(demo_queries)
