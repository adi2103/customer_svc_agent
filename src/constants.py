"""
Constants for Adventure Outfitters Customer Service Agent
Centralizes magic strings, patterns, and configuration values.
"""

# Brand Constants
BRAND_NAME = "Adventure Outfitters"
BRAND_CATCHPHRASE = "Onward into the unknown!"
BRAND_EMOJI = "🏔️"
BRAND_STAR_EMOJI = "🌟"

# Early Risers Promotion
EARLY_RISERS_START_HOUR = 8
EARLY_RISERS_END_HOUR = 10
EARLY_RISERS_TIMEZONE = "US/Pacific"
EARLY_RISERS_DISCOUNT_PERCENT = 10

# Order Patterns
ORDER_NUMBER_PREFIX = "W"
ORDER_NUMBER_PATTERN = r"#?W\d{3,}"

# File Paths
DATA_DIR = "data"
CONFIG_DIR = "config"
LOGS_DIR = "logs"
TEMPLATES_DIR = "config/templates"

# Data Files
CUSTOMER_ORDERS_FILE = "data/customer_orders.json"
PRODUCT_CATALOG_FILE = "data/product_catalog.json"
PROMO_CODES_FILE = "data/promo_codes.json"

# Agent Names
COORDINATOR_AGENT = "AdventureOutfittersAgent"
ORDER_STATUS_AGENT = "OrderStatusAgent"
PRODUCT_RECOMMENDATION_AGENT = "ProductRecommendationAgent"
EARLY_RISERS_AGENT = "EarlyRisersPromotionAgent"


# Intent Names
class Intent:
    ORDER_STATUS = "ORDER_STATUS"
    PRODUCT_RECOMMENDATION = "PRODUCT_RECOMMENDATION"
    EARLY_RISERS_PROMOTION = "EARLY_RISERS_PROMOTION"
    WHO_ARE_YOU = "WHO_ARE_YOU"
    UNKNOWN = "UNKNOWN"


# Entity Keys
class EntityKeys:
    ORDER_NUMBER = "OrderNumber"
    EMAIL = "Email"
    PRODUCT_NAME = "ProductName"
    SKU = "SKU"
    REFERENCED_PRODUCTS = "ReferencedProducts"
    REFERENCED_ORDER = "ReferencedOrder"


# Error Messages
ERROR_MESSAGES = {
    "processing_error": (
        f"{BRAND_EMOJI} I encountered an issue while processing your request. "
        f"Please try again! {BRAND_CATCHPHRASE} {BRAND_STAR_EMOJI}"
    ),
    "unexpected_error": (
        f"{BRAND_EMOJI} I encountered an unexpected error. "
        f"Please try again or contact our support team. {BRAND_CATCHPHRASE} {BRAND_STAR_EMOJI}"
    ),
    "order_lookup_error": (
        f"{BRAND_EMOJI} I encountered an issue while looking up your order. "
        f"Please try again or contact our support team. {BRAND_CATCHPHRASE} {BRAND_STAR_EMOJI}"
    ),
    "product_search_error": (
        f"{BRAND_EMOJI} I encountered an issue while searching for products. "
        f"Please try again or browse our catalog directly. {BRAND_CATCHPHRASE} {BRAND_STAR_EMOJI}"
    ),
    "promo_code_error": (
        f"{BRAND_EMOJI} I encountered an issue while generating your Early Risers discount code. "
        f"Please try again! {BRAND_CATCHPHRASE} {BRAND_STAR_EMOJI}"
    ),
}

# Success Messages
SUCCESS_MESSAGES = {
    "order_found": f"{BRAND_STAR_EMOJI} Thanks for choosing {BRAND_NAME}! {BRAND_CATCHPHRASE} {BRAND_EMOJI}",
    "early_bird_thanks": (
        f"{BRAND_STAR_EMOJI} Thanks for being an early bird! "
        f"The mountains are calling, and you're ready to answer! {BRAND_CATCHPHRASE} {BRAND_EMOJI}"
    ),
}

# Chat Interface
CHAT_QUIT_COMMANDS = ["quit", "exit", "bye", "q"]
CHAT_HELP_COMMANDS = ["help", "h", "?"]

# LLM Configuration
DEFAULT_TEMPERATURE = 0.3
MAX_TOKENS = 1000
