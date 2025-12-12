"""
Integration tests for API Gateway
"""
import pytest
import httpx
import asyncio
from typing import Dict, Any


class TestAPIGateway:
    """Test API Gateway endpoints"""

    def setup_method(self):
        """Setup test client"""
        self.base_url = "http://localhost:8000"
        self.client = httpx.Client(base_url=self.base_url, timeout=30.0)

    def teardown_method(self):
        """Cleanup test client"""
        self.client.close()

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "DocQA-MS API Gateway" in data["message"]

    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.options("/health")
        assert response.status_code == 200

        # Check CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

    def test_security_headers(self):
        """Test security headers are present"""
        response = self.client.get("/health")

        # Check security headers
        security_headers = [
            "content-security-policy",
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection",
            "referrer-policy"
        ]

        for header in security_headers:
            assert header in response.headers, f"Missing security header: {header}"

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            # Create multiple concurrent requests
            tasks = []
            for i in range(10):
                tasks.append(client.get("/health"))

            # Execute all requests concurrently
            responses = await asyncio.gather(*tasks)

            # All should succeed
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"


class TestServiceIntegration:
    """Test integration with other services"""

    def setup_method(self):
        """Setup test client"""
        self.api_gateway_url = "http://localhost:8000"
        self.client = httpx.Client(timeout=30.0)

    def teardown_method(self):
        """Cleanup test client"""
        self.client.close()

    def test_document_upload_flow(self):
        """Test complete document upload flow"""
        # This would test the full flow from upload to processing
        # Requires authentication and file upload
        # For now, just test the endpoint exists
        response = self.client.get(f"{self.api_gateway_url}/docs")
        assert response.status_code == 200

    def test_qa_flow(self):
        """Test Q&A flow integration"""
        # Test that QA endpoints are accessible through gateway
        response = self.client.get(f"{self.api_gateway_url}/docs")
        assert response.status_code == 200

        # Check that QA endpoints are documented
        docs = response.text
        assert "qa" in docs.lower() or "question" in docs.lower()


class TestErrorHandling:
    """Test error handling"""

    def setup_method(self):
        """Setup test client"""
        self.base_url = "http://localhost:8000"
        self.client = httpx.Client(base_url=self.base_url, timeout=30.0)

    def teardown_method(self):
        """Cleanup test client"""
        self.client.close()

    def test_404_error(self):
        """Test 404 error handling"""
        response = self.client.get("/nonexistent-endpoint")
        assert response.status_code == 404

        data = response.json()
        assert "error" in data
        assert "code" in data["error"]

    def test_method_not_allowed(self):
        """Test method not allowed error"""
        response = self.client.post("/health")  # Health only accepts GET
        assert response.status_code == 405

    def test_invalid_json(self):
        """Test invalid JSON handling"""
        response = self.client.post(
            "/api/v1/documents",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        # Should handle gracefully
        assert response.status_code in [400, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])