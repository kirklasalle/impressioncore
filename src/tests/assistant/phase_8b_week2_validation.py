#!/usr/bin/env python3
"""
Phase 8B Week 2 Validation Test: Task Management & Reminders

This script validates the implementation status of Phase 8B Week 2 components
and identifies missing implementations that need to be completed.

Created: 2025-01-06
Author: ImpressionCore Development Team
Phase: 8B Week 2 - Task Management & Reminders
"""

import sys
import importlib
from pathlib import Path

# Add src to path
# Add project root to path (to allow src.* imports)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

def test_component_imports():
    """Test if all required components can be imported"""
    results = {}
    
    # Task Management Components
    task_components = {
        'TaskManager': 'src.assistant.tasks.task_manager',
        'Task': 'src.assistant.tasks.models',
        'TaskPriority': 'src.assistant.tasks.models',
        'TaskStatus': 'src.assistant.tasks.models',
        'TaskStorage': 'src.assistant.tasks.task_storage',
        'TaskScheduler': 'src.assistant.tasks.task_scheduler',
    }
    
    # Reminder Components
    reminder_components = {
        'ReminderEngine': 'src.assistant.reminders.reminder_engine',
        'Reminder': 'src.assistant.tasks.models',
        'TriggerType': 'src.assistant.tasks.models',
        'NotificationManager': 'src.assistant.reminders.notification_manager',
        'TriggerSystem': 'src.assistant.reminders.trigger_system',
    }
    
    # Integration Components
    integration_components = {
        'TaskIntegration': 'src.assistant.integration.task_integration',
        'CalendarIntegration': 'src.assistant.integration.calendar_integration',
        'ProductivityAnalytics': 'src.assistant.integration.productivity_analytics',
    }
    
    all_components = {**task_components, **reminder_components, **integration_components}
    
    print("=== Phase 8B Week 2 Component Validation ===")
    print()
    
    for component_name, module_path in all_components.items():
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, component_name):
                results[component_name] = "✅ Available"
                print(f"✅ {component_name:25} - Available")
            else:
                results[component_name] = "❌ Class/Function Missing"
                print(f"❌ {component_name:25} - Class/Function Missing from {module_path}")
        except ImportError as e:
            results[component_name] = f"❌ Import Error: {str(e)}"
            print(f"❌ {component_name:25} - Import Error: {module_path}")
        except Exception as e:
            results[component_name] = f"❌ Error: {str(e)}"
            print(f"❌ {component_name:25} - Error: {str(e)}")
    
    return results

def test_integration_points():
    """Test integration with existing Personal Assistant Core"""
    print("\n=== Integration Points Validation ===")
    print()
    
    integration_tests = []
    
    # Test Query Processor integration
    try:
        from src.assistant.core.query_processor import QueryProcessor
        query_processor = QueryProcessor()
        # Check if task intents are supported
        integration_tests.append(("Query Processor", "✅ Available"))
        print("✅ Query Processor        - Available for task intent integration")
    except Exception as e:
        integration_tests.append(("Query Processor", f"❌ {str(e)}"))
        print(f"❌ Query Processor        - Error: {str(e)}")
    
    # Test NLU Engine integration
    try:
        from src.assistant.nlp.nlu_engine import NLUEngine
        nlu_engine = NLUEngine()
        integration_tests.append(("NLU Engine", "✅ Available"))
        print("✅ NLU Engine             - Available for task entity extraction")
    except Exception as e:
        integration_tests.append(("NLU Engine", f"❌ {str(e)}"))
        print(f"❌ NLU Engine             - Error: {str(e)}")
    
    # Test Response Generator integration
    try:
        from src.assistant.core.response_generator import ResponseGenerator
        response_gen = ResponseGenerator()
        integration_tests.append(("Response Generator", "✅ Available"))
        print("✅ Response Generator     - Available for task responses")
    except Exception as e:
        integration_tests.append(("Response Generator", f"❌ {str(e)}"))
        print(f"❌ Response Generator     - Error: {str(e)}")
    
    return integration_tests

def check_missing_components():
    """Identify missing components that need implementation"""
    print("\n=== Missing Components Analysis ===")
    print()
    
    required_files = [
        "src/assistant/tasks/task_storage.py",
        "src/assistant/tasks/task_scheduler.py",
        "src/assistant/reminders/notification_manager.py", 
        "src/assistant/reminders/trigger_system.py",
        "src/assistant/integration/calendar_integration.py",
        "src/assistant/integration/productivity_analytics.py",
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        full_path = Path(file_path)
        if full_path.exists():
            existing_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} - MISSING")
    
    print(f"\nSummary:")
    print(f"✅ Existing files: {len(existing_files)}")
    print(f"❌ Missing files:  {len(missing_files)}")
    
    return missing_files, existing_files

def main():
    """Run complete Phase 8B Week 2 validation"""
    print("Phase 8B Week 2: Task Management & Reminders - Validation Report")
    print("=" * 70)
    
    # Test component imports
    component_results = test_component_imports()
    
    # Test integration points
    integration_results = test_integration_points()
    
    # Check missing components
    missing_files, existing_files = check_missing_components()
    
    # Generate summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    total_components = len(component_results)
    available_components = len([r for r in component_results.values() if r == "✅ Available"])
    missing_components = total_components - available_components
    
    print(f"📊 Component Status:")
    print(f"   ✅ Available:     {available_components}/{total_components}")
    print(f"   ❌ Missing:       {missing_components}/{total_components}")
    print(f"   📁 Files Missing: {len(missing_files)}")
    
    completion_percentage = (available_components / total_components) * 100
    print(f"\n🎯 Implementation Progress: {completion_percentage:.1f}%")
    
    if missing_components == 0:
        print("\n🎉 Phase 8B Week 2 is READY for validation testing!")
        return True
    else:
        print(f"\n⚠️  Phase 8B Week 2 requires {missing_components} more components")
        print("\nNext steps:")
        for file_path in missing_files:
            print(f"   📝 Implement: {file_path}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
