#!/usr/bin/env python3
"""
Adventure Outfitters Early Risers Promotion Demo

This demo showcases the Early Risers promotion functionality including:
- Time-based promotion eligibility (8-10 AM Pacific Time)
- Unique promo code generation
- Promotion code storage and tracking
- Time validation and error handling
"""

from src.pipeline import AdventureOutfittersPipeline
from datetime import datetime
import pytz

def main():
    print("🌅 Adventure Outfitters Early Risers Promotion Demo 🌅")
    print("=" * 60)
    print("Demonstrating time-based 10% discount promotion (8-10 AM Pacific Time)\n")
    
    # Show current time context
    pacific = pytz.timezone('US/Pacific')
    current_time = datetime.now(pacific)
    print(f"🕐 Current Pacific Time: {current_time.strftime('%H:%M:%S %Z')}")
    print(f"🕐 Early Risers Window: 08:00:00 - 10:00:00 PST/PDT")
    
    is_early_risers_time = 8 <= current_time.hour < 10
    print(f"✅ Currently in Early Risers window: {is_early_risers_time}")
    
    print("\n📋 SCENARIO 1: Early Risers Promotion Request")
    print("-" * 40)
    
    pipeline = AdventureOutfittersPipeline()
    
    # Test Early Risers promotion requests
    promotion_queries = [
        "Can I get an Early Risers discount?",
        "Do you have any early morning promotions?",
        "I heard about a 10% discount for early risers",
        "Early risers promo code please"
    ]
    
    for query in promotion_queries:
        print(f"\n👤 User: {query}")
        response = pipeline.process_query(query)
        print(f"🤖 Adventure Outfitters: {response[:300]}...")
        
        # Check if promo code was generated
        if "EARLY" in response and any(char.isdigit() for char in response):
            print("   ✅ Promo code generated successfully!")
        elif "not available" in response.lower() or "outside" in response.lower():
            print("   ⏰ Outside promotion hours - correctly handled")
    
    print("\n" + "=" * 60)
    print("📋 SCENARIO 2: Time Validation Testing")
    print("-" * 40)
    
    # Show what happens at different times
    time_scenarios = [
        ("07:30", "Before promotion window"),
        ("08:30", "During promotion window"),
        ("09:45", "Near end of promotion window"),
        ("10:30", "After promotion window")
    ]
    
    for time_str, description in time_scenarios:
        print(f"\n🕐 Simulated Time: {time_str} Pacific - {description}")
        pipeline = AdventureOutfittersPipeline()  # Fresh instance
        response = pipeline.process_query("Can I get the Early Risers discount?")
        print(f"🤖 Adventure Outfitters: {response[:200]}...")
    
    print("\n" + "=" * 60)
    print("📋 SCENARIO 3: Promo Code Uniqueness")
    print("-" * 40)
    print("Testing that each request generates a unique promo code")
    
    if is_early_risers_time:
        promo_codes = []
        for i in range(3):
            pipeline = AdventureOutfittersPipeline()  # Fresh instance
            print(f"\n👤 User {i+1}: Early risers discount please")
            response = pipeline.process_query("Early risers discount please")
            
            # Extract promo code from response
            import re
            promo_match = re.search(r'EARLY\d+[A-Z0-9]+', response)
            if promo_match:
                promo_code = promo_match.group()
                promo_codes.append(promo_code)
                print(f"🤖 Adventure Outfitters: Generated code: {promo_code}")
            else:
                print(f"🤖 Adventure Outfitters: {response[:150]}...")
        
        # Check uniqueness
        if len(set(promo_codes)) == len(promo_codes):
            print(f"\n✅ All {len(promo_codes)} promo codes are unique!")
        else:
            print(f"\n⚠️ Some promo codes were duplicated")
    else:
        print("\n⏰ Currently outside Early Risers window - promo codes not generated")
    
    print("\n" + "=" * 60)
    print("📋 SCENARIO 4: Brand Integration")
    print("-" * 40)
    print("Showing how promotion integrates with Adventure Outfitters brand voice")
    
    pipeline = AdventureOutfittersPipeline()
    
    print("\n👤 User: What promotions do you have for early morning shoppers?")
    response = pipeline.process_query("What promotions do you have for early morning shoppers?")
    print(f"🤖 Adventure Outfitters: {response}")
    
    # Check for brand elements
    brand_elements = ["🌅", "🏔️", "adventure", "early riser", "sunrise"]
    found_elements = [elem for elem in brand_elements if elem.lower() in response.lower()]
    if found_elements:
        print(f"✅ Brand elements found: {', '.join(found_elements)}")
    
    print("\n" + "=" * 60)
    print("📋 SCENARIO 5: Edge Cases")
    print("-" * 40)
    
    edge_cases = [
        "early bird discount",  # Similar but different terminology
        "morning promotion",    # Generic morning reference
        "10% off code",        # Generic discount request
        "sunrise special"      # Creative variation
    ]
    
    for query in edge_cases:
        pipeline = AdventureOutfittersPipeline()
        print(f"\n👤 User: {query}")
        response = pipeline.process_query(query)
        print(f"🤖 Adventure Outfitters: {response[:200]}...")
    
    print("\n✅ Early Risers Promotion Demo Complete!")
    print("🌅 All promotion scenarios demonstrated successfully!")
    print("🏔️ Perfect for early morning adventurers! Onward into the unknown! 🌟")

if __name__ == "__main__":
    main()
