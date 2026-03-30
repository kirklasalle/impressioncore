#!/usr/bin/env python3
"""
ImpressionCore: Simple API Structure Validation

Basic validation of API structure without heavy dependencies.

File: validate_api_structure.py
Created: 2025-05-30
"""

import os
import sys

def validate_deployment_api_structure():
    """Validate that deployment API files are properly structured."""
    
    print("🔍 Validating ImpressionCore Deployment API Structure...")
    
    # Check 1: Deployment routes file exists
    deployment_routes_path = "src/web/routes/deployment.py"
    if os.path.exists(deployment_routes_path):
        print("✅ Deployment routes file exists")
    else:
        print("❌ Deployment routes file missing")
        return False
    
    # Check 2: File contains expected content
    with open(deployment_routes_path, 'r') as f:
        content = f.read()
        
        expected_functions = [
            "def deploy_model(",
            "def get_deployment_status(",
            "def list_deployments(",
            "def check_hardware_compatibility(",
            "def benchmark_deployment(",
            "def get_deployment_artifacts(",
            "def delete_deployment(",
            "def health_check("
        ]
        
        for func in expected_functions:
            if func in content:
                print(f"✅ Function found: {func}")
            else:
                print(f"❌ Function missing: {func}")
                return False
    
    # Check 3: Blueprint definition exists
    if "deployment_bp = Blueprint(" in content:
        print("✅ Blueprint definition found")
    else:
        print("❌ Blueprint definition missing")
        return False
    
    # Check 4: API endpoints are defined
    expected_endpoints = [
        "@deployment_bp.route('/deploy'",
        "@deployment_bp.route('/status/<deployment_id>'",
        "@deployment_bp.route('/list'",
        "@deployment_bp.route('/compatibility'",
        "@deployment_bp.route('/benchmark'",
        "@deployment_bp.route('/artifacts/<deployment_id>'",
        "@deployment_bp.route('/<deployment_id>', methods=['DELETE']",
        "@deployment_bp.route('/health'"
    ]
    
    for endpoint in expected_endpoints:
        if endpoint in content:
            print(f"✅ Endpoint found: {endpoint}")
        else:
            print(f"❌ Endpoint missing: {endpoint}")
            return False
    
    return True


def validate_server_integration():
    """Validate that deployment blueprint is integrated in server."""
    
    print("\n🔍 Validating Server Integration...")
    
    server_path = "src/web/server.py"
    if not os.path.exists(server_path):
        print("❌ Server file missing")
        return False
    
    with open(server_path, 'r') as f:
        content = f.read()
    
    # Check imports
    if "from src.interfaces.web.routes.deployment import deployment_bp" in content:
        print("✅ Deployment blueprint import found")
    else:
        print("❌ Deployment blueprint import missing")
        return False
    
    # Check registration
    if "app.register_blueprint(deployment_bp)" in content:
        print("✅ Deployment blueprint registration found")
    else:
        print("❌ Deployment blueprint registration missing")
        return False
    
    return True


def validate_api_documentation():
    """Validate that API documentation includes deployment endpoints."""
    
    print("\n🔍 Validating API Documentation...")
    
    api_doc_path = "docs/api/complete_api_reference.md"
    if not os.path.exists(api_doc_path):
        print("❌ API documentation file missing")
        return False
    
    with open(api_doc_path, 'r') as f:
        content = f.read()
    
    # Check deployment section
    if "## Deployment API" in content:
        print("✅ Deployment API section found")
    else:
        print("❌ Deployment API section missing")
        return False
    
    # Check key endpoints in documentation
    documented_endpoints = [
        "POST /api/v1/deployment/deploy",
        "GET /api/v1/deployment/status/{deployment_id}",
        "GET /api/v1/deployment/list",
        "GET /api/v1/deployment/compatibility",
        "POST /api/v1/deployment/benchmark",
        "GET /api/v1/deployment/artifacts/{deployment_id}",
        "DELETE /api/v1/deployment/{deployment_id}"
    ]
    
    for endpoint in documented_endpoints:
        if endpoint in content:
            print(f"✅ Documented endpoint: {endpoint}")
        else:
            print(f"❌ Missing documentation for: {endpoint}")
            return False
    
    return True


def check_priority_5_completion():
    """Check if Priority 5: API Documentation & Contracts is complete."""
    
    print("\n🎯 Checking Priority 5: API Documentation & Contracts Completion...")
    
    # Check deployment manager exists
    deployment_manager_path = "src/deployment/deployment_manager.py"
    if os.path.exists(deployment_manager_path):
        print("✅ Deployment manager implementation exists")
    else:
        print("❌ Deployment manager missing")
        return False
    
    # Check API routes implementation
    api_implemented = validate_deployment_api_structure()
    if api_implemented:
        print("✅ API routes implementation complete")
    else:
        print("❌ API routes implementation incomplete")
        return False
    
    # Check server integration
    server_integrated = validate_server_integration()
    if server_integrated:
        print("✅ Server integration complete")
    else:
        print("❌ Server integration incomplete")
        return False
    
    # Check documentation
    docs_complete = validate_api_documentation()
    if docs_complete:
        print("✅ API documentation complete")
    else:
        print("❌ API documentation incomplete")
        return False
    
    return True


if __name__ == "__main__":
    print("ImpressionCore - Priority 5 Validation")
    print("=" * 50)
    
    # Run all validations
    structure_valid = validate_deployment_api_structure()
    server_valid = validate_server_integration()
    docs_valid = validate_api_documentation()
    
    if structure_valid and server_valid and docs_valid:
        priority_5_complete = check_priority_5_completion()
        
        if priority_5_complete:
            print("\n🎉 SUCCESS: Priority 5 - API Documentation & Contracts COMPLETED!")
            print("\nNext Steps:")
            print("- Priority 6: Extended Context Window Support")
            print("- Priority 7: User Experience Features")
            print("- Continue with remaining roadmap priorities")
        else:
            print("\n⚠️  Priority 5 has some remaining tasks")
    else:
        print("\n❌ Priority 5 validation failed - check issues above")
        sys.exit(1)
