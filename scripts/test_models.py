#!/usr/bin/env python3
"""Test script to verify multi-model LiteLLM setup."""

import asyncio
import os
import sys

import httpx


async def test_litellm_health() -> bool:
    """Test if LiteLLM proxy is healthy."""
    print("🔍 Testing LiteLLM proxy health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:4000/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ LiteLLM proxy is healthy")
                return True
            print(f"❌ LiteLLM proxy returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ LiteLLM proxy health check failed: {e}")
        return False


async def list_available_models() -> list[str]:
    """List available models from LiteLLM proxy."""
    print("\n🔍 Fetching available models...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:4000/model/info",
                headers={"Authorization": "Bearer sk-1234"},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            models = [model["model_name"] for model in data.get("data", [])]

            if models:
                print(f"✅ Found {len(models)} available models:")
                for model in models:
                    print(f"   - {model}")
            else:
                print("⚠️  No models found")

            return models
    except Exception as e:
        print(f"❌ Failed to list models: {e}")
        return []


async def test_model(model_name: str) -> dict[str, any]:
    """Test a specific model with a simple prompt."""
    print(f"\n🔍 Testing model: {model_name}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:4000/chat/completions",
                headers={
                    "Authorization": "Bearer sk-1234",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model_name,
                    "messages": [
                        {"role": "user", "content": "Say 'Hello from {model_name}' in one sentence"}
                    ],
                    "max_tokens": 50,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})

            print(f"✅ {model_name} responded:")
            print(f"   Response: {content[:100]}...")
            print(f"   Tokens: {usage.get('total_tokens', 'N/A')}")

            return {
                "model": model_name,
                "success": True,
                "content": content,
                "usage": usage,
            }

    except Exception as e:
        print(f"❌ {model_name} failed: {e}")
        return {"model": model_name, "success": False, "error": str(e)}


async def test_api_health() -> bool:
    """Test if FastAPI backend is healthy."""
    print("\n🔍 Testing FastAPI backend...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API is healthy: {data}")
                return True
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check failed: {e}")
        print("   💡 Make sure docker-compose is running: docker-compose up -d")
        return False


async def main() -> None:
    """Run all tests."""
    print("=" * 60)
    print("🚀 LiteLLM Multi-Model Setup Test")
    print("=" * 60)

    # Test API health
    api_healthy = await test_api_health()
    if not api_healthy:
        print("\n⚠️  API is not running. Some tests may fail.")

    # Test LiteLLM proxy health
    litellm_healthy = await test_litellm_health()
    if not litellm_healthy:
        print("\n❌ LiteLLM proxy is not healthy. Exiting.")
        print("   💡 Start services: docker-compose up -d")
        sys.exit(1)

    # List available models
    models = await list_available_models()
    if not models:
        print("\n⚠️  No models configured. Check litellm-config.yaml")
        sys.exit(1)

    # Test each model (or subset if too many)
    print("\n" + "=" * 60)
    print("🧪 Testing Model Responses")
    print("=" * 60)

    test_models = models[:3]  # Test first 3 models to save time
    if len(models) > 3:
        print(f"ℹ️  Testing {len(test_models)} of {len(models)} models")

    results = []
    for model in test_models:
        result = await test_model(model)
        results.append(result)
        await asyncio.sleep(1)  # Rate limiting

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful

    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")

    if failed > 0:
        print("\n⚠️  Failed models:")
        for result in results:
            if not result["success"]:
                print(f"   - {result['model']}: {result.get('error', 'Unknown error')}")

    print("\n" + "=" * 60)
    print("💡 How to switch models:")
    print("=" * 60)
    print("1. Edit .env and change MODEL=your-model-name")
    print("2. Restart: docker-compose restart api")
    print("3. Or use MODEL env var: MODEL=gpt-4 docker-compose up api")
    print("\nAvailable models:", ", ".join(models))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
