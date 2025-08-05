from datetime import datetime
from typing import Any, Dict, List, Optional

from src.common.logging import logger


class ConversationMemory:
    """
    ConversationMemory maintains a summarized context of the conversation
    to help with contextual follow-up questions and references.

    This is different from StateManager which is used for task-specific state.
    ConversationMemory focuses on maintaining relevant context across the entire conversation.
    """

    def __init__(self):
        """
        Initialize the ConversationMemory with empty context.
        """
        self._conversation_context: Dict[str, Any] = {}
        self._recent_interactions: List[Dict[str, Any]] = []
        self._max_recent_interactions = 5  # Keep last 5 interactions for context
        logger.info("ConversationMemory initialized")

    def add_interaction(
        self,
        intent: str,
        query: str,
        entities: Dict[str, Any],
        agent_used: str,
        key_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a new interaction to the conversation memory.

        Args:
            intent (str): The detected intent (ORDER_STATUS, PRODUCT_RECOMMENDATION, etc.)
            query (str): The user's query
            entities (Dict[str, Any]): Extracted entities from the query
            agent_used (str): Which agent processed the request
            key_info (Optional[Dict[str, Any]]): Key information from the response
                (e.g., order details, products mentioned)
        """
        try:
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "intent": intent,
                "query": query,
                "entities": entities,
                "agent_used": agent_used,
                "key_info": key_info or {},
            }

            self._recent_interactions.append(interaction)

            # Keep only the most recent interactions
            if len(self._recent_interactions) > self._max_recent_interactions:
                self._recent_interactions = self._recent_interactions[-self._max_recent_interactions :]

            # Update conversation context based on the interaction
            self._update_context(interaction)

            logger.info(f"Added interaction to conversation memory: intent={intent}, agent={agent_used}")

        except Exception as e:
            logger.error(f"Error adding interaction to conversation memory: {e}")

    def _update_context(self, interaction: Dict[str, Any]) -> None:
        """
        Update the conversation context based on the new interaction.

        Args:
            interaction (Dict[str, Any]): The interaction to process
        """
        try:
            intent = interaction["intent"]
            entities = interaction["entities"]
            key_info = interaction["key_info"]

            # Update customer information if available
            if entities.get("Email"):
                self._conversation_context["customer_email"] = entities["Email"]

            # Handle order-related context
            if intent == "ORDER_STATUS" and key_info:
                order_info = {
                    "order_number": key_info.get("order_number"),
                    "customer_name": key_info.get("customer_name"),
                    "products": key_info.get("products", []),
                    "status": key_info.get("status"),
                    "last_checked": interaction["timestamp"],
                }
                self._conversation_context["last_order_lookup"] = order_info

                # Store product references for contextual questions
                if key_info.get("products"):
                    self._conversation_context["recent_products"] = key_info["products"]

            # Handle product recommendation context
            elif intent == "PRODUCT_RECOMMENDATION" and key_info:
                if key_info.get("products_mentioned"):
                    self._conversation_context["recent_products"] = key_info["products_mentioned"]

            # Handle promotion context
            elif intent == "EARLY_RISERS_PROMOTION" and key_info:
                if key_info.get("promo_code"):
                    self._conversation_context["last_promo_code"] = key_info["promo_code"]

        except Exception as e:
            logger.error(f"Error updating conversation context: {e}")

    def get_contextual_info(self, current_query: str) -> Dict[str, Any]:
        """
        Get relevant contextual information for the current query.

        Args:
            current_query (str): The current user query

        Returns:
            Dict[str, Any]: Relevant context information
        """
        try:
            context = {}

            # Check if query might be referring to previous order
            if self._is_order_reference(current_query):
                if "last_order_lookup" in self._conversation_context:
                    context["referenced_order"] = self._conversation_context["last_order_lookup"]

            # Check if query might be referring to products
            if self._is_product_reference(current_query):
                if "recent_products" in self._conversation_context:
                    context["referenced_products"] = self._conversation_context["recent_products"]

            # Add customer info if available
            if "customer_email" in self._conversation_context:
                context["customer_email"] = self._conversation_context["customer_email"]

            # Add recent interaction summary
            if self._recent_interactions:
                context["recent_interactions_summary"] = self._get_recent_summary()

            return context

        except Exception as e:
            logger.error(f"Error getting contextual info: {e}")
            return {}

    def _is_order_reference(self, query: str) -> bool:
        """
        Check if the query might be referring to a previous order lookup.

        Args:
            query (str): The user query

        Returns:
            bool: True if query seems to reference previous order
        """
        order_reference_keywords = [
            "that order",
            "my order",
            "the order",
            "this order",
            "those products",
            "these products",
            "the products",
            "my products",
            "what are those",
            "what are these",
            "tell me about",
            "more about",
        ]

        query_lower = query.lower()
        return any(keyword in query_lower for keyword in order_reference_keywords)

    def _is_product_reference(self, query: str) -> bool:
        """
        Check if the query might be referring to products mentioned earlier.

        Args:
            query (str): The user query

        Returns:
            bool: True if query seems to reference previous products
        """
        product_reference_keywords = [
            "those products",
            "these products",
            "the products",
            "what are those",
            "what are these",
            "tell me about them",
            "more details",
            "more info",
            "describe them",
        ]

        query_lower = query.lower()
        return any(keyword in query_lower for keyword in product_reference_keywords)

    def _get_recent_summary(self) -> str:
        """
        Get a summary of recent interactions.

        Returns:
            str: Summary of recent interactions
        """
        try:
            if not self._recent_interactions:
                return ""

            key_info = {}
            summary_parts = []
            for interaction in self._recent_interactions[-3:]:  # Last 3 interactions
                intent = interaction["intent"]
                key_info = interaction.get("key_info", {})

                if intent == "ORDER_STATUS":
                    if key_info.get("order_number", ""):
                        summary_parts.append(
                            f"Looked up order {key_info['order_number']} with products {key_info.get('products', [])}"
                        )
                elif intent == "PRODUCT_RECOMMENDATION":
                    summary_parts.append(f"Provided product recommendations about {key_info.get('products_mentioned', [])}")
                elif intent == "EARLY_RISERS_PROMOTION":
                    summary_parts.append(f"Provided Early Risers promotion code {key_info.get('promo_code', '')}")
                elif intent == "WHO_ARE_YOU":
                    summary_parts.append(f"Provided a brief introduction about Adventure Outfitters")
                else:
                    summary_parts.append(f"No relevant intent was detected. Asked the user to clarify and reiterated about the capabilities of the agent")
                if key_info.get("entities"):
                    summary_parts.append(f"Entities that were extracted from the user query: {key_info.get('entities', [])}")

            return "; ".join(summary_parts)

        except Exception as e:
            logger.error(f"Error generating recent summary: {e}")
            return ""

    def clear_context(self) -> None:
        """
        Clear all conversation context (useful for new conversations).
        """
        self._conversation_context.clear()
        self._recent_interactions.clear()
        logger.info("Conversation context cleared")

    def get_full_context(self) -> Dict[str, Any]:
        """
        Get the full conversation context for debugging or advanced use cases.

        Returns:
            Dict[str, Any]: Full conversation context
        """
        return {"context": self._conversation_context, "recent_interactions": self._recent_interactions}
