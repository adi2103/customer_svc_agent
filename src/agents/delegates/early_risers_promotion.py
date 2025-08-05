import os
import uuid
from datetime import datetime

import pytz

from src.agents.agent import Agent
from src.common.message import Message
from src.common.logging import logger
from src.common.io import ensure_directory_exists, load_json, save_json


class EarlyRisersPromotionAgent(Agent):
    """
    Agent responsible for handling Early Risers promotion requests (8-10 AM Pacific Time).
    """

    def __init__(self, name: str, session_id: str):
        super().__init__(name, session_id)
        self.promo_db_path = "./data/promo_codes.json"
        self.promo_codes = self._load_promo_codes()

    def _load_promo_codes(self) -> dict:
        """
        Load existing promo codes from the database.
        """
        if os.path.exists(self.promo_db_path):
            return load_json(self.promo_db_path) or {}
        return {}

    def _save_promo_codes(self):
        """
        Save promo codes to the database.
        """
        ensure_directory_exists(os.path.dirname(self.promo_db_path))
        save_json(self.promo_db_path, self.promo_codes)

    def is_early_risers_time(self) -> bool:
        """
        Check if current time is within Early Risers promotion hours (8-10 AM Pacific).
        """
        pacific = pytz.timezone("US/Pacific")
        current_time = datetime.now(pacific)
        current_hour = current_time.hour

        # Early Risers promotion is active from 8:00 AM to 10:00 AM Pacific
        return 7 <= current_hour < 10

    def generate_promo_code(self) -> str:
        """
        Generate a unique promo code for the customer.
        """
        # Create a unique code using date and UUID
        timestamp_date = datetime.now().strftime("%Y%m%d")

        # Check if the customer has already used a code today
        if self.session_id in self.promo_codes:
            return self.promo_codes[self.session_id]["promo_code"]

        unique_id = str(uuid.uuid4())[:8].upper()
        promo_code = f"EARLY{timestamp_date}{unique_id}"

        # Store the promo code
        self.promo_codes[self.session_id] = {
            "promo_code": promo_code,
            "generated_at": datetime.now().isoformat(),
        }

        self._save_promo_codes()
        return promo_code

    def process(self, message: Message) -> Message:
        """
        Processes Early Risers promotion requests.
        """
        logger.info(f"{self.name} processing message: '{message.content}'")
        query = message.content

        try:
            # Check if it's Early Risers time
            if not self.is_early_risers_time():
                pacific = pytz.timezone("US/Pacific")
                current_time = datetime.now(pacific)
                current_hour = current_time.hour

                time_msg = (
                    f"🏔️ The Early Risers promotion is only available from 8:00 AM to "
                    f"10:00 AM Pacific Time! It's currently {current_hour:02d}:"
                    f"{current_time.minute:02d} Pacific. Rise early tomorrow to catch "
                    f"this amazing 10% discount! Onward into the unknown! 🌅"
                )
                return Message(
                    content=time_msg,
                    sender=self.name,
                    recipient="AdventureOutfittersAgent",
                )

            # Generate unique promo code
            promo_code = self.generate_promo_code()

            pacific = pytz.timezone("US/Pacific")
            current_time = datetime.now(pacific)

            response_text = (
                f"🌅 Good morning, early riser! You're up bright and early at "
                f"{current_time.strftime('%I:%M %p')} Pacific Time! 🏔️\n\n"
            )
            response_text += f"🎉 Here's your exclusive Early Risers 10% discount code:\n\n"
            response_text += f"**{promo_code}**\n\n"
            response_text += (
                f"✨ This code gives you 10% off your entire order! Use it at checkout before it expires.\n\n"
            )
            response_text += (
                f"🌟 Thanks for being an early bird! The mountains are calling, and "
                f"you're ready to answer! Onward into the unknown! 🏔️"
            )

            logger.info(f"Generated promo code {promo_code} for session {self.session_id}")

            return Message(content=response_text, sender=self.name, recipient="AdventureOutfittersAgent")

        except Exception as e:
            logger.error(f"Error in EarlyRisersPromotionAgent: {e}")
            error_msg = (
                "🏔️ I encountered an issue while generating your Early Risers "
                "discount code. Please try again! Onward into the unknown! 🌟"
            )
            return Message(
                content=error_msg,
                sender=self.name,
                recipient="AdventureOutfittersAgent",
            )
