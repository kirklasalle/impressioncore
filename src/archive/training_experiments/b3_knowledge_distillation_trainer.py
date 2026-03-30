"""
Path A: Knowledge Distillation Trainer
Train B3-Hope (student) to learn from DialoGPT-medium (teacher)

Created: October 6, 2025
Status: Path A Implementation
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from training.b3_constitutional_trainer import B3HopeConfig, ImpressionCoreB3Hope
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()


class ConversationDataset(Dataset):
    """Dataset for conversation pairs"""

    def __init__(self, conversations, tokenizer, max_length=128):
        self.conversations = conversations
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.conversations)

    def __getitem__(self, idx):
        conv = self.conversations[idx]

        # Format as dialogue
        text = f"Human: {conv['context']}\nAssistant: {conv['response']}"

        # Tokenize
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'labels': encoding['input_ids'].squeeze(0).clone()
        }


class KnowledgeDistillationTrainer:
    """Train student model via knowledge distillation from teacher"""

    def __init__(
        self,
        student_checkpoint: str = "F:/models/checkpoints/b3/b3_massive_final.pth",
        teacher_name: str = "microsoft/DialoGPT-medium",
        teacher_cache: str = "F:/models/teachers/dialogpt_medium",
        output_dir: str = "F:/models/checkpoints/b3/distillation",
        device: str = 'cuda'
    ):
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        console.print("\n[cyan]="*40)
        console.print("[bold cyan]🎓 KNOWLEDGE DISTILLATION TRAINER")
        console.print("[cyan]="*40 + "\n")

        # Load tokenizer
        console.print("📚 Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            teacher_name,
            cache_dir=teacher_cache
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        console.print("✅ Tokenizer loaded\n")

        # Load teacher model
        console.print("🎓 Loading teacher model (DialoGPT-medium, 354M params)...")
        self.teacher = AutoModelForCausalLM.from_pretrained(
            teacher_name,
            cache_dir=teacher_cache,
            use_safetensors=True
        ).to(self.device)
        self.teacher.eval()  # Teacher always in eval mode
        for param in self.teacher.parameters():
            param.requires_grad = False  # Freeze teacher
        console.print("✅ Teacher loaded and frozen\n")

        # Load student model
        console.print("🎒 Loading student model (B3-Hope, 35.5M params)...")
        config = B3HopeConfig()
        self.student = ImpressionCoreB3Hope(config).to(self.device)

        # Load checkpoint if exists
        if Path(student_checkpoint).exists():
            checkpoint = torch.load(student_checkpoint, map_location='cpu', weights_only=False)
            self.student.load_state_dict(checkpoint['model_state_dict'])
            console.print(f"✅ Student loaded from {student_checkpoint}\n")
        else:
            console.print("⚠️  No checkpoint found, using fresh initialization\n")

        # Optimizer
        self.optimizer = torch.optim.AdamW(
            self.student.parameters(),
            lr=5e-5,
            weight_decay=0.01
        )

        console.print("[green]✅ Distillation trainer initialized!")
        console.print(f"[cyan]Device: {self.device}")
        console.print(f"[cyan]Teacher params: {sum(p.numel() for p in self.teacher.parameters()):,}")
        console.print(f"[cyan]Student params: {sum(p.numel() for p in self.student.parameters()):,}")
        console.print(f"[cyan]Compression ratio: {sum(p.numel() for p in self.teacher.parameters()) / sum(p.numel() for p in self.student.parameters()):.1f}x\n")

    def distillation_loss(self, student_logits, teacher_logits, labels, temperature=2.0, alpha=0.5):
        """
        Compute distillation loss

        Args:
            student_logits: Student model output logits
            teacher_logits: Teacher model output logits
            labels: Ground truth labels
            temperature: Temperature for soft targets (higher = softer)
            alpha: Weight for distillation loss vs hard loss (0-1)

        Returns:
            Combined loss
        """
        # Soft targets loss (KL divergence between teacher and student)
        soft_loss = F.kl_div(
            F.log_softmax(student_logits / temperature, dim=-1),
            F.softmax(teacher_logits / temperature, dim=-1),
            reduction='batchmean'
        ) * (temperature ** 2)

        # Hard targets loss (standard cross-entropy)
        hard_loss = F.cross_entropy(
            student_logits.view(-1, student_logits.size(-1)),
            labels.view(-1),
            ignore_index=self.tokenizer.pad_token_id
        )

        # Combine losses
        total_loss = alpha * soft_loss + (1 - alpha) * hard_loss

        return total_loss, soft_loss.item(), hard_loss.item()

    def create_simple_dataset(self, num_samples=1000):
        """Create a simple conversation dataset for initial training"""

        console.print(f"\n📝 Generating {num_samples} simple conversation pairs...")

        conversations = []

        # Template-based simple conversations
        templates = [
            # Greetings
            {"context": "Hello", "response": "Hello! How can I help you today?"},
            {"context": "Hi there", "response": "Hi! What can I do for you?"},
            {"context": "Good morning", "response": "Good morning! How are you?"},
            {"context": "How are you?", "response": "I'm doing well, thank you! How about you?"},

            # Questions about AI
            {"context": "What is AI?", "response": "AI stands for Artificial Intelligence. It's the simulation of human intelligence by machines."},
            {"context": "What is machine learning?", "response": "Machine learning is a subset of AI where computers learn from data without being explicitly programmed."},
            {"context": "What is deep learning?", "response": "Deep learning uses neural networks with many layers to learn complex patterns from large amounts of data."},
            {"context": "Explain neural networks", "response": "Neural networks are computing systems inspired by the human brain, consisting of interconnected nodes that process information."},

            # General knowledge
            {"context": "What is Python?", "response": "Python is a popular programming language known for its simplicity and readability. It's widely used in AI and data science."},
            {"context": "What is a computer?", "response": "A computer is an electronic device that processes data and performs calculations according to programmed instructions."},
            {"context": "What is the internet?", "response": "The internet is a global network connecting millions of computers worldwide, enabling communication and information sharing."},

            # Capabilities
            {"context": "What can you do?", "response": "I can help answer questions, explain concepts, and have conversations on various topics."},
            {"context": "Can you help me?", "response": "Yes, I'd be happy to help! What do you need assistance with?"},
            {"context": "Tell me about yourself", "response": "I'm an AI assistant designed to help answer questions and provide information on various topics."},

            # Gratitude
            {"context": "Thank you", "response": "You're welcome! Let me know if you need anything else."},
            {"context": "Thanks for your help", "response": "I'm glad I could help! Feel free to ask if you have more questions."},
        ]

        # Repeat templates to reach num_samples
        while len(conversations) < num_samples:
            conversations.extend(templates)

        conversations = conversations[:num_samples]

        console.print(f"✅ Generated {len(conversations)} conversation pairs\n")

        return conversations

    def train_epoch(self, dataloader, epoch, total_epochs, temperature=2.0, alpha=0.5):
        """Train for one epoch"""

        self.student.train()

        total_loss = 0
        total_soft_loss = 0
        total_hard_loss = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task(
                f"[cyan]Epoch {epoch}/{total_epochs}",
                total=len(dataloader)
            )

            for batch_idx, batch in enumerate(dataloader):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)

                # Forward pass through student
                student_outputs = self.student(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    return_loss=False
                )
                student_logits = student_outputs['logits']

                # Forward pass through teacher
                with torch.no_grad():
                    teacher_outputs = self.teacher(
                        input_ids=input_ids,
                        attention_mask=attention_mask
                    )
                    teacher_logits = teacher_outputs.logits

                # Compute distillation loss
                loss, soft_loss, hard_loss = self.distillation_loss(
                    student_logits, teacher_logits, labels, temperature, alpha
                )

                # Backward pass
                self.optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.student.parameters(), 1.0)
                self.optimizer.step()

                # Accumulate losses
                total_loss += loss.item()
                total_soft_loss += soft_loss
                total_hard_loss += hard_loss

                progress.update(task, advance=1)

        avg_loss = total_loss / len(dataloader)
        avg_soft = total_soft_loss / len(dataloader)
        avg_hard = total_hard_loss / len(dataloader)

        return avg_loss, avg_soft, avg_hard

    def train(self, num_epochs=20, batch_size=4, temperature=2.0, alpha=0.5):
        """Run complete distillation training"""

        console.print("\n[cyan]="*40)
        console.print("[bold cyan]🚀 STARTING KNOWLEDGE DISTILLATION")
        console.print("[cyan]="*40 + "\n")

        # Create dataset
        conversations = self.create_simple_dataset(num_samples=1000)
        dataset = ConversationDataset(conversations, self.tokenizer)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        console.print(f"[green]Training Configuration:")
        console.print(f"  Epochs: {num_epochs}")
        console.print(f"  Batch size: {batch_size}")
        console.print(f"  Dataset size: {len(dataset)}")
        console.print(f"  Steps per epoch: {len(dataloader)}")
        console.print(f"  Temperature: {temperature}")
        console.print(f"  Alpha (distillation weight): {alpha}")
        console.print(f"  Learning rate: {self.optimizer.param_groups[0]['lr']}")
        console.print()

        start_time = datetime.now()

        # Training loop
        for epoch in range(1, num_epochs + 1):
            avg_loss, avg_soft, avg_hard = self.train_epoch(
                dataloader, epoch, num_epochs, temperature, alpha
            )

            console.print(f"\n[green]Epoch {epoch}/{num_epochs} Complete:")
            console.print(f"  Total Loss: {avg_loss:.4f}")
            console.print(f"  Soft Loss (KL Div): {avg_soft:.4f}")
            console.print(f"  Hard Loss (CE): {avg_hard:.4f}")

            # Save checkpoint every 5 epochs
            if epoch % 5 == 0:
                checkpoint_path = self.output_dir / f"b3_distilled_epoch{epoch}.pth"
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.student.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'loss': avg_loss,
                }, checkpoint_path)
                console.print(f"[cyan]  💾 Checkpoint saved: {checkpoint_path}")

            console.print()

        # Save final model
        final_path = self.output_dir / "b3_distilled_final.pth"
        torch.save({
            'epoch': num_epochs,
            'model_state_dict': self.student.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'loss': avg_loss,
        }, final_path)

        elapsed = datetime.now() - start_time

        console.print("\n[cyan]="*40)
        console.print("[bold green]✅ DISTILLATION TRAINING COMPLETE!")
        console.print("[cyan]="*40)
        console.print(f"\n[green]Final Model: {final_path}")
        console.print(f"[green]Training Time: {elapsed}")
        console.print(f"[green]Final Loss: {avg_loss:.4f}")
        console.print("\n[yellow]Next: Test the distilled model for conversation quality!")
        console.print()


def main():
    """Main entry point"""

    trainer = KnowledgeDistillationTrainer()
    trainer.train(
        num_epochs=20,
        batch_size=4,
        temperature=2.0,
        alpha=0.7  # 70% distillation, 30% hard targets
    )


if __name__ == "__main__":
    main()
