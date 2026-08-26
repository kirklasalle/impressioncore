#!/usr/bin/env python3
"""
Test visualization routes in ImpressionCore.
"""

import pytest
from src.interfaces.web.server import create_app

@pytest.fixture
def full_app():
    """Create a test application instance using create_app()"""
    app = create_app()
    app.config['TESTING'] = True
    # Disable error handlers/redirects if needed, or use default
    return app

@pytest.fixture
def full_client(full_app):
    """Create test client using full application"""
    return full_app.test_client()

def test_visualization_dashboard_loads(full_client):
    """Test that the singular /visualization dashboard route loads successfully."""
    # Ensure session contains user to pass potential require_auth if present
    with full_client.session_transaction() as sess:
        sess['user'] = 'admin'
        sess['user_id'] = 'admin'
        
    response = full_client.get('/visualization')
    assert response.status_code == 200
    assert b'Visualization' in response.data

def test_architecture_page_lists_core_models(full_client):
    """Test that the architecture visualization dropdown includes the core offering models."""
    response = full_client.get('/visualization/architecture')

    assert response.status_code == 200
    assert b'value="b1_39m"' in response.data
    assert b'value="b2_50m"' in response.data
    assert b'value="b3_504m"' in response.data
    assert b'B1 Hope 39M' in response.data
    assert b'B2 Insight 50M' in response.data
    assert b'B3 Apex 504M' in response.data

def test_visualizations_redirects(full_client):
    """Test that the plural /visualizations route redirects (302) to /visualization."""
    response = full_client.get('/visualizations')
    assert response.status_code == 302
    # Flask redirects to either absolute or relative URL
    assert response.headers['Location'].endswith('/visualization')
