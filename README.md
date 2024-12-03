# CSCI-499-Capstone-Project

This app is a web platform designed to enhance the concert-going experience by connecting users with similar music tastes and simplifying media sharing. Users can explore trending live performances, and find potential concert buddies through a matching system based on past events or musical preferences. The platform also offers instant messaging for users to connect, coordinate, and find concert buddies of a lifetime! After the concert, users can also conveniently share photos and videos in a centralized space, making it a one-stop hub for discovering, attending, and sharing concert memories with the people you experienced them with!

# Documentation:
## app.py:
This script is a Flask-based web application that integrates with a Supabase database to manage user accounts, surveys, and personalized concert recommendations. It provides routes for key user actions, including registration, login, survey submission, and viewing concert recommendations based on user preferences.
Main functionalities include:
  1. Account Management: Users can register, log in, and log out. Account details are securely stored in Supabase, and sessions manage user authentication across routes.
  2. Survey Submission: After registering, users complete a survey to provide demographic details and music preferences, which are stored in Supabase.
  3. Concert Recommendations: Based on survey data, the application recommends concerts. Users can navigate through concert options using "previous" and "next" controls. Concerts are fetched dynamically, allowing a personalized experience.
  4. Error Handling: Each database interaction is wrapped in error handling to ensure robust responses in case of connectivity issues or input errors.
  5. Session Management: Sessions track user-specific data across requests, and session clearing is implemented upon logout for privacy and data reset.

## api.py:
This script uses the requests library to fetch live concert event data from the "real-time-events-search" API based on genre, location, and optional budget parameters. It organizes the results into a structured format and includes a sample function with example data, which can be used as a placeholder or test data.
Main functionalities include:
  1. get_concerts: Fetches concerts matching specified criteria (genre, location, budget) and organizes the information into a list of dictionaries with concert details. The function processes JSON data from the API response, extracting details like concert name, description, time, and venue info.
  2. example_concerts: Returns a predefined list of concert event data, simulating what a real API call might return. Contains sample concerts with fields such as name, description, start_time, thumbnail, and venue information.

## fetch_user.py:
This script sets up a user JSON file which fetches all the users that have signed up for an account. This serves as a helper function to initialize a user JSON file to match people.
Main functionalities include:
  1. Connecting to the Supabase DB through the Supabase API.
  2. Fetching all users that are currently signed up and storing them in a JSON format.

## faiss_match.py:
This script uses FAISS to perform a similarity search on users to recommend to the currently logged-in user. First, each user's information is turned into an embedding that gets stored in the FAISS vector database. The database is then searched later to recommend people to the current user. A history of previously recommended users is also maintained to avoid recommending the same users again.

Main functionalities include:
  1. Turning each user's information into an embedding & storing it in a FAISS vector store.
  2. Querying through the vector database to find the most similar user to the current user through the use of nearest-neighbor searches [similarity search].
  For more information, visit: https://www.datacamp.com/blog/faiss-facebook-ai-similarity-search

Optional functionality:
  1. Including prompt engineering to provide a reason for the given recommendation. This is done in the hope of convincing users why the two matched users are a good match, resulting in more successful matches.



