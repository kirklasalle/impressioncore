#!/usr/bin/env python3
"""
ImpressionCore - Brain-Inspired Multimodal AI Framework

File: src\examples\brainsim_knowledge_demo_fixed.py
Project: ImpressionCore - Brain-Inspired Multimodal AI Framework
Created: 2025-05-25
Modified: 2025-05-25
Version: 1.0.0

Authors:
- Kirk LaSalle & GitHub Copilot

License: MIT
Copyright (c) 2025 ImpressionCore Team

Tags: [examples]
Dependencies: [] # TODO: Auto-detect or allow manual input
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)

Description:
# TODO: Add a brief description of this file's purpose.

Design Philosophy:
# TODO: Add design philosophy if applicable.

Memory Considerations:
# TODO: Document any specific memory considerations for this file.

Examples:
# TODO: Provide usage examples if applicable.

Notes:
# TODO: Add any relevant notes.
"""
\n\n"""
Enhanced BrainSim demo with knowledge integration and rich visualizations.

This script demonstrates how to integrate external knowledge with BrainSim
for improved reasoning and responses, with enhanced visual output.
"""

import os
import sys
import logging
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich import print as rprint
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.traceback import install
from rich.tree import Tree

# Install rich traceback handler for better error visualization
install(show_locals=True)

# Initialize rich console
console = Console()

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent  # Go up to impressioncore root
sys.path.append(str(project_root))

# Import BrainSim components
from src.brainsim.brainsim import BrainSim

# Import Knowledge Store components - using proper imports
from src.core.knowledge.uks import UniversalKnowledgeStore, KnowledgeNode

# Define simple versions of needed components that weren't found
class BrainCore:
    """Simple BrainCore implementation."""
    
    def __init__(self):
        self.brain_sim = BrainSim()
        self.working_memory = None
        self.long_term_memory = None
        self.reasoning_engine = None
    
    def set_memory(self, working_memory, long_term_memory):
        """Set memory components."""
        self.working_memory = working_memory
        self.long_term_memory = long_term_memory
    
    def set_reasoning_engine(self, reasoning_engine):
        """Set reasoning engine component."""
        self.reasoning_engine = reasoning_engine
    
    def process(self, query):
        """Process a query using available components."""
        # Extract concepts using BrainSim
        concepts = self.brain_sim.extract_concepts(query)
        
        # Use intent analysis from BrainSim
        intent = self.brain_sim.analyze_intent(query)
        
        # Create a simple response based on the query
        if "brainsim" in query.lower():
            return "BrainSim is a brain-inspired cognitive architecture for intelligent processing."
        elif "memory" in query.lower():
            return "Memory systems in cognitive architectures store and retrieve information as needed."
        elif "neural" in query.lower():
            return "Neural processing involves neurons exchanging signals through synapses."
        elif "cognitive" in query.lower():
            return "Cognitive architectures model intelligent behavior through structured computational processes."
        else:
            return f"I processed your query about {', '.join(concepts)}. It seems you're interested in learning more about this topic."


class WorkingMemory:
    """Simple WorkingMemory implementation."""
    
    def __init__(self):
        self.memory = {}
    
    def store(self, key, value):
        """Store a value in working memory."""
        self.memory[key] = value
    
    def retrieve(self, key):
        """Retrieve a value from working memory."""
        return self.memory.get(key)


class LongTermMemory:
    """Simple LongTermMemory implementation."""
    
    def __init__(self):
        self.memory = {}
    
    def store(self, key, value):
        """Store a value in long-term memory."""
        self.memory[key] = value
    
    def retrieve(self, key):
        """Retrieve a value from long-term memory."""
        return self.memory.get(key)


class ReasoningEngine:
    """Simple ReasoningEngine implementation."""
    
    def __init__(self):
        self.brain_sim = BrainSim()
    
    def reason(self, scenario, facts):
        """Perform reasoning on a scenario with facts."""
        return self.brain_sim.common_sense_reason(scenario, facts)


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def create_knowledge_store():
    """Create and populate a knowledge store with basic facts."""
    console.log("[bold green]Creating knowledge store with basic facts...")
    
    # Create knowledge store
    uks = UniversalKnowledgeStore()
    
    # Add knowledge about BrainSim
    brainsim = KnowledgeNode("BrainSim")
        brainsim.add_attribute("type", "software")  # Using add_attribute instead of set_attribute
        brainsim.add_attribute("purpose", "cognitive simulation")
        brainsim.add_attribute("description", "BrainSim is a brain-inspired cognitive architecture that simulates human-like reasoning processes")
        uks.add_node(brainsim)
        
        # Add components
        components = [
            {"name": "WorkingMemory", "purpose": "stores temporary information currently being processed"},
            {"name": "LongTermMemory", "purpose": "stores persistent knowledge that can be recalled when needed"},
            {"name": "ReasoningEngine", "purpose": "applies different reasoning strategies to solve problems"},
            {"name": "BrainCore", "purpose": "coordinates all components and manages information flow"}
        ]
        
        for comp in components:
            component = KnowledgeNode(comp["name"])
            component.add_attribute("type", "component")  # Using add_attribute
            component.add_attribute("purpose", comp["purpose"])
            uks.add_node(component)
            
            # Using add_relationship instead of add_relation
            uks.add_relationship("BrainSim", "has_component", comp["name"])
        
        # Add knowledge about neural processing
        neural = KnowledgeNode("Neural Processing")
        neural.add_attribute("type", "concept")  # Using add_attribute
        neural.add_attribute("description", "Neural processing involves neurons exchanging signals through synapses, with patterns of activity representing information")
        uks.add_node(neural)
        
        # Add knowledge about cognitive architecture
        cognitive = KnowledgeNode("Cognitive Architecture")
        cognitive.add_attribute("type", "concept")  # Using add_attribute
        cognitive.add_attribute("description", "A cognitive architecture is a blueprint for intelligent agents, defining the computational structures underlying cognition")
        uks.add_node(cognitive)  # Add node first before creating relationships
        
        # Add components of cognitive architecture
        arch_components = [
            {"name": "Perception", "desc": "Processes sensory input"},
            {"name": "Attention", "desc": "Focuses processing on relevant information"},
            {"name": "Working Memory", "desc": "Maintains current context and goals"},
            {"name": "Long-term Memory", "desc": "Stores facts and relationships"},
            {"name": "Reasoning", "desc": "Applies different strategies to solve problems"},
            {"name": "Learning", "desc": "Improves performance based on experience"},
            {"name": "Executive Function", "desc": "Coordinates cognitive processes and decision making"}
        ]
        
        for comp in arch_components:
            component = KnowledgeNode(comp["name"])
            component.add_attribute("type", "cognitive_component")  # Using add_attribute
            component.add_attribute("description", comp["desc"])
            uks.add_node(component)
            
            # Using add_relationship instead of add_relation
            uks.add_relationship("Cognitive Architecture", "includes", comp["name"])
    
    console.log(f"[green]Created knowledge store with [bold]{len(uks.nodes)}[/bold] nodes")
    return uks

class EnhancedBrainSim:
    """
    Enhanced BrainSim with knowledge integration.
    
    This class integrates BrainSim with the Universal Knowledge Store
    for improved reasoning and responses.
    """
    
    def __init__(self):
        """Initialize EnhancedBrainSim."""
        console.log("[bold green]Initializing Enhanced BrainSim...")
            
        # Create BrainSim components
        self.brain_core = BrainCore()
        self.working_memory = WorkingMemory()
        self.long_term_memory = LongTermMemory()
        self.reasoning_engine = ReasoningEngine()
        
        # Connect components
        self.brain_core.set_memory(self.working_memory, self.long_term_memory)
        self.brain_core.set_reasoning_engine(self.reasoning_engine)
        
        # Create and integrate knowledge store
        self.knowledge_store = create_knowledge_store()
        
        # Populate long-term memory with knowledge from UKS
        self._populate_memory_from_knowledge()
        
        console.log("[bold green]EnhancedBrainSim initialized successfully ✓")
    
    def _populate_memory_from_knowledge(self):
        """Populate long-term memory with knowledge from UKS."""
        # For each node in the knowledge store
        for node_id, node in self.knowledge_store.nodes.items():
            # Create a memory entry with node attributes
            memory_key = f"knowledge_{node_id.lower().replace(' ', '_')}"
            
            # Create a structured representation of the node
            memory_value = {
                "name": node.name,
                "attributes": node.attributes,
                "type": node.get_attribute("type") if "type" in node.attributes else "unknown",
                "description": node.get_attribute("description") if "description" in node.attributes else ""
            }
            
            # Add related nodes
            related = []
            for relation in node.relations:
                target_name = relation["target"]
                if target_name in self.knowledge_store.nodes:
                    related.append({
                        "relation": relation["type"],
                        "target": target_name
                    })
            
            memory_value["related"] = related
            
            # Store in long-term memory
            self.long_term_memory.store(memory_key, memory_value)
    
    def process_query(self, query):
        """
        Process a query using BrainSim and knowledge integration.
        
        Args:
            query: The query to process
            
        Returns:
            Response text
        """
        # First, store query in working memory
        self.working_memory.store("current_query", query)
        
        # Try to find relevant knowledge in UKS
        keywords = query.lower().replace("?", "").replace(".", "").split()
        relevant_nodes = []
        
        for keyword in keywords:
            if len(keyword) > 3:  # Skip short words
                # Find nodes with keyword in name or attributes
                for node_id, node in self.knowledge_store.nodes.items():
                    if (keyword in node.name.lower() or 
                        any(keyword in str(v).lower() for v in node.attributes.values())):
                        relevant_nodes.append(node)
        
        # Remove duplicates while preserving order
        unique_nodes = []
        unique_ids = set()
        for node in relevant_nodes:
            if node.name not in unique_ids:
                unique_nodes.append(node)
                unique_ids.add(node.name)
        
        # If we found relevant knowledge
        if unique_nodes:
            # Store the relevant knowledge in working memory
            self.working_memory.store("relevant_knowledge", [
                {"name": node.name, "attributes": node.attributes} 
                for node in unique_nodes[:3]  # Limit to top 3 most relevant
            ])
            
            # Generate a knowledge-enhanced response
            relevant_info = []
            for node in unique_nodes[:3]:
                desc = node.get_attribute("description") if "description" in node.attributes else ""
                if desc:
                    relevant_info.append(desc)
            
            if relevant_info:
                # Use the description directly for a more informative response
                return relevant_info[0]
        
        # If no specific knowledge found or multiple nodes, fall back to BrainSim
        return self.brain_core.process(query)
    
def main():
    """Run the enhanced BrainSim demo with rich visualizations."""
    console.print(Panel.fit(
        "[bold cyan]Enhanced BrainSim Demo[/bold cyan]\n"
        "[yellow]With Knowledge Integration and Rich Visualizations[/yellow]",
        border_style="green"
    ))
    
    try:
        # Create enhanced BrainSim
        brain = EnhancedBrainSim()
        
        # Define demo questions
        questions = [
            "What is BrainSim?",
            "How does neural processing work?",
            "What are the components of cognitive architecture?",
            "What is working memory?",
            "How is reasoning implemented in BrainSim?",
            "What is the difference between working memory and long-term memory?"
        ]
        
        # Process each question with nice visuals
        table = Table(title="BrainSim Knowledge Demo Results", show_header=True, header_style="bold magenta")
        table.add_column("Question", style="dim", width=50)
        table.add_column("Response", style="green")
        table.add_column("Time", justify="right")
        
        # Create a progress bar for processing questions
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn()
        ) as progress:
            process_task = progress.add_task("[cyan]Processing queries...", total=len(questions))
            
            for question in questions:
                # Time the response
                start_time = time.time()
                response = brain.process_query(question)
                elapsed = time.time() - start_time
                
                # Add result to table
                table.add_row(
                    question,
                    response,
                    f"{elapsed:.3f}s"
                )
                
                # Update progress
                progress.update(process_task, advance=1)
        
        # Display the results table
        console.print(table)
        
        # Show a knowledge graph visualization
        console.print("\n[bold green]Knowledge Graph Sample:[/bold green]")
        tree = Tree("[bold yellow]BrainSim[/bold yellow]")
        components = tree.add("[bold blue]Components[/bold blue]")
        components.add("[green]WorkingMemory[/green]")
        components.add("[green]LongTermMemory[/green]")
        components.add("[green]ReasoningEngine[/green]")
        components.add("[green]BrainCore[/green]")
        
        console.print(tree)
        
        console.print(Panel("[bold green]Demo completed successfully![/bold green]", border_style="green"))
        
    except Exception as e:
        console.print_exception()
        logger.error(f"Error running demo: {e}", exc_info=True)
        
if __name__ == "__main__":
    main()
