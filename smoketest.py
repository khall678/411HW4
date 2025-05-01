import requests


def run_smoketest():
    base_url = "http://localhost:5001/api"
    username = "test"
    password = "test"

    test_Tag = {
        "title": "Tag"
    }

    test_Shrek = {
        "title": "Shrek"
    }

    health_response = requests.get(f"{base_url}/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "success"

    delete_user_response = requests.delete(f"{base_url}/reset-users")
    assert delete_user_response.status_code == 200
    assert delete_user_response.json()["status"] == "success"
    print("Reset users successful")

    #delete_movie_response = requests.delete(f"{base_url}/reset-boxers")
    #assert delete_movie_response.status_code == 200
    #assert delete_movie_response.json()["status"] == "success"
    #print("Reset boxers successful")


    create_user_response = requests.put(f"{base_url}/create-user", json={
        "username": username,
        "password": password
    })
    assert create_user_response.status_code == 201
    assert create_user_response.json()["status"] == "success"
    print("User creation successful")

    session = requests.Session()

    # Log in
    login_resp = session.post(f"{base_url}/login", json={
        "username": username,
        "password": password
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["status"] == "success"
    print("Login successful")

    create_movie_resp = session.post(f"{base_url}/add-favorite-movie", json=test_Tag)
    assert create_movie_resp.status_code == 201
    assert create_movie_resp.json()["status"] == "success"
    print("Movie creation successful")

    # Change password
    change_password_resp = session.post(f"{base_url}/change-password", json={
        "new_password": "new_password"
    })
    assert change_password_resp.status_code == 200
    assert change_password_resp.json()["status"] == "success"
    print("Password change successful")

    # Log in with new password
    login_resp = session.post(f"{base_url}/login", json={
        "username": username,
        "password": "new_password"
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["status"] == "success"
    print("Login with new password successful")

    create_movie_resp = session.post(f"{base_url}/add-favorite-movie", json=test_Shrek)
    assert create_movie_resp.status_code == 201
    assert create_movie_resp.json()["status"] == "success"
    print("Movie creation successful")

    # Test see-all-favorites
    get_favorites_resp = session.get(f"{base_url}/see-all-favorites")
    assert get_favorites_resp.status_code == 200
    #print(get_favorites_resp.json())
    movie_list = get_favorites_resp.json().get("movies", [])
    assert isinstance(movie_list, list), "Response is not a list"
    assert len(movie_list) > 0, "No movies found in the favorites list"
    print("See all favorites test passed")


    # Test get movie details
    get_movie_resp = session.post(f"{base_url}/get-movie-details", json=test_Tag)
    #print(f"Status Code: {get_movie_resp.status_code}")
    #print(f"Response Text: {get_movie_resp.text}")
    assert get_movie_resp.status_code == 200
    movie_details = get_movie_resp.json().get("data", {})
    assert "title" in movie_details
    assert "year" in movie_details
    assert "actors" in movie_details
    print("Get movie details test passed")

 
    # Test delete movie by id
    movie_id = movie_details["id"]
    #print(f"movie id for delete {movie_id}")
    delete_movie_resp = session.delete( f"{base_url}/delete-favorite-movie", json={"movie_id": movie_id})
    assert delete_movie_resp.status_code == 200, f"Delete failed: {delete_movie_resp.text}"

    delete_response = delete_movie_resp.json()
    assert delete_response["message"].startswith("Movie"), "Unexpected delete message"
    print("Delete movie test passed")


    # Clear all favorites
    clear_favorites_resp = session.delete(f"{base_url}/clear-all-favorites")
    assert clear_favorites_resp.status_code == 200
    get_favorites_resp = session.get(f"{base_url}/see-all-favorites")
    assert get_favorites_resp.status_code == 200
    assert len(get_favorites_resp.json()["movies"]) == 0
    print("Clear all favorites test passed")

    # Log out
    logout_resp = session.post(f"{base_url}/logout")
    assert logout_resp.status_code == 200
    assert logout_resp.json()["status"] == "success"
    print("Logout successful")

    create_movie_logged_out_resp = session.post(f"{base_url}/add-favorite-movie", json=test_Tag)
    # This should fail because we are logged out
    assert create_movie_logged_out_resp.status_code == 401
    assert create_movie_logged_out_resp.json()["status"] == "error"
    print("Movie creation failed as expected")

if __name__ == "__main__":
    run_smoketest()
