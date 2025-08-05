"""
Test suite for Order Status conversation flows.
Tests various conversation patterns and context management scenarios.
"""

import unittest
from unittest.mock import patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pipeline import AdventureOutfittersPipeline


class TestOrderStatusFlows(unittest.TestCase):
    """Test order status conversation flows and context management."""
    
    def setUp(self):
        """Set up test pipeline for each test."""
        self.pipeline = AdventureOutfittersPipeline()
    
    def tearDown(self):
        """Clean up after each test."""
        # Reset any state between tests
        if hasattr(self.pipeline.adventure_outfitters_agent.sub_agents['OrderStatusAgent'], 'state_manager'):
            self.pipeline.adventure_outfitters_agent.sub_agents['OrderStatusAgent'].state_manager.clear_state()
    
    def test_email_first_then_valid_order(self):
        """Test: Email first, then valid order number."""
        # Step 1: Provide email
        response1 = self.pipeline.process_query('ethan.harris@example.com')
        
        # Assertions for step 1
        self.assertIn('ethan.harris@example.com', response1)
        self.assertIn('order number', response1.lower())
        self.assertIn('#W001', response1)  # Should show example format
        
        # Step 2: Provide valid order number
        response2 = self.pipeline.process_query('#W007')
        
        # Assertions for step 2
        self.assertIn('Ethan Harris', response2)
        self.assertIn('#W007', response2)
        self.assertIn('ethan.harris@example.com', response2)
        self.assertIn('Fulfilled', response2)
        self.assertIn('SOBP001', response2)
        self.assertIn('SOSB006', response2)
    
    def test_email_first_then_invalid_order_then_valid(self):
        """Test: Email first, invalid order number (maintains context), then valid order."""
        # Step 1: Provide email
        response1 = self.pipeline.process_query('ethan.harris@example.com')
        self.assertIn('ethan.harris@example.com', response1)
        
        # Step 2: Provide invalid order number
        response2 = self.pipeline.process_query('677623')
        
        # Assertions for step 2 - should maintain context
        self.assertIn('ethan.harris@example.com', response2)  # Should acknowledge stored email
        self.assertIn('677623', response2)  # Should mention the invalid number
        self.assertIn('#W001', response2)  # Should show correct format
        self.assertIn('start with', response2.lower())  # Should explain format
        
        # Step 3: Provide valid order number
        response3 = self.pipeline.process_query('#W007')
        
        # Assertions for step 3
        self.assertIn('Ethan Harris', response3)
        self.assertIn('Fulfilled', response3)
    
    def test_order_first_then_email(self):
        """Test: Order number first, then email."""
        # Step 1: Provide order number
        response1 = self.pipeline.process_query('#W005')
        
        # Assertions for step 1
        self.assertIn('#W005', response1)
        self.assertIn('email', response1.lower())
        
        # Step 2: Provide email
        response2 = self.pipeline.process_query('charlie.davis@example.com')
        
        # Assertions for step 2
        self.assertIn('Charlie Davis', response2)
        self.assertIn('#W005', response2)
        self.assertIn('charlie.davis@example.com', response2)
        self.assertIn('Delivered', response2)
        self.assertIn('SOBN008', response2)
        self.assertIn('TRK112233445', response2)
    
    def test_both_at_once(self):
        """Test: Both email and order number provided at once."""
        response = self.pipeline.process_query('Check order #W001 for john.doe@example.com')
        
        # Assertions
        self.assertIn('John Doe', response)
        self.assertIn('#W001', response)
        self.assertIn('john.doe@example.com', response)
        self.assertIn('Delivered', response)
        self.assertIn('SOBP001', response)
        self.assertIn('SOWB004', response)
        self.assertIn('TRK123456789', response)
    
    def test_order_not_found_maintains_context(self):
        """Test: Order not found but context is maintained."""
        # Step 1: Provide email
        response1 = self.pipeline.process_query('ethan.harris@example.com')
        self.assertIn('ethan.harris@example.com', response1)
        
        # Step 2: Provide non-existent order
        response2 = self.pipeline.process_query('#W999')
        
        # Assertions for step 2
        self.assertIn('ethan.harris@example.com', response2)  # Should maintain context
        self.assertIn('#W999', response2)  # Should mention the order number
        self.assertIn("couldn't find", response2.lower())  # Should indicate not found
        self.assertIn('double-check', response2.lower())  # Should suggest checking
    
    def test_invalid_email_format_with_stored_order(self):
        """Test: Invalid email format when order is already stored."""
        # Step 1: Provide order number
        response1 = self.pipeline.process_query('#W007')
        self.assertIn('#W007', response1)
        
        # Step 2: Provide invalid email format
        response2 = self.pipeline.process_query('not-an-email')
        
        # Assertions for step 2
        self.assertIn('#W007', response2)  # Should maintain stored order
        self.assertIn('email address', response2.lower())  # Should ask for valid email
    
    def test_general_order_inquiry(self):
        """Test: General order inquiry without specific details."""
        response = self.pipeline.process_query('order')
        
        # Assertions
        self.assertIn('email', response.lower())
        self.assertIn('order number', response.lower())
        self.assertIn('#W001', response)  # Should show example
    
    def test_mixed_case_email_and_order(self):
        """Test: Mixed case email and order number handling."""
        response = self.pipeline.process_query('Check order #w001 for JOHN.DOE@EXAMPLE.COM')
        
        # Should still find the order (case insensitive)
        self.assertIn('John Doe', response)
        self.assertIn('Delivered', response)
    
    def test_order_without_hash_prefix(self):
        """Test: Order number without # prefix gets normalized."""
        # Step 1: Provide email
        response1 = self.pipeline.process_query('john.doe@example.com')
        self.assertIn('john.doe@example.com', response1)
        
        # Step 2: Provide order without # prefix
        response2 = self.pipeline.process_query('W001')
        
        # Should still find the order
        self.assertIn('John Doe', response2)
        self.assertIn('#W001', response2)  # Should normalize to include #
        self.assertIn('Delivered', response2)
    
    def test_multiple_conversation_resets(self):
        """Test: Multiple conversation flows don't interfere with each other."""
        # First conversation
        response1 = self.pipeline.process_query('ethan.harris@example.com')
        response2 = self.pipeline.process_query('#W007')
        self.assertIn('Ethan Harris', response2)
        
        # Second conversation (should start fresh)
        response3 = self.pipeline.process_query('john.doe@example.com')
        response4 = self.pipeline.process_query('#W001')
        self.assertIn('John Doe', response4)
        self.assertNotIn('Ethan Harris', response4)  # Should not leak from previous conversation


class TestOrderStatusEdgeCases(unittest.TestCase):
    """Test edge cases and error scenarios for order status."""
    
    def setUp(self):
        """Set up test pipeline for each test."""
        self.pipeline = AdventureOutfittersPipeline()
    
    def tearDown(self):
        """Clean up after each test."""
        if hasattr(self.pipeline.adventure_outfitters_agent.sub_agents['OrderStatusAgent'], 'state_manager'):
            self.pipeline.adventure_outfitters_agent.sub_agents['OrderStatusAgent'].state_manager.clear_state()
    
    def test_empty_query(self):
        """Test: Empty or whitespace-only query."""
        response = self.pipeline.process_query('   ')
        
        # Should handle gracefully
        self.assertIn('🏔️', response)  # Should maintain brand voice
        self.assertTrue(len(response) > 0)  # Should provide some response
    
    def test_very_long_invalid_order_number(self):
        """Test: Very long invalid order number."""
        # Step 1: Provide email
        response1 = self.pipeline.process_query('test@example.com')
        
        # Step 2: Provide very long invalid order
        response2 = self.pipeline.process_query('123456789012345678901234567890')
        
        # Should handle gracefully and maintain context
        self.assertIn('test@example.com', response2)
        self.assertIn('order number', response2.lower())
    
    def test_special_characters_in_input(self):
        """Test: Special characters in input."""
        response = self.pipeline.process_query('order #@$%^&*()')
        
        # Should handle gracefully
        self.assertIn('🏔️', response)
        self.assertIn('email', response.lower())
    
    def test_multiple_emails_in_query(self):
        """Test: Multiple email addresses in single query."""
        response = self.pipeline.process_query('test1@example.com and test2@example.com')
        
        # Should extract one email or handle gracefully
        self.assertIn('🏔️', response)
        self.assertTrue('example.com' in response)


class TestOrderStatusResponseQuality(unittest.TestCase):
    """Test response quality and brand voice consistency."""
    
    def setUp(self):
        """Set up test pipeline for each test."""
        self.pipeline = AdventureOutfittersPipeline()
    
    def test_brand_voice_consistency(self):
        """Test: All responses maintain Adventure Outfitters brand voice."""
        test_queries = [
            'order',
            'ethan.harris@example.com',
            '#W007',
            'invalid-order-123',
            'Check order #W001 for john.doe@example.com'
        ]
        
        for query in test_queries:
            response = self.pipeline.process_query(query)
            
            # Should contain brand elements
            self.assertTrue(
                any(element in response for element in ['🏔️', '🌟', '🌲', 'Onward into the unknown']),
                f"Response for '{query}' lacks brand voice elements: {response}"
            )
    
    def test_response_length_reasonable(self):
        """Test: Responses are not too long or too short."""
        response = self.pipeline.process_query('Check order #W001 for john.doe@example.com')
        
        # Should be substantial but not excessive
        self.assertGreater(len(response), 50, "Response too short")
        self.assertLess(len(response), 1000, "Response too long")
    
    def test_no_technical_jargon(self):
        """Test: Responses don't contain technical jargon or error messages."""
        response = self.pipeline.process_query('invalid-input-12345')
        
        # Should not contain technical terms
        technical_terms = ['error', 'exception', 'null', 'none', 'debug', 'traceback']
        for term in technical_terms:
            self.assertNotIn(term.lower(), response.lower(), 
                           f"Response contains technical term '{term}': {response}")


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
