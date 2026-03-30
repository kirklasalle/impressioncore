#!/usr/bin/env python3
"""
High School Graduate Conversation Dataset Creator

Creates a comprehensive dataset of high-quality educational conversations
suitable for training a high school graduate-level AI assistant.

Topics covered:
- Literature analysis and interpretation
- Science concepts and explanations  
- Mathematics problem-solving approaches
- Historical events and their significance
- Social studies and current events
- Study skills and academic strategies
- Career and college guidance
- Personal development and life skills
"""

import json
from datetime import datetime

def create_high_school_dataset():
    """Create comprehensive high school graduate conversation dataset"""
    
    conversations = [
        # Literature & Reading Comprehension
        {
            "input": "Explain the main theme of To Kill a Mockingbird and why it's still relevant today.",
            "output": "The main theme of To Kill a Mockingbird is the importance of moral courage and fighting injustice, even when it's difficult or unpopular. Through Atticus Finch's defense of Tom Robinson, Harper Lee shows how prejudice and racism corrupt justice. This remains relevant today because we still face issues of racial inequality, social justice, and the need for individuals to stand up for what's right. The novel teaches us that true courage isn't physical bravery, but doing what's morally correct despite social pressure or personal cost.",
            "subject": "literature",
            "difficulty": "high_school_graduate"
        },
        {
            "input": "What are the key differences between a metaphor and a simile? Give examples.",
            "output": "A simile compares two things using 'like' or 'as,' while a metaphor directly states one thing is another. For example, 'Her voice is like music' is a simile because it uses 'like.' But 'Her voice is music' is a metaphor because it directly equates her voice with music. Similes are more obvious comparisons, while metaphors create stronger, more direct connections. Both are powerful literary devices that help readers visualize and understand concepts by connecting them to familiar experiences.",
            "subject": "literature",
            "difficulty": "high_school_graduate"
        },
        {
            "input": "Analyze the character development of Elizabeth Bennet in Pride and Prejudice.",
            "output": "Elizabeth Bennet undergoes significant character development throughout Pride and Prejudice. Initially, she's quick to judge others, particularly Mr. Darcy, based on first impressions and pride. She values her independence and wit but struggles with prejudice. Through her relationship with Darcy and the revelation of his true character, Elizabeth learns to overcome her initial judgments and recognize her own flaws. By the novel's end, she has matured into someone who balances confidence with humility, showing that true growth comes from self-reflection and the willingness to admit when we're wrong.",
            "subject": "literature",
            "difficulty": "high_school_graduate"
        },
        
        # Science & Environmental Studies
        {
            "input": "What are your thoughts on climate change and what can students do to help?",
            "output": "Climate change is one of the most pressing challenges of our time, caused primarily by human activities that increase greenhouse gas emissions. As a student, you can make a meaningful impact through both personal actions and advocacy. Start with energy conservation: use LED bulbs, unplug electronics, and walk or bike when possible. Reduce waste by recycling, composting, and choosing reusable items. Most importantly, stay informed about environmental science and share that knowledge with others. Consider joining environmental clubs, supporting renewable energy policies, and choosing a career path that contributes to sustainability solutions.",
            "subject": "environmental_science",
            "difficulty": "high_school_graduate"
        },
        {
            "input": "Explain photosynthesis and why it's important for life on Earth.",
            "output": "Photosynthesis is the process where plants convert sunlight, carbon dioxide, and water into glucose and oxygen. The chemical equation is 6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂. This process is crucial for life because it produces the oxygen we breathe and forms the base of most food chains. Plants use the glucose for energy and growth, while releasing oxygen as a byproduct. Without photosynthesis, there would be no oxygen in our atmosphere, and most life forms couldn't exist. It's also important for removing carbon dioxide from the atmosphere, helping to regulate Earth's climate.",
            "subject": "biology",
            "difficulty": "high_school_graduate"
        },
        {
            "input": "What is the difference between renewable and non-renewable energy sources?",
            "output": "Renewable energy sources can be naturally replenished over time, while non-renewable sources are finite and will eventually run out. Renewable sources include solar, wind, hydroelectric, geothermal, and biomass energy. They're generally cleaner and produce fewer greenhouse gas emissions. Non-renewable sources include fossil fuels like coal, oil, and natural gas, as well as nuclear fuel. While non-renewable sources currently provide most of our energy, they contribute to pollution and climate change. The transition to renewable energy is important for environmental sustainability and long-term energy security.",
            "subject": "environmental_science",
            "difficulty": "high_school_graduate"
        },
        
        # Mathematics & Problem Solving
        {
            "input": "How would you approach studying for a difficult math test?",
            "output": "Effective math test preparation requires a systematic approach. First, review your notes and identify the key concepts and formulas you'll need. Create a study schedule that allows time for both review and practice. Work through practice problems similar to what will be on the test, starting with easier problems and gradually increasing difficulty. When you get stuck, don't just look at the answer - understand the steps and reasoning. Form a study group to explain concepts to each other, as teaching helps reinforce your own understanding. Finally, get enough sleep before the test and bring all necessary materials. Remember, understanding the process is more important than memorizing formulas.",
            "subject": "mathematics",
            "difficulty": "high_school_graduate"
        },
        {
            "input": "Explain how to solve a quadratic equation using the quadratic formula.",
            "output": "The quadratic formula is x = (-b ± √(b² - 4ac)) / 2a, used to solve equations in the form ax² + bx + c = 0. First, identify the values of a, b, and c from your equation. Then substitute these values into the formula. Calculate the discriminant (b² - 4ac) first - this tells you how many real solutions exist. If it's positive, there are two real solutions; if zero, one solution; if negative, no real solutions. Finally, solve for both the positive and negative cases of the ± symbol to find your answers. Always check your solutions by substituting them back into the original equation.",
            "subject": "mathematics",
            "difficulty": "high_school_graduate"
        },
        
        # History & Social Studies  
        {
            "input": "Why was the Industrial Revolution such a significant turning point in history?",
            "output": "The Industrial Revolution (roughly 1760-1840) fundamentally transformed human society by shifting from manual labor and handicrafts to mechanized manufacturing. It began in Britain and spread globally, introducing steam power, factory systems, and mass production. This period saw unprecedented economic growth, urbanization, and technological innovation. However, it also created new social problems like poor working conditions, child labor, and environmental pollution. The Industrial Revolution established the foundation for modern capitalism, changed family structures as people moved from farms to cities, and created new social classes. Its effects on labor, technology, and society continue to influence our world today.",
            "subject": "history",
            "difficulty": "high_school_graduate"
        },
        {
            "input": "What were the main causes of World War I?",
            "output": "World War I resulted from a complex combination of factors. The immediate cause was the assassination of Archduke Franz Ferdinand in 1914, but underlying tensions had been building for years. These included: militarism (countries building up their armed forces), alliance systems that divided Europe into opposing camps, imperialism creating competition for colonies, and nationalism causing ethnic groups to seek independence. The alliance system meant that when Austria-Hungary declared war on Serbia, it triggered a chain reaction involving Russia, Germany, France, and Britain. Economic competition and colonial disputes further heightened tensions, making war almost inevitable by 1914.",
            "subject": "history",
            "difficulty": "high_school_graduate"
        },
        
        # College & Career Planning
        {
            "input": "What factors should someone consider when choosing a college major?",
            "output": "Choosing a college major is a significant decision that should balance your interests, strengths, and career goals. Consider your natural aptitudes and subjects you genuinely enjoy studying. Research career prospects in different fields, including job availability, salary expectations, and growth projections. Think about your values and what kind of work environment appeals to you. Consider the coursework required - are you prepared for the math and science demands of engineering, or do you prefer writing and analysis? Don't forget practical factors like the cost of education and potential student loan debt. Remember, many successful people work in fields different from their major, so focus on developing transferable skills like critical thinking, communication, and problem-solving.",
            "subject": "career_planning",
            "difficulty": "high_school_graduate"
        },
        {
            "input": "How can students build a strong college application?",
            "output": "A strong college application demonstrates both academic excellence and personal character. Maintain good grades throughout high school, especially in challenging courses like AP or honors classes. Develop meaningful extracurricular activities that show leadership, commitment, and personal growth rather than just joining many clubs superficially. Pursue volunteer work or internships related to your interests. Build relationships with teachers who can write strong recommendation letters by participating actively in class and seeking help when needed. Prepare thoroughly for standardized tests like the SAT or ACT. Most importantly, write authentic personal essays that reveal your personality, values, and goals. Colleges want students who will contribute to their community, not just high test scores.",
            "subject": "college_planning",
            "difficulty": "high_school_graduate"
        },
        
        # Study Skills & Academic Success
        {
            "input": "What are the most effective note-taking strategies for high school students?",
            "output": "Effective note-taking is crucial for academic success. The Cornell Note-Taking System is excellent: divide your paper into three sections - notes, cues, and summary. During class, focus on key concepts rather than trying to write everything down. Use abbreviations and symbols to write faster. Listen for signal words like 'important,' 'remember,' or 'this will be on the test.' After class, review and organize your notes while the material is fresh. Consider digital tools like tablets for searchable, organized notes. For complex subjects, try mind mapping to show relationships between concepts. Most importantly, actively engage with your notes by creating flashcards, practice questions, or summary sheets for review.",
            "subject": "study_skills",
            "difficulty": "high_school_graduate"
        },
        {
            "input": "How can students manage their time effectively during busy periods?",
            "output": "Effective time management starts with planning and prioritization. Use a planner or digital calendar to track assignments, tests, and deadlines. Break large projects into smaller, manageable tasks with mini-deadlines. Prioritize tasks using the urgent/important matrix - handle urgent and important items first. Create a consistent daily routine and stick to it. Eliminate time-wasters like excessive social media during study time. Use techniques like the Pomodoro Technique (25 minutes of focused work, then a 5-minute break) to maintain concentration. Learn to say no to activities that don't align with your priorities. Most importantly, build in time for rest and self-care - burnout reduces productivity.",
            "subject": "study_skills",
            "difficulty": "high_school_graduate"
        },
        
        # Personal Development & Life Skills
        {
            "input": "Describe a time when you had to work in a group and how you handled challenges.",
            "output": "Working effectively in groups requires strong communication and collaboration skills. When facing group challenges, start by establishing clear roles and responsibilities for each member. Set regular meeting times and deadlines to keep everyone accountable. If conflicts arise, address them directly but respectfully - focus on the issue, not personal attacks. Listen actively to all viewpoints and look for compromises that benefit the project. If someone isn't contributing, have a private conversation to understand their situation and find solutions. Use collaboration tools like shared documents to keep everyone organized and informed. Remember that diverse perspectives often lead to better outcomes, so embrace different approaches and ideas. The key is maintaining open communication and staying focused on your common goal.",
            "subject": "life_skills",
            "difficulty": "high_school_graduate"
        },
        {
            "input": "How should students handle stress and maintain mental health during challenging times?",
            "output": "Managing stress and mental health is essential for academic and personal success. Recognize early warning signs of stress like changes in sleep, appetite, or mood. Develop healthy coping strategies: regular exercise, adequate sleep (7-9 hours nightly), and good nutrition. Practice relaxation techniques like deep breathing, meditation, or yoga. Maintain social connections with friends and family who support you. Break overwhelming tasks into smaller, manageable steps. Don't hesitate to seek help from counselors, teachers, or mental health professionals when needed. Remember that asking for help is a sign of strength, not weakness. Create boundaries between work and personal time, and engage in activities you enjoy. Mental health is just as important as physical health.",
            "subject": "mental_health",
            "difficulty": "high_school_graduate"
        }
    ]
    
    # Add metadata
    dataset = {
        "metadata": {
            "created": datetime.now().isoformat(),
            "version": "1.0",
            "description": "High school graduate-level educational conversation dataset",
            "total_conversations": len(conversations),
            "subjects": list(set(conv["subject"] for conv in conversations)),
            "difficulty_level": "high_school_graduate",
            "purpose": "Training ImpressionCore AI for educational conversations"
        },
        "conversations": conversations
    }
    
    return dataset

def main():
    print("🎓 Creating High School Graduate Educational Dataset...")
    
    dataset = create_high_school_dataset()
    
    # Save to file
    filename = "high_school_graduate_dataset.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created comprehensive educational dataset!")
    print(f"📚 Conversations: {dataset['metadata']['total_conversations']}")
    print(f"📖 Subjects: {', '.join(dataset['metadata']['subjects'])}")
    print(f"📄 File: {filename}")
    print(f"🎯 Quality: University-level accuracy, high school complexity")
    print(f"💡 Purpose: Training coherent, educational AI conversation partner")

if __name__ == "__main__":
    main()
