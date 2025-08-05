import json
from enum import Enum
from typing import List, Optional

from src.agents.agent import Agent
from src.common.message import Message
from src.common.logging import logger
from src.memory.conversation import ConversationMemory


class Intent(Enum):
    """
    Enum to define possible user intents for Adventure Outfitters customer service.
    """

    ORDER_STATUS = 1
    PRODUCT_RECOMMENDATION = 2
    EARLY_RISERS_PROMOTION = 3
    WHO_ARE_YOU = 4
    UNKNOWN = 5


class AdventureOutfittersAgent(Agent):
    """
    Adventure Outfitters customer service agent responsible for routing customer queries
    to specialized agents based on detected intent and generating consolidated responses.
    """

    def __init__(self, name: str, sub_agents: List[Agent], session_id: str):
        """
        Initializes the AdventureOutfittersAgent with a set of sub-agents.
        """
        super().__init__(name, session_id)
        self.sub_agents = {agent.name: agent for agent in sub_agents}
        self.conversation_memory = ConversationMemory()
        logger.info(f"{self.name} initialized with {len(self.sub_agents)} sub-agents.")

    def determine_intent(self, query: str) -> tuple[Intent, dict]:
        """
        Determines the customer's intent and extracts entities based on their query using the LLM.
        Now includes conversation context to better understand contextual references.

        Returns:
            tuple: (Intent, entities_dict)
        """
        logger.info(f"Determining intent for query: '{query}'")
        try:

            template = self.template_manager.create_template("coordinator", "route")
            system_instructions = template.get("system", "")

            user_instructions = self.template_manager.fill_template(template.get("user", ""), query=query)
            user_instructions += self._get_conversation_context_string(query)

            messages = [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_instructions},
            ]

            response = self.llm_adapter.chat(
                messages, temperature=0.1
            )  # Lower temperature for more deterministic intent detection

            if response.get("success"):
                try:
                    response_text = response["content"].strip()
                    logger.debug(f"Raw LLM response: {response_text}")

                    # Try multiple parsing strategies
                    out_dict = None

                    # Strategy 1: Direct JSON parsing
                    if response_text.startswith("{") and response_text.endswith("}"):
                        try:
                            out_dict = json.loads(response_text)
                        except json.JSONDecodeError:
                            pass

                    # Strategy 2: Extract JSON from markdown code blocks
                    if out_dict is None:
                        import re

                        # Look for JSON in code blocks
                        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
                        if json_match:
                            try:
                                out_dict = json.loads(json_match.group(1))
                            except json.JSONDecodeError:
                                pass

                    # Strategy 3: Extract any JSON-like structure
                    if out_dict is None:
                        json_match = re.search(r'\{[^{}]*"intent"[^{}]*\}', response_text, re.DOTALL)
                        if json_match:
                            try:
                                out_dict = json.loads(json_match.group())
                            except json.JSONDecodeError:
                                pass

                    # Strategy 4: Look for intent value directly
                    if out_dict is None:
                        intent_match = re.search(r'"intent":\s*"([^"]+)"', response_text)
                        if intent_match:
                            out_dict = {"intent": intent_match.group(1), "entities": {}}

                    if out_dict is None:
                        logger.error(f"No JSON found in response: {response_text}")
                        return Intent.UNKNOWN, {}

                    intent_str = out_dict.get("intent", "UNKNOWN").upper()
                    entities = out_dict.get("entities", {})

                    context_info = self.conversation_memory.get_contextual_info(query)
                    if context_info and intent_str == "PRODUCT_RECOMMENDATION":
                        if context_info.get("referenced_products"):
                            entities["ReferencedProducts"] = context_info["referenced_products"]
                        if context_info.get("referenced_order"):
                            entities["ReferencedOrder"] = context_info["referenced_order"]

                    logger.info(f"Determined intent: {intent_str}")
                    logger.info(f"Extracted entities: {entities}")

                    if intent_str in [intent.name for intent in Intent]:
                        return Intent[intent_str], entities
                    else:
                        logger.warning(f"Invalid intent '{intent_str}', defaulting to UNKNOWN")
                        return Intent.UNKNOWN, {}

                except Exception as e:
                    logger.error(f"Error parsing intent response: {e}")
                    logger.error(f"Response content: {response_text}")
                    return Intent.UNKNOWN, {}
            else:
                logger.error(f"LLM request failed: {response.get('error')}")
                return Intent.UNKNOWN, {}

        except Exception as e:
            logger.error(f"Unexpected error while determining intent: {e}")
            return Intent.UNKNOWN, {}

    def _format_context_for_llm(self, context_info: dict) -> str:
        """
        Format conversation context information for the LLM.

        Args:
            context_info (dict): Context information from ConversationMemory

        Returns:
            str: Formatted context string
        """
        context_parts = []

        if context_info.get("referenced_order"):
            order = context_info["referenced_order"]
            order_num = order.get("order_number")
            customer = order.get("customer_name")
            products = order.get("products", [])
            context_parts.append(f"Recently looked up order: {order_num} for {customer} " f"with products {products}")

        if context_info.get("referenced_products"):
            products = context_info["referenced_products"]
            context_parts.append(f"Recently mentioned products: {products}")

        if context_info.get("customer_email"):
            context_parts.append(f"Customer email: {context_info['customer_email']}")

        if context_info.get("recent_interactions_summary"):
            context_parts.append(f"Recent activity: {context_info['recent_interactions_summary']}")

        return "\n".join(context_parts) if context_parts else "No relevant context available."

    def _generate_unknown_intent_response(self, query: str) -> Message:
        """
        Generate an LLM response for UNKNOWN intent queries using conversation context.

        Args:
            query (str): The user's query that couldn't be handled

        Returns:
            Message: Generated response acknowledging the unsupported request
        """
        try:
            template = self.template_manager.create_template("coordinator", "unknown")
            system_instructions = template.get("system", "")

            # Format context information for the LLM
            context_summary = self._get_conversation_context_string(query)

            user_instructions = self.template_manager.fill_template(
                template.get("user", ""), query=query, context_info=context_summary
            )

            logger.info(f"Generating UNKNOWN intent response for query: '{query}'")

            messages = [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_instructions},
            ]

            response = self.llm_adapter.chat(messages, temperature=0.5)  # Higher temperature for more varied responses

            if response.get("success"):
                unknown_response = response["content"].strip()
                
                # Apply supervisor guardrails
                supervisor_template = self.template_manager.create_template("coordinator", "supervisor")
                supervisor_system = self.template_manager.fill_template(
                    supervisor_template.get("system", ""), query=query, consolidated_response=unknown_response
                )
                supervisor_user = self.template_manager.fill_template(
                    supervisor_template.get("user", ""), query=query, consolidated_response=unknown_response
                )
                
                supervisor_messages = [
                    {"role": "system", "content": supervisor_system},
                    {"role": "user", "content": supervisor_user},
                ]
                
                supervisor_response = self.llm_adapter.chat(supervisor_messages)
                
                if supervisor_response.get("success"):
                    response_text = supervisor_response["content"].strip()
                else:
                    logger.error(f"Supervisor failed for unknown intent: {supervisor_response.get('error')}")
                    response_text = unknown_response
                    
                return Message(content=response_text, sender=self.name, recipient="Customer")
            else:
                logger.error(f"UNKNOWN intent response generation failed: {response.get('error')}")
                # Fallback to static response if LLM fails
                welcome_msg = (
                    "🏔️ Hello there, fellow adventurer! I'm here to help you with "
                    "your Adventure Outfitters experience! 🌟\n\n🎒 I can help you with:\n"
                    "• **Order Status & Tracking** - Check your order status and get "
                    "tracking information\n• **Product Recommendations** - Find the "
                    "perfect outdoor gear for your next adventure\n\nJust let me know "
                    "what you need, and I'll get you equipped for your journey! "
                    "Onward into the unknown! 🏔️"
                )
                return Message(
                    content=welcome_msg,
                    sender=self.name,
                    recipient="Customer",
                )

        except Exception as e:
            logger.error(f"Error generating UNKNOWN intent response: {e}")
            # Fallback to static response if there's an error
            welcome_msg = (
                "🏔️ Hello there, fellow adventurer! I'm here to help you with "
                "your Adventure Outfitters experience! 🌟\n\n🎒 I can help you with:\n"
                "• **Order Status & Tracking** - Check your order status and get "
                "tracking information\n• **Product Recommendations** - Find the "
                "perfect outdoor gear for your next adventure\n\nJust let me know "
                "what you need, and I'll get you equipped for your journey! "
                "Onward into the unknown! 🏔️"
            )
            return Message(
                content=welcome_msg,
                sender=self.name,
                recipient="Customer",
            )

    def route_to_agent(self, intent: Intent) -> Optional[Agent]:
        """
        Routes the query to the appropriate sub-agent based on the determined intent.
        """
        intent_to_agent = {
            Intent.ORDER_STATUS: "OrderStatusAgent",
            Intent.PRODUCT_RECOMMENDATION: "ProductRecommendationAgent",
            Intent.EARLY_RISERS_PROMOTION: "EarlyRisersPromotionAgent",
            Intent.UNKNOWN: None,
        }

        agent_name = intent_to_agent.get(intent)
        if not agent_name:
            logger.info(f"No valid agent found for intent: {intent}")
            return None

        logger.info(f"Routing to agent: '{agent_name}'")
        return self.sub_agents.get(agent_name)

    def process(self, message: Message) -> Message:
        """
        Processes the incoming message, determines intent, routes to the appropriate sub-agent,
        and returns a consolidated response. Now includes conversation memory management.
        """
        logger.info(f"{self.name} processing message: '{message.content}'")

        try:
            query = message.content

            # Determine the customer's intent and extract entities
            intent, entities = self.determine_intent(query)

            # Route to the appropriate sub-agent
            sub_agent = self.route_to_agent(intent)
            if intent == Intent.UNKNOWN and sub_agent is None:
                # Record the interaction even for unknown intents
                self.conversation_memory.add_interaction(
                    intent=intent.name, query=query, entities=entities, agent_used="None", key_info={}
                )

                # Generate LLM response for UNKNOWN intent with conversation context
                return self._generate_unknown_intent_response(query)

            summary = ""
            past_conversation_context = self._get_conversation_context_string(query)
            if sub_agent is not None:
                # Create message with entities in metadata
                sub_message = Message(
                    content=query,
                    sender=self.name,
                    recipient=sub_agent.name,
                    metadata={"intent": intent.name, "entities": entities},
                )
                logger.info(f"Delegating message to '{sub_agent.name}' with entities: {entities}")

                # Get the response from the sub-agent
                sub_response = sub_agent.process(sub_message)
                summary = sub_response.content

                # Extract key information from the response for conversation memory
                key_info = self._extract_key_info_from_response(intent, sub_response, entities)

                # Record the interaction in conversation memory
                self.conversation_memory.add_interaction(
                    intent=intent.name, query=query, entities=entities, agent_used=sub_agent.name, key_info=key_info
                )

            # Consolidate the final response with Adventure Outfitters branding
            template = self.template_manager.create_template("coordinator", "consolidate")
            system_instructions = self.template_manager.fill_template(
                template.get("system", ""), query=query, summary=summary, intent=intent.name
            )
            user_instructions = self.template_manager.fill_template(
                template.get("user", ""), query=query, summary=summary
            )

            user_instructions += past_conversation_context

            logger.info("Generating final response for the customer.")

            messages = [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_instructions},
            ]

            response = self.llm_adapter.chat(messages)

            if response.get("success"):
                consolidated_response = response["content"].strip()
                
                # Apply supervisor guardrails
                supervisor_template = self.template_manager.create_template("coordinator", "supervisor")
                supervisor_system = self.template_manager.fill_template(
                    supervisor_template.get("system", ""), query=query, consolidated_response=consolidated_response
                )
                supervisor_user = self.template_manager.fill_template(
                    supervisor_template.get("user", ""), query=query, consolidated_response=consolidated_response
                )
                
                supervisor_messages = [
                    {"role": "system", "content": supervisor_system},
                    {"role": "user", "content": supervisor_user},
                ]
                
                supervisor_response = self.llm_adapter.chat(supervisor_messages)
                
                if supervisor_response.get("success"):
                    final_response_text = supervisor_response["content"].strip()
                else:
                    logger.error(f"Supervisor failed, using consolidated response: {supervisor_response.get('error')}")
                    final_response_text = consolidated_response
                    
                return Message(content=final_response_text, sender=self.name, recipient="Customer")
            else:
                logger.error(f"Final response generation failed: {response.get('error')}")
                error_msg = (
                    "🏔️ I encountered an issue while processing your request. "
                    "Please try again! Onward into the unknown! 🌟"
                )
                return Message(
                    content=error_msg,
                    sender=self.name,
                    recipient="Customer",
                )

        except Exception as e:
            import traceback

            traceback.print_exc()
            logger.error(f"Unexpected error during processing: {e.with_traceback(e.__traceback__)}")
            error_msg = (
                "🏔️ I encountered an error while processing your request. "
                "Please try again later! Onward into the unknown! 🌟"
            )
            return Message(
                content=error_msg,
                sender=self.name,
                recipient="Customer",
            )

    def _extract_key_info_from_response(self, intent: Intent, sub_response: Message, entities: dict) -> dict:
        """
        Extract key information from the sub-agent response for conversation memory.

        Args:
            intent (Intent): The detected intent
            sub_response (Message): Response from the sub-agent
            entities (dict): Extracted entities

        Returns:
            dict: Key information to store in conversation memory
        """
        try:
            key_info = {}
            response_content = sub_response.content.lower()

            if intent == Intent.ORDER_STATUS:
                # Extract order information from the response
                import re

                # Look for order number
                order_match = re.search(r"#(W\d+)", sub_response.content)
                if order_match:
                    key_info["order_number"] = f"#{order_match.group(1)}"

                # Look for customer name
                name_match = re.search(r"hello ([^!]+)!", sub_response.content, re.IGNORECASE)
                if name_match:
                    key_info["customer_name"] = name_match.group(1).strip()

                # Look for products (SKUs)
                product_matches = re.findall(r"(SO[A-Z]{2}\d+)", sub_response.content)
                if product_matches:
                    key_info["products"] = product_matches

                # Look for status
                if "delivered" in response_content:
                    key_info["status"] = "delivered"
                elif "fulfilled" in response_content:
                    key_info["status"] = "fulfilled"
                elif "in-transit" in response_content:
                    key_info["status"] = "in-transit"
                elif "error" in response_content:
                    key_info["status"] = "error"

            elif intent == Intent.PRODUCT_RECOMMENDATION:
                # Extract mentioned products from product recommendations
                import re

                product_matches = re.findall(r"(SO[A-Z]{2}\d+)", sub_response.content)
                if product_matches:
                    key_info["products_mentioned"] = product_matches

            elif intent == Intent.EARLY_RISERS_PROMOTION:
                # Extract promo code if generated
                import re

                promo_match = re.search(r"EARLY\d+[A-Z0-9]+", sub_response.content)
                if promo_match:
                    key_info["promo_code"] = promo_match.group()

            if entities:
                key_info["entities"] = entities

            return key_info

        except Exception as e:
            logger.error(f"Error extracting key info from response: {e}")
            return {}

    def _get_conversation_context_string(self, query: str) -> str:
        """
        Add context information to the user instructions.
        """
        context_info = self.conversation_memory.get_contextual_info(query)
        if context_info:
            logger.info(f"Using conversation context: {context_info}")
            context_summary = self._format_context_for_llm(context_info)
            return f"\n<Past Conversation Context>:{context_summary}</Past Conversation Context>"
        return ""
