import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities data before each test."""
    # Store original activities
    original_activities = copy.deepcopy(activities)
    
    # Reset to initial state before each test
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })
    
    yield
    
    # Restore original activities after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Test the root endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "static/index.html" in response.headers["location"]


class TestGetActivities:
    """Test the GET /activities endpoint."""
    
    def test_get_activities_success(self, client, reset_activities):
        """Test getting all activities successfully."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        
        # Check structure of activity data
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_has_correct_participant_counts(self, client, reset_activities):
        """Test that activities have correct participant counts."""
        response = client.get("/activities")
        data = response.json()
        
        assert len(data["Chess Club"]["participants"]) == 2
        assert len(data["Programming Class"]["participants"]) == 2
        assert len(data["Gym Class"]["participants"]) == 2


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was added
        get_response = client.get("/activities")
        activities_data = get_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity."""
        response = client.post(
            "/activities/Non-existent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_already_registered(self, client, reset_activities):
        """Test signup when student is already registered."""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is already signed up"
    
    def test_signup_with_encoded_activity_name(self, client, reset_activities):
        """Test signup with URL-encoded activity name."""
        response = client.post(
            "/activities/Programming%20Class/signup?email=newcoder@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant was added
        get_response = client.get("/activities")
        activities_data = get_response.json()
        assert "newcoder@mergington.edu" in activities_data["Programming Class"]["participants"]
    
    def test_signup_with_encoded_email(self, client, reset_activities):
        """Test signup with URL-encoded email."""
        response = client.post(
            "/activities/Chess Club/signup?email=test%2Buser@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant was added with correct email
        get_response = client.get("/activities")
        activities_data = get_response.json()
        assert "test+user@mergington.edu" in activities_data["Chess Club"]["participants"]


class TestUnregisterFromActivity:
    """Test the DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity."""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was removed
        get_response = client.get("/activities")
        activities_data = get_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
        # But other participant should still be there
        assert "daniel@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test unregistration from non-existent activity."""
        response = client.delete(
            "/activities/Non-existent Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_student_not_registered(self, client, reset_activities):
        """Test unregistration when student is not registered."""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"
    
    def test_unregister_with_encoded_activity_name(self, client, reset_activities):
        """Test unregistration with URL-encoded activity name."""
        response = client.delete(
            "/activities/Programming%20Class/unregister?email=emma@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        get_response = client.get("/activities")
        activities_data = get_response.json()
        assert "emma@mergington.edu" not in activities_data["Programming Class"]["participants"]


class TestEndToEndWorkflow:
    """Test complete signup and unregister workflow."""
    
    def test_signup_then_unregister_workflow(self, client, reset_activities):
        """Test complete workflow: signup then unregister."""
        email = "workflow@mergington.edu"
        activity = "Chess Club"
        
        # Step 1: Get initial participant count
        get_response = client.get("/activities")
        initial_participants = get_response.json()[activity]["participants"]
        initial_count = len(initial_participants)
        
        # Step 2: Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Step 3: Verify signup
        get_response = client.get("/activities")
        after_signup_participants = get_response.json()[activity]["participants"]
        assert len(after_signup_participants) == initial_count + 1
        assert email in after_signup_participants
        
        # Step 4: Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Step 5: Verify unregistration
        get_response = client.get("/activities")
        final_participants = get_response.json()[activity]["participants"]
        assert len(final_participants) == initial_count
        assert email not in final_participants
        # Original participants should still be there
        for original_participant in initial_participants:
            assert original_participant in final_participants


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_missing_email_parameter(self, client, reset_activities):
        """Test API calls without email parameter."""
        # Signup without email
        response = client.post("/activities/Chess Club/signup")
        # FastAPI will return 422 for missing required query parameter
        assert response.status_code == 422
        
        # Unregister without email
        response = client.delete("/activities/Chess Club/unregister")
        assert response.status_code == 422
    
    def test_empty_email_parameter(self, client, reset_activities):
        """Test API calls with empty email parameter."""
        response = client.post("/activities/Chess Club/signup?email=")
        # Should still work with empty email (depending on business logic)
        # This test documents current behavior
        assert response.status_code in [200, 400, 422]
    
    def test_special_characters_in_activity_name(self, client, reset_activities):
        """Test handling of special characters in activity names."""
        # This tests the current behavior with existing activities
        response = client.get("/activities")
        data = response.json()
        
        # Verify activities with spaces work correctly
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data