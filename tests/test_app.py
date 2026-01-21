"""
Tests for the Mergington High School Activities API
"""

import sys
from pathlib import Path
from urllib.parse import quote

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Test cases for /activities endpoint"""
    
    def test_get_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response is a dictionary of activities
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Verify structure of an activity
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)
    
    def test_activities_have_expected_names(self):
        """Test that expected activities are present"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        for activity in expected_activities:
            assert activity in data


class TestSignupEndpoint:
    """Test cases for /activities/{activity_name}/signup endpoint"""
    
    def test_signup_with_valid_email(self):
        """Test signup with valid email"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@example.com",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@example.com" in data["message"]
    
    def test_signup_with_invalid_email(self):
        """Test signup with invalid email format"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=notanemail",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "Invalid email address format" in data["detail"]
    
    def test_signup_with_invalid_activity(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@example.com",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_participant(self):
        """Test that duplicate signups are rejected"""
        email = "duplicate@test.com"
        activity = "Chess%20Club"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/{activity}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_emails_with_special_characters(self):
        """Test signup with various valid email formats"""
        valid_emails = [
            "user.name@example.com",
            "user+tag@example.com",
            "user_name@example.com",
            "user-name@example.com",
            "user123@example.co.uk"
        ]
        
        for i, email in enumerate(valid_emails):
            response = client.post(
                f"/activities/Art%20Studio/signup?email={quote(email)}",
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code == 200, f"Failed for email: {email}"


class TestUnregisterEndpoint:
    """Test cases for /unregister endpoint"""
    
    def test_unregister_participant(self):
        """Test unregistering a participant"""
        email = "unregister@test.com"
        
        # First, sign up
        signup_response = client.post(
            f"/activities/Tennis%20Club/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )
        assert signup_response.status_code == 200
        
        # Then unregister
        unregister_response = client.delete(f"/unregister?email={email}")
        assert unregister_response.status_code == 200
        data = unregister_response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]
    
    def test_unregister_nonexistent_participant(self):
        """Test unregistering a participant that doesn't exist"""
        response = client.delete("/unregister?email=notexist@example.com")
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]


class TestEmailValidation:
    """Test cases for email validation"""
    
    def test_invalid_email_formats(self):
        """Test that invalid email formats are rejected"""
        invalid_emails = [
            "notanemail",
            "missing@domain",
            "@nodomain.com",
            "spaces in@email.com",
            "double@@domain.com"
        ]
        
        for email in invalid_emails:
            response = client.post(
                f"/activities/Music%20Ensemble/signup?email={email}",
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code == 400, f"Should reject: {email}"
            data = response.json()
            assert "Invalid email address format" in data["detail"]
