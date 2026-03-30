#!/usr/bin/env python3
"""
High School Graduate Conversation Dataset Generator

This script creates high-quality conversation examples for training
a high school graduate-level AI conversation partner.

Focus: Educational conversations across core subjects
Quality: University-level accuracy, high school complexity
Goal: Create coherent, helpful, encouraging responses
"""

# High School Graduate Conversation Dataset
high_school_conversations = [
    {
        "input": "Explain the main theme of To Kill a Mockingbird and why it's still relevant today.",
        "output": "The main theme of To Kill a Mockingbird is the importance of moral courage and standing up for what's right, even when it's difficult. Through Atticus Finch's defense of Tom Robinson, Harper Lee shows us that true courage means doing the right thing even when everyone else disagrees. The novel also explores themes of prejudice, social inequality, and the loss of innocence as Scout and Jem learn about the harsh realities of their society. These themes remain relevant today because we still face issues of racial injustice, social inequality, and the need for individuals to stand up against discrimination. The book teaches us that everyone deserves to be treated with dignity and respect, regardless of their background."
    },
    {
        "input": "What are your thoughts on climate change and what can students do to help?",
        "output": "Climate change is one of the most pressing issues of our time, caused primarily by human activities that release greenhouse gases into the atmosphere. As a student, you can make a real difference! Start with small changes like using reusable water bottles, walking or biking instead of driving when possible, and turning off lights when you leave a room. You can also get involved in environmental clubs at school, participate in local clean-up events, and educate others about sustainability. Consider pursuing studies in environmental science, renewable energy, or related fields. Remember, collective action makes a big impact - when students work together and advocate for change, you can influence policy and create lasting environmental improvements."
    },
    {
        "input": "How would you approach studying for a difficult math test?",
        "output": "Great question! Here's a step-by-step approach that works well: First, review your class notes and identify the main concepts that will be covered. Create a study schedule that breaks down the material over several days - cramming doesn't work well for math. Practice problems from your textbook, starting with easier ones and gradually working up to more challenging problems. Form a study group with classmates to work through difficult problems together. Don't just memorize formulas - make sure you understand the underlying concepts and when to apply each method. If you're stuck on something, don't hesitate to ask your teacher for help during office hours. Finally, get plenty of sleep before the test - your brain needs rest to perform at its best!"
    },
    {
        "input": "What factors should someone consider when choosing a college major?",
        "output": "Choosing a college major is an important decision that should balance your interests, skills, and career goals. First, think about what subjects genuinely interest you - you'll be more motivated to excel in areas you find engaging. Consider your natural strengths and talents, as these often align with career success. Research potential career paths and job markets for different majors, including salary expectations and growth opportunities. Don't forget to consider the coursework requirements - some majors are more math-heavy, others focus on writing or lab work. Talk to professionals in fields that interest you, and consider internships or job shadowing to get real-world experience. Remember, many successful people don't work directly in their major field, so focus on developing transferable skills like critical thinking, communication, and problem-solving."
    },
    {
        "input": "Describe a time when you had to work in a group and how you handled challenges.",
        "output": "As an AI, I don't have personal experiences, but I can share effective strategies for group work that many students find helpful. When working in groups, it's important to establish clear roles and deadlines early on. If someone isn't contributing, try addressing it directly but diplomatically - sometimes people need encouragement or clearer expectations. When conflicts arise, focus on the project goals rather than personal differences. Good communication is key - use group chats or shared documents to keep everyone informed. If you're naturally a leader, make sure to listen to everyone's ideas and give credit where it's due. If you're more reserved, challenge yourself to contribute actively. Remember, diverse perspectives often lead to better solutions, so embrace different viewpoints and working styles within your group."
    },
    {
        "input": "What advice would you give to someone struggling with time management?",
        "output": "Time management is a skill that improves with practice! Start by tracking how you currently spend your time for a few days - you might be surprised where time goes. Use a planner or digital calendar to schedule important tasks and deadlines. Break large projects into smaller, manageable steps and tackle them one at a time. Try the 'two-minute rule' - if something takes less than two minutes, do it immediately instead of putting it off. Eliminate time wasters like excessive social media scrolling during study time. Learn to say no to commitments that don't align with your priorities. Set specific study times and stick to them, but also schedule breaks and fun activities. Finally, be realistic about what you can accomplish in a day - overcommitting leads to stress and poor-quality work."
    }
]

def save_training_dataset():
    """Save the high-quality training dataset"""
    import json
    
    # Save as JSON for easy loading
    with open('high_school_training_data.json', 'w') as f:
        json.dump(high_school_conversations, f, indent=2)
    
    print(f"✅ Saved {len(high_school_conversations)} high-quality conversation examples")
    print("📚 Topics covered: Literature, Environment, Study Skills, Career Planning, Teamwork, Time Management")
    print("🎯 Quality: University-level accuracy with high school complexity")
    print("📄 File: high_school_training_data.json")

if __name__ == "__main__":
    save_training_dataset()
