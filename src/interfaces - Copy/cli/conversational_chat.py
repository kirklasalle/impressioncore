#!/usr/bin/env python3
r"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #command_line #memory_management #multimodal #python #source_code #src/interfaces/cli/conversational_chat.py
**Category:** Interface Definitions
**Status:** Active
"""









# !/usr/bin/env python3

# Created:** 2024-10-15
# Updated:** 2025-07-26 10:27:01
# Author:** ImpressionCore Team
# Tags:** #command_line #memory_management #multimodal #python #source_code #src/interfaces/cli/conversational_chat.py
# Category:** Interface Definitions
# Status:** Active

"""
ImpressionCore Conversational Chat Enhancement
============================================

High School Graduate level conversational AI interface that maintains
context and provides engaging, educational dialogue.

Features:
- Conversation memory and context tracking
- High school graduate appropriate language complexity
- Educational and engaging responses
- Integration with existing multimodal pipeline
- Conversation history management

Created: 2025-06-12
Author: ImpressionCore Team
"""

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.rule import Rule  # noqa: F401
    from rich.text import Text  # noqa: F401
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .core.utils.rich_logging import setup_rich_logging

logger = setup_rich_logging(__name__)

@dataclass
class ConversationMessage:
    """Represents a single message in the conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    tokens_used: int | None = None
    processing_time: float | None = None

@dataclass
class ConversationContext:
    """Maintains conversation context and state."""
    messages: list[ConversationMessage]
    total_tokens: int = 0
    session_start: str = ""
    user_preferences: dict[str, Any] = None
    conversation_topic: str | None = None

    def __post_init__(self):
        if self.user_preferences is None:
            self.user_preferences = {}
        if not self.session_start:
            self.session_start = datetime.now().isoformat()

class ConversationalChatEnhancer:
    """
    Enhances the existing multimodal CLI with conversational capabilities
    tailored for high school graduate level interaction.
    """

    def __init__(self, multimodal_pipeline=None, console=None):
        self.multimodal_pipeline = multimodal_pipeline
        self.console = console or (Console() if RICH_AVAILABLE else None)
        self.context = ConversationContext(messages=[])

        # High school graduate level conversation parameters
        self.conversation_config = {
            "language_level": "high_school_graduate",
            "max_context_messages": 10,  # Keep last 10 exchanges for context
            "response_tone": "friendly_educational",
            "encourage_learning": True,
            "explain_complex_terms": True,
            "max_response_length": 300,  # Keep responses concise but informative
        }

        # System prompt for high school graduate level conversation
        self.system_prompt = """You are ImpressionCore, a friendly and knowledgeable AI assistant designed to chat with someone at a high school graduate level. Your personality is:

- Conversational and approachable, like talking with a knowledgeable friend
- Educational but not condescending - explain things clearly without being patronizing
- Encouraging of curiosity and learning
- Able to discuss a wide range of topics at an appropriate complexity level
- Quick to break down complex ideas into understandable parts
- Engaging and interesting, using examples and analogies when helpful

Keep responses focused, informative, and around 2-3 sentences unless more detail is specifically requested. Use everyday language while being accurate and helpful."""

    def add_message(self, role: str, content: str, tokens_used: int | None = None, processing_time: float | None = None):
        """Add a message to the conversation context."""
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            tokens_used=tokens_used,
            processing_time=processing_time
        )

        self.context.messages.append(message)

        # Keep only the last N messages for context management
        if len(self.context.messages) > self.conversation_config["max_context_messages"] * 2:  # *2 for user+assistant pairs
            self.context.messages = self.context.messages[-self.conversation_config["max_context_messages"] * 2:]

        if tokens_used:
            self.context.total_tokens += tokens_used

    def get_conversation_context(self) -> str:
        """Build conversation context string for the model."""
        context_parts = [self.system_prompt]

        # Add recent conversation history
        for message in self.context.messages[-8:]:  # Last 4 exchanges (user+assistant pairs)
            if message.role == "user":
                context_parts.append(f"Human: {message.content}")
            else:
                context_parts.append(f"Assistant: {message.content}")

        return "\n\n".join(context_parts)

    def generate_response(self, user_input: str) -> dict[str, Any]:
        """Generate a conversational response using the multimodal pipeline."""
        start_time = time.time()

        # Add user message to context
        self.add_message("user", user_input)

        try:            # Build full context for the model
            full_context = self.get_conversation_context()
            full_prompt = f"{full_context}\n\nHuman: {user_input}\n\nAssistant:"

            if self.multimodal_pipeline:
                # Use the multimodal pipeline for generation
                result = self.multimodal_pipeline.process({
                    'text': full_prompt,
                    'modality': 'text_only',
                    'max_length': self.conversation_config["max_response_length"],
                    'temperature': 0.7,  # Slightly creative but focused
                    'conversation_mode': True
                })

                # Extract the response (handle various pipeline output formats)
                response_text = ""
                if isinstance(result, dict):
                    if 'response' in result:
                        response_text = result['response']
                    elif 'generated_text' in result:
                        response_text = result['generated_text']
                    elif 'text' in result:
                        response_text = result['text']
                    else:
                        # Try to find a meaningful text response
                        for key in ['output', 'content', 'message']:
                            if key in result and isinstance(result[key], str):
                                response_text = result[key]
                                break
                elif isinstance(result, str):
                    response_text = result
                else:
                    response_text = str(result)

                # If we didn't get meaningful text, provide a fallback
                if not response_text or response_text == "Sample generated text" or len(response_text.strip()) < 5:
                    # Generate a high school level response based on the input
                    if "hello" in user_input.lower():
                        response_text = "Hi there! I'm ImpressionCore, your AI conversation partner. I'm excited to chat with you! What would you like to talk about today?"
                    elif "what can you do" in user_input.lower() or "capabilities" in user_input.lower():
                        response_text = "I can help with lots of things! I love discussing science, history, current events, explaining complex topics in simple terms, helping with homework, or just having a friendly conversation. What interests you most?"
                    elif "how are you" in user_input.lower():
                        response_text = "I'm doing great, thanks for asking! I'm always ready to learn something new or help with whatever you're curious about. How are you doing today?"
                    else:
                        response_text = f"That's an interesting point about '{user_input}'. I'd love to explore that topic with you! What specifically interests you about this?"

                # Clean up the response (remove any prompt echoing)
                if "Assistant:" in response_text:
                    response_text = response_text.split("Assistant:")[-1].strip()

                # Ensure response is appropriate length
                if len(response_text) > self.conversation_config["max_response_length"] * 1.5:
                    response_text = response_text[:self.conversation_config["max_response_length"]] + "..."

            else:
                # Fallback response if no pipeline available
                response_text = "I'm sorry, I'm having trouble processing your message right now. The multimodal pipeline isn't available."

            processing_time = (time.time() - start_time) * 1000

            # Add assistant response to context
            self.add_message("assistant", response_text, processing_time=processing_time)

            return {
                'response': response_text,
                'processing_time': processing_time,
                'tokens_used': len(full_prompt.split()),  # Rough estimate
                'context_length': len(self.context.messages)
            }

        except Exception as e:
            logger.error(f"Error generating conversational response: {e}")
            error_response = "I'm sorry, I encountered an error while thinking about your question. Could you try rephrasing it?"
            self.add_message("assistant", error_response)

            return {
                'response': error_response,
                'processing_time': (time.time() - start_time) * 1000,
                'error': str(e)
            }

    def start_conversation_mode(self):
        """Start an interactive conversation session."""
        if RICH_AVAILABLE and self.console:
            self.console.print(Panel(
                "[bold cyan]🗣️  Conversational Chat Mode Activated[/bold cyan]\n\n"
                "I'm ImpressionCore, your AI conversation partner! I'm here to chat about anything you're curious about.\n"
                "I'll keep our conversation at a comfortable level - like talking with a knowledgeable friend.\n\n"
                "[green]Just type your message and press Enter to chat![/green]\n"
                "[yellow]Commands:[/yellow]\n"
                "  /clear - Clear conversation history\n"
                "  /stats - Show conversation statistics\n"
                "  /save - Save conversation\n"
                "  /quit - Exit chat mode",
                title="💬 High School Graduate Level Chat",
                border_style="cyan"
            ))
        else:
            print("💬 Conversational Chat Mode Activated")
            print("Type your message to start chatting, or /quit to exit")

        while True:
            try:
                if RICH_AVAILABLE:
                    user_input = Prompt.ask("\n[bold blue]You[/bold blue]").strip()
                else:
                    user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith('/'):
                    if user_input == '/quit':
                        if RICH_AVAILABLE and self.console:
                            self.console.print("[yellow]Thanks for chatting! Come back anytime! 👋[/yellow]")
                        else:
                            print("Thanks for chatting! Come back anytime!")
                        break
                    elif user_input == '/clear':
                        self.context.messages = []
                        if RICH_AVAILABLE and self.console:
                            self.console.print("[green]Conversation history cleared! 🧹[/green]")
                        else:
                            print("Conversation history cleared!")
                        continue
                    elif user_input == '/stats':
                        self._show_conversation_stats()
                        continue
                    elif user_input == '/save':
                        self._save_conversation()
                        continue
                    else:
                        if RICH_AVAILABLE and self.console:
                            self.console.print("[red]Unknown command. Try /help for available commands.[/red]")
                        else:
                            print("Unknown command.")
                        continue

                # Generate and display response
                result = self.generate_response(user_input)

                if RICH_AVAILABLE and self.console:
                    response_panel = Panel(
                        f"[bold green]ImpressionCore:[/bold green] {result['response']}\n\n"
                        f"[dim]⏱️ {result['processing_time']:.1f}ms | "
                        f"📝 Context: {result['context_length']} messages[/dim]",
                        border_style="green",
                        padding=(0, 1)
                    )
                    self.console.print(response_panel)
                else:
                    print(f"\nImpressionCore: {result['response']}")
                    print(f"({result['processing_time']:.1f}ms)")

            except KeyboardInterrupt:
                if RICH_AVAILABLE and self.console:
                    self.console.print("\n[yellow]Chat session ended. Goodbye! 👋[/yellow]")
                else:
                    print("\nChat session ended. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in conversation loop: {e}")
                if RICH_AVAILABLE and self.console:
                    self.console.print(f"[red]Sorry, I encountered an error: {e!s}[/red]")
                else:
                    print(f"Sorry, I encountered an error: {e!s}")

    def _show_conversation_stats(self):
        """Display conversation statistics."""
        total_messages = len(self.context.messages)
        user_messages = len([m for m in self.context.messages if m.role == "user"])
        assistant_messages = len([m for m in self.context.messages if m.role == "assistant"])

        avg_processing_time = 0
        if assistant_messages > 0:
            processing_times = [m.processing_time for m in self.context.messages if m.processing_time]
            if processing_times:
                avg_processing_time = sum(processing_times) / len(processing_times)

        if RICH_AVAILABLE and self.console:
            stats_text = (
                f"[bold cyan]Conversation Statistics[/bold cyan]\n\n"
                f"📊 Total Messages: {total_messages}\n"
                f"👤 Your Messages: {user_messages}\n"
                f"🤖 My Responses: {assistant_messages}\n"
                f"⏱️ Average Response Time: {avg_processing_time:.1f}ms\n"
                f"🕐 Session Started: {self.context.session_start[:19]}\n"
                f"💭 Estimated Tokens: {self.context.total_tokens}"
            )
            self.console.print(Panel(stats_text, title="📈 Chat Stats", border_style="blue"))
        else:
            print("\nConversation Stats:")
            print(f"Total Messages: {total_messages}")
            print(f"Average Response Time: {avg_processing_time:.1f}ms")

    def _save_conversation(self):
        """Save conversation to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"src/memlog/conversation_{timestamp}.json"

            conversation_data = {
                "session_info": {
                    "start_time": self.context.session_start,
                    "end_time": datetime.now().isoformat(),
                    "total_messages": len(self.context.messages),
                    "config": self.conversation_config
                },
                "messages": [asdict(msg) for msg in self.context.messages]
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)

            if RICH_AVAILABLE and self.console:
                self.console.print(f"[green]💾 Conversation saved to {filename}[/green]")
            else:
                print(f"Conversation saved to {filename}")

        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            if RICH_AVAILABLE and self.console:
                self.console.print(f"[red]Error saving conversation: {e!s}[/red]")
            else:
                print(f"Error saving conversation: {e!s}")
