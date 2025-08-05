import json
import re

from src.agents.agent import Agent
from src.common.message import Message
from src.common.logging import logger
from src.memory.manage import StateManager
from src.common.io import load_json


class OrderStatusAgent(Agent):
    """
    Agent responsible for handling order status and tracking queries.
    """

    def __init__(self, name: str, session_id: str):
        super().__init__(name, session_id)
        self.orders_data = load_json("./data/customer_orders.json") or []
        self.state_manager = StateManager()

    def find_order(self, email: str, order_number: str) -> dict:
        """
        Find an order by email and order number.
        """
        for order in self.orders_data:
            if order.get("Email", "").lower() == email.lower() and order.get("OrderNumber", "") == order_number:
                return order
        return None

    def extract_email_from_text(self, text: str) -> str:
        """
        Extract email address from text using regex.
        """
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        match = re.search(email_pattern, text)
        return match.group() if match else None

    def extract_order_number_from_text(self, text: str) -> str:
        """
        Extract order number from text using regex.
        Handles both #W001 and W001 formats.
        """
        # Try with # prefix first
        order_pattern = r"#W\d+"
        match = re.search(order_pattern, text)
        if match:
            return match.group()

        # Try without # prefix, but ensure it starts with W and has digits
        order_pattern = r"\bW\d+\b"
        match = re.search(order_pattern, text)
        if match:
            return "#" + match.group()  # Add # prefix for consistency

        return None

    def extract_order_info(self, query: str) -> tuple:
        """
        Extract email and order number from the query using LLM.
        """
        try:
            template = self.template_manager.create_template("delegate", "order_extraction")
            system_instructions = template.get("system", "")
            user_instructions = self.template_manager.fill_template(template.get("user", ""), query=query)

            messages = [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_instructions},
            ]

            response = self.llm_adapter.chat(messages)

            if response.get("success"):
                try:
                    response_text = response["content"]
                    # Try to parse JSON response
                    if response_text.startswith("{") and response_text.endswith("}"):
                        out_dict = json.loads(response_text)
                    else:
                        # Extract JSON from response if wrapped
                        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
                        if json_match:
                            out_dict = json.loads(json_match.group())
                        else:
                            return None, None

                    email = out_dict.get("email")
                    order_number = out_dict.get("order_number")
                    return email, order_number

                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Error parsing order extraction response: {e}")
                    return None, None
            else:
                logger.error(f"Order extraction failed: {response.get('error')}")
                return None, None

        except Exception as e:
            logger.error(f"Error extracting order info: {e}")
            return None, None

    def _generate_order_response(self, email: str, order_number: str) -> Message:
        """
        Generate order status response message.
        """
        order = self.find_order(email, order_number)

        if not order:
            # Don't clear state when order not found - user might want to try again
            not_found_msg = (
                f"🏔️ I couldn't find order **{order_number}** for `{email}` in our system. "
                f"\n\nCould you double-check your order number? Our order numbers typically "
                f"look like #W001, #W002, etc. You can also try a different email if you "
                f"used multiple addresses.\n\nOnward into the unknown! 🌟"
            )
            return Message(
                content=not_found_msg,
                sender=self.name,
                recipient="AdventureOutfittersAgent",
            )

        # Clear state only on successful order lookup
        self.state_manager.clear_state()

        # Generate order status response
        status = order.get("Status", "unknown")
        tracking_number = order.get("TrackingNumber")
        customer_name = order.get("CustomerName", "valued customer")
        products = order.get("ProductsOrdered", [])

        # Create tracking link if tracking number exists
        tracking_info = ""
        if tracking_number:
            tracking_link = f"https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking_number}"
            tracking_info = f"\n📦 Track your package: {tracking_link}"

        status_message = f"🏔️ Hello {customer_name}! Here's your order status:\n\n"
        status_message += f"📋 Order: {order_number}\n"
        status_message += f"📧 Email: {email}\n"
        status_message += f"🎒 Products: {', '.join(products)}\n"
        status_message += f"📊 Status: {status.title()}\n"

        if tracking_number:
            status_message += f"🚚 Tracking: {tracking_number}"
            status_message += tracking_info

        status_message += "\n\n🌟 Thanks for choosing Adventure Outfitters! Onward into the unknown! 🏔️"

        return Message(content=status_message, sender=self.name, recipient="AdventureOutfittersAgent")

    def process(self, message: Message) -> Message:
        """
        Processes order status queries with conversation context support using StateManager.
        """
        logger.info(f"{self.name} processing message: '{message.content}'")
        query = message.content

        try:
            # Get entities from coordinator metadata if available
            entities = message.metadata.get("entities", {})
            email_from_entities = entities.get("Email")
            order_from_entities = entities.get("OrderNumber")

            # Also extract from text as fallback
            email_from_text = self.extract_email_from_text(query)
            order_from_text = self.extract_order_number_from_text(query)

            # Prefer entities from coordinator, fallback to text extraction
            email_from_current = email_from_entities or email_from_text
            order_from_current = order_from_entities or order_from_text

            # Get stored values from state
            stored_email = self.state_manager.get_value("email")
            stored_order = self.state_manager.get_value("order_number")

            # Check if user provided both email and order number in one message
            if email_from_current and order_from_current:
                return self._generate_order_response(email_from_current, order_from_current)

            # If we have stored email and user provides order number
            if stored_email and order_from_current:
                return self._generate_order_response(stored_email, order_from_current)

            # If we have stored order and user provides email
            if stored_order and email_from_current:
                return self._generate_order_response(email_from_current, stored_order)

            # If user provides just an email (and it looks like a standalone email)
            if email_from_current and not order_from_current and "@" in query and len(query.split()) == 1:
                self.state_manager.add_entry("email", email_from_current)
                email_msg = (
                    f"🏔️ Got it! I have your email: {email_from_current}. Now I need "
                    f"your order number (like #W001, #W002, etc.) to find your gear! 🌟"
                )
                return Message(
                    content=email_msg,
                    sender=self.name,
                    recipient="AdventureOutfittersAgent",
                )

            # If user provides just an order number
            if order_from_current and not email_from_current:
                self.state_manager.add_entry("order_number", order_from_current)
                order_msg = (
                    f"🏔️ Perfect! I have your order number: {order_from_current}. "
                    f"Now I need the email address associated with this order. 🌟"
                )
                return Message(
                    content=order_msg,
                    sender=self.name,
                    recipient="AdventureOutfittersAgent",
                )

            # Handle case where we have stored email but user provides invalid order format
            if stored_email and not order_from_current and not email_from_current:
                # Check if the input might be an attempted order number but in wrong format
                if query.strip().isdigit() or any(char.isdigit() for char in query):
                    invalid_order_msg = (
                        f"🏔️ I have your email ({stored_email}) but that doesn't look like "
                        f"one of our order numbers. Our order numbers start with 'W' and look "
                        f"like #W001, #W002, etc. Could you check your order confirmation email "
                        f"for the correct format? 🌟"
                    )
                    return Message(
                        content=invalid_order_msg,
                        sender=self.name,
                        recipient="AdventureOutfittersAgent",
                    )

            # Handle case where we have stored order but user provides something that's not an email
            if stored_order and not email_from_current and not order_from_current:
                email_needed_msg = (
                    f"🏔️ I have your order number ({stored_order}) but I need a valid "
                    f"email address to look up your order. Could you provide the email "
                    f"you used when placing the order? 🌟"
                )
                return Message(
                    content=email_needed_msg,
                    sender=self.name,
                    recipient="AdventureOutfittersAgent",
                )

            # Try to extract both from current query using LLM as fallback
            if not email_from_current and not order_from_current:
                email, order_number = self.extract_order_info(query)
                email_from_current = email_from_current or email
                order_from_current = order_from_current or order_number

            # Use stored values if current extraction failed
            final_email = email_from_current or stored_email
            final_order = order_from_current or stored_order

            # If we have both pieces of information, process the order
            if final_email and final_order:
                return self._generate_order_response(final_email, final_order)

            # If we still don't have both pieces of information
            missing_info = []
            if not final_email:
                missing_info.append("email address")
            if not final_order:
                missing_info.append("order number")

            if len(missing_info) == 2:
                instructions_msg = (
                    "🏔️ To check your order status, I need your email address and order "
                    "number. You can say something like: 'Check order #W001 for "
                    "john.doe@example.com' 🌟"
                )
                return Message(
                    content=instructions_msg,
                    sender=self.name,
                    recipient="AdventureOutfittersAgent",
                )
            elif "email address" in missing_info:
                missing_email_msg = (
                    f"🏔️ I have your order number ({final_order}) but I still need "
                    f"your email address. What email did you use for this order? 🌟"
                )
                return Message(
                    content=missing_email_msg,
                    sender=self.name,
                    recipient="AdventureOutfittersAgent",
                )
            else:
                missing_order_msg = (
                    f"🏔️ I have your email ({final_email}) but I still need your "
                    f"order number. What's your order number? 🌟"
                )
                return Message(
                    content=missing_order_msg,
                    sender=self.name,
                    recipient="AdventureOutfittersAgent",
                )

        except Exception as e:
            logger.error(f"Error in OrderStatusAgent: {e}")
            lookup_error_msg = (
                "🏔️ I encountered an issue while looking up your order. Please try "
                "again or contact our support team. Onward into the unknown! 🌟"
            )
            return Message(
                content=lookup_error_msg,
                sender=self.name,
                recipient="AdventureOutfittersAgent",
            )
