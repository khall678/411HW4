import os

from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from config import ProductionConfig, TestConfig


from new_idea.db import db
from new_idea.model.movies_model import Movies
from new_idea.model.user_model import Users
from new_idea.utils.logger import configure_logger
from new_idea.utils.api_utils import get_movie_info

FLASK_ENV = os.getenv('FLASK_ENV')
PORT = os.getenv('PORT', 5001)  # Default to 5001 if not set
DB_PATH = os.getenv('DB_PATH')
X_RAPIDAPI_KEY = os.getenv('X-RAPIDAPI-KEY')
X_RAPIDAPI_HOST = os.getenv('X-RAPIDAPI-HOST')

#app.config['ENV'] = FLASK_ENV


load_dotenv()


def create_app(config_name='production'):
    app = Flask(__name__)
    configure_logger(app.logger)

    if config_name == 'testing':
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(ProductionConfig)

    # Initialize your extensions here (db, etc.)
    db.init_app(app)

    with app.app_context():
        db.create_all()  # Recreate all tables

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.filter_by(username=user_id).first()

    @login_manager.unauthorized_handler
    def unauthorized():
        return make_response(jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401)




    ####################################################
    #
    # Healthchecks
    #
    ####################################################


    @app.route('/api/health', methods=['GET'])
    def healthcheck() -> Response:
        """
        Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.

        """
        app.logger.info("Health check endpoint hit")
        return make_response(jsonify({
            'status': 'success',
            'message': 'Service is running'
        }), 200)


    ##########################################################
    #
    # User Management
    #
    #########################################################

    @app.route('/api/create-user', methods=['PUT'])
    def create_user() -> Response:
        """Register a new user account.

        Expected JSON Input:
            - username (str): The desired username.
            - password (str): The desired password.

        Returns:
            JSON response indicating the success of the user creation.

        Raises:
            400 error if the username or password is missing.
            500 error if there is an issue creating the user in the database.
        """
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Username and password are required"
                }), 400)

            Users.create_user(username, password)
            return make_response(jsonify({
                "status": "success",
                "message": f"User '{username}' created successfully"
            }), 201)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)
        except Exception as e:
            app.logger.error(f"User creation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while creating user",
                "details": str(e)
            }), 500)

    @app.route('/api/login', methods=['POST'])
    def login() -> Response:
        """Authenticate a user and log them in.

        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The password of the user.

        Returns:
            JSON response indicating the success of the login attempt.

        Raises:
            401 error if the username or password is incorrect.
        """
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Username and password are required"
                }), 400)

            if Users.check_password(username, password):
                user = Users.query.filter_by(username=username).first()
                login_user(user)
                return make_response(jsonify({
                    "status": "success",
                    "message": f"User '{username}' logged in successfully"
                }), 200)
            else:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Invalid username or password"
                }), 401)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 401)
        except Exception as e:
            app.logger.error(f"Login failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred during login",
                "details": str(e)
            }), 500)

    @app.route('/api/logout', methods=['POST'])
    @login_required
    def logout() -> Response:
        """Log out the current user.

        Returns:
            JSON response indicating the success of the logout operation.

        """
        logout_user()
        return make_response(jsonify({
            "status": "success",
            "message": "User logged out successfully"
        }), 200)

    @app.route('/api/change-password', methods=['POST'])
    @login_required
    def change_password() -> Response:
        """Change the password for the current user.

        Expected JSON Input:
            - new_password (str): The new password to set.

        Returns:
            JSON response indicating the success of the password change.

        Raises:
            400 error if the new password is not provided.
            500 error if there is an issue updating the password in the database.
        """
        try:
            data = request.get_json()
            new_password = data.get("new_password")

            if not new_password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "New password is required"
                }), 400)

            username = current_user.username
            Users.update_password(username, new_password)
            return make_response(jsonify({
                "status": "success",
                "message": "Password changed successfully"
            }), 200)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)
        except Exception as e:
            app.logger.error(f"Password change failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while changing password",
                "details": str(e)
            }), 500)

    @app.route('/api/reset-users', methods=['DELETE'])
    def reset_users() -> Response:
        """Recreate the users table to delete all users.

        Returns:
            JSON response indicating the success of recreating the Users table.

        Raises:
            500 error if there is an issue recreating the Users table.
        """
        try:
            app.logger.info("Received request to recreate Users table")
            with app.app_context():
                Users.__table__.drop(db.engine)
                Users.__table__.create(db.engine)
            app.logger.info("Users table recreated successfully")
            return make_response(jsonify({
                "status": "success",
                "message": f"Users table recreated successfully"
            }), 200)

        except Exception as e:
            app.logger.error(f"Users table recreation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while deleting users",
                "details": str(e)
            }), 500)

    ##########################################################
    #
    # Movies
    #
    ##########################################################

    @app.route('/api/add-favorite-movie', methods=['POST'])
    @login_required
    def add_favorite_movie():
        """Route to add a movie to the user's favorite list

        Expected JSON Input:
            - title (str): The movie title.
        
        Returns a JSON repsonse indicating success/failure

         Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the movie to the database.
        """
        app.logger.info("Received request to add a foavorite movie")
        try:
            data = request.get_json()
            
            required_fields = ["title"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                app.logger.warning(f"Missing required fields: {missing_fields}")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }), 400)
            
            title = data['title']

            if (
                not isinstance(title, str)
            ):
                app.logger.warning("Invalid input data types")
                return make_response(jsonify({
                    "status": "error",
                    "message": "Invalid input types: title should be a string"
                }), 400)
            
            title = data['title'].strip()
            
            app.logger.info(f"Adding movie: {title}")
            new_movie = Movies.add_favorite_movie(title)

            app.logger.info(f"Movie added successfully: {title}")
            return make_response(jsonify({
                "status": "success",
                "message": f"Movie '{title}' added successfully",
                "data": {
                    "title": new_movie.title,
                    "year": new_movie.year,
                    "actors": new_movie.actors
                }
            }), 201)

        except Exception as e:
            app.logger.error(f"Failed to add favorite movie: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while adding the movie.",
                "details": str(e)
            }), 500)

    @app.route('/api/see-all-favorites', methods=['GET'])
    @login_required
    def see_all_favorites():
        """Get all favorite movies of the logged-in user.

        Returns:
            JSON response with the list of favorite movies.
        """
        try:
            # Fetch all movies from the database
            movies = Movies.query.all()

            movie_list = []
            for movie in movies:
                movie_list.append({
                    'title': movie.title
                })

            return make_response(jsonify({
                "status": "success",
                "movies": movie_list
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to fetch favorite movies: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An error occurred while fetching favorite movies",
                "details": str(e)
            }), 500)



    @app.route('/api/delete-favorite-movie', methods=['DELETE'])
    @login_required
    def delete_favorite_movie():
        """
        Route to delete a movie from the user's favorite list by movie_id.

        Expected JSON input:
            - movie_id (int): The ID of the movie to delete.

        Returns:
            JSON indicating success or failure.
        """
        try:
            data = request.get_json()

            if "movie_id" not in data or not isinstance(data["movie_id"], int):
                return make_response(jsonify({
                    "status": "error",
                    "message": "Missing or invalid 'movie_id' field"
                }), 400)

            movie_id = data["movie_id"]
            result = Movies.delete_favorite_movie(movie_id)

            if "error" in result:
                return make_response(jsonify({
                    "status": "error",
                    "message": result["error"]
                }), 404)

            return make_response(jsonify({
                "status": "success",
                "message": result["message"],
                "deleted_id": result["deleted_id"]
            }), 200)

        except Exception as e:
            app.logger.error(f"Error deleting movie: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An error occurred while deleting the movie",
                "details": str(e)
            }), 500)


    @app.route('/api/clear-all-favorites', methods=['DELETE'])
    @login_required
    def clear_all_favorites():
        """Clear all favorite movies of the logged-in user.

        Returns:
            JSON response indicating success or failure.
        """
        try:
            db.session.query(Movies).delete()  # Delete all movies
            db.session.commit()

            return make_response(jsonify({
                "status": "success",
                "message": "All favorite movies cleared"
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to clear favorite movies: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An error occurred while clearing favorite movies",
                "details": str(e)
            }), 500)

    @app.route('/api/get-movie-details', methods=['POST'])
    @login_required
    def get_movie_details():
        """
        Route to retrieve movie details from the database.

        Expected JSON Input:
            - title (str): The movie title.

        Returns:
            JSON response with movie details (title, year, actors) or error message.

        Raises:
            400 error if input validation fails.
            404 error if movie is not found.
            500 error for database or server issues.
        """
        app.logger.info("Received request to fetch movie details")

        try:
            data = request.get_json()

            if not data or 'title' not in data:
                app.logger.warning("Missing 'title' in request")
                return make_response(jsonify({
                    "status": "error",
                    "message": "Missing required field: title"
                }), 400)

            title = data['title']
            if not isinstance(title, str):
                app.logger.warning("Invalid input type for 'title'")
                return make_response(jsonify({
                    "status": "error",
                    "message": "Invalid input type: title should be a string"
                }), 400)

            title = title.strip()
            app.logger.info(f"Attempting to retrieve movie details for title: {title}")

            movie = Movies.get_movie_details(title)
        

            return make_response(jsonify({
                "status": "success",
                "data": movie
            }), 200)

        except ValueError as e:
            app.logger.warning(f"Movie not found: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 404)

        except Exception as e:
            app.logger.error(f"Internal error while fetching movie details: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving the movie.",
                "details": str(e)
            }), 500)

    return app

if __name__ == '__main__':
    app = create_app()
    app.logger.info("Starting Flask app...")
    try:
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
    except Exception as e:
        app.logger.error(f"Flask app encountered an error: {e}")
    finally:
        app.logger.info("Flask app has stopped.")