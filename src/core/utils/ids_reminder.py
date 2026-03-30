"""
IDS Reminder Module

CRITICAL REMINDER:
IDS = ImpressionCore Documentation System

This module serves as a constant reminder that:
- IDS stands for ImpressionCore Documentation System
- NOT "Integrated Data Store" or any other interpretation
- It is the documentation management and search system for this project

Created to prevent confusion and misidentification of the IDS system.
"""

# Constant reminder for the IDS system
IDS_FULL_NAME = "ImpressionCore Documentation System"
IDS_ACRONYM = "IDS"
IDS_PURPOSE = "Documentation management, search, and maintenance system for ImpressionCore project"

def get_ids_reminder():
    """Return a clear reminder of what IDS stands for."""
    return f"{IDS_ACRONYM} = {IDS_FULL_NAME}"

def verify_ids_understanding():
    """Verify understanding of IDS meaning."""
    print(f"✓ {IDS_ACRONYM} stands for: {IDS_FULL_NAME}")
    print(f"✓ Purpose: {IDS_PURPOSE}")
    return True

if __name__ == "__main__":
    verify_ids_understanding()
