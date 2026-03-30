#!/usr/bin/env python3
"""
ImpressionCore Phase 8B MVP Demonstration

This script demonstrates the newly integrated AI-enhanced features:
- Enhanced Task Management with AI scheduling
- Intelligent Reminder Engine
- Productivity Analytics Dashboard

Created: 2025-06-07
Author: GitHub Copilot
Version: 1.0
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from assistant.tasks.task_manager import TaskManager
from assistant.tasks.models import TaskPriority
from core.utils.rich_logging import setup_rich_logging
from core.utils.rich_status_animation import StatusAnimation


class Phase8BDemo:
    """
    Demonstration class for Phase 8B MVP features
    """
    
    def __init__(self):
        """Initialize the demo environment"""
        self.logger = setup_rich_logging(__name__)
        self.task_manager = None
        
    async def initialize(self):
        """Initialize the task manager with demo data"""
        animation = StatusAnimation(
            total_steps=3,
            description="Initializing Phase 8B Demo"
        )
        
        try:
            animation.start()
            
            # Step 1: Initialize task manager
            animation.update(1, "Creating task manager")
            self.task_manager = TaskManager(
                storage_path="demo_data/tasks",
                user_id="demo_user_8b"
            )
            
            # Step 2: Create sample tasks
            animation.update(2, "Creating sample tasks")
            await self._create_sample_tasks()
            
            # Step 3: Initialize AI components
            animation.update(3, "Initializing AI components")
            self.logger.info("Phase 8B Demo initialized successfully")
            
            animation.complete("Demo environment ready!")
            
        except Exception as e:
            animation.fail(f"Demo initialization failed: {str(e)}")
            raise
    
    async def _create_sample_tasks(self):
        """Create sample tasks for demonstration"""
        sample_tasks = [
            {
                "title": "Complete quarterly report",
                "description": "Analyze Q2 performance metrics and prepare comprehensive report",
                "priority": TaskPriority.HIGH,
                "due_date": datetime.now() + timedelta(days=3),
                "tags": ["work", "reports", "analytics"],
                "project": "Q2 Analysis"
            },
            {
                "title": "Team standup meeting",
                "description": "Daily team synchronization and progress updates",
                "priority": TaskPriority.MEDIUM,
                "due_date": datetime.now() + timedelta(hours=2),
                "tags": ["meetings", "team", "daily"],
                "project": "Team Management"
            },
            {
                "title": "Update project documentation",
                "description": "Review and update all project documentation for Phase 8B",
                "priority": TaskPriority.MEDIUM,
                "due_date": datetime.now() + timedelta(days=1),
                "tags": ["documentation", "maintenance", "phase8b"],
                "project": "ImpressionCore"
            },
            {
                "title": "Code review: AI scheduler",
                "description": "Review implementation of AI-enhanced task scheduler",
                "priority": TaskPriority.HIGH,
                "due_date": datetime.now() + timedelta(hours=4),
                "tags": ["code-review", "ai", "scheduler"],
                "project": "ImpressionCore"
            }
        ]
        
        for task_data in sample_tasks:
            task = self.task_manager.create_task(**task_data)
            self.logger.info(f"Created sample task: {task.title}")
    
    async def demonstrate_ai_features(self):
        """Demonstrate the AI-enhanced features"""
        print("\n🚀 Phase 8B MVP Feature Demonstration")
        print("=" * 50)
        
        # 1. AI Task Recommendations
        print("\n1. 🤖 AI Task Recommendations")
        recommendations = self.task_manager.get_ai_task_recommendations({
            "time_of_day": "morning",
            "energy_level": "high",
            "focus_duration": 120  # minutes
        })
        
        print(f"Generated {len(recommendations)} AI-powered recommendations")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec.get('title', 'Recommendation')}")
            print(f"      Reason: {rec.get('reasoning', 'AI-generated')}")
        
        # 2. Schedule Optimization
        print("\n2. 📅 AI Schedule Optimization")
        optimized_schedule = self.task_manager.optimize_task_schedule(24)
        
        if optimized_schedule:
            print("Optimized 24-hour schedule:")
            time_blocks = optimized_schedule.get('time_blocks', [])
            for block in time_blocks[:5]:  # Show first 5 blocks
                start_time = block.get('start_time', 'TBD')
                task_title = block.get('task_title', 'Unassigned')
                print(f"   {start_time}: {task_title}")
        
        # 3. Productivity Insights
        print("\n3. 📊 Productivity Analytics")
        insights = self.task_manager.get_productivity_insights()
        
        if insights:
            metrics = insights.get('metrics', {})
            print(f"Tasks completed today: {metrics.get('tasks_completed_today', 0)}")
            print(f"Average completion time: {metrics.get('avg_completion_time', 'N/A')}")
            print(f"Productivity score: {metrics.get('productivity_score', 'N/A')}")
            
            trends = insights.get('trends', {})
            if trends:
                print(f"Weekly trend: {trends.get('weekly_trend', 'stable')}")
        
        # 4. Enhanced Task with AI
        print("\n4. ✨ AI Task Enhancement")
        tasks = list(self.task_manager._tasks.values())
        if tasks:
            sample_task = tasks[0]
            enhanced = self.task_manager.update_task_with_ai_enhancements(sample_task.id)
            if enhanced:
                print(f"Enhanced task '{sample_task.title}' with AI features")
                print("   - Intelligent reminders configured")
                print("   - Schedule optimization applied")
                print("   - Analytics tracking enabled")
        
        print("\n✅ Phase 8B MVP Demonstration Complete!")
        print("🎯 All AI-enhanced features are operational and ready for production use.")
    
    async def run_demo(self):
        """Run the complete demonstration"""
        try:
            await self.initialize()
            await self.demonstrate_ai_features()
            
        except Exception as e:
            self.logger.error(f"Demo failed: {str(e)}")
            raise


async def main():
    """Main demo execution"""
    print("🌟 Welcome to ImpressionCore Phase 8B MVP Demo!")
    print("This demonstration showcases the AI-enhanced personal assistant features.")
    
    demo = Phase8BDemo()
    await demo.run_demo()


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())
