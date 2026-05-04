#!/usr/bin/env python3
"""
Test WebSocket connection to Valtronics backend
"""

import asyncio
import websockets
import json
import sys

async def test_websocket():
    """Test WebSocket connection and message handling"""
    uri = "ws://localhost:8000/ws"
    
    try:
        print(f"🔌 Connecting to WebSocket: {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")
            
            # Send a test message
            test_message = {
                "type": "ping",
                "timestamp": "2026-05-04T16:10:00Z"
            }
            
            await websocket.send(json.dumps(test_message))
            print(f"📤 Sent: {test_message}")
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"📥 Received: {response}")
            
            return True
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ WebSocket connection refused - server may not be running")
        return False
    except asyncio.TimeoutError:
        print("⏰ WebSocket response timeout")
        return False
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_websocket())
    sys.exit(0 if success else 1)
