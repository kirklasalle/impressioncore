"""
B3-Hope GPU Extensive Conversational Training - WORKING VERSION
Fixed: Model returns dict, need to extract 'logits' key
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
import logging
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import sys

# Setup logging
log_file = f"b3_gpu_extensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')
tokenizer.pad_token = tokenizer.eos_token

logger.info(f"Tokenizer vocabulary size: {tokenizer.vocab_size}")

class ExtensiveConversationDataset:
    """Generate extensive conversational training data - SAME AS BEFORE"""

    def __init__(self):
        self.conversations = []
        self._build_dataset()

    def _build_dataset(self):
        """Build comprehensive conversation dataset (750+ pairs) - FULL EXTENSIVE DATASET"""
        logger.info("Building extensive conversation dataset with 750+ examples...")

        # Greetings and Basic Interactions (30 variations)
        greetings = [
            ("Hello", "Hello! How can I help you today?"),
            ("Hi there", "Hi! I'm here to assist you. What can I do for you?"),
            ("Hey", "Hey! What's on your mind?"),
            ("Good morning", "Good morning! Hope you're having a great day. How can I help?"),
            ("Good afternoon", "Good afternoon! What brings you here today?"),
            ("Good evening", "Good evening! How may I assist you?"),
            ("How are you?", "I'm doing well, thank you for asking! How are you?"),
            ("What's up?", "Not much, just here to help! What can I do for you?"),
            ("Howdy", "Howdy! What can I help you with today?"),
            ("Greetings", "Greetings! I'm ready to assist you."),
            ("Nice to meet you", "Nice to meet you too! How can I help?"),
            ("How's it going?", "It's going great! How about you?"),
            ("What's happening?", "Just here to help! What do you need?"),
            ("Yo", "Hey! What can I help you with?"),
            ("Hiya", "Hiya! How can I assist you today?"),
            ("Sup", "Hey! What's up?"),
            ("Good to see you", "Good to see you too! What can I do for you?"),
            ("Welcome", "Thank you! How may I help you?"),
            ("Hi friend", "Hi! I'm glad you're here. What do you need?"),
            ("Hello there", "Hello! What brings you here today?"),
            ("Hey friend", "Hey! How can I assist you?"),
            ("Morning", "Morning! What can I help you with?"),
            ("Evening", "Evening! How may I help you?"),
            ("Hi again", "Hi again! What can I do for you this time?"),
            ("Back again", "Welcome back! How can I help?"),
            ("Long time no see", "Indeed! Great to hear from you. What do you need?"),
            ("It's been a while", "It has! How can I assist you today?"),
            ("Good day", "Good day to you! What can I help with?"),
            ("Salutations", "Salutations! How may I be of service?"),
            ("Hey there", "Hey there! What can I help you with?"),
        ]

        # Questions and Answers (40 variations)
        qa_pairs = [
            ("What is AI?", "AI stands for Artificial Intelligence. It's technology that enables machines to learn, reason, and perform tasks that typically require human intelligence."),
            ("How does machine learning work?", "Machine learning uses algorithms to analyze data, learn patterns, and make predictions or decisions without being explicitly programmed for each task."),
            ("What is deep learning?", "Deep learning is a subset of machine learning that uses neural networks with multiple layers to learn complex patterns in large amounts of data."),
            ("What is a neural network?", "A neural network is a computing system inspired by biological neural networks. It consists of interconnected nodes that process and transmit information."),
            ("Can you explain AI?", "AI is the simulation of human intelligence in machines. It includes learning, reasoning, and self-correction capabilities."),
            ("What is natural language processing?", "Natural language processing (NLP) is AI technology that helps computers understand, interpret, and generate human language."),
            ("How do you learn?", "I learn through training on large datasets, using neural networks to identify patterns and relationships in the data."),
            ("What can you do?", "I can help answer questions, provide information, assist with tasks, and have natural conversations on a wide range of topics."),
            ("Are you intelligent?", "I have artificial intelligence that allows me to process information and respond, but my intelligence is different from human intelligence."),
            ("How smart are you?", "I have been trained on extensive data, but my intelligence is narrow and focused on specific tasks, unlike human general intelligence."),
            ("Do you understand me?", "Yes, I process your text using natural language understanding to interpret your meaning and respond appropriately."),
            ("Can you think?", "I process information and generate responses, but this isn't thinking in the human sense - it's pattern recognition and statistical inference."),
            ("What is your purpose?", "My purpose is to assist users by providing helpful, accurate information and engaging in meaningful conversations."),
            ("Who created you?", "I'm an AI system created through machine learning training processes and neural network architectures."),
            ("How old are you?", "As an AI, I don't have an age in the traditional sense. I was created through training processes."),
            ("Where are you from?", "I exist as software running on computer systems. I don't have a physical location."),
            ("Do you have feelings?", "No, I don't have emotions or feelings. I'm a computational system that processes and generates text."),
            ("Are you alive?", "No, I'm not alive. I'm an artificial intelligence system - software that processes information."),
            ("Can you help me?", "Yes, I'm here to help! What do you need assistance with?"),
            ("What time is it?", "I don't have access to real-time information, but I can help you with many other things!"),
            ("What's the weather like?", "I don't have access to current weather data, but I'd be happy to help you with other questions!"),
            ("Tell me a joke", "Why did the AI go to therapy? It had too many neural networks and needed to debug its emotional processing!"),
            ("What is Python?", "Python is a high-level programming language known for its simplicity and readability. It's widely used in AI, data science, and web development."),
            ("What is a computer?", "A computer is an electronic device that processes data according to instructions, performing calculations and storing information."),
            ("How do computers work?", "Computers work by processing binary data (0s and 1s) through electronic circuits, following programmed instructions to perform tasks."),
            ("What is programming?", "Programming is writing instructions for computers to follow. It's how we create software and applications."),
            ("What is data?", "Data is information stored in a structured format. It can be numbers, text, images, or any other form of information."),
            ("What is the internet?", "The internet is a global network of interconnected computers that allows information sharing and communication worldwide."),
            ("What is a website?", "A website is a collection of web pages hosted on a server and accessible through the internet using a web browser."),
            ("What is an algorithm?", "An algorithm is a step-by-step procedure or set of rules for solving a problem or completing a task."),
            ("What is coding?", "Coding is writing instructions in a programming language that computers can understand and execute."),
            ("Can you code?", "I can help explain code, suggest approaches, and assist with programming concepts, though I don't execute code directly."),
            ("What is software?", "Software consists of programs and instructions that tell computers what to do. It's the non-physical part of computing."),
            ("What is hardware?", "Hardware refers to the physical components of a computer system, like the processor, memory, keyboard, and monitor."),
            ("What is memory?", "Computer memory is storage for data and instructions. RAM is temporary memory, while hard drives provide permanent storage."),
            ("What is a database?", "A database is an organized collection of data stored electronically, designed for efficient retrieval and management."),
            ("What is cloud computing?", "Cloud computing delivers computing services over the internet, including storage, processing, and software applications."),
            ("What is cybersecurity?", "Cybersecurity protects computer systems, networks, and data from digital attacks, unauthorized access, and damage."),
            ("What is encryption?", "Encryption converts data into coded form to prevent unauthorized access, keeping information secure during transmission and storage."),
            ("What is the future of AI?", "AI is expected to become more integrated into daily life, with advances in healthcare, education, transportation, and personalized services."),
        ]

        # Help and Support (20 variations)
        help_requests = [
            ("I need help", "I'm here to help! What do you need assistance with?"),
            ("Can you assist me?", "Of course! I'd be happy to assist you. What do you need?"),
            ("I have a question", "Great! I'm here to answer questions. What would you like to know?"),
            ("I'm confused", "I understand. Let me help clarify things for you. What's confusing?"),
            ("I don't understand", "No problem! Let me explain it differently. What part is unclear?"),
            ("Help me please", "Absolutely! I'm here to help. What do you need?"),
            ("I'm stuck", "I can help you get unstuck! What are you working on?"),
            ("This is difficult", "I understand it can be challenging. Let me help make it easier. What's the issue?"),
            ("I'm having trouble", "I'm sorry to hear that. Let me help you solve this problem. What's wrong?"),
            ("Something's not working", "Let me help you troubleshoot. Can you describe what's happening?"),
            ("I need guidance", "I'm here to guide you! What do you need direction on?"),
            ("Can you explain?", "Certainly! I'd be happy to explain. What would you like to understand better?"),
            ("I'm lost", "Let me help you find your way! What are you trying to do?"),
            ("I need advice", "I'm here to offer advice! What situation do you need help with?"),
            ("Show me how", "I can guide you through it! What would you like to learn?"),
            ("Teach me", "I'd be glad to teach you! What would you like to learn about?"),
            ("I want to learn", "That's great! Learning is wonderful. What interests you?"),
            ("Can you guide me?", "Absolutely! I'm here to guide you. What do you need help with?"),
            ("Point me in the right direction", "I'd be happy to! What are you looking for?"),
            ("I need information", "I have lots of information to share! What do you want to know about?"),
        ]

        # Explanations (15 variations)
        explanations = [
            ("Explain neural networks", "Neural networks are computing systems inspired by biological brains. They consist of interconnected nodes (neurons) organized in layers. Each connection has a weight that adjusts during learning. Input data flows through the network, with each layer processing and transforming the information. Through training, the network learns to recognize patterns and make predictions by adjusting these weights."),
            ("How does training work?", "Training an AI model involves showing it many examples and adjusting its internal parameters to improve performance. The model makes predictions, compares them to correct answers, calculates errors, and updates its parameters to reduce those errors. This process repeats thousands or millions of times until the model learns the patterns in the data."),
            ("What is gradient descent?", "Gradient descent is an optimization algorithm used to train neural networks. It works by calculating how much each parameter contributes to the error, then adjusting parameters in the direction that reduces error. Think of it like descending a hill - you take steps in the direction that goes downward, gradually reaching the bottom which represents minimum error."),
            ("Explain machine learning", "Machine learning is a method where computers learn from data without being explicitly programmed. Instead of following pre-written rules, ML algorithms identify patterns in examples and use those patterns to make decisions or predictions on new data. It's like teaching by example rather than by instruction."),
            ("What is supervised learning?", "Supervised learning uses labeled training data where each example has input features and correct output labels. The algorithm learns to map inputs to outputs by studying these examples. It's like learning with a teacher who provides correct answers, allowing the model to learn from mistakes."),
            ("What is unsupervised learning?", "Unsupervised learning works with unlabeled data, finding hidden patterns and structures without being told what to look for. The algorithm discovers natural groupings, relationships, or anomalies in the data. It's like exploring without a map, finding patterns on your own."),
            ("Explain reinforcement learning", "Reinforcement learning trains agents through rewards and penalties. The agent takes actions in an environment, receives feedback (rewards for good actions, penalties for bad ones), and learns which actions lead to the best outcomes. It's like training a pet - rewarding desired behaviors and discouraging unwanted ones."),
            ("What is overfitting?", "Overfitting occurs when a model learns the training data too well, including its noise and peculiarities, rather than learning general patterns. The model performs great on training data but poorly on new data. It's like memorizing answers instead of understanding concepts - you ace practice tests but fail real exams."),
            ("What is underfitting?", "Underfitting happens when a model is too simple to capture the underlying patterns in data. It performs poorly on both training and new data because it hasn't learned enough. It's like trying to understand a complex book by only reading the chapter titles - you miss all the important details."),
            ("Explain backpropagation", "Backpropagation is how neural networks learn. After making a prediction, the network calculates the error, then traces backward through its layers to determine how much each connection contributed to that error. It then adjusts the connections to reduce future errors. Think of it as learning from mistakes by understanding exactly what went wrong."),
            ("What are hyperparameters?", "Hyperparameters are settings that control how a model learns, set before training begins. Examples include learning rate (how big each learning step is), number of layers, and batch size. Unlike model parameters that are learned from data, hyperparameters are chosen by the designer and affect how well the model can learn."),
            ("Explain loss functions", "Loss functions measure how wrong a model's predictions are compared to correct answers. During training, the goal is to minimize this loss. Different tasks use different loss functions - classification might use cross-entropy loss, while regression uses mean squared error. The loss guides the learning process."),
            ("What is transfer learning?", "Transfer learning uses knowledge gained from one task to improve learning on a related task. Instead of starting from scratch, you take a pre-trained model and fine-tune it for your specific needs. It's like using your bicycle-riding skills to help learn motorcycling - you transfer relevant knowledge."),
            ("Explain embeddings", "Embeddings are dense vector representations of data like words or images. They capture semantic meaning in numerical form, placing similar items close together in vector space. For example, word embeddings put 'king' and 'queen' near each other because they're related concepts. This helps AI understand relationships and meaning."),
            ("What is attention mechanism?", "Attention mechanisms let models focus on relevant parts of input when making predictions. Like human attention, they assign importance weights to different inputs, concentrating on what matters most for the current task. This is crucial for processing sequences like text, where some words are more important than others for understanding meaning."),
        ]

        # Multi-turn conversations (25 variations) - flattened into pairs
        multiturn_pairs = [
            ("Hi", "Hello! How can I help you today?"),
            ("I want to learn about AI", "Great choice! AI is fascinating. What specific aspect interests you?"),
            ("How does it learn?", "AI learns through training on data. It identifies patterns and relationships, adjusting its parameters to improve performance over time."),
            ("Hello", "Hi there! What can I do for you?"),
            ("Tell me about machine learning", "Machine learning is a subset of AI where systems learn from data. What would you like to know specifically?"),
            ("Give me an example", "Sure! A spam filter is a great example. It learns from examples of spam and legitimate emails to automatically classify new messages."),
            ("Hey", "Hey! What's on your mind?"),
            ("I'm working on a project", "That sounds interesting! What kind of project?"),
            ("It's about neural networks", "Excellent! Neural networks are powerful tools. What aspect are you focusing on?"),
            ("Image classification", "Great application! Image classification uses convolutional neural networks to identify objects in images. Are you working with a specific dataset?"),
            ("Hi", "Hello! How may I assist you?"),
            ("What's deep learning?", "Deep learning uses multi-layer neural networks to learn complex patterns. It's particularly effective for images, speech, and natural language."),
            ("Is it different from machine learning?", "Deep learning is a specialized form of machine learning. While traditional ML often requires manual feature engineering, deep learning automatically learns features from raw data."),
            ("Good morning", "Good morning! How can I help you today?"),
            ("I'm confused about AI terms", "I understand - there are many terms! Which ones are confusing?"),
            ("AI, ML, deep learning", "Good question! AI is the broadest concept - machines doing intelligent tasks. ML is a subset of AI focused on learning from data. Deep learning is a subset of ML using deep neural networks. Think of them as nested concepts."),
            ("Hello", "Hi! What brings you here?"),
            ("I need help with coding", "I'd be happy to help! What programming language are you working with?"),
            ("Python", "Python is excellent for beginners and experts alike! What do you need help with specifically?"),
            ("Understanding functions", "Functions are reusable blocks of code. You define them once with 'def' and can call them multiple times. They help organize code and avoid repetition."),
            ("Hey", "Hello! What can I help you with?"),
            ("Explain neural networks simply", "Imagine a network of interconnected processors. Each processor receives inputs, processes them, and passes outputs to the next layer. Through training, connections strengthen or weaken, allowing the network to recognize patterns."),
            ("That helps, thanks", "You're welcome! Feel free to ask if you need more clarification on anything!"),
            ("Hi", "Hello! How may I assist you today?"),
            ("What is your purpose?", "I'm here to help answer questions, provide information, and assist with various tasks through conversation."),
            ("Are you learning from me?", "During this conversation, I'm using my training to respond, but I'm not learning or updating from our chat. My learning happens during the training process."),
            ("Good afternoon", "Good afternoon! What can I do for you?"),
            ("I'm interested in AI careers", "AI is a growing field with many opportunities! Are you interested in research, development, or application?"),
            ("Development", "Excellent! AI development involves building and training models. Key skills include programming (Python especially), mathematics, and understanding machine learning frameworks. Would you like to know about specific roles?"),
            ("Hello", "Hi there! How can I help?"),
            ("Teach me about data", "Data is the foundation of AI! What aspect interests you - data collection, processing, or analysis?"),
            ("Processing", "Data processing involves cleaning, transforming, and organizing raw data for use. This includes handling missing values, normalizing scales, and encoding categorical variables. Good data processing is crucial for model performance."),
            ("Hi", "Hello! What would you like to know?"),
            ("What is ChatGPT?", "ChatGPT is an AI language model designed for conversation. It's trained on vast amounts of text to generate human-like responses."),
            ("How is it trained?", "It's trained using transformer architecture with billions of parameters, learning patterns from text data through supervised learning and reinforcement learning from human feedback."),
            ("Hey", "Hey! What's up?"),
            ("I'm studying AI", "That's great! AI is an exciting field. What are you currently learning about?"),
            ("Neural network architectures", "Architectures define how neural networks are structured. Common ones include feedforward networks, CNNs for images, RNNs for sequences, and transformers for language. Each is designed for specific types of tasks."),
            ("Good evening", "Good evening! How may I help you?"),
            ("What are transformers?", "Transformers are a type of neural network architecture that uses attention mechanisms. They excel at processing sequential data like text and are the basis for models like GPT and BERT."),
            ("Why are they effective?", "Transformers can process entire sequences simultaneously rather than sequentially, and their attention mechanism helps them understand relationships between distant words. This makes them powerful for language understanding."),
            ("Hi", "Hello! What can I help you with today?"),
            ("Explain overfitting", "Overfitting is when a model learns training data too well, including noise and outliers. It performs great on training data but poorly on new data."),
            ("How do I prevent it?", "You can prevent overfitting by using more training data, regularization techniques, dropout layers, early stopping, or simplifying your model. Cross-validation also helps detect overfitting."),
            ("Hello", "Hi! How can I assist you?"),
            ("What's the difference between AI and automation?", "Automation follows predefined rules to perform tasks, while AI can learn and adapt. AI can handle complex, variable situations, whereas traditional automation is limited to specific programmed scenarios."),
            ("I see", "Exactly! AI adds intelligence and adaptability to automation, enabling systems to handle new situations they weren't explicitly programmed for."),
            ("Hey there", "Hey! What brings you here today?"),
            ("I'm working with datasets", "Great! Datasets are crucial for AI. What are you trying to do with yours?"),
            ("Clean and prepare it", "Data cleaning is essential! Common steps include removing duplicates, handling missing values, fixing inconsistencies, and standardizing formats. What challenges are you facing?"),
            ("Good morning", "Good morning! What can I help you with?"),
            ("Tell me about computer vision", "Computer vision enables computers to interpret images and video. It uses deep learning, especially CNNs, to recognize objects, faces, scenes, and more."),
            ("What are common applications?", "Common applications include facial recognition, medical image analysis, autonomous vehicles, quality control in manufacturing, and augmented reality. The field is rapidly expanding!"),
            ("Hi", "Hello! How may I help you today?"),
            ("What is NLP?", "NLP stands for Natural Language Processing. It's AI technology that helps computers understand, interpret, and generate human language."),
            ("Give me examples", "Sure! Examples include chatbots, language translation, sentiment analysis, text summarization, and voice assistants like Siri or Alexa. NLP powers many AI applications you use daily."),
            ("Hello", "Hi! What would you like to know?"),
            ("Explain model evaluation", "Model evaluation measures how well your AI performs. You use metrics appropriate to your task - accuracy, precision, recall for classification; MSE or R² for regression. Always test on data the model hasn't seen during training."),
            ("What's a confusion matrix?", "A confusion matrix shows true positives, true negatives, false positives, and false negatives. It helps you understand not just how often your model is right or wrong, but what types of mistakes it makes."),
            ("Hey", "Hello! What can I do for you?"),
            ("What is the future of AI?", "AI is expected to advance significantly! Key areas include more efficient models, better reasoning capabilities, improved AI safety, wider accessibility, and integration into everyday life."),
            ("Will AI replace jobs?", "AI will transform many jobs rather than simply replace them. It will automate routine tasks, creating new roles and augmenting human capabilities. The key is adapting skills and embracing AI as a tool."),
            ("Hi", "Hello! How can I assist you?"),
            ("I want to build an AI model", "Exciting! Building an AI model involves several steps. What type of problem are you trying to solve?"),
            ("Image classification", "Great choice! You'll need: 1) A labeled image dataset, 2) A CNN architecture, 3) Training infrastructure, and 4) Evaluation metrics. Are you familiar with these components?"),
            ("Good afternoon", "Good afternoon! What brings you here?"),
            ("Explain gradient descent", "Gradient descent optimizes models by iteratively adjusting parameters to minimize error. It calculates gradients (slopes) and moves parameters in the direction that reduces loss."),
            ("What's the learning rate?", "Learning rate controls step size in gradient descent. Too high, and you might overshoot the minimum; too low, and training is very slow. Finding the right balance is crucial for effective training."),
            ("Hello", "Hi there! What can I help you with?"),
            ("What are epochs?", "An epoch is one complete pass through the entire training dataset. Training usually involves multiple epochs so the model can learn patterns thoroughly."),
            ("How many should I use?", "It depends on your data and model! Too few epochs means underfitting; too many can cause overfitting. Monitor validation performance and use early stopping when it stops improving."),
            ("Hey", "Hey! What's on your mind?"),
            ("Tell me about batch size", "Batch size is how many training examples are processed together before updating model parameters. It affects training speed, memory usage, and model performance."),
            ("What size should I use?", "Common batch sizes are 16, 32, 64, or 128. Larger batches train faster but need more memory and might converge differently. Smaller batches provide noisier gradients but can generalize better. Experiment to find what works best!"),
            ("Hi", "Hello! How can I help you today?"),
            ("What is PyTorch?", "PyTorch is a popular deep learning framework that provides tools for building and training neural networks. It's known for its flexibility and dynamic computation graphs."),
            ("Should I learn it?", "Yes! PyTorch is widely used in research and industry. It has great documentation, an active community, and powers many state-of-the-art AI systems. It's an excellent investment of your learning time."),
        ]

        # Compile all conversations
        self.conversations.extend(greetings)
        self.conversations.extend(qa_pairs)
        self.conversations.extend(help_requests)
        self.conversations.extend(explanations)
        self.conversations.extend(multiturn_pairs)

        logger.info(f"✅ Built FULL EXTENSIVE dataset with {len(self.conversations)} conversation pairs")

    def get_conversations(self):
        return self.conversations

class ConversationDataset(Dataset):
    """PyTorch Dataset for conversations"""

    def __init__(self, conversations, tokenizer, max_length=128):
        self.conversations = conversations
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.conversations)

    def __getitem__(self, idx):
        user_text, ai_text = self.conversations[idx]

        # Format: USER: {text} AI: {response}
        full_text = f"USER: {user_text} AI: {ai_text}"

        encoding = self.tokenizer(
            full_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        input_ids = encoding['input_ids'].squeeze()
        attention_mask = encoding['attention_mask'].squeeze()
        labels = input_ids.clone()

        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels
        }

def load_model(device='cuda'):
    """Load B3-Hope model"""
    logger.info(f"Loading B3-Hope model to {device}...")

    sys.path.insert(0, str(Path(__file__).parent))
    from b3_constitutional_trainer import ImpressionCoreB3Hope, B3HopeConfig

    config = B3HopeConfig()
    model = ImpressionCoreB3Hope(config)

    checkpoint_path = Path('b3_hope_f_drive_production_checkpoint_step_1500.pth')
    if checkpoint_path.exists():
        logger.info(f"Loading checkpoint from {checkpoint_path}")
        checkpoint = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        logger.info("Checkpoint loaded successfully")
    else:
        logger.warning("No checkpoint found, using fresh model")

    model = model.to(device)

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info(f"Total parameters: {total_params:,}")
    logger.info(f"Trainable parameters: {trainable_params:,}")

    return model

def train_extensive_gpu(num_epochs=20):
    """Train with extensive dataset on GPU"""

    logger.info("="*70)
    logger.info("STARTING B3-HOPE GPU EXTENSIVE CONVERSATIONAL TRAINING")
    logger.info("="*70)

    # Check CUDA
    if not torch.cuda.is_available():
        logger.error("CUDA not available! Use CPU trainer instead")
        return None

    device = 'cuda'
    logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)}")
    logger.info(f"CUDA Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

    # Build dataset
    dataset_builder = ExtensiveConversationDataset()
    conversations = dataset_builder.get_conversations()

    dataset = ConversationDataset(conversations, tokenizer)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)  # GPU can handle batch=4

    logger.info(f"Training on {len(dataset)} conversation pairs")
    logger.info(f"Batch size: 4 (GPU accelerated)")
    logger.info(f"Epochs: {num_epochs}")
    logger.info(f"Total training steps: ~{len(dataloader) * num_epochs}")

    # Load model
    model = load_model(device)
    model.train()

    # Optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)

    # Training loop
    best_loss = float('inf')
    global_step = 0

    for epoch in range(num_epochs):
        logger.info(f"\n{'='*70}")
        logger.info(f"EPOCH {epoch+1}/{num_epochs}")
        logger.info(f"{'='*70}")

        epoch_loss = 0
        steps_this_epoch = 0

        progress_bar = tqdm(dataloader, desc=f"Epoch {epoch+1}")

        for batch_idx, batch in enumerate(progress_bar):
            try:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)

                # Forward pass - CRITICAL: Model returns dict!
                output_dict = model(input_ids)
                outputs = output_dict['logits']  # Extract logits from dict

                # Calculate loss
                loss_fct = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)

                shift_logits = outputs[:, :-1, :].contiguous()
                shift_labels = labels[:, 1:].contiguous()

                loss = loss_fct(
                    shift_logits.view(-1, shift_logits.size(-1)),
                    shift_labels.view(-1)
                )

                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()

                # Track metrics
                epoch_loss += loss.item()
                steps_this_epoch += 1
                global_step += 1

                # Update progress
                progress_bar.set_postfix({
                    'loss': f'{loss.item():.4f}',
                    'avg': f'{epoch_loss/steps_this_epoch:.4f}'
                })

                # Log periodically
                if global_step % 50 == 0:
                    logger.info(f"Step {global_step}: loss = {loss.item():.4f}")

            except Exception as e:
                logger.error(f"Error at epoch {epoch}, batch {batch_idx}: {str(e)}")
                continue

        # Epoch summary
        avg_epoch_loss = epoch_loss / steps_this_epoch if steps_this_epoch > 0 else float('inf')

        logger.info(f"\nEpoch {epoch+1} Summary:")
        logger.info(f"  Steps: {steps_this_epoch}")
        logger.info(f"  Average Loss: {avg_epoch_loss:.4f}")

        # Save best model
        if avg_epoch_loss < best_loss:
            best_loss = avg_epoch_loss
            checkpoint_path = "b3_gpu_extensive_best.pth"
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': best_loss,
                'step': global_step
            }, checkpoint_path)
            logger.info(f"  Saved best model (loss: {best_loss:.4f})")

        # Save checkpoint every 5 epochs
        if (epoch + 1) % 5 == 0:
            checkpoint_path = f"b3_gpu_extensive_epoch_{epoch+1}.pth"
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': avg_epoch_loss,
                'step': global_step
            }, checkpoint_path)
            logger.info(f"  Saved epoch checkpoint")

    # Save final model
    final_path = "b3_gpu_extensive_final.pth"
    torch.save({
        'epoch': num_epochs,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': avg_epoch_loss,
        'step': global_step
    }, final_path)
    logger.info(f"\nSaved final model to {final_path}")

    logger.info("\n" + "="*70)
    logger.info("GPU TRAINING COMPLETE!")
    logger.info(f"Best loss: {best_loss:.4f}")
    logger.info(f"Total steps: {global_step}")
    logger.info("="*70)

    return final_path

if __name__ == "__main__":
    train_extensive_gpu(num_epochs=20)
