#!/usr/bin/env python3
"""
Free Model Analysis and Recommendations for B3 Distillation

**Created:** August 9, 2025
**Author:** Kirk LaSalle & GitHub Copilot
**Tags:** #analysis #model_selection #b3_distillation
**Category:** Training Analysis
**Status:** Active

Analyzes the discovered free models and provides detailed recommendations
for B3 remote distillation based on model capabilities and architecture.
"""

import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

def analyze_free_models():
    """Analyze the discovered free models and provide detailed recommendations"""

    # Load the analysis data
    try:
        with open('openrouter_model_analysis.json') as f:
            data = json.load(f)
    except FileNotFoundError:
        console.print("❌ Analysis file not found. Please run openrouter_model_discovery.py first.")
        return

    free_models = data['analysis']['free']

    console.print(Panel.fit(
        f"📊 Free Model Analysis Report\n"
        f"🕒 Generated: {data['timestamp']}\n"
        f"🆓 {len(free_models)} Free Models Available",
        style="bold cyan"
    ))

    # Category analysis
    categories = {}
    architectures = {}
    context_ranges = {"Small (≤8K)": 0, "Medium (8K-32K)": 0, "Large (32K-64K)": 0, "Very Large (≥64K)": 0}

    for model in free_models:
        # Provider analysis
        model_id = model['id']
        provider = model_id.split('/')[0] if '/' in model_id else 'Unknown'
        categories[provider] = categories.get(provider, 0) + 1

        # Architecture analysis
        arch = model['architecture']
        architectures[arch] = architectures.get(arch, 0) + 1

        # Context length analysis
        context = model['context_length']
        if context <= 8192:
            context_ranges["Small (≤8K)"] += 1
        elif context <= 32768:
            context_ranges["Medium (8K-32K)"] += 1
        elif context <= 65536:
            context_ranges["Large (32K-64K)"] += 1
        else:
            context_ranges["Very Large (≥64K)"] += 1

    # Display category breakdown
    provider_table = Table(title="🏢 Free Models by Provider")
    provider_table.add_column("Provider", style="cyan")
    provider_table.add_column("Count", style="green")
    provider_table.add_column("Percentage", style="yellow")

    total_models = len(free_models)
    for provider, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_models) * 100
        provider_table.add_row(provider, str(count), f"{percentage:.1f}%")

    console.print(provider_table)

    # Architecture breakdown
    arch_table = Table(title="🏗️ Architecture Distribution")
    arch_table.add_column("Architecture", style="cyan")
    arch_table.add_column("Count", style="green")
    arch_table.add_column("Capability", style="yellow")

    for arch, count in sorted(architectures.items(), key=lambda x: x[1], reverse=True):
        capability = "Multimodal" if "+" in arch else "Text Only"
        arch_table.add_row(arch, str(count), capability)

    console.print(arch_table)

    # Context length distribution
    context_table = Table(title="📏 Context Length Distribution")
    context_table.add_column("Range", style="cyan")
    context_table.add_column("Count", style="green")
    context_table.add_column("Suitability", style="yellow")

    suitability_map = {
        "Small (≤8K)": "Limited",
        "Medium (8K-32K)": "Good",
        "Large (32K-64K)": "Excellent",
        "Very Large (≥64K)": "Outstanding"
    }

    for range_name, count in context_ranges.items():
        suitability = suitability_map[range_name]
        context_table.add_row(range_name, str(count), suitability)

    console.print(context_table)

    # Top recommendations with detailed analysis
    top_models = [
        {
            "id": "qwen/qwen2.5-vl-72b-instruct",
            "name": "Qwen2.5 VL 72B Instruct",
            "context": "32K",
            "type": "Multimodal (Vision + Text)",
            "strengths": ["Latest Qwen family", "Vision capability", "Large parameter count", "Instruction tuned"],
            "use_case": "Perfect for multimodal B3 enhancement"
        },
        {
            "id": "meta-llama/llama-3.3-70b-instruct",
            "name": "Llama 3.3 70B Instruct",
            "context": "64K",
            "type": "Text Generation",
            "strengths": ["Latest Llama family", "High context", "Proven architecture", "Meta backing"],
            "use_case": "Excellent for conversation quality improvement"
        },
        {
            "id": "deepseek/deepseek-r1:free",
            "name": "DeepSeek R1",
            "context": "163K",
            "type": "Reasoning Model",
            "strengths": ["Massive context", "Reasoning focused", "Latest release", "High performance"],
            "use_case": "Outstanding for logical reasoning enhancement"
        },
        {
            "id": "google/gemini-2.0-flash-exp",
            "name": "Gemini 2.0 Flash",
            "context": "1M+",
            "type": "Multimodal Flash",
            "strengths": ["Massive context", "Google's latest", "Flash architecture", "Experimental access"],
            "use_case": "Revolutionary context handling for B3"
        },
        {
            "id": "moonshotai/kimi-k2:free",
            "name": "Kimi K2 (Current)",
            "context": "32K",
            "type": "Text Generation",
            "strengths": ["Already configured", "Proven with B3", "Reliable", "Known performance"],
            "use_case": "Safe baseline choice for initial distillation"
        }
    ]

    console.print(Panel.fit("🎯 Top 5 Strategic Recommendations for B3 Distillation", style="bold green"))

    for i, model in enumerate(top_models, 1):
        # Create a rich panel for each recommendation
        content = Text()
        content.append(f"Model: {model['name']}\n", style="bold cyan")
        content.append(f"ID: {model['id']}\n", style="dim")
        content.append(f"Context: {model['context']} • Type: {model['type']}\n\n", style="yellow")
        content.append("Strengths:\n", style="bold green")
        for strength in model['strengths']:
            content.append(f"  • {strength}\n", style="green")
        content.append(f"\nUse Case: {model['use_case']}", style="bold blue")

        console.print(Panel(content, title=f"#{i} Recommendation", border_style="green"))

    # Strategic recommendations
    console.print(Panel.fit(
        "🚀 B3 Distillation Strategy Recommendations\n\n"
        "1️⃣ Start with Kimi K2 (already configured, proven baseline)\n"
        "2️⃣ Try DeepSeek R1 for reasoning improvements (massive 163K context)\n"
        "3️⃣ Experiment with Llama 3.3 70B for conversation quality\n"
        "4️⃣ Test Qwen2.5 VL 72B for multimodal capabilities\n"
        "5️⃣ Explore Gemini 2.0 Flash for revolutionary context handling\n\n"
        "💡 Progressive approach: Start conservative, then experiment with cutting-edge models",
        style="bold magenta"
    ))

    # Model selection criteria
    criteria_table = Table(title="🔍 Model Selection Criteria for B3 Distillation")
    criteria_table.add_column("Criterion", style="cyan")
    criteria_table.add_column("Importance", style="green")
    criteria_table.add_column("Recommendation", style="yellow")

    criteria = [
        ("Context Length", "Critical", "≥32K tokens for complex conversations"),
        ("Architecture", "High", "Text-optimized or multimodal for B3 enhancement"),
        ("Provider Reliability", "High", "Established providers (Meta, Google, OpenAI, Qwen)"),
        ("Model Size", "Medium", "70B+ parameters for quality teacher models"),
        ("Instruction Tuning", "Critical", "Must be instruction/chat tuned for conversation"),
        ("Recency", "Medium", "Recent models (2024-2025) for latest capabilities"),
        ("Proven Track Record", "High", "Models with demonstrated performance")
    ]

    for criterion, importance, recommendation in criteria:
        criteria_table.add_row(criterion, importance, recommendation)

    console.print(criteria_table)

def main():
    """Main analysis function"""
    analyze_free_models()

if __name__ == "__main__":
    main()
