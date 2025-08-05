#!/usr/bin/env python3
"""
Adventure Outfitters Order Status Demo

This demo showcases the order status functionality including:
- Email-first order lookup flow
- Complete order lookup with both email and order number
- Multi-step conversation handling
- Entity extraction and state management
"""

from src.pipeline import AdventureOutfittersPipeline

def main():
    print("🏔️ Adventure Outfitters Order Status Demo 🏔️")
    print("=" * 60)
    print("Demonstrating order lookup capabilities with conversation state management\n")
    
    pipeline = AdventureOutfittersPipeline()
    
    print("📋 SCENARIO 1: Email-First Order Lookup")
    print("-" * 40)
    
    # Step 1: User provides just email
    print("\n👤 User: john.doe@example.com")
    response1 = pipeline.process_query("john.doe@example.com")
    print(f"🤖 Adventure Outfitters: {response1}")
    
    # Step 2: User provides order number
    print("\n👤 User: #W001")
    response2 = pipeline.process_query("#W001")
    print(f"🤖 Adventure Outfitters: {response2}")
    
    print("\n" + "=" * 60)
    print("📋 SCENARIO 2: Complete Order Lookup")
    print("-" * 40)
    
    # Reset for new conversation
    pipeline = AdventureOutfittersPipeline()
    
    # Complete order lookup in one query
    print("\n👤 User: Check order #W002 for jane.smith@example.com")
    response3 = pipeline.process_query("Check order #W002 for jane.smith@example.com")
    print(f"🤖 Adventure Outfitters: {response3}")
    
    print("\n" + "=" * 60)
    print("📋 SCENARIO 3: Error Handling")
    print("-" * 40)
    
    # Test with non-existent order
    print("\n👤 User: Check order #W999 for nonexistent@example.com")
    response4 = pipeline.process_query("Check order #W999 for nonexistent@example.com")
    print(f"🤖 Adventure Outfitters: {response4}")
    
    print("\n" + "=" * 60)
    print("📋 SCENARIO 4: Different Order Statuses")
    print("-" * 40)
    
    # Test different order statuses
    test_cases = [
        ("ethan.harris@example.com", "#W007", "Fulfilled"),
        ("diana.evans@example.com", "#W006", "In-Transit"),
        ("bob.brown@example.com", "#W004", "Error")
    ]
    
    for email, order, expected_status in test_cases:
        pipeline = AdventureOutfittersPipeline()  # Fresh instance
        print(f"\n👤 User: Check order {order} for {email}")
        response = pipeline.process_query(f"Check order {order} for {email}")
        print(f"🤖 Adventure Outfitters: {response[:200]}...")
        print(f"   Expected Status: {expected_status}")
    
    print("\n✅ Order Status Demo Complete!")
    print("🏔️ All order lookup scenarios demonstrated successfully! 🌟")

if __name__ == "__main__":
    main()
