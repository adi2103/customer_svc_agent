import json

from src.agents.agent import Agent
from src.common.message import Message
from src.common.logging import logger
from src.common.io import load_json


class ProductRecommendationAgent(Agent):
    """
    Agent responsible for handling product recommendation queries.
    """

    def __init__(self, name: str, session_id: str):
        super().__init__(name, session_id)
        self.products_data = load_json("./data/product_catalog.json") or []

    def search_products(self, query: str) -> list:
        """
        Search for products based on query keywords.
        """
        query_lower = query.lower()
        matching_products = []

        for product in self.products_data:
            # Search in product name, description, and tags
            product_text = (
                product.get("ProductName", "").lower()
                + " "
                + product.get("Description", "").lower()
                + " "
                + " ".join(product.get("Tags", [])).lower()
            )

            # Simple keyword matching
            query_words = query_lower.split()
            matches = sum(1 for word in query_words if word in product_text)

            if matches > 0:
                product["relevance_score"] = matches
                matching_products.append(product)

        # Sort by relevance score
        matching_products.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return matching_products[:5]  # Return top 5 matches

    def get_products_by_skus(self, skus: list) -> list:
        """
        Get specific products by their SKU codes.

        Args:
            skus (list): List of SKU codes to look up

        Returns:
            list: List of matching products
        """
        matching_products = []
        for product in self.products_data:
            if product.get("SKU") in skus:
                matching_products.append(product)
        return matching_products

    def process(self, message: Message) -> Message:
        """
        Processes product recommendation queries by searching the catalog.
        Now handles contextual queries about specific products from previous interactions
        and direct SKU lookups.
        """
        logger.info(f"{self.name} processing message: '{message.content}'")
        query = message.content

        try:
            # Check entities from coordinator
            entities = message.metadata.get("entities", {})
            referenced_products = entities.get("ReferencedProducts")
            direct_sku = entities.get("SKU")

            matching_products = []

            # Handle direct SKU lookup
            if direct_sku:
                logger.info(f"Handling direct SKU lookup: {direct_sku}")
                # Convert single SKU to list for consistent processing
                sku_list = [direct_sku] if isinstance(direct_sku, str) else direct_sku
                matching_products = self.get_products_by_skus(sku_list)

                if matching_products:
                    # Generate detailed information about the specific product
                    template = self.template_manager.create_template("delegate", "product_recommendation")
                    system_instructions = template.get("system", "")

                    # Prepare product information for the LLM
                    products_info = []
                    for product in matching_products:
                        product_info = {
                            "name": product.get("ProductName", ""),
                            "sku": product.get("SKU", ""),
                            "description": product.get("Description", ""),
                            "inventory": product.get("Inventory", 0),
                            "tags": product.get("Tags", []),
                        }
                        products_info.append(product_info)

                    # Modify the query to be more specific for SKU lookups
                    sku_query = (
                        f"The customer is asking about product with SKU {direct_sku}. "
                        f"Please provide detailed information about this specific product."
                    )

                    user_instructions = self.template_manager.fill_template(
                        template.get("user", ""), query=sku_query, products=json.dumps(products_info, indent=2)
                    )

                    messages = [
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": user_instructions},
                    ]

                    response = self.llm_adapter.chat(messages)

                    if response.get("success"):
                        recommendation_text = response["content"].strip()
                        return Message(content=recommendation_text, sender=self.name, recipient="AdventureOutfittersAgent")

            # Handle contextual queries about specific products
            if referenced_products and not matching_products:
                logger.info(f"Handling contextual query about products: {referenced_products}")
                matching_products = self.get_products_by_skus(referenced_products)

                if matching_products:
                    # Generate detailed information about the specific products
                    template = self.template_manager.create_template("delegate", "product_recommendation")
                    system_instructions = template.get("system", "")

                    # Prepare product information for the LLM with context
                    products_info = []
                    for product in matching_products:
                        product_info = {
                            "name": product.get("ProductName", ""),
                            "sku": product.get("SKU", ""),
                            "description": product.get("Description", ""),
                            "inventory": product.get("Inventory", 0),
                            "tags": product.get("Tags", []),
                        }
                        products_info.append(product_info)

                    # Modify the query to be more specific for contextual responses
                    contextual_query = (
                        f"The customer is asking about these specific products from their "
                        f"recent order or previous inquiry: {query}. Please provide "
                        f"detailed information about these products."
                    )

                    user_instructions = self.template_manager.fill_template(
                        template.get("user", ""), query=contextual_query, products=json.dumps(products_info, indent=2)
                    )

                    messages = [
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": user_instructions},
                    ]

                    response = self.llm_adapter.chat(messages)

                    if response.get("success"):
                        recommendation_text = response["content"].strip()
                        return Message(content=recommendation_text, sender=self.name, recipient="AdventureOutfittersAgent")

            # If no specific products found through SKU or contextual lookup, do regular search
            if not matching_products:
                matching_products = self.search_products(query)

            if not matching_products:
                no_products_msg = (
                    "🏔️ I couldn't find any products matching your request. Could you try "
                    "describing what type of outdoor gear you're looking for? We have "
                    "backpacks, skis, and other adventure essentials! Onward into the "
                    "unknown! 🌟"
                )
                return Message(
                    content=no_products_msg,
                    sender=self.name,
                    recipient="AdventureOutfittersAgent",
                )

            # Generate product recommendations using LLM
            template = self.template_manager.create_template("delegate", "product_recommendation")
            system_instructions = template.get("system", "")

            # Prepare product information for the LLM
            products_info = []
            for product in matching_products:
                product_info = {
                    "name": product.get("ProductName", ""),
                    "sku": product.get("SKU", ""),
                    "description": product.get("Description", ""),
                    "inventory": product.get("Inventory", 0),
                    "tags": product.get("Tags", []),
                }
                products_info.append(product_info)

            user_instructions = self.template_manager.fill_template(
                template.get("user", ""), query=query, products=json.dumps(products_info, indent=2)
            )

            messages = [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_instructions},
            ]

            response = self.llm_adapter.chat(messages)

            if response.get("success"):
                recommendation_text = response["content"].strip()
                return Message(content=recommendation_text, sender=self.name, recipient="AdventureOutfittersAgent")
            else:
                logger.error(f"Product recommendation generation failed: {response.get('error')}")

                # Fallback to simple product listing
                response_text = "🏔️ Here are some great products I found for you:\n\n"
                for i, product in enumerate(matching_products[:3], 1):
                    response_text += (
                        f"{i}. **{product.get('ProductName', 'Unknown Product')}** (SKU: {product.get('SKU', 'N/A')})\n"
                    )
                    response_text += f"   {product.get('Description', 'No description available')}\n"
                    response_text += f"   In Stock: {product.get('Inventory', 0)} units\n\n"

                response_text += "🌟 These products are perfect for your next adventure! Onward into the unknown! 🏔️"

                return Message(content=response_text, sender=self.name, recipient="AdventureOutfittersAgent")

        except Exception as e:
            logger.error(f"Error in ProductRecommendationAgent: {e}")
            search_error_msg = (
                "🏔️ I encountered an issue while searching for products. Please try "
                "again or browse our catalog directly. Onward into the unknown! 🌟"
            )
            return Message(
                content=search_error_msg,
                sender=self.name,
                recipient="AdventureOutfittersAgent",
            )
