#!/usr/bin/env python3
"""
Simple test for Phase 8B task manager functionality

Tests basic task creation and management without full AI features
to ensure the core system is working.

Created: 2025-06-07
Author: GitHub Copilot
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_task_manager():
    """Test basic task manager functionality"""
    print("🧪 Testing ImpressionCore Phase 8B Task Manager")
    print("=" * 50)
    
    try:
        # Import basic modules first
        from assistant.tasks.models import TaskPriority
        print("✅ Task models imported successfully")
        
        from assistant.tasks.task_manager import TaskManager
        print("✅ TaskManager imported successfully")
        
        # Initialize task manager
        task_manager = TaskManager(
            storage_path="test_data/tasks",
            user_id="test_user"
        )
        print("✅ TaskManager initialized successfully")
        
        # Create a test task
        task = task_manager.create_task(
            title="Test Phase 8B Integration",
            description="Testing basic task creation functionality",
            priority=TaskPriority.HIGH,
            due_date=datetime.now() + timedelta(days=1),
            tags=["test", "phase8b"],
            project="ImpressionCore Testing"
        )
        print(f"✅ Task created: {task.title} (ID: {task.id})")
        
        # Test task retrieval
        retrieved_task = task_manager.get_task(task.id)
        if retrieved_task:
            print(f"✅ Task retrieved successfully: {retrieved_task.title}")
        
        # Test task listing
        all_tasks = task_manager.list_tasks()
        print(f"✅ Task listing works: {len(all_tasks)} total tasks")
        
        # Test AI recommendations (should use fallback)
        recommendations = task_manager.get_ai_task_recommendations({
            "time_of_day": "morning",
            "context": "testing"
        })
        print(f"✅ AI recommendations (fallback): {len(recommendations)} recommendations")
        
        # Test schedule optimization (should use fallback)
        schedule = task_manager.optimize_task_schedule(24)
        print(f"✅ Schedule optimization (fallback): {len(schedule)} schedule items")
        
        print("\n🎉 All basic tests passed! Phase 8B core functionality is working.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_task_manager()
    if success:
        print("\n🚀 Ready to proceed with full AI integration!")
        sys.exit(0)
    else:
        print("\n⚠️  Fix basic functionality before proceeding")
        sys.exit(1)
