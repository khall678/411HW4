import os

from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# from flask_cors import CORS

from config import ProductionConfig

from new_idea.db import db
from new_idea.model.movies_model import Movie
from New_idea.model.user_model import Users
from new_idea.utils.logger import configure_logger
from new_idea.utils.app_utils import get_movie_info


load_dotenv()

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    configure_logger(app.logger)

    app.config.from_object(config_class)

    db.init_app(app)  # Initialize db with app
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
    """Route to add a movie to the user's favorite list"""
    try:
        data = request.get_json()
        movie_name = data.get("name")

        # Fetch movie details from the external API (IMDb via RapidAPI)
        movie_details = get_movie_info(movie_name)
        if not movie_details or 'results' not in movie_details or len(movie_details['results']) == 0:
            return make_response(jsonify({
                "status": "error",
                "message": "Movie not found"
            }), 400)

        movie_info = movie_details['results'][0]
        genre = movie_info.get("genre", "Unknown")
        description = movie_info.get("description", "No description available.")
        year = movie_info.get("year", "Unknown")

        # Store the movie in the database (or some in-memory store)
        movie = Movie.create_movie(movie_name, genre, description, year)
        
        return make_response(jsonify({
            "status": "success",
            "message": f"Movie '{movie_name}' added to favorites."
        }), 201)

    except Exception as e:
        app.logger.error(f"Error adding favorite movie: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An error occurred while adding the movie.",
            "details": str(e)
        }), 500)


@app.route('/api/get-favorite-movie', methods=['GET'])
@login_required
def get_favorite_movie():
    """Route to get details of a specific favorite movie"""
    try:
        movie_id = request.args.get('id')
        movie = Movie.get_movie_by_id(movie_id)
        if not movie:
            return make_response(jsonify({
                "status": "error",
                "message": "Movie not found"
            }), 404)
        
        # Fetch movie details from the API (optional to keep data updated)
        movie_details = get_movie_info(movie.name)

        return make_response(jsonify({
            "status": "success",
            "movie": movie_details
        }), 200)

    except Exception as e:
        app.logger.error(f"Error fetching favorite movie: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An error occurred while fetching the movie.",
            "details": str(e)
        }), 500)


@app.route('/api/view-all-favorites', methods=['GET'])
@login_required
def view_all_favorites():
    """Route to view all favorite movies"""
    try:
        favorite_movies = Movie.get_all_movies()
        all_movies_details = []
        for movie in favorite_movies:
            # Get updated details from the API
            movie_details = get_movie_info(movie.name)
            all_movies_details.append(movie_details)
        
        return make_response(jsonify({
            "status": "success",
            "movies": all_movies_details
        }), 200)

    except Exception as e:
        app.logger.error(f"Error viewing all favorites: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An error occurred while viewing all favorite movies.",
            "details": str(e)
        }), 500)


@app.route('/api/see-all-favorites', methods=['GET'])
@login_required
def see_all_favorites():
    """Route to see all favorite movie names"""
    try:
        favorite_movies = Movie.get_all_movies()
        movie_names = [movie.name for movie in favorite_movies]
        
        return make_response(jsonify({
            "status": "success",
            "movies": movie_names
        }), 200)

    except Exception as e:
        app.logger.error(f"Error seeing all favorites: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An error occurred while retrieving favorite movie names.",
            "details": str(e)
        }), 500)


@app.route('/api/delete-favorite-movie', methods=['DELETE'])
@login_required
def delete_favorite_movie():
    """Route to delete a movie from favorites"""
    try:
        movie_id = request.args.get('id')
        movie = Movie.delete_movie(movie_id)
        if not movie:
            return make_response(jsonify({
                "status": "error",
                "message": "Movie not found"
            }), 404)

        return make_response(jsonify({
            "status": "success",
            "message": f"Movie with ID {movie_id} removed from favorites."
        }), 200)

    except Exception as e:
        app.logger.error(f"Error deleting favorite movie: {e}")
        return make_response(jsonify({
            "status": "error",
            "message": "An error occurred while deleting the movie.",
            "details": str(e)
        }), 500)

if __name__ == '__main__':
    app = create_app()
    app.logger.info("Starting Flask app...")
    try:
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
    except Exception as e:
        app.logger.error(f"Flask app encountered an error: {e}")
    finally:
        app.logger.info("Flask app has stopped.")