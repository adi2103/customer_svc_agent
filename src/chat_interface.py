#!/usr/bin/env python3
"""
Adventure Outfitters Customer Service Chat Interface
Interactive chat loop for customers to communicate with the Adventure Outfitters agent.
"""

import os
import sys
import uuid

from src.common.logging import logger
from src.constants import CHAT_HELP_COMMANDS, CHAT_QUIT_COMMANDS
from src.pipeline import AdventureOutfittersPipeline


class ChatInterface:
    """
    Interactive chat interface for Adventure Outfitters customer service.
    """

    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.pipeline = AdventureOutfittersPipeline(self.session_id)
        self.session_active = True

    def display_welcome(self):
        """Display welcome message and instructions."""
        print("\n" + "=" * 70)
        print("🏔️  WELCOME TO ADVENTURE OUTFITTERS CUSTOMER SERVICE  🏔️")
        print("=" * 70)
        print("🌟 Ready to help you gear up for your next adventure!")
        print("🎒 Ask about order status or product recommendations")
        print("\nType 'quit', 'exit', or 'bye' to end the conversation")
        print("Type 'help' for assistance")
        print("=" * 70)
        print("Onward into the unknown! 🌟\n")

    def display_help(self):
        """Display help information."""
        print("\n🏔️ ADVENTURE OUTFITTERS HELP 🏔️")
        print("-" * 40)
        print("I can help you with:")
        print("📦 Order Status: 'Check my order #W001 for john.doe@example.com'")
        print("🎒 Product Recommendations: 'I need a hiking backpack'")
        print("\nCommands:")
        print("• 'quit', 'exit', 'bye' - End conversation")
        print("• 'help' - Show this help message")
        print("-" * 40)

    def get_user_input(self) -> str:
        """Get input from the user with a branded prompt."""
        try:
            return input("You: ").strip()
        except KeyboardInterrupt:
            print("\n\n🏔️ Thanks for visiting Adventure Outfitters! Onward into the unknown! 🌟")
            sys.exit(0)
        except EOFError:
            return "quit"

    def should_quit(self, user_input: str) -> bool:
        """Check if user wants to quit the conversation."""
        return user_input.lower() in CHAT_QUIT_COMMANDS

    def process_special_commands(self, user_input: str) -> bool:
        """Process special commands like help. Returns True if command was processed."""
        if user_input.lower() in CHAT_HELP_COMMANDS:
            self.display_help()
            return True
        return False

    def run(self):
        """Run the interactive chat interface."""
        self.display_welcome()

        while self.session_active:
            try:
                user_input = self.get_user_input()

                # Handle empty input
                if not user_input:
                    print("🏔️ I'm here to help! Please ask me anything about Adventure Outfitters. 🌟\n")
                    continue

                # Check for quit commands
                if self.should_quit(user_input):
                    goodbye_msg = (
                        "\n🏔️ Thanks for choosing Adventure Outfitters! May your adventures "
                        "be epic! Onward into the unknown! 🌟\n"
                    )
                    print(goodbye_msg)
                    break

                # Process special commands
                if self.process_special_commands(user_input):
                    print()  # Add spacing after help
                    continue

                # Process the query through the agent pipeline
                print("\nAdventure Outfitters: ", end="", flush=True)
                response = self.pipeline.process_query(user_input)
                print(response)
                print()  # Add spacing after response

            except Exception as e:
                logger.error(f"Error in chat interface: {e}")
                print("🏔️ I encountered an unexpected error. Please try again! Onward into the unknown! 🌟\n")


def main():
    """Main entry point for the chat interface."""
    try:
        chat = ChatInterface()
        chat.run()
    except KeyboardInterrupt:
        print("\n\n🏔️ Thanks for visiting Adventure Outfitters! Onward into the unknown! 🌟")
    except Exception as e:
        logger.error(f"Fatal error in chat interface: {e}")
        print(f"🏔️ A critical error occurred: {e}")
        print("Please contact our support team. Onward into the unknown! 🌟")


if __name__ == "__main__":
    main()
