#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #api #python #source_code #src/scripts/utilities/test_api.py #testing
**Category:** Source Code
**Status:** Active
"""



import os

import requests
from rich.console import Console
from rich.panel import Panel


def test_openrouter_api():
    """Test OpenRouter API connectivity"""
    console = Console()

    console.print(Panel.fit(
        "🔬 OpenRouter API Connectivity Test\n"
        "Testing your API credentials and connection",
        style="bold blue"
    ))

    # Get API key from environment or config
    api_key = os.getenv('OPENROUTER_API_KEY')

    if not api_key:
        # Try to load from config file
        try:
            from b3_remote_config import RemoteDistillationConfig
            config = RemoteDistillationConfig.load_from_file("remote_distillation_config.json")
            api_key = config.openrouter.api_key
            console.print("✅ Loaded API key from config file")
        except Exception as e:
            console.print(f"❌ No API key found: {e}")
            return False
    else:
        console.print("✅ Found API key in environment")

    if not api_key:
        console.print("❌ No API key available for testing")
        return False

    # Test API with simple request
    console.print("🌐 Testing API connection...")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://impressioncore.ai",
        "X-Title": "ImpressionCore B3 Remote Distillation"
    }

    payload = {
        "model": "moonshotai/kimi-k2:free",
        "messages": [
            {
                "role": "user",
                "content": "Hello! This is a test message from ImpressionCore B3. Please respond with 'API test successful' if you can see this."
            }
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        console.print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            console.print(f"✅ API Response: {message}")
            console.print("🎉 API test successful!")
            return True
        else:
            console.print(f"❌ API Error: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.Timeout:
        console.print("❌ API request timed out")
        return False
    except requests.exceptions.RequestException as e:
        console.print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_openrouter_api()
    if success:
        print("\n🚀 Ready to run remote distillation!")
    else:
        print("\n🔧 Please check your API key configuration.")
