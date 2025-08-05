Don't reveal user info in an example. Use something totally random.

```
🏔️ Hello there, fellow adventurer! I'm here to help you with your Adventure Outfitters experience! 🌟

🎒 I can help you with:
• **Order Status & Tracking** - Check your order status and get tracking information
• **Product Recommendations** - Find the perfect outdoor gear for your next adventure

Just let me know what you need, and I'll get you equipped for your journey! Onward into the unknown! 🏔️

You: my order

Adventure Outfitters: 2025-08-05 17:23:48,981 [INFO] [coordinator] [/src/agents/coordinator.py]: AdventureOutfittersAgent processing message: 'my order'
2025-08-05 17:23:48,987 [INFO] [coordinator] [/src/agents/coordinator.py]: Determining intent for query: 'my order'
2025-08-05 17:23:48,987 [INFO] [models] [/.venv/lib/python3.12/site-packages/google/genai/models.py]: AFC is enabled with max remote calls: 10.
2025-08-05 17:23:50,552 [INFO] [_client] [/.venv/lib/python3.12/site-packages/httpx/_client.py]: HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"
2025-08-05 17:23:50,554 [INFO] [models] [/.venv/lib/python3.12/site-packages/google/genai/models.py]: AFC remote call 1 is done.
2025-08-05 17:23:50,554 [INFO] [coordinator] [/src/agents/coordinator.py]: Determined intent: ORDER_STATUS
2025-08-05 17:23:50,554 [INFO] [coordinator] [/src/agents/coordinator.py]: Routing to agent: 'OrderStatusAgent'
2025-08-05 17:23:50,554 [INFO] [coordinator] [/src/agents/coordinator.py]: Delegating message to 'OrderStatusAgent'
2025-08-05 17:23:50,555 [INFO] [order_status] [/src/agents/delegates/order_status.py]: OrderStatusAgent processing message: 'my order'
2025-08-05 17:23:50,559 [INFO] [models] [/.venv/lib/python3.12/site-packages/google/genai/models.py]: AFC is enabled with max remote calls: 10.
2025-08-05 17:23:51,429 [INFO] [_client] [/.venv/lib/python3.12/site-packages/httpx/_client.py]: HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"
2025-08-05 17:23:51,430 [INFO] [models] [/.venv/lib/python3.12/site-packages/google/genai/models.py]: AFC remote call 1 is done.
2025-08-05 17:23:51,433 [INFO] [coordinator] [/src/agents/coordinator.py]: Generating final response for the customer.
2025-08-05 17:23:51,433 [INFO] [models] [/.venv/lib/python3.12/site-packages/google/genai/models.py]: AFC is enabled with max remote calls: 10.
2025-08-05 17:23:56,121 [INFO] [_client] [/.venv/lib/python3.12/site-packages/httpx/_client.py]: HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"
2025-08-05 17:23:56,127 [INFO] [models] [/.venv/lib/python3.12/site-packages/google/genai/models.py]: AFC remote call 1 is done.
2025-08-05 17:23:56,127 [INFO] [pipeline] [/src/pipeline.py]: Query processed: 'my order' -> Response: 'Hey there, fellow adventurer! 🌲 Ready to track your gear for your next epic journey? 🗺️ I can absolu...'
Hey there, fellow adventurer! 🌲 Ready to track your gear for your next epic journey? 🗺️ I can absolutely help you check on your order's progress!

To get a clear view of your expedition's status, I'll just need a couple of crucial coordinates from you: your **email address** and your **order number**. 🧭

Could you please send those over? For example, you could say something like: 'Check order #W001 for john.doe@example.com'.

Once we have that, we'll get you all set for your next grand adventure! Onward into the unknown! 🌟🏔️
```