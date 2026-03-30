#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024
**Updated:** August-04-2025
**Author:** ImpressionCore Team
**Tags:** #python #source_code #src/scripts/utilities/verify_f_drive_structure.py #testing #training
**Category:** Source Code
**Status:** Active
"""



import json
import os
from datetime import datetime


def verify_f_drive_structure():
    """Verify the F: drive structure and generate a report"""

    # Only verify the F: drive structure, do not create or modify any directories.

    verification_results = {
        "timestamp": datetime.now().isoformat(),
        "f_drive_accessible": False,
        "structure_verification": {},
        "missing_directories": [],
        "missing_files": [],
        "existing_structure": {},
        "recommendations": [],
        "status": "UNKNOWN"
    }

    # Check if F: drive is accessible
    f_drive_root = "F:/data"
    try:
        if os.path.exists(f_drive_root):
            verification_results["f_drive_accessible"] = True
            print(f"✅ F: drive accessible at {f_drive_root}")
        else:
            verification_results["f_drive_accessible"] = False
            print(f"❌ F: drive not accessible at {f_drive_root}")
            verification_results["status"] = "FAILED - F: DRIVE NOT ACCESSIBLE"
            return verification_results
    except Exception as e:
        verification_results["f_drive_accessible"] = False
        verification_results["status"] = f"FAILED - ERROR: {e!s}"
        print(f"❌ Error accessing F: drive: {e}")
        return verification_results

    # Verify structure recursively
    def verify_directory_structure(expected, current_path, results_path):
        """Recursively verify directory structure"""
        current_results = {}

        for item_name, item_structure in expected.items():
            full_path = os.path.join(current_path, item_name)
            item_exists = os.path.exists(full_path)

            current_results[item_name] = {
                "exists": item_exists,
                "path": full_path,
                "type": "directory" if isinstance(item_structure, dict) else "file" if isinstance(item_structure, list) else "unknown"
            }

            if item_exists:
                if isinstance(item_structure, dict):
                    # It's a directory with subdirectories
                    if os.path.isdir(full_path):
                        print(f"✅ Directory: {full_path}")
                        current_results[item_name]["subdirectories"] = verify_directory_structure(
                            item_structure, full_path, [*results_path, item_name]
                        )
                    else:
                        print(f"❌ Expected directory but found file: {full_path}")
                        current_results[item_name]["error"] = "Expected directory but found file"
                elif isinstance(item_structure, list):
                    # It's a directory that should contain specific files
                    if os.path.isdir(full_path):
                        print(f"✅ Directory: {full_path}")
                        current_results[item_name]["expected_contents"] = item_structure
                        current_results[item_name]["actual_contents"] = []
                        current_results[item_name]["missing_contents"] = []

                        # Check expected contents
                        for expected_item in item_structure:
                            expected_item_path = os.path.join(full_path, expected_item)
                            if os.path.exists(expected_item_path):
                                current_results[item_name]["actual_contents"].append(expected_item)
                                print(f"  ✅ Found: {expected_item}")
                            else:
                                current_results[item_name]["missing_contents"].append(expected_item)
                                verification_results["missing_files"].append(expected_item_path)
                                print(f"  ❌ Missing: {expected_item_path}")
                    else:
                        print(f"❌ Expected directory but found file: {full_path}")
                        current_results[item_name]["error"] = "Expected directory but found file"
            else:
                print(f"❌ Missing: {full_path}")
                verification_results["missing_directories"].append(full_path)

        return current_results

    # Start verification
    print("🔍 Starting F: drive structure verification...")
    verification_results["structure_verification"] = verify_directory_structure(
        expected_structure["F:/data"], f_drive_root, ["data"]
    )

    # Scan existing structure
    def scan_existing_structure(path, max_depth=3, current_depth=0):
        """Scan and document existing structure"""
        if current_depth >= max_depth:
            return {"truncated": True, "reason": "Max depth reached"}

        try:
            structure = {}
            if os.path.isdir(path):
                items = os.listdir(path)
                for item in items[:50]:  # Limit to first 50 items per directory
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        structure[item] = {
                            "type": "directory",
                            "contents": scan_existing_structure(item_path, max_depth, current_depth + 1)
                        }
                    else:
                        file_size = os.path.getsize(item_path)
                        structure[item] = {
                            "type": "file",
                            "size_bytes": file_size,
                            "size_mb": round(file_size / (1024*1024), 2)
                        }
                if len(items) > 50:
                    structure["...additional_items"] = f"{len(items) - 50} more items not shown"
            return structure
        except Exception as e:
            return {"error": str(e)}

    print("📊 Scanning existing structure...")
    verification_results["existing_structure"] = scan_existing_structure(f_drive_root)

    # Generate recommendations
    if verification_results["missing_directories"]:
        verification_results["recommendations"].append(
            f"Create {len(verification_results['missing_directories'])} missing directories"
        )

    if verification_results["missing_files"]:
        verification_results["recommendations"].append(
            f"Create {len(verification_results['missing_files'])} missing files"
        )

    # Determine overall status
    if not verification_results["missing_directories"] and not verification_results["missing_files"]:
        verification_results["status"] = "COMPLETE - All structure verified"
    elif len(verification_results["missing_directories"]) + len(verification_results["missing_files"]) < 10:
        verification_results["status"] = "MOSTLY_COMPLETE - Minor missing items"
    else:
        verification_results["status"] = "INCOMPLETE - Significant missing structure"

    print(f"📋 Verification complete. Status: {verification_results['status']}")
    return verification_results

def generate_verification_report(results):
    """Generate a comprehensive verification report"""

    report_content = f"""# F: Drive Structure Verification Report

# Generated:** {results['timestamp']}
# Status:** {results['status']}
# F: Drive Accessible:** {'✅ Yes' if results['f_drive_accessible'] else '❌ No'}

## Summary

- **Missing Directories:** {len(results['missing_directories'])}
- **Missing Files:** {len(results['missing_files'])}
- **Overall Status:** {results['status']}

## Missing Directories
"""

    if results['missing_directories']:
        for missing_dir in results['missing_directories']:
            report_content += f"- ❌ `{missing_dir}`\n"
    else:
        report_content += "✅ All expected directories found!\n"

    report_content += "\n## Missing Files\n"

    if results['missing_files']:
        for missing_file in results['missing_files']:
            report_content += f"- ❌ `{missing_file}`\n"
    else:
        report_content += "✅ All expected files found!\n"

    report_content += """
## Recommendations

"""

    if results['recommendations']:
        for rec in results['recommendations']:
            report_content += f"- 📋 {rec}\n"
    else:
        report_content += "✅ No recommendations - structure is complete!\n"

    report_content += f"""
## Detailed Structure Verification

The following shows the verification results for each expected component:

```json
{json.dumps(results['structure_verification'], indent=2)}
```

## Existing Structure Sample

The following shows a sample of the actual F: drive structure:

```json
{json.dumps(results['existing_structure'], indent=2)}
```

---

# Verification Script:** verify_f_drive_structure.py
# ImpressionCore Team**
# Date:** July 30, 2025
"""

    return report_content

def main():
    """Main execution function"""
    print("🚀 ImpressionCore F: Drive Structure Verification")
    print("=" * 50)

    # Run verification
    results = verify_f_drive_structure()

    # Generate report
    report_content = generate_verification_report(results)

    # Save report
    report_filename = f"f_drive_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path = os.path.join(".", report_filename)

    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"📄 Report saved to: {report_path}")
    except Exception as e:
        print(f"❌ Error saving report: {e}")
        print("📄 Report content:")
        print(report_content)

    # Save JSON results for programmatic use
    json_filename = f"f_drive_verification_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    json_path = os.path.join(".", json_filename)

    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"📊 JSON results saved to: {json_path}")
    except Exception as e:
        print(f"❌ Error saving JSON results: {e}")

    print("=" * 50)
    print(f"✅ Verification complete! Status: {results['status']}")

if __name__ == "__main__":
    main()
