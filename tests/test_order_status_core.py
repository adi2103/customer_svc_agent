"""
Core test suite for Order Status functionality.
Focuses on essential conversation flows to avoid API rate limits.
"""

import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pipeline import AdventureOutfittersPipeline


class TestOrderStatusCore(unittest.TestCase):
    """Test core order status functionality."""
    
    def setUp(self):
        """Set up test pipeline for each test."""
        self.pipeline = AdventureOutfittersPipeline()
    
    def tearDown(self):
        """Clean up after each test."""
        # Reset any state between tests
        if hasattr(self.pipeline.adventure_outfitters_agent.sub_agents['OrderStatusAgent'], 'state_manager'):
            self.pipeline.adventure_outfitters_agent.sub_agents['OrderStatusAgent'].state_manager.clear_state()
    
    def test_complete_order_lookup_success(self):
        """Test: Complete order lookup with both email and order number."""
        response = self.pipeline.process_query('Check order #W001 for john.doe@example.com')
        
        # Assertions
        self.assertIn('John Doe', response)
        self.assertIn('#W001', response)
        self.assertIn('john.doe@example.com', response)
        self.assertIn('Delivered', response)
        self.assertIn('SOBP001', response)
        self.assertIn('SOWB004', response)
        self.assertIn('TRK123456789', response)
        self.assertIn('🏔️', response)  # Brand voice
    
    def test_email_then_order_flow(self):
        """Test: Email first, then order number flow."""
        # Step 1: Provide email
        response1 = self.pipeline.process_query('ethan.harris@example.com')
        
        # Should acknowledge email and ask for order
        self.assertIn('ethan.harris@example.com', response1)
        self.assertIn('order number', response1.lower())
        self.assertIn('🏔️', response1)
        
        # Step 2: Provide order number
        response2 = self.pipeline.process_query('#W007')
        
        # Should find the order
        self.assertIn('Ethan Harris', response2)
        self.assertIn('#W007', response2)
        self.assertIn('Fulfilled', response2)
    
    def test_invalid_order_maintains_context(self):
        """Test: Invalid order number maintains conversation context."""
        # Step 1: Provide email
        response1 = self.pipeline.process_query('ethan.harris@example.com')
        self.assertIn('ethan.harris@example.com', response1)
        
        # Step 2: Provide invalid order number
        response2 = self.pipeline.process_query('677623')
        
        # Should maintain context and explain the issue
        self.assertIn('ethan.harris@example.com', response2)  # Context maintained
        self.assertIn('677623', response2)  # Acknowledge invalid input
        self.assertIn('W001', response2)  # Show correct format
        self.assertIn('🏔️', response2)  # Brand voice
    
    def test_brand_voice_consistency(self):
        """Test: All responses maintain Adventure Outfitters brand voice."""
        test_queries = [
            'Check order #W001 for john.doe@example.com',
            'ethan.harris@example.com',
            'invalid-order-123'
        ]
        
        for query in test_queries:
            response = self.pipeline.process_query(query)
            
            # Should contain brand elements
            self.assertTrue(
                any(element in response for element in ['🏔️', '🌟', '🌲', 'Onward into the unknown']),
                f"Response for '{query}' lacks brand voice elements: {response[:100]}..."
            )
    
    def test_response_quality(self):
        """Test: Responses are of good quality."""
        response = self.pipeline.process_query('Check order #W001 for john.doe@example.com')
        
        # Should be substantial but not excessive
        self.assertGreater(len(response), 50, "Response too short")
        self.assertLess(len(response), 1000, "Response too long")
        
        # Should not contain technical terms
        technical_terms = ['error', 'exception', 'null', 'none', 'debug', 'traceback']
        for term in technical_terms:
            self.assertNotIn(term.lower(), response.lower(), 
                           f"Response contains technical term '{term}': {response}")


class TestOrderStatusRegression(unittest.TestCase):
    """Regression tests for previously fixed issues."""
    
    def setUp(self):
        """Set up test pipeline for each test."""
        self.pipeline = AdventureOutfittersPipeline()
    
    def tearDown(self):
        """Clean up after each test."""
        if hasattr(self.pipeline.adventure_outfitters_agent.sub_agents['OrderStatusAgent'], 'state_manager'):
            self.pipeline.adventure_outfitters_agent.sub_agents['OrderStatusAgent'].state_manager.clear_state()
    
    def test_context_not_lost_on_invalid_input(self):
        """Regression test: Context should not be lost when invalid input is provided."""
        # This was the original issue - system would restart flow on invalid input
        
        # Step 1: Provide email
        response1 = self.pipeline.process_query('ethan.harris@example.com')
        self.assertIn('ethan.harris@example.com', response1)
        
        # Step 2: Provide invalid order (this used to restart the flow)
        response2 = self.pipeline.process_query('677623')
        
        # CRITICAL: Should maintain context, not restart
        self.assertIn('ethan.harris@example.com', response2, 
                     "Context was lost! System restarted flow instead of maintaining conversation state.")
        
        # Should also explain the issue
        self.assertIn('677623', response2)
        self.assertTrue(
            any(phrase in response2.lower() for phrase in ['start with', 'w001', 'format']),
            "Should explain correct order number format"
        )
    
    def test_responses_less_redundant(self):
        """Regression test: Responses should be more focused, less redundant."""
        response = self.pipeline.process_query('Check order #W999 for test@example.com')
        
        # Should be focused, not overly verbose
        redundant_phrases = [
            'deep dive into the wilderness',
            'trail map didn\'t quite lead us',
            'making sure your pack is perfectly loaded'
        ]
        
        for phrase in redundant_phrases:
            self.assertNotIn(phrase.lower(), response.lower(),
                           f"Response contains redundant phrase: '{phrase}'")
        
        # Should still be helpful and maintain brand voice
        self.assertIn('🏔️', response)
        self.assertIn('couldn\'t find', response.lower())


if __name__ == '__main__':
    # Run core tests only
    unittest.main(verbosity=2)
