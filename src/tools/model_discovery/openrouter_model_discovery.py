#!/usr/bin/env python3
"""
OpenRouter Model Discovery and Analysis Tool

**Created:** August 9, 2025
**Author:** Kirk LaSalle & GitHub Copilot
**Tags:** #api #openrouter #model_discovery #remote_distillation
**Category:** Training Tools
**Status:** Active

This script connects to OpenRouter API to discover available models,
with special focus on free models for B3 remote distillation.
"""

import json
import time
from pathlib import Path
from typing import Any

import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

class OpenRouterModelDiscovery:
    """OpenRouter API model discovery and analysis"""

    def __init__(self, api_key: str | None = None):
        """Initialize with API key from config or environment"""
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://impressioncore.ai",
            "X-Title": "ImpressionCore B3 Model Discovery"
        }

    def load_api_key_from_config(self) -> str:
        """Load API key from existing configuration"""
        config_path = Path("logs/training/remote_distillation_config.json")

        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
                return config.get("openrouter", {}).get("api_key", "")
            except Exception as e:
                console.print(f"⚠️ Error loading config: {e}")
                return ""
        return ""

    def get_available_models(self) -> list[dict[str, Any]]:
        """Fetch all available models from OpenRouter API"""

        if not self.api_key:
            self.api_key = self.load_api_key_from_config()

        if not self.api_key:
            console.print("❌ No API key found. Please check configuration.")
            return []

        self.headers["Authorization"] = f"Bearer {self.api_key}"

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("🌐 Fetching models from OpenRouter API...", total=None)

            try:
                response = requests.get(
                    f"{self.base_url}/models",
                    headers=self.headers,
                    timeout=30
                )

                if response.status_code == 200:
                    models_data = response.json()
                    return models_data.get("data", [])
                else:
                    console.print(f"❌ API Error: {response.status_code} - {response.text}")
                    return []

            except Exception as e:
                console.print(f"❌ Request failed: {e}")
                return []

    def analyze_models(self, models: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """Analyze models and categorize by pricing"""

        free_models = []
        paid_models = []
        unknown_pricing = []

        for model in models:
            model_info = {
                "id": model.get("id", "Unknown"),
                "name": model.get("name", "Unknown"),
                "description": model.get("description", "No description"),
                "context_length": model.get("context_length", 0),
                "architecture": model.get("architecture", {}).get("modality", "Unknown"),
                "pricing": model.get("pricing", {}),
                "top_provider": model.get("top_provider", {})
            }

            # Check if model is free
            pricing = model.get("pricing", {})
            prompt_cost = float(pricing.get("prompt", "0") or "0")
            completion_cost = float(pricing.get("completion", "0") or "0")

            if prompt_cost == 0 and completion_cost == 0:
                free_models.append(model_info)
            elif prompt_cost > 0 or completion_cost > 0:
                paid_models.append(model_info)
            else:
                unknown_pricing.append(model_info)

        return {
            "free": free_models,
            "paid": paid_models,
            "unknown": unknown_pricing
        }

    def display_free_models(self, free_models: list[dict[str, Any]]):
        """Display free models in a formatted table"""

        console.print(Panel.fit(
            f"🆓 Found {len(free_models)} Free Models Available for B3 Distillation",
            style="bold green"
        ))

        if not free_models:
            console.print("No free models found.")
            return

        # Create table for free models
        table = Table(title="🆓 Free Models for B3 Remote Distillation")
        table.add_column("Model ID", style="cyan", width=30)
        table.add_column("Name", style="green", width=25)
        table.add_column("Context", style="blue", width=10)
        table.add_column("Architecture", style="yellow", width=15)
        table.add_column("Provider", style="magenta", width=20)

        # Sort by context length (descending)
        sorted_models = sorted(free_models, key=lambda x: x.get("context_length", 0), reverse=True)

        for model in sorted_models:
            table.add_row(
                model.get("id", "Unknown")[:28],
                model.get("name", "Unknown")[:23],
                f"{model.get('context_length', 0):,}",
                model.get("architecture", "Unknown")[:13],
                model.get("top_provider", {}).get("name", "Unknown")[:18]
            )

        console.print(table)

    def save_model_analysis(self, analysis: dict[str, list[dict[str, Any]]]):
        """Save model analysis to JSON file"""

        output_file = "openrouter_model_analysis.json"

        # Add metadata
        analysis_with_metadata = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_models": sum(len(models) for models in analysis.values()),
            "free_model_count": len(analysis["free"]),
            "paid_model_count": len(analysis["paid"]),
            "analysis": analysis
        }

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_with_metadata, f, indent=2, ensure_ascii=False)

            console.print(f"✅ Model analysis saved to: {output_file}")

        except Exception as e:
            console.print(f"⚠️ Error saving analysis: {e}")

    def recommend_models_for_distillation(self, free_models: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Recommend best free models for B3 distillation"""

        # Filter and rank models for distillation suitability
        suitable_models = []

        for model in free_models:
            # Criteria for good distillation teachers:
            # 1. High context length (>= 8k tokens)
            # 2. Text generation capability
            # 3. Established provider

            context_length = model.get("context_length", 0)
            architecture = model.get("architecture", "").lower()
            model_id = model.get("id", "").lower()

            # Score the model
            score = 0
            reasons = []

            # Context length scoring
            if context_length >= 32000:
                score += 3
                reasons.append("Very high context")
            elif context_length >= 16000:
                score += 2
                reasons.append("High context")
            elif context_length >= 8000:
                score += 1
                reasons.append("Good context")

            # Architecture scoring
            if "text" in architecture:
                score += 2
                reasons.append("Text optimized")

            # Model type scoring (prefer instruction/chat models)
            if any(keyword in model_id for keyword in ["instruct", "chat", "assistant"]):
                score += 2
                reasons.append("Instruction tuned")

            # Known good models
            if any(provider in model_id for provider in ["gpt", "claude", "gemini", "llama", "qwen", "phi"]):
                score += 1
                reasons.append("Established model")

            if score >= 3:  # Minimum threshold
                model["distillation_score"] = score
                model["recommendation_reasons"] = reasons
                suitable_models.append(model)

        # Sort by score
        suitable_models.sort(key=lambda x: x["distillation_score"], reverse=True)

        return suitable_models[:10]  # Top 10 recommendations

def main():
    """Main function"""
    console.print(Panel.fit(
        "🌐 OpenRouter Model Discovery & Analysis\n"
        "Discovering Free Models for B3 Remote Distillation",
        style="bold magenta"
    ))

    # Initialize discovery tool
    discovery = OpenRouterModelDiscovery()

    # Get all models
    console.print("\n🔍 Fetching available models...")
    models = discovery.get_available_models()

    if not models:
        console.print("❌ Failed to fetch models. Please check API key and connection.")
        return

    console.print(f"✅ Found {len(models)} total models")

    # Analyze models
    analysis = discovery.analyze_models(models)

    # Display summary
    summary_table = Table(title="📊 Model Analysis Summary")
    summary_table.add_column("Category", style="cyan")
    summary_table.add_column("Count", style="green")

    summary_table.add_row("🆓 Free Models", str(len(analysis["free"])))
    summary_table.add_row("💰 Paid Models", str(len(analysis["paid"])))
    summary_table.add_row("❓ Unknown Pricing", str(len(analysis["unknown"])))
    summary_table.add_row("📊 Total Models", str(len(models)))

    console.print(summary_table)

    # Display free models
    discovery.display_free_models(analysis["free"])

    # Get recommendations
    recommendations = discovery.recommend_models_for_distillation(analysis["free"])

    if recommendations:
        console.print(Panel.fit(
            f"🎯 Top {len(recommendations)} Recommended Models for B3 Distillation",
            style="bold blue"
        ))

        rec_table = Table(title="🎯 B3 Distillation Recommendations")
        rec_table.add_column("Rank", style="bold", width=6)
        rec_table.add_column("Model ID", style="cyan", width=30)
        rec_table.add_column("Score", style="green", width=8)
        rec_table.add_column("Reasons", style="yellow")

        for i, model in enumerate(recommendations, 1):
            rec_table.add_row(
                f"#{i}",
                model["id"][:28],
                str(model["distillation_score"]),
                ", ".join(model["recommendation_reasons"])
            )

        console.print(rec_table)

    # Save analysis
    discovery.save_model_analysis(analysis)

    console.print(Panel.fit(
        "✅ Model Discovery Complete!\n\n"
        f"🆓 {len(analysis['free'])} free models available\n"
        f"🎯 {len(recommendations)} models recommended\n"
        f"📄 Analysis saved to openrouter_model_analysis.json",
        style="bold green"
    ))

if __name__ == "__main__":
    main()
