"""
debug_openai_api.py

Created: August 21, 2025
Author: GitHub Copilot
Purpose: Debug OpenAI API issues and test with simpler content

This script helps diagnose the 400 Bad Request errors we're seeing.
"""

import json
import os

import requests

# Set API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ No API key found in environment")
    api_key = "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"

print(f"✅ Using API key: {api_key[:20]}...")

def test_simple_embedding():
    """Test with very simple text to isolate the issue."""

    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Start with very simple text
    simple_texts = [
        "Hello world",
        "This is a test",
        "OpenAI embeddings API test"
    ]

    payload = {
        "model": "text-embedding-3-small",
        "input": simple_texts,
        "encoding_format": "float"
    }

    print("🧪 Testing simple embedding request...")
    print(f"📋 Payload: {json.dumps(payload, indent=2)}")
    print(f"🔗 URL: {url}")
    print(f"🔐 Headers: {headers}")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        print(f"📊 Response status: {response.status_code}")
        print(f"📋 Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! API is working")
            print(f"📐 Embeddings count: {len(data.get('data', []))}")
            print(f"💰 Usage: {data.get('usage', {})}")
            return True
        else:
            print(f"❌ FAILED with status {response.status_code}")
            print(f"📄 Response text: {response.text}")

            try:
                error_data = response.json()
                print(f"🚨 Error details: {json.dumps(error_data, indent=2)}")
            except Exception:
                print("🚨 Could not parse error as JSON")

            return False

    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

def test_chunk_content():
    """Test with actual chunk content that was failing."""

    # Read the first chunk from our problem file
    try:
        with open("docs/CHRONOLOGICAL_INDEX.md", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        print("❌ Could not read CHRONOLOGICAL_INDEX.md")
        return False

    # Take first 1000 characters
    test_chunk = content[:1000]

    print("🧪 Testing with real chunk content...")
    print(f"📄 Chunk length: {len(test_chunk)} characters")
    print(f"📄 First 100 chars: {test_chunk[:100]}...")

    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "text-embedding-3-small",
        "input": [test_chunk],
        "encoding_format": "float"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        print(f"📊 Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS with real content!")
            print(f"💰 Usage: {data.get('usage', {})}")
            return True
        else:
            print("❌ FAILED with real content")
            print(f"📄 Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception with real content: {e}")
        return False

def validate_api_key():
    """Validate the API key format and test connection."""

    print("🔍 Validating API key...")

    if not api_key:
        print("❌ No API key provided")
        return False

    if not api_key.startswith("sk-"):
        print("❌ API key doesn't start with 'sk-'")
        return False

    print(f"✅ API key format looks correct: {api_key[:20]}...")

    # Test with models endpoint first (simpler)
    try:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )

        if response.status_code == 200:
            print("✅ API key is valid - can access models endpoint")
            return True
        else:
            print(f"❌ API key validation failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ API key validation error: {e}")
        return False

def main():
    """Run comprehensive API debugging."""

    print("🚀 Starting OpenAI API debugging...")
    print("="*60)

    # Step 1: Validate API key
    print("\n1️⃣ VALIDATING API KEY")
    print("-" * 30)
    if not validate_api_key():
        print("❌ API key validation failed - stopping")
        return

    # Step 2: Test simple embedding
    print("\n2️⃣ TESTING SIMPLE EMBEDDING")
    print("-" * 30)
    if not test_simple_embedding():
        print("❌ Simple embedding failed - API issue")
        return

    # Step 3: Test with real content
    print("\n3️⃣ TESTING REAL CONTENT")
    print("-" * 30)
    if not test_chunk_content():
        print("❌ Real content failed - content issue")
        return

    print("\n✅ ALL TESTS PASSED!")
    print("🎉 OpenAI API is working correctly")

if __name__ == "__main__":
    main()
