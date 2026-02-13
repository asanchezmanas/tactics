import sys
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.main import app

client = TestClient(app)

def test_blog_index_loads():
    """Verify that the blog index page is accessible."""
    response = client.get("/blog")
    assert response.status_code == 200
    assert "Insights" in response.text
    print("✓ Blog Index: Loaded successfully.")

def test_blog_post_rendering_radar():
    """Verify that a specific blog post (Radar) renders correctly from Markdown."""
    response = client.get("/blog/radar-rentabilidad")
    assert response.status_code == 200
    assert "Radar de Rentabilidad" in response.text
    # Check that it's rendered as HTML (contains a paragraph for example)
    assert "<p>" in response.text
    print("✓ Blog Post (Radar): Rendered successfully.")

def test_blog_post_rendering_ltv():
    """Verify LTV article rendering with slug mapping."""
    response = client.get("/blog/que-es-el-ltv")
    assert response.status_code == 200
    assert "Customer Lifetime Value" in response.text
    print("✓ Blog Post (LTV): Rendered successfully.")

def test_blog_post_404():
    """Verify that a non-existent slug returns 404."""
    response = client.get("/blog/articulo-inexistente")
    assert response.status_code == 404
    print("✓ Blog Post (404): Handled correctly.")

if __name__ == "__main__":
    print("\n--- Starting Tactics Blog Engine Tests ---\n")
    try:
        test_blog_index_loads()
        test_blog_post_rendering_radar()
        test_blog_post_rendering_ltv()
        test_blog_post_404()
        print("\n--- ALL BLOG TESTS PASSED SUCCESSFULLY ---\n")
    except Exception as e:
        print(f"\n--- TEST FAILED: {str(e)} ---\n")
        sys.exit(1)
