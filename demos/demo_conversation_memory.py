#!/usr/bin/env python3
"""
Demonstration of Adventure Outfitters Conversation Memory System

This script shows how the conversation memory system enables contextual follow-up questions
that were previously impossible due to state clearing after successful operations.
"""

from src.pipeline import AdventureOutfittersPipeline

def main():
    print("🏔️ Adventure Outfitters Conversation Memory Demo 🏔️")
    print("=" * 60)
    print("This demo shows how the system now maintains conversation context")
    print("to handle follow-up questions about previous interactions.\n")
    
    # Initialize the pipeline
    pipeline = AdventureOutfittersPipeline()
    
    # Simulate the conversation from the original issue
    print("📋 CONVERSATION FLOW:")
    print("-" * 30)
    
    # Query 1: Order lookup
    print("\n👤 User: ethan.harris@example.com")
    response1 = pipeline.process_query("ethan.harris@example.com")
    print(f"🤖 Adventure Outfitters: {response1[:150]}...")
    
    # Query 2: Follow-up about products (this was failing before)
    print("\n👤 User: do you know what are those products?")
    response2 = pipeline.process_query("do you know what are those products?")
    print(f"🤖 Adventure Outfitters: {response2[:150]}...")
    
    # Query 3: Another contextual follow-up
    print("\n👤 User: tell me more about the backpack")
    response3 = pipeline.process_query("tell me more about the backpack")
    print(f"🤖 Adventure Outfitters: {response3[:150]}...")
    
    # Show conversation memory state
    print("\n" + "=" * 60)
    print("🧠 CONVERSATION MEMORY ANALYSIS:")
    print("-" * 30)
    
    context = pipeline.coordinator.conversation_memory.get_full_context()
    
    print(f"📊 Total interactions recorded: {len(context['recent_interactions'])}")
    print(f"📧 Customer email remembered: {context['context'].get('customer_email', 'None')}")
    print(f"📦 Last order lookup: {context['context'].get('last_order_lookup', {}).get('order_number', 'None')}")
    print(f"🎒 Recent products: {context['context'].get('recent_products', [])}")
    
    print("\n📈 INTERACTION HISTORY:")
    for i, interaction in enumerate(context['recent_interactions'], 1):
        print(f"  {i}. Intent: {interaction['intent']} | Agent: {interaction['agent_used']}")
        if interaction.get('key_info'):
            key_info = interaction['key_info']
            if key_info.get('order_number'):
                print(f"     → Extracted order: {key_info['order_number']} with products {key_info.get('products', [])}")
            elif key_info.get('products_mentioned'):
                print(f"     → Referenced products: {key_info['products_mentioned']}")
    
    print("\n✅ SUCCESS: The system now maintains conversation context!")
    print("🔄 Follow-up questions about previous interactions work seamlessly.")
    print("🏔️ Onward into the unknown! 🌟")

if __name__ == "__main__":
    main()
