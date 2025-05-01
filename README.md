# 411HW4
Route: /api/add-favorite-movie
  Request Type: POST
  Purpose: Adds a movie to the current user's list of favorite movies. Validates input, retrieves details from an external API, and stores it.
  Authentication Required: Yes (@login_required)
  Request Body:
    {
     title (str): The movie title.
    }
  Response Format: JSON
    Success Response Example:
    Code: 201
    {
      "status": "success",
      "message": "Movie 'Inception' added successfully",
      "data": {
        "title": "Inception",
        "year": "2010",
        "actors": "Leonardo DiCaprio, Joseph Gordon-Levitt"
      }
    }
    Error Response Examples:
    Code: 400 (Missing Fields)
    {
      "status": "error",
      "message": "Missing required fields: title"
    }
    Code: 400 (Invalid Data Type)
    {
      "status": "error",
      "message": "Invalid input types: title should be a string"
    }
    Code: 500
    {
      "status": "error",
      "message": "An internal error occurred while adding the movie.",
      "details": "Internal server error message"
    }

    
Route: /api/see-all-favorites
  Request Type: GET
  Purpose: Returns a list of favorite movie names (titles only) for the logged-in user.
  Authentication Required: Yes (@login_required)
  Request Body: None
  Response Format: JSON
    Success Response Example:
      Code: 200
      {
        "status": "success",
        "movies": ["Inception", "The Matrix"]
      }
    Error Response Example:
      Code: 500
      {
        "status": "error",
        "message": "An error occurred while fetching favorite movies.",
        "details": "Internal server error message"
      }



Route: /api/delete-favorite-movie
  Request Type: DELETE
  Purpose: Deletes a specific movie from the logged-in user’s favorites by movie_id sent in the request body.
  Authentication Required: Yes (@login_required)
  Request Body:
    {
      movie_id (int): The ID of the movie to delete.
    }
  Response Format: JSON
    Success Response Example:
      Code: 200
      {
        "status": "success",
        "message": "Movie deleted successfully",
        "deleted_id": 12
      }
    Error Response Examples:
      Code: 400 (Missing or Invalid Input)
      {
        "status": "error",
        "message": "Missing or invalid 'movie_id' field"
      }
      Code: 404 (Movie Not Found)
      {
        "status": "error",
        "message": "Movie not found or does not belong to the user"
      }
      Code: 500
      {
        "status": "error",
        "message": "An error occurred while deleting the movie",
        "details": "Internal server error message"
      }


Route: /api/clear-all-favorites
  ● Request Type: DELETE
  ● Purpose: Clear all favorite movies of the logged-in user.
  ● Request Body:
    ○ None
  ● Response Format: JSON
    Success Response Example:
      ■ Code: 200
      ■ Content: { "message": "All favorite movies cleared"}
    Failure Response Example:
      ■ Code: 500
      ■ Content: {"status": "error",
                      "message": "An error occurred while clearing favorite movies",
                    "details": str(e) }
  ● Example Request:
    { N/A}
  ● Example Response:
    {
    Code: 200,
    "message": "All favorite movies cleared.",
    "status": "success"
    }


Route: /api/get-movie-details
  ● Request Type: POST
  ● Purpose: Retrieves movie details from the database
  ● Request Body:
    ○ title (str): The movie title
  ● Response Format: JSON
    Success Response Example:
      ■ Code: 200
      ■ Content: { "data": movie}
    Failure Response Example:
    	■ Code: 400
      ■ Content: {"status": "error",
                          "message": "Missing required field: title"}
      ■ Code: 400
      ■ Content: {"status": "error",
                          "message": "Invalid input type: title should be a string"
      }
      ■ Code: 500
      ■ Content: {"status": "error",
                      "message": "An internal error occurred while retrieving the movie.",
         	"details": str(e)
      }
  ● Example Request:
    {
    "title": "Tag"
    }
  ● Example Response:
    {
    Code: 200,
    "Status”: success,
    "data": {
        "title": "Tag",
        "year": 2018,
        "actors": ["Ed Helms", "Jon Hamm", "Jeremy Renner"]
      }
    }     
