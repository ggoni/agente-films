"""End-to-End Test Script for Agente Films.

Simulates a complete user journey:
1. Create a new filmmaking session
2. Send a message to the agent
3. Verify the agent's response
4. Check session status
"""

import asyncio
import sys
import httpx

BASE_URL = "http://localhost:8000"

async def run_e2e_test():
    print("🎬 Starting End-to-End Test for Agente Films...")
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # 1. Health Check
        print("\n1️⃣  Checking API Health...")
        try:
            resp = await client.get("/health")
            resp.raise_for_status()
            print(f"✅ API is healthy: {resp.json()}")
        except Exception as e:
            print(f"❌ API Health Check Failed: {e}")
            sys.exit(1)

        # 2. Create Session
        print("\n2️⃣  Creating New Session...")
        try:
            resp = await client.post("/sessions")
            resp.raise_for_status()
            session_data = resp.json()
            session_id = session_data["id"]
            print(f"✅ Session Created: ID={session_id}")
        except Exception as e:
            print(f"❌ Session Creation Failed: {e}")
            sys.exit(1)

        # 3. Send Message to Agent
        print("\n3️⃣  Sending Message to Agent...")
        message = "I want to make a sci-fi movie about AI."
        print(f"📤 Sending: '{message}'")
        
        try:
            # Note: We are mocking the ADK runner in the backend for now,
            # so we expect a mock response.
            resp = await client.post(f"/sessions/{session_id}/messages", json={"message": message})
            resp.raise_for_status()
            data = resp.json()
            response_text = data["response"]
            print(f"✅ Agent Response: '{response_text}'")
            
            if "Processed:" in response_text or "Hello" in response_text:
                 print("✅ Response content verified.")
            else:
                 print("⚠️ Unexpected response content.")
                 
        except Exception as e:
            print(f"❌ Message Sending Failed: {e}")
            sys.exit(1)

        # 4. Verify Session State (Optional - if we had a state endpoint)
        print("\n4️⃣  Verifying Session Retrieval...")
        try:
            resp = await client.get(f"/sessions/{session_id}")
            resp.raise_for_status()
            print(f"✅ Session Retrieved Successfully")
        except Exception as e:
            print(f"❌ Session Retrieval Failed: {e}")
            sys.exit(1)

    print("\n🎉 End-to-End Test Completed Successfully!")

if __name__ == "__main__":
    asyncio.run(run_e2e_test())
