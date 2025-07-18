#!/usr/bin/env python3
"""
Script to detect and test Ollama connection from DevContainer.
"""

import asyncio
import sys
from typing import Optional

import httpx


async def test_ollama_connection(base_url: str) -> bool:
    """Test if Ollama is accessible at the given URL."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base_url}/api/tags")
            return response.status_code == 200
    except Exception as e:
        print(f"Failed to connect to {base_url}: {e}")
        return False


async def find_ollama_url() -> Optional[str]:
    """Try to find the correct Ollama URL."""
    # List of possible URLs to try
    urls_to_try = [
        "http://localhost:11434",          # Standard local
        "http://host.docker.internal:11434",  # Docker Desktop
        "http://172.17.0.1:11434",         # Docker default bridge
        "http://172.168.0.1:11434",        # Common container gateway
        "http://10.0.2.2:11434",           # VirtualBox/VMware
        "http://192.168.1.1:11434",        # Common router IP
    ]

    print("🔍 Searching for Ollama server...")

    for url in urls_to_try:
        print(f"   Trying {url}...")
        if await test_ollama_connection(url):
            print(f"✅ Found Ollama at {url}")
            return url

    print("❌ Could not find Ollama server")
    return None


async def list_ollama_models(base_url: str) -> None:
    """List available Ollama models."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                if models:
                    print(f"📋 Available models at {base_url}:")
                    for model in models:
                        print(f"   - {model['name']}")
                else:
                    print(f"⚠️  No models found at {base_url}")
            else:
                print(f"❌ Failed to list models: {response.status_code}")
    except Exception as e:
        print(f"❌ Error listing models: {e}")


async def main() -> int:
    """Main function to find and test Ollama connection."""
    print("🧠 Ollama Connection Detector")
    print("=" * 40)

    # Try to find Ollama
    ollama_url = await find_ollama_url()

    if ollama_url:
        print(f"\n🎯 Set your OLLAMA_BASE_URL to: {ollama_url}")
        print(f"   export OLLAMA_BASE_URL={ollama_url}")

        # List available models
        print("\n📋 Checking available models...")
        await list_ollama_models(ollama_url)

        print(f"\n✅ You can now use Ollama at {ollama_url}")
        return 0
    else:
        print("\n❌ Ollama not found. Please ensure:")
        print("   1. Ollama is running on the host machine")
        print("   2. It's accessible on port 11434")
        print("   3. The DevContainer has network access to the host")
        print("\n💡 Try running: ollama serve --host 0.0.0.0 on the host")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
    sys.exit(asyncio.run(main()))
