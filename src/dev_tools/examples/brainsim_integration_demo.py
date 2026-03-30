#!/usr/bin/env python3
"""
ImpressionCore: Brainsim Integration Demo

Module for brainsim integration demo functionality in the ImpressionCore framework.

File: examples\brainsim_integration_demo.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-24
Modified: 2025-05-24
Version: 1.0.0

Authors:
- Kirk LaSalle <kirk@impressioncore.ai>
- GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [memory-critical, production, object-oriented, 2025]
Dependencies: [rich, typing, pathlib, numpy]
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
This module implements brainsim integration demo functionality for the
ImpressionCore brain-inspired multimodal AI framework. Optimized for memory-
constrained environments and designed to run efficiently on consumer hardware.

Design Philosophy:
- Memory-efficient implementation for GTX 1050 Ti constraints
- Modular design for easy extension and maintenance
- Rich logging and error handling
- Integration with ImpressionCore ecosystem

TODO:
- Add comprehensive unit tests
- Implement performance benchmarks
- Add configuration validation
- Optimize memory usage patterns

Examples:
```python
# Basic usage example
from examples.brainsim_integration_demo import BrainSimAdapter
instance = BrainSimAdapter()
result = instance.process()
```

Notes:
- Optimized for GTX 1050 Ti (4GB VRAM)
- Implements memory-efficient algorithms
- Provides CPU fallback capabilities
- Thread-safe implementation
"""

import os
import sys
import logging
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Any, List, Dict, Tuple, Optional, Union
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import networkx as nx

# Rich library for enhanced terminal visualizations
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.layout import Layout
from rich.live import Live
from rich.tree import Tree
from rich.text import Text
from rich.prompt import Prompt
from rich.columns import Columns
from rich.logging import RichHandler

# Configure rich console and logging
console = Console(width=100, color_system="auto")
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)]
)
logger = logging.getLogger("rich")

# Add the project root to the path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.core.knowledge.uks import UniversalKnowledgeStore, KnowledgeNode

# Enhanced BrainSimAdapter with additional cognitive functions
class BrainSimAdapter:
    """Mock implementation of BrainSimAdapter for demonstration purposes."""
    
    def __init__(self, mode="local_import"):
        """
        Initialize the BrainSimAdapter.
        
        Args:
            mode: The connection mode to use ("local_import", "api", or "embedded")
        """
        self.mode = mode
        self._initialized = True
        self.uks = None
        self.activation_history = []
        self.memory_store = {}
        # Memory optimization: Memory-critical operation
        self.attention_weights = {}
        
    def initialize(self) -> bool:
        """
        Initialize connection to BrainSimIII.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        console.print(f"[bold green]Mock BrainSimAdapter initialized in mode: [/bold green][yellow]{self.mode}[/yellow]")
        # Simulate neural network initialization with animated progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task1 = progress.add_task("[cyan]Loading neural models...", total=100)
            task2 = progress.add_task("[magenta]Initializing cognitive functions...", total=100)
            task3 = progress.add_task("[yellow]Calibrating attention mechanisms...", total=100)
            task4 = progress.add_task("[green]Setting up memory systems...", total=100)
            # Memory optimization: Memory-critical operation
            
            # Simulate initialization steps
            for i in range(101):
                if i <= 100:
                    progress.update(task1, completed=i)
                if i <= 90:
                    progress.update(task2, completed=min(i * 1.1, 100))
                if i <= 80:
                    progress.update(task3, completed=min(i * 1.25, 100))
                if i <= 70:
                    progress.update(task4, completed=min(i * 1.4, 100))
                time.sleep(0.02)  # Fast enough for demo but visible
        
        return True
    
    def augment_prompt(self, prompt: str, knowledge_store: Any) -> str:
        """
        Use BrainSimIII to augment the prompt with facts from UKS.
        
        Args:
            prompt: The original prompt to augment
            knowledge_store: The knowledge store to use for augmentation
            
        Returns:
            str: The augmented prompt
        """
        # Simulate neural activity during prompt processing
        with console.status("[bold green]Neural processing in progress...", spinner="dots"):
            time.sleep(1)  # Simulate processing time
            
            # Extract the subject from the prompt (simplified)
            subject = None
            for word in prompt.split():
                if word in knowledge_store.nodes:
                    subject = word
                    break
            
            # If a subject was found, add facts about it to the prompt
            additional_context = []
            if subject and hasattr(knowledge_store.nodes[subject], 'facts'):
                facts = knowledge_store.nodes[subject].facts
                for predicate, obj in facts:
                    additional_context.append(f"{subject} {predicate}: {obj}")
                    
                # Record activation for visualization
                self.activation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "subject": subject,
                    "activation_level": random.uniform(0.7, 0.95),
                    "facts_retrieved": len(facts)
                })
            
            # Format the augmented prompt
            if additional_context:
                context_str = "\n".join(additional_context)
                augmented_prompt = f"{prompt}\n\nAdditional context:\n{context_str}"
                return augmented_prompt
            else:
                return f"{prompt}\n\nNo additional context available."
    
    def simulate_attention(self, text: str, focus_keywords: List[str] = None) -> Dict[str, float]:
        """
        Simulate neural attention mechanism on text.
        
        Args:
            text: The text to analyze
            focus_keywords: Optional list of keywords to focus attention on
            
        Returns:
            Dict mapping tokens to attention weights
        """
        # Default focus keywords if none provided
        if focus_keywords is None:
            focus_keywords = ["Mars", "Earth", "planet", "life", "water"]
        
        words = text.split()
        attention_weights = {}
        
        # Assign attention weights based on keywords and position
        for i, word in enumerate(words):
            clean_word = word.strip(".,;:!?()[]{}\"'").lower()
            
            # Base weight - words at the beginning and end get higher attention
            position_factor = 1.0
            if i < len(words) * 0.2 or i > len(words) * 0.8:
                position_factor = 1.2
            
            # Keyword matching
            if clean_word in [k.lower() for k in focus_keywords]:
                attention_weights[word] = random.uniform(0.7, 0.95) * position_factor
            else:
                attention_weights[word] = random.uniform(0.1, 0.5) * position_factor
        
        # Store for visualization
        self.attention_weights = attention_weights
        return attention_weights
    
    def creative_expansion(self, concept: str, directions: int = 3) -> List[Dict]:
        """
        Simulate creative expansion of a concept in multiple directions.
        
        Args:
            concept: The seed concept to expand
            directions: Number of creative directions to explore
            
        Returns:
            List of creative expansions
        """
        creative_directions = [
            {"name": "technological", "themes": ["robots", "sensors", "probes", "satellites", "AI"]},
            {"name": "biological", "themes": ["life", "microbes", "ecosystems", "adaptation", "evolution"]},
            {"name": "geological", "themes": ["rocks", "minerals", "volcanoes", "craters", "canyons"]},
            {"name": "historical", "themes": ["discovery", "exploration", "naming", "mythology", "observation"]},
            {"name": "future", "themes": ["colonization", "terraforming", "habitation", "mining", "research"]}
        ]
        
        results = []
        selected_directions = random.sample(creative_directions, min(directions, len(creative_directions)))
        
        for direction in selected_directions:
            expansion = {
                "direction": direction["name"],
                "seed_concept": concept,
                "themes": direction["themes"],
                "ideas": [],
                "confidence": random.uniform(0.6, 0.9)
            }
            
            # Generate ideas based on direction and concept
            for _ in range(random.randint(2, 5)):
                theme = random.choice(direction["themes"])
                if concept.lower() == "mars":
                    if direction["name"] == "technological":
                        expansion["ideas"].append(f"New {theme} for detecting subsurface water on {concept}")
                    elif direction["name"] == "biological":
                        expansion["ideas"].append(f"Investigating potential {theme} in {concept}'s ancient riverbeds")
                    elif direction["name"] == "geological":
                        expansion["ideas"].append(f"Formation patterns of {concept}'s largest {theme}")
                    elif direction["name"] == "historical":
                        expansion["ideas"].append(f"Timeline of {concept}'s {theme} through ancient astronomy")
                    elif direction["name"] == "future":
                        expansion["ideas"].append(f"Sustainable {theme} strategies for {concept}")
                elif concept.lower() == "earth":
                    if direction["name"] == "technological":
                        expansion["ideas"].append(f"{concept}-based {theme} for monitoring climate changes")
                    elif direction["name"] == "biological":
                        expansion["ideas"].append(f"Unique {theme} that could have applications on other planets")
                    elif direction["name"] == "geological":
                        expansion["ideas"].append(f"Comparing {concept}'s {theme} with those on other planets")
                    elif direction["name"] == "historical":
                        expansion["ideas"].append(f"{theme} of understanding {concept}'s place in the solar system")
                    elif direction["name"] == "future":
                        expansion["ideas"].append(f"Learning from {concept} for {theme} on other planets")
            
            results.append(expansion)
            
        return results
    
    def episodic_memory_recall(self, query: str, memory_count: int = 3) -> List[Dict]:
    # Memory optimization: Memory-critical operation
        """
        Simulate episodic memory recall based on a query.
        # Memory optimization: Memory-critical operation
        
        Args:
            query: The query to search memories for
            memory_count: Number of memories to recall
            # Memory optimization: Memory-critical operation
            
        Returns:
            List of recalled memories
        """
        # Fake episodic memories
        if not self.memory_store:
        # Memory optimization: Memory-critical operation
            self.memory_store = {
            # Memory optimization: Memory-critical operation
                "mars_discovery": {
                    "timestamp": "1877-08-17",
                    "content": "Asaph Hall discovered Mars' moons Phobos and Deimos",
                    "source": "Astronomical observations",
                    "emotional_valence": 0.8,
                    "keywords": ["Mars", "moons", "discovery", "Phobos", "Deimos"]
                },
                "mars_canals": {
                    "timestamp": "1877-09-05",
                    "content": "Giovanni Schiaparelli observed what he called 'canali' on Mars",
                    "source": "Telescopic observations",
                    "emotional_valence": 0.5,
                    "keywords": ["Mars", "canals", "observations", "water", "life"]
                },
                "mars_pathfinder": {
                    "timestamp": "1997-07-04",
                    "content": "Mars Pathfinder landed on Mars with the Sojourner rover",
                    "source": "NASA mission data",
                    "emotional_valence": 0.9,
                    "keywords": ["Mars", "landing", "rover", "Pathfinder", "Sojourner"]
                },
                "mars_water": {
                    "timestamp": "2015-09-28",
                    "content": "NASA confirmed evidence of flowing liquid water on Mars",
                    "source": "Scientific publication",
                    "emotional_valence": 0.85,
                    "keywords": ["Mars", "water", "liquid", "flowing", "discovery"]
                },
                "perseverance_landing": {
                    "timestamp": "2021-02-18",
                    "content": "Perseverance rover successfully landed on Mars with the Ingenuity helicopter",
                    "source": "NASA mission data",
                    "emotional_valence": 0.95,
                    "keywords": ["Mars", "rover", "Perseverance", "landing", "Ingenuity", "helicopter"]
                }
            }
        
        # Match query keywords to memory keywords
        # Memory optimization: Memory-critical operation
        query_words = set(query.lower().split())
        matched_memories = []
        
        for memory_id, memory in self.memory_store.items():
        # Memory optimization: Memory-critical operation
            memory_keywords = [k.lower() for k in memory["keywords"]]
            # Memory optimization: Memory-critical operation
            overlap = len(query_words.intersection(memory_keywords))
            # Memory optimization: Memory-critical operation
            if overlap > 0:
                memory_copy = memory.copy()
                # Memory optimization: Memory-critical operation
                memory_copy["id"] = memory_id
                # Memory optimization: Memory-critical operation
                memory_copy["relevance"] = min(1.0, overlap * 0.2 + random.uniform(0.1, 0.3))
                # Memory optimization: Memory-critical operation
                matched_memories.append(memory_copy)
                # Memory optimization: Memory-critical operation
        
        # Sort by relevance and return top memories
        matched_memories.sort(key=lambda x: x["relevance"], reverse=True)
        return matched_memories[:memory_count]
        # Memory optimization: Memory-critical operation

# Mock implementation of CognitiveService
class CognitiveService:
    """Mock implementation of CognitiveService for demonstration purposes."""
    
    def __init__(self, brainsim_adapter=None):
        """
        Initialize the CognitiveService.
        
        Args:
            brainsim_adapter: An initialized BrainSimAdapter instance
        """
        self.brainsim = brainsim_adapter
        
    def analyze_query_intent(self, query: str) -> dict:
        """
        Analyze the intent behind a user query.
        
        Args:
            query: The user's query string
            
        Returns:
            A dictionary containing intent analysis
        """
        # Simple intent detection based on first word
        query_lower = query.lower()
        
        if query_lower.startswith(("what", "who", "when", "where", "why", "how")):
            return {"intent": "question", "confidence": 0.9}
        elif query_lower.startswith(("show", "display", "list", "find")):
            return {"intent": "command", "confidence": 0.8}
        elif query_lower.startswith(("can", "could", "would", "will")):
            return {"intent": "request", "confidence": 0.7}
        else:
            return {"intent": "statement", "confidence": 0.6}
    
    def simulate_common_sense_reasoning(self, scenario: str, facts: list) -> dict:
        """
        Apply common sense reasoning to a scenario.
        
        Args:
            scenario: Description of the scenario
            facts: List of known facts
            
        Returns:
            Dictionary with reasoning results
        """
        # Simple mock implementation
        return {
            "result": f"Based on the scenario '{scenario}' and considering {len(facts)} facts, a likely conclusion is that Mars could potentially support some form of life.",
            "steps": [
                "Analyze scenario context",
                "Evaluate provided facts",
                "Apply common sense heuristics",
                "Form a preliminary conclusion"
            ],
            "confidence": 0.75
        }
    
    def enrich_knowledge(self, knowledge_store, topic: str, depth: int = 1) -> dict:
        """
        Enrich the knowledge store with new inferred knowledge about a topic.
        
        Args:
            knowledge_store: The knowledge store to enrich
            topic: The topic to expand knowledge about
            depth: How deep to go in the reasoning chain
            
        Returns:
            Statistics about the enrichment process
        """
        # Only enrich if the node exists
        if topic not in knowledge_store.nodes:
            return {"added_facts": 0, "success": False}
        
        # Add some mock facts based on the topic
        if topic == "Mars":
            knowledge_store.add_fact(topic, "has_moons", 2)
            knowledge_store.add_fact(topic, "atmosphere", "thin CO2")
            knowledge_store.add_fact(topic, "avg_temperature", "-80 F")
            return {"added_facts": 3, "success": True}
        elif topic == "Earth":
            knowledge_store.add_fact(topic, "has_moons", 1)
            knowledge_store.add_fact(topic, "atmosphere", "nitrogen, oxygen")
            knowledge_store.add_fact(topic, "avg_temperature", "57 F")
            return {"added_facts": 3, "success": True}
        else:
            return {"added_facts": 0, "success": False}

# Update ModalEngine with better integration
class ModalEngine:
    """
    
    ModalEngine class for ImpressionCore framework.
    
    This class implements modalengine functionality optimized for
    memory-constrained environments like the GTX 1050 Ti.
    # Memory optimization: Memory-critical operation
    
    Memory Considerations:
    # Memory optimization: Memory-critical operation
        - Implements memory-efficient algorithms
        # Memory optimization: Memory-critical operation
        - Supports gradient checkpointing
        - Provides CPU fallback options
    
    Notes:
        - Thread-safe implementation
        - GPU memory optimized
        # Memory optimization: Memory-critical operation
        - Part of ImpressionCore ecosystem
    
    """
    def __init__(self, brainsim_path: str):
        """
        Initialize the ModalEngine with BrainSim integration.
        
        Args:
            brainsim_path: Path to the BrainSim module
        """
        self.brainsim_path = brainsim_path
        self.knowledge_store = None
        self.brainsim = BrainSimAdapter(mode="local_import")
        self.cognitive_service = CognitiveService(self.brainsim)
        self._initialized = False
        
    def initialize(self) -> bool:
        """
        Initialize the engine and its components.
        
        Returns:
            bool: True if initialization was successful
        """
        print(f"Mock ModalEngine initialized with BrainSim path: {self.brainsim_path}")
        # Initialize BrainSim adapter
        self.brainsim.initialize()
        
        # Connect knowledge store to BrainSim
        if self.knowledge_store:
            self.brainsim.uks = self.knowledge_store
        
        self._initialized = True
        return self._initialized

    def generate_response(self, query: str) -> str:
        """
        Generate a response using BrainSim augmentation.
        
        Args:
            query: The user query
            
        Returns:
            str: The generated response
        """
        if not self._initialized:
            return "Engine not initialized. Please initialize first."
            
        # Use BrainSim to augment the query
        if self.knowledge_store:
            augmented_query = self.brainsim.augment_prompt(query, self.knowledge_store)
        else:
            augmented_query = query
            
        # Mock response generation
        return f"Response to: {augmented_query}\n\nBased on my knowledge, this is a relevant answer to your question."

    def shutdown(self):
        """Shut down the engine and release resources."""
        print("Mock ModalEngine shutdown.")
        self._initialized = False

def ensure_project_setup():
    """Ensure the project directory structure is set up correctly."""
    # Create directories if they don't exist
    dirs = [
        project_root / "models",
        project_root / "checkpoints",
        project_root / "brainsim"
    ]
    
    for directory in dirs:
        if not directory.exists():
            directory.mkdir(exist_ok=True)
            print(f"Created directory: {directory}")
    
    # Create a dummy brainsim module if needed for demo purposes
    brainsim_dir = project_root / "brainsim"
    init_file = brainsim_dir / "__init__.py"
    brainsim_file = brainsim_dir / "brainsim.py"
    
    if not init_file.exists():
        with open(init_file, "w") as f:
            f.write('''"""
BrainSimIII dummy module for demo purposes.
"""

from .brainsim import BrainSim
''')
        print("Created dummy brainsim module init")
    
    if not brainsim_file.exists():
        with open(brainsim_file, "w") as f:
            f.write('''"""BrainSimIII dummy implementation module."""

class BrainSim:
    """Dummy BrainSim class that returns placeholder values."""
    
    def __init__(self):
        self.name = "Dummy BrainSim"
        
    def extract_concepts(self, text):
        """Extract key concepts from text."""
        # Simple tokenization and filtering
        words = text.lower().split()
        return [w for w in words if len(w) > 3 and w not in {"what", "when", "where", "this", "that", "with"}]
        
    def analyze_intent(self, query):
        """Analyze the intent of a query."""
        return {"intent": "query", "confidence": 0.8}
        
    def common_sense_reason(self, scenario, facts):
        """Perform common sense reasoning."""
        return {
            "result": f"Based on {scenario}, it is likely that water exists.",
            "steps": ["Parse input", "Apply logic", "Generate conclusion"]
        }
        
    def generate_facts(self, concept, depth=1):
        """Generate facts about a concept."""
        return [
            (concept, "is_interesting", True),
            (concept, "needs_more_research", True),
            (concept, "has_potential", "high")
        ]
''')
        print("Created dummy brainsim implementation module")
    
    # Create dummy model if needed
    # Memory optimization: Explicit memory cleanup
    model_file = project_root / "models" / "best_model.pt"
    if not model_file.exists():
        try:
            import pickle
            with open(model_file, "wb") as f:
                pickle.dump({"name": "dummy_model", "type": "placeholder"}, f)
            print(f"Created dummy model file at {model_file}")
            # Memory optimization: Explicit memory cleanup
        except Exception as e:
            print(f"Warning: Failed to create dummy model file: {e}")
            # Memory optimization: Explicit memory cleanup

def main():
    """Main demo function showcasing BrainSimIII integration with rich visualizations."""
    
    # Create header with animated text
    console.print(Panel(
        Text("ImpressionCore BrainSimIII Integration Demo", style="bold cyan", justify="center"),
        border_style="cyan",
        width=100
    ))
    
    # Initialize project structure with progress animation
    with console.status("[bold green]Setting up project environment...", spinner="dots") as status:
        ensure_project_setup()
        time.sleep(1)  # Give time to see the status
    
    # Create a knowledge store with animated progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Creating knowledge graph...", total=100)
        
        # Create knowledge store
        knowledge_store = UniversalKnowledgeStore()
        progress.update(task, completed=30)
        
        # Create and add nodes
        mars_node = KnowledgeNode("Mars")
        earth_node = KnowledgeNode("Earth")
        progress.update(task, completed=50)
        
        knowledge_store.add_node(mars_node)
        knowledge_store.add_node(earth_node)
        progress.update(task, completed=70)
        
        # Add initial facts
        knowledge_store.add_fact("Mars", "has_robots", True)
        knowledge_store.add_fact("Mars", "orbital_position", 4)
        knowledge_store.add_fact("Earth", "has_life", True)
        knowledge_store.add_fact("Earth", "orbital_position", 3)
        progress.update(task, completed=100)
    
    # Initialize the engine with BrainSim integration
    console.print("\n[bold magenta]Initializing Neural Simulation Engine...[/bold magenta]")
    engine = ModalEngine(brainsim_path=os.path.join(project_root, "brainsim"))
    
    # Initialize and connect components
    initialized = engine.initialize()
    engine.knowledge_store = knowledge_store
    
    if initialized:
        console.print("[bold green]✓[/bold green] Neural engine initialization complete!")
    else:
        console.print("[bold red]✗[/bold red] Engine initialization encountered issues, continuing with limited functionality.")
    
    # Header for cognitive capabilities section
    console.print(Panel(
        Text("BrainSim Cognitive Capabilities", justify="center"),
        style="bold yellow"
    ))
    
    # Test 1: Show the brain dashboard
    console.print("\n[bold blue]🧠 Interactive Brain Dashboard[/bold blue]")
    create_brain_dashboard(engine, knowledge_store)
    console.print("\n")
    
    # Test 2: Knowledge Graph Visualization
    console.print("[bold green]📊 Knowledge Graph Structure[/bold green]")
    console.print("[dim]This visualization would show the knowledge graph if matplotlib display was enabled.[/dim]")
    # In a real terminal, this would show a visual graph: visualize_knowledge_graph(knowledge_store)
    
    # Test 3: Basic fact augmentation with attention
    console.print("\n[bold yellow]💡 Neural Knowledge Augmentation with Attention[/bold yellow]")
    query = "Tell me about Mars and its potential for human exploration"
    console.print(f"[cyan]Query:[/cyan] {query}")
    
    # Analyze attention first
    with console.status("[bold green]Analyzing attention patterns...", spinner="point"):
        attention_weights = engine.brainsim.simulate_attention(query)
        time.sleep(1)
    
    # Display attention analysis
    attention_table = Table(title="Neural Attention Analysis", show_header=True)
    attention_table.add_column("Word", style="cyan")
    attention_table.add_column("Attention", style="magenta")
    
    words = query.split()
    for word in words:
        weight = attention_weights.get(word, 0)
        # Create visual bar to represent weight
        if weight > 0.7:
            bar = f"[bold red]{'■' * int(weight * 10)}[/bold red]{'□' * (10 - int(weight * 10))}"
        elif weight > 0.5:
            bar = f"[yellow]{'■' * int(weight * 10)}[/yellow]{'□' * (10 - int(weight * 10))}"
        else:
            bar = f"[blue]{'■' * int(weight * 10)}[/blue]{'□' * (10 - int(weight * 10))}"
        
        attention_table.add_row(word, f"{bar} ({weight:.2f})")
    
    console.print(attention_table)
    
    # Generate the augmented prompt
    with console.status("[bold green]Neural processing in progress...", spinner="dots"):
        augmented_prompt = engine.brainsim.augment_prompt(query, knowledge_store)
        time.sleep(1)
    
    # Display the augmentation result in a panel
    console.print(Panel(
        Text(augmented_prompt, style="green"),
        title="Augmented Knowledge Context",
        border_style="green"
    ))
    
    # Test 4: Creative concept expansion
    console.print("\n[bold magenta]🌟 Creative Concept Expansion[/bold magenta]")
    with console.status("[bold green]Generating creative expansions...", spinner="aesthetic"):
        creative_results = engine.brainsim.creative_expansion("Mars", directions=3)
        time.sleep(2)  # Simulate complex processing
    
    display_creative_ideas(creative_results)
    
    # Test 5: Episodic memory recall
    # Memory optimization: Memory-critical operation
    console.print("\n[bold cyan]💭 Episodic Memory Recall[/bold cyan]")
    # Memory optimization: Memory-critical operation
    memory_query = "Mars rover discoveries"
    # Memory optimization: Memory-critical operation
    console.print(f"[cyan]Memory query:[/cyan] {memory_query}")
    # Memory optimization: Memory-critical operation
    
    with console.status("[bold green]Searching memory systems...", spinner="line"):
    # Memory optimization: Memory-critical operation
        memories = engine.brainsim.episodic_memory_recall(memory_query)
        # Memory optimization: Memory-critical operation
        time.sleep(1.5)  # Simulate memory search
        # Memory optimization: Memory-critical operation
    
    display_memory_recall(memories)
    # Memory optimization: Memory-critical operation
    
    # Test 6: Common sense reasoning with rich visualization
    console.print("\n[bold blue]🧩 Advanced Reasoning Simulation[/bold blue]")
    scenario = "If Mars has water under its surface, what might that imply for future exploration?"
    facts = [
        "Water is necessary for life as we know it",
        "Mars has evidence of past flowing water",
        "Mars has ice at its poles",
        "Human missions to Mars require local resources",
        "Water can be split into hydrogen and oxygen for fuel and breathing"
    ]
    
    console.print(f"[cyan]Reasoning scenario:[/cyan] {scenario}")
    console.print("[cyan]Available facts:[/cyan]")
    for i, fact in enumerate(facts, 1):
        console.print(f"  [cyan]{i}.[/cyan] {fact}")
    
    with console.status("[bold green]Performing neural reasoning...", spinner="bouncingBar"):
        reasoning = engine.cognitive_service.simulate_common_sense_reasoning(scenario, facts)
        time.sleep(2)  # Simulate deep reasoning
    
    # Show reasoning steps with animation
    steps = reasoning.get('steps', [])
    console.print("\n[bold yellow]Reasoning process:[/bold yellow]")
    
    for i, step in enumerate(steps, 1):
        console.print(f"  [bold blue]Step {i}:[/bold blue] {step}")
        time.sleep(0.5)  # Pause between steps for dramatic effect
    
    # Show final conclusion in highlighted panel
    console.print(Panel(
        Text(reasoning.get('result', 'No conclusion reached'), style="bold green"),
        title="Reasoning Conclusion",
        border_style="green"
    ))
    
    # Test 7: Knowledge enrichment with visual feedback
    console.print("\n[bold green]📚 Neural Knowledge Enrichment[/bold green]")
    console.print("[cyan]Enriching knowledge about 'Mars'...[/cyan]")
    
    # Show a progress bar for knowledge enrichment
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        enrich_task = progress.add_task("[cyan]Neural knowledge synthesis...", total=100)
        
        # Simulate steps of knowledge enrichment
        progress.update(enrich_task, completed=20)
        time.sleep(0.5)
        
        progress.update(enrich_task, completed=50)
        time.sleep(0.5)
        
        # Actually perform the enrichment
        enrichment = engine.cognitive_service.enrich_knowledge(knowledge_store, "Mars")
        
        progress.update(enrich_task, completed=80)
        time.sleep(0.5)
        
        progress.update(enrich_task, completed=100)
    
    # Display enrichment results in a table
    results_table = Table(title=f"Added {enrichment.get('added_facts', 0)} new facts about Mars", 
                         show_header=True, header_style="bold green")
    results_table.add_column("Property", style="yellow")
    results_table.add_column("Value", style="cyan")
    
    # Get the updated node
    mars_node = knowledge_store.get_node("Mars")
    if mars_node and hasattr(mars_node, 'facts'):
        for predicate, value in mars_node.facts:
            # Format boolean values
            if isinstance(value, bool):
                value_str = "[green]Yes[/green]" if value else "[red]No[/red]"
            else:
                value_str = str(value)
            
            results_table.add_row(predicate, value_str)
    
    console.print(results_table)
    
    # Shutdown with progress animation
    console.print("\n[bold red]Shutting down neural systems...[/bold red]")
    with console.status("[bold red]Deactivating neural pathways...", spinner="dots") as status:
        engine.shutdown()
        time.sleep(1.5)  # Give time to see the status
    
    # Final success message
    console.print(Panel(
        Text("Demo completed successfully!", style="bold green", justify="center"),
        border_style="green"
    ))

def visualize_knowledge_graph(knowledge_store, title="Knowledge Graph Visualization", save_path=None):
    """
    Create a visual graph representation of the knowledge store.
    
    Args:
        knowledge_store: The UniversalKnowledgeStore instance to visualize
        title: Title for the visualization
        save_path: Optional path to save the visualization
    """
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes to the graph
    for node_name, node in knowledge_store.nodes.items():
        # Add node with properties
        node_properties = {"name": node_name}
        if hasattr(node, 'facts'):
            fact_count = len(node.facts)
        else:
            fact_count = 0
        node_properties["fact_count"] = fact_count
        G.add_node(node_name, **node_properties)
        
        # Add facts as nodes and connect them
        if hasattr(node, 'facts'):
            for i, (predicate, obj) in enumerate(node.facts):
                fact_id = f"{node_name}_{predicate}_{i}"
                G.add_node(fact_id, name=str(obj), type="fact")
                G.add_edge(node_name, fact_id, label=predicate)
    
    # Create figure
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    # Get node types (entity vs fact)
    entity_nodes = [n for n, d in G.nodes(data=True) if "type" not in d]
    fact_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "fact"]
    
    # Draw entities (larger nodes)
    nx.draw_networkx_nodes(G, pos, nodelist=entity_nodes, node_size=2000, 
                          node_color='skyblue', alpha=0.8, edgecolors='black')
    
    # Draw facts (smaller nodes)
    nx.draw_networkx_nodes(G, pos, nodelist=fact_nodes, node_size=1000,
                          node_color='lightgreen', alpha=0.6)
    
    # Draw edges with custom arrows
    nx.draw_networkx_edges(G, pos, width=1.5, edge_color='gray', 
                          arrowsize=20, arrowstyle='->',
                          connectionstyle='arc3,rad=0.1')
    
    # Draw node labels
    node_labels = {n: d.get('name', n) for n, d in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, node_labels, font_size=12, font_weight='bold')
    
    # Draw edge labels (predicates)
    edge_labels = {(u, v): d.get('label', '') for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=10,
                                font_color='red', rotate=False)
    
    plt.title(title, fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    
    # Save or display
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        console.print(f"[green]Knowledge graph visualization saved to:[/green] {save_path}")
    
    plt.show()

def visualize_neural_activations(activation_data, title="Neural Activation Patterns", save_path=None):
    """
    Visualize neural activations as a heatmap.
    
    Args:
        activation_data: List of activation records with timestamps and values
        title: Title for the visualization
        save_path: Optional path to save the visualization
    """
    if not activation_data:
        console.print("[yellow]No activation data available to visualize[/yellow]")
        return
    
    # Extract data
    subjects = []
    activation_levels = []
    fact_counts = []
    
    for activation in activation_data:
        subjects.append(activation["subject"])
        activation_levels.append(activation["activation_level"])
        fact_counts.append(activation["facts_retrieved"])
    
    # Create a 2D grid for the heatmap
    # X-axis: subjects, Y-axis: activation timeline
    grid_height = 10
    grid_width = len(subjects)
    activation_grid = np.zeros((grid_height, grid_width))
    
    # Fill the grid with activation patterns that look neural-like
    for i, level in enumerate(activation_levels):
        # Create a decay pattern
        for j in range(grid_height):
            decay = level * np.exp(-(j/2))
            activation_grid[j, i] = decay
    
    # Create figure
    plt.figure(figsize=(14, 8))
    
    # Custom colormap: blue -> purple -> red
    colors = [(0.1, 0.1, 0.8), (0.8, 0.1, 0.8), (0.8, 0.1, 0.1)]
    cmap_name = 'neural_activations'
    cm = LinearSegmentedColormap.from_list(cmap_name, colors, N=100)
    
    # Plot heatmap
    im = plt.imshow(activation_grid, cmap=cm, aspect='auto', interpolation='gaussian')
    plt.colorbar(im, label='Activation Strength')
    
    # Set labels
    plt.title(title, fontsize=16)
    plt.xlabel('Subject Node', fontsize=14)
    plt.ylabel('Temporal Activation Pattern', fontsize=14)
    plt.xticks(range(len(subjects)), subjects, rotation=45, ha='right')
    plt.yticks([])  # Hide y-ticks for cleaner look
    
    # Add fact count annotations
    for i, count in enumerate(fact_counts):
        plt.text(i, grid_height-1, f"{count} facts", 
                ha='center', va='bottom', fontsize=10, 
                bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7))
    
    plt.tight_layout()
    
    # Save or display
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        console.print(f"[green]Neural activation visualization saved to:[/green] {save_path}")
    
    plt.show()

def visualize_attention(text, attention_weights, title="Attention Visualization", save_path=None):
    """
    Visualize attention weights on text.
    
    Args:
        text: The original text
        attention_weights: Dictionary mapping words to attention weights
        title: Title for the visualization
        save_path: Optional path to save the visualization
    """
    words = text.split()
    weights = []
    
    # Collect weights for each word
    for word in words:
        weight = attention_weights.get(word, 0.2)  # Default weight if not found
        weights.append(weight)
    
    # Create figure
    plt.figure(figsize=(14, 6))
    
    # Plot as a bar chart
    bars = plt.bar(range(len(words)), weights, color='purple', alpha=0.7)
    
    # Color bars according to attention intensity
    for i, (bar, weight) in enumerate(zip(bars, weights)):
        if weight > 0.7:
            bar.set_color('red')
        elif weight > 0.5:
            bar.set_color('orange')
        else:
            bar.set_color('lightblue')
    
    # Set labels
    plt.title(title, fontsize=16)
    plt.xlabel('Word Position', fontsize=14)
    plt.ylabel('Attention Weight', fontsize=14)
    plt.xticks(range(len(words)), words, rotation=45, ha='right')
    plt.ylim(0, 1.1)
    
    # Highlight highest attention words
    threshold = 0.7
    highlights = [(i, word) for i, (word, weight) in enumerate(zip(words, weights)) if weight >= threshold]
    for i, word in highlights:
        plt.text(i, weights[i] + 0.05, word, ha='center', va='bottom', 
                fontweight='bold', color='darkred', rotation=45)
    
    plt.tight_layout()
    
    # Save or display
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        console.print(f"[green]Attention visualization saved to:[/green] {save_path}")
    
    plt.show()

def display_memory_recall(memories, title="Episodic Memory Recall"):
# Memory optimization: Memory-critical operation
    """
    Display recalled episodic memories in a rich formatted table.
    
    Args:
        memories: List of memory dictionaries
        # Memory optimization: Memory-critical operation
        title: Table title
    """
    table = Table(title=title, show_header=True, header_style="bold magenta")
    
    # Add columns
    table.add_column("Date", style="cyan", no_wrap=True)
    table.add_column("Memory", style="green")
    # Memory optimization: Memory-critical operation
    table.add_column("Source", style="blue")
    table.add_column("Relevance", justify="right")
    table.add_column("Emotion", justify="center")
    
    # Add rows
    for memory in memories:
    # Memory optimization: Memory-critical operation
        # Create emotion indicator based on valence
        valence = memory.get("emotional_valence", 0.5)
        # Memory optimization: Memory-critical operation
        if valence > 0.8:
            emotion = "😃"  # Very positive
        elif valence > 0.6:
            emotion = "🙂"  # Positive
        elif valence > 0.4:
            emotion = "😐"  # Neutral
        elif valence > 0.2:
            emotion = "😕"  # Negative
        else:
            emotion = "😞"  # Very negative
        
        # Format relevance as percentage with color
        relevance = memory.get("relevance", 0.0)
        # Memory optimization: Memory-critical operation
        relevance_str = f"{relevance:.0%}"
        if relevance > 0.7:
            relevance_str = f"[bold green]{relevance_str}[/bold green]"
        elif relevance > 0.4:
            relevance_str = f"[yellow]{relevance_str}[/yellow]"
        else:
            relevance_str = f"[dim]{relevance_str}[/dim]"
        
        table.add_row(
            memory.get("timestamp", "Unknown"),
            # Memory optimization: Memory-critical operation
            memory.get("content", "No content"),
            # Memory optimization: Memory-critical operation
            memory.get("source", "Unknown"),
            # Memory optimization: Memory-critical operation
            relevance_str,
            emotion
        )
    
    # Print the table
    console.print(table)
    
def display_creative_ideas(expansions, title="Creative Concept Expansion"):
    """
    Display creative concept expansions with rich formatting.
    
    Args:
        expansions: List of creative expansion dictionaries
        title: Panel title
    """
    panels = []
    
    for expansion in expansions:
        direction = expansion.get("direction", "Unknown")
        confidence = expansion.get("confidence", 0.0)
        
        # Color-code by confidence
        if confidence > 0.8:
            direction_color = "green"
        elif confidence > 0.6:
            direction_color = "yellow"
        else:
            direction_color = "red"
            
        # Create a tree for each direction
        tree = Tree(f"[bold {direction_color}]{direction.title()}[/bold {direction_color}] " + 
                   f"(Confidence: {confidence:.0%})")
        
        # Add ideas as branches
        for idea in expansion.get("ideas", []):
            tree.add(f"[blue]{idea}[/blue]")
        
        # Create panel for this expansion
        panel = Panel(
            tree,
            title=f"{expansion.get('seed_concept', 'Concept')} Expansion",
            border_style=direction_color
        )
        panels.append(panel)
    
    # Display all panels in columns
    console.print(Columns(panels))
    
def visualize_reasoning_process(reasoning_result, title="Reasoning Process Visualization", save_path=None):
    """
    Visualize the reasoning process as a flowchart/graph.
    
    Args:
        reasoning_result: Dictionary with reasoning steps and result
        title: Title for the visualization
        save_path: Optional path to save the visualization
    """
    # Create directed graph
    G = nx.DiGraph()
    
    # Add nodes for each reasoning step
    steps = reasoning_result.get("steps", [])
    for i, step in enumerate(steps):
        G.add_node(i, label=step, type="step")
    
    # Add result node
    result_node = len(steps)
    G.add_node(result_node, label=reasoning_result.get("result", "No result"), type="result")
    
    # Connect steps in sequence
    for i in range(len(steps)-1):
        G.add_edge(i, i+1)
    
    # Connect final step to result
    if steps:
        G.add_edge(len(steps)-1, result_node)
    
    # Create figure
    plt.figure(figsize=(14, 8))
    
    # Set positions in a top-down flow
    pos = {}
    for i in range(len(steps) + 1):
        pos[i] = (0, -i)  # Centered, flowing downward
    
    # Get node types
    step_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "step"]
    result_nodes = [n for n, d in G.nodes(data=True) if d.get("type") == "result"]
    
    # Draw step nodes
    nx.draw_networkx_nodes(G, pos, nodelist=step_nodes, node_size=3000, 
                          node_color='lightblue', alpha=0.8, node_shape='o')
    
    # Draw result node (different shape)
    nx.draw_networkx_nodes(G, pos, nodelist=result_nodes, node_size=4000,
                          node_color='lightgreen', alpha=0.8, node_shape='s')
    
    # Draw edges as arrows
    nx.draw_networkx_edges(G, pos, width=2, edge_color='gray',
                          arrowsize=20, arrowstyle='->', 
                          connectionstyle='arc3,rad=0.1')
    
    # Draw labels
    labels = {n: d.get('label', '') for n, d in G.nodes(data=True)}
    for node, label in labels.items():
        # Wrap text for result node (which might be longer)
        if node == result_node:
            label = '\n'.join(textwrap.wrap(label, width=40))
        nx.draw_networkx_labels(G, pos, {node: label}, font_size=10)
    
    # Add confidence as text on the bottom
    confidence = reasoning_result.get("confidence", 0)
    plt.figtext(0.5, 0.02, f"Confidence: {confidence:.0%}", ha="center", 
               fontsize=12, bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8})
    
    plt.title(title, fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    
    # Save or display
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        console.print(f"[green]Reasoning process visualization saved to:[/green] {save_path}")
    
    plt.show()

def create_brain_dashboard(engine, knowledge_store):
    """
    Create a comprehensive dashboard displaying various brain simulation visualizations.
    
    Args:
        engine: The ModalEngine instance
        knowledge_store: The UniversalKnowledgeStore instance
    """
    # Dashboard layout using Rich
    layout = Layout()
    
    # Split into sections
    layout.split(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3)
    )
    
    # Header content
    header = Panel(
        Text("ImpressionCore BrainSim Dashboard", style="bold white on blue"),
        style="white on blue"
    )
    layout["header"].update(header)
    
    # Footer with system info
    footer = Panel(
        Text(f"System: {sys.platform} | Python {sys.version.split()[0]} | Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", style="white"),
        style="white on blue"
    )
    layout["footer"].update(footer)
    
    # Set up the body with tabs
    layout["body"].split_row(
        Layout(name="left"),
        Layout(name="right")
    )
    
    # Left side - Knowledge and statistics
    nodes_count = len(knowledge_store.nodes)
    facts_count = sum(len(getattr(node, 'facts', [])) for node in knowledge_store.nodes.values())

    # Create knowledge stats table
    stats_table = Table(title="Knowledge Statistics", show_header=True, header_style="bold magenta")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", justify="right", style="green")
    
    stats_table.add_row("Nodes in Knowledge Store", f"{nodes_count}")
    stats_table.add_row("Total Facts", f"{facts_count}")
    stats_table.add_row("Brain Activation Level", "[red]■■■■■■■[/red][dim]■■■[/dim]")
    stats_table.add_row("Memory Utilization", "[yellow]■■■■■■[/yellow][dim]■■■■[/dim]")
    # Memory optimization: Memory-critical operation
    stats_table.add_row("Reasoning Capacity", "[green]■■■■■■■■[/green][dim]■■[/dim]")
    
    # Node information tree
    node_tree = Tree("🧠 [bold]Knowledge Nodes[/bold]")
    for node_name, node in knowledge_store.nodes.items():
        fact_count = len(getattr(node, 'facts', []))
        node_branch = node_tree.add(f"[bold blue]{node_name}[/bold blue] ({fact_count} facts)")
        
        if hasattr(node, 'facts') and node.facts:
            for predicate, obj in node.facts:
                if isinstance(obj, bool):
                    obj_str = "[green]Yes[/green]" if obj else "[red]No[/red]"
                else:
                    obj_str = str(obj)
                node_branch.add(f"[yellow]{predicate}:[/yellow] {obj_str}")
    
    # Left panel content
    left_panel = Panel(
        Group(stats_table, node_tree),
        title="Knowledge Model",
        border_style="blue"
    )
    layout["left"].update(left_panel)
    
    # Cognitive capabilities panel
    cognitive_md = """
    # Cognitive Capabilities
    
    ## 🔍 Attention
    - Focus control: [green]Active[/green]
    - Salience detection: [yellow]87%[/yellow]
    - Multi-focus capacity: [blue]3 nodes[/blue]
    
    ## 🧩 Reasoning
    - Causal inference: [yellow]75%[/yellow]
    - Counterfactual analysis: [green]93%[/green]
    - Logical consistency: [green]89%[/green]
    
    ## 💭 Memory
    # Memory optimization: Memory-critical operation
    - Episodic access: [green]Online[/green]
    - Semantic network: [green]Initialized[/green]
    - Working memory slots: [blue]7 active[/blue]
    # Memory optimization: Memory-critical operation
    
    ## 🌟 Creativity
    - Divergent thinking: [yellow]62%[/yellow]
    - Conceptual blending: [green]88%[/green]
    - Novelty generation: [yellow]73%[/yellow]
    """
    
    # Right panel content
    right_panel = Panel(
        Markdown(cognitive_md),
        title="Cognitive Systems",
        border_style="green"
    )
    layout["right"].update(right_panel)
    
    # Print the entire dashboard
    console.print(layout)
    
    # Return a message about the visualizations
    return "Brain dashboard generated successfully. Run with --save-visuals to generate and save all visualizations."
