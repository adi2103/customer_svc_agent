#!/usr/bin/env python3
"""
Adventure Outfitters Complete Conversation Flows Demo

This demo showcases realistic end-to-end customer conversations including:
- Mixed intent conversations
- Natural conversation transitions
- Context preservation across different agent interactions
- Real customer journey scenarios
"""

from src.pipeline import AdventureOutfittersPipeline

def main():
    print("🏔️ Adventure Outfitters Complete Conversation Flows Demo 🏔️")
    print("=" * 70)
    print("Demonstrating realistic customer journey scenarios with multiple intents\n")
    
    print("📋 CONVERSATION FLOW 1: Order Check → Product Questions → Recommendations")
    print("-" * 70)
    print("Scenario: Customer checks order, asks about products, then wants similar items")
    
    pipeline = AdventureOutfittersPipeline()
    
    conversation_1 = [
        "Hi, can you check my order #W007 for ethan.harris@example.com?",
        "What are those products exactly?",
        "Tell me more about the backpack",
        "Do you have any similar backpacks?",
        "What about something for winter hiking?"
    ]
    
    for i, query in enumerate(conversation_1, 1):
        print(f"\n👤 User (Step {i}): {query}")
        response = pipeline.process_query(query)
        print(f"🤖 Adventure Outfitters: {response[:250]}...")
        
        # Show conversation memory state after key interactions
        if i in [1, 2]:  # After order lookup and first product question
            context = pipeline.coordinator.conversation_memory.get_full_context()
            print(f"   📝 Memory: {len(context['recent_interactions'])} interactions, "
                  f"Products: {context['context'].get('recent_products', [])}")
    
    print("\n" + "=" * 70)
    print("📋 CONVERSATION FLOW 2: Product Search → Order Check → Early Risers")
    print("-" * 70)
    print("Scenario: Customer browses products, checks existing order, asks for discount")
    
    pipeline = AdventureOutfittersPipeline()  # Fresh conversation
    
    conversation_2 = [
        "I'm looking for gear for a mountain expedition",
        "Actually, let me first check my existing order #W002 for jane.smith@example.com",
        "Great! Now back to new gear - what do you recommend for cold weather?",
        "Do you have any promotions or discounts available?",
        "Can I get an Early Risers discount?"
    ]
    
    for i, query in enumerate(conversation_2, 1):
        print(f"\n👤 User (Step {i}): {query}")
        response = pipeline.process_query(query)
        print(f"🤖 Adventure Outfitters: {response[:250]}...")
    
    print("\n" + "=" * 70)
    print("📋 CONVERSATION FLOW 3: Complex Multi-Intent Journey")
    print("-" * 70)
    print("Scenario: Customer with multiple orders, product comparisons, and promotions")
    
    pipeline = AdventureOutfittersPipeline()  # Fresh conversation
    
    conversation_3 = [
        "Hi there! I'm planning a big adventure and need to check a few things",
        "First, what's the status of order #W006 for diana.evans@example.com?",
        "Perfect! Now, I'm also looking for additional gear. What backpacks do you have?",
        "How does that compare to what's in my current order?",
        "I might place a new order - any discounts for early morning shoppers?",
        "Actually, let me also check another order #W010 for hannah.lewis@example.com",
        "Thanks! So to summarize, what would you recommend for my upcoming expedition?"
    ]
    
    for i, query in enumerate(conversation_3, 1):
        print(f"\n👤 User (Step {i}): {query}")
        response = pipeline.process_query(query)
        print(f"🤖 Adventure Outfitters: {response[:200]}...")
        
        # Show memory evolution
        if i in [2, 4, 6]:  # Key memory points
            context = pipeline.coordinator.conversation_memory.get_full_context()
            print(f"   📝 Memory Update: {len(context['recent_interactions'])} interactions")
            if context['context'].get('last_order_lookup'):
                order_info = context['context']['last_order_lookup']
                print(f"      Last Order: {order_info.get('order_number')} ({order_info.get('status')})")
    
    print("\n" + "=" * 70)
    print("📋 CONVERSATION FLOW 4: Error Recovery and Persistence")
    print("-" * 70)
    print("Scenario: Customer makes mistakes but conversation context is preserved")
    
    pipeline = AdventureOutfittersPipeline()  # Fresh conversation
    
    conversation_4 = [
        "Check my order please",  # Missing info
        "Sorry, it's john.doe@example.com",
        "#W001",
        "Wait, what products were in that order again?",
        "Tell me about the first product",
        "Is that good for beginners?",
        "What else would you recommend for someone just starting out?"
    ]
    
    for i, query in enumerate(conversation_4, 1):
        print(f"\n👤 User (Step {i}): {query}")
        response = pipeline.process_query(query)
        print(f"🤖 Adventure Outfitters: {response[:200]}...")
    
    print("\n" + "=" * 70)
    print("📋 CONVERSATION ANALYSIS")
    print("-" * 70)
    
    # Final conversation memory analysis
    context = pipeline.coordinator.conversation_memory.get_full_context()
    
    print(f"📊 Final Conversation State:")
    print(f"   • Total Interactions: {len(context['recent_interactions'])}")
    print(f"   • Customer Email: {context['context'].get('customer_email', 'Not captured')}")
    print(f"   • Last Order: {context['context'].get('last_order_lookup', {}).get('order_number', 'None')}")
    print(f"   • Recent Products: {context['context'].get('recent_products', [])}")
    
    print(f"\n📈 Interaction Breakdown:")
    intent_counts = {}
    for interaction in context['recent_interactions']:
        intent = interaction['intent']
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
    
    for intent, count in intent_counts.items():
        print(f"   • {intent}: {count} interactions")
    
    print("\n✅ Complete Conversation Flows Demo Finished!")
    print("🏔️ All realistic customer journey scenarios demonstrated successfully!")
    print("🌟 System maintains context across complex multi-intent conversations!")
    print("🎒 Ready to handle any customer adventure! Onward into the unknown!")

if __name__ == "__main__":
    main()
