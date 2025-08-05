The agent chat returns the same formatted response in all the cases. This can be improved to be more generic and dynamic.
- Is it possible?
- What are the best options to do that?
- let's compare and choose one which doesn't cause regression and hallucination but still provides better user experience and dynamic behavior for questions that are too general.

```
 python -m src.chat_interface
✅ Gemini provider initialized with gemini-2.5-flash
2025-08-05 17:17:00,992 [INFO] [agent] [/src/agents/agent.py]: Agent OrderStatusAgent initialized with shared resources.
✅ Gemini provider initialized with gemini-2.5-flash
2025-08-05 17:17:01,007 [INFO] [agent] [/src/agents/agent.py]: Agent ProductRecommendationAgent initialized with shared resources.
✅ Gemini provider initialized with gemini-2.5-flash
2025-08-05 17:17:01,021 [INFO] [agent] [/src/agents/agent.py]: Agent EarlyRisersPromotionAgent initialized with shared resources.
✅ Gemini provider initialized with gemini-2.5-flash
2025-08-05 17:17:01,034 [INFO] [agent] [/src/agents/agent.py]: Agent AdventureOutfittersAgent initialized with shared resources.
2025-08-05 17:17:01,035 [INFO] [coordinator] [/src/agents/coordinator.py]: AdventureOutfittersAgent initialized with 3 sub-agents.
2025-08-05 17:17:01,035 [INFO] [pipeline] [/src/pipeline.py]: Adventure Outfitters Pipeline initialized successfully

======================================================================
🏔️  WELCOME TO ADVENTURE OUTFITTERS CUSTOMER SERVICE  🏔️
======================================================================
🌟 Ready to help you gear up for your next adventure!
🎒 Ask about order status or product recommendations

Type 'quit', 'exit', or 'bye' to end the conversation
Type 'help' for assistance
======================================================================
Onward into the unknown! 🌟

You: who are you?

Adventure Outfitters: 2025-08-05 17:17:06,697 [INFO] [coordinator] [/src/agents/coordinator.py]: AdventureOutfittersAgent processing message: 'who are you?'
2025-08-05 17:17:06,703 [INFO] [coordinator] [/src/agents/coordinator.py]: Determining intent for query: 'who are you?'
2025-08-05 17:17:06,704 [INFO] [models] [/.venv/lib/python3.12/site-packages/google/genai/models.py]: AFC is enabled with max remote calls: 10.
2025-08-05 17:17:08,551 [INFO] [_client] [/.venv/lib/python3.12/site-packages/httpx/_client.py]: HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"
2025-08-05 17:17:08,552 [INFO] [models] [/.venv/lib/python3.12/site-packages/google/genai/models.py]: AFC remote call 1 is done.
2025-08-05 17:17:08,553 [INFO] [coordinator] [/src/agents/coordinator.py]: Determined intent: UNKNOWN
2025-08-05 17:17:08,553 [ERROR] [coordinator] [/src/agents/coordinator.py]: No valid agent found for intent: Intent.UNKNOWN
2025-08-05 17:17:08,553 [INFO] [pipeline] [/src/pipeline.py]: Query processed: 'who are you?' -> Response: '🏔️ Hello there, fellow adventurer! I'm here to help you with your Adventure Outfitters experience! 🌟

🎒...'
🏔️ Hello there, fellow adventurer! I'm here to help you with your Adventure Outfitters experience! 🌟

🎒 I can help you with:
• **Order Status & Tracking** - Check your order status and get tracking information
• **Product Recommendations** - Find the perfect outdoor gear for your next adventure

Just let me know what you need, and I'll get you equipped for your journey! Onward into the unknown! 🏔️

You: how are you?

Adventure Outfitters: 2025-08-05 17:17:12,430 [INFO] [coordinator] [/src/agents/coordinator.py]: AdventureOutfittersAgent processing message: 'how are you?'
2025-08-05 17:17:12,431 [INFO] [coordinator] [/src/agents/coordinator.py]: Determining intent for query: 'how are you?'
2025-08-05 17:17:12,431 [INFO] [models] [/.venv/lib/python3.12/site-packages/google/genai/models.py]: AFC is enabled with max remote calls: 10.
2025-08-05 17:17:14,036 [INFO] [_client] [/.venv/lib/python3.12/site-packages/httpx/_client.py]: HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"
2025-08-05 17:17:14,039 [INFO] [models] [/.venv/lib/python3.12/site-packages/google/genai/models.py]: AFC remote call 1 is done.
2025-08-05 17:17:14,039 [INFO] [coordinator] [/src/agents/coordinator.py]: Determined intent: UNKNOWN
2025-08-05 17:17:14,039 [ERROR] [coordinator] [/src/agents/coordinator.py]: No valid agent found for intent: Intent.UNKNOWN
2025-08-05 17:17:14,039 [INFO] [pipeline] [/src/pipeline.py]: Query processed: 'how are you?' -> Response: '🏔️ Hello there, fellow adventurer! I'm here to help you with your Adventure Outfitters experience! 🌟

🎒...'
🏔️ Hello there, fellow adventurer! I'm here to help you with your Adventure Outfitters experience! 🌟

🎒 I can help you with:
• **Order Status & Tracking** - Check your order status and get tracking information
• **Product Recommendations** - Find the perfect outdoor gear for your next adventure

Just let me know what you need, and I'll get you equipped for your journey! Onward into the unknown! 🏔️

You: 
```