# CSCI-499-Capstone-Project

This app is a web platform designed to enhance the concert-going experience by connecting users with similar music tastes and simplifying media sharing. Users can explore trending live performances, and find potential concert buddies through a matching system based on past events or musical preferences. The platform also offers instant messaging for users to connect, coordinate, and find concert buddies of a lifetime! After the concert, users can also conveniently share photos and videos in a centralized space, making it a one-stop hub for discovering, attending, and sharing concert memories with the people you experienced them with!

# Documentation:
### app.py:
This script is a Flask-based web application that integrates with a Supabase database to manage user accounts, surveys, and personalized concert recommendations. It provides routes for key user actions, including registration, login, survey submission, and viewing concert recommendations based on user preferences.
Main functionalities include:
  1. Account Management: Users can register, log in, and log out. Account details are securely stored in Supabase, and sessions manage user authentication across routes.
  2. Survey Submission: After registering, users complete a survey to provide demographic details and music preferences, which are stored in Supabase.
  3. Concert Recommendations: Based on survey data, the application recommends concerts. Users can navigate through concert options using "previous" and "next" controls. Concerts are fetched dynamically, allowing a personalized experience.
  4. Error Handling: Each database interaction is wrapped in error handling to ensure robust responses in case of connectivity issues or input errors.
  5. Session Management: Sessions track user-specific data across requests, and session clearing is implemented upon logout for privacy and data reset.
  6. User Recommendation: Based on the survey data, the application will recommend other users that the current user can match with to attend concerts together.

### api.py:
This script uses the requests library to fetch live concert event data from the "real-time-events-search" API based on genre, location, and optional budget parameters. It organizes the results into a structured format and includes a sample function with example data, which can be used as a placeholder or test data.
Main functionalities include:
  1. get_concerts: Fetches concerts matching specified criteria (genre, location, budget) and organizes the information into a list of dictionaries with concert details. The function processes JSON data from the API response, extracting details like concert name, description, time, and venue info.
  2. example_concerts: Returns a predefined list of concert event data, simulating what a real API call might return. Contains sample concerts with fields such as name, description, start_time, thumbnail, and venue information.

### fetch_user.py:
This script sets up a user JSON file which fetches all the users that have signed up for an account. This serves as a helper function to initialize a user JSON file to match people.
Main functionalities include:
  1. Connecting to the Supabase DB through the Supabase API.
  2. Fetching all users that are currently signed up and storing them in a JSON format.

### faiss_match.py:
This script uses FAISS to perform a similarity search on users to recommend to the currently logged-in user. First, each user's information is turned into an embedding that gets stored in the FAISS vector database. The database is then searched later to recommend people to the current user. A history of previously recommended users is also maintained to avoid recommending the same users again.

Main functionalities include:
  1. Turning each user's information into an embedding & storing it in a FAISS vector store.
  2. Querying through the vector database to find the most similar user to the current user through the use of nearest-neighbor searches [similarity search].
  For more information, visit: https://www.datacamp.com/blog/faiss-facebook-ai-similarity-search

Optional functionality:
  1. Including prompt engineering to provide a reason for the given recommendation. This is done in the hope of convincing users why the two matched users are a good match, resulting in more successful matches.

Sample Matching Test Case:

We are currently in user 'ninh' who is 25, have a certain music genre that they said they liked in their survey & we try to find a buddy that they could match with.

  ![Screenshot 2024-12-03 at 8 17 23 PM](https://github.com/user-attachments/assets/14b4c1b9-ed07-4b35-bedb-aa72cd8299cf)

We created a sample user named 'sameuserasninh' who is a test user that has all the similar information as 'ninh'. We are expecting this to get recommended when we click 'match me with a buddy' for user 'ninh'.

  ![Screenshot 2024-12-03 at 8 17 14 PM](https://github.com/user-attachments/assets/45ae06ce-cb1f-4a72-8fa9-216ef051ecc4)

As expected, for user 'ninh', the test user 'sameuserasninh' was recommended.


# Getting Started:
These are the steps on setting up the project locally.

### Prerequisites
  1. Make sure you have Python installed on your local machine. You can check if you have Python installed by running the following command:
      ```sh
      python --version
      ```
      - If not, install python. For more information, visit: 
        - https://realpython.com/installing-python/
        - https://docs.python.org/3/installing/index.html
  2. Install pip and virtualenv
      - Make sure that pip (Python's package installer) and virtualenv (for creating isolated Python environments) are installed. You can check by running these command:
        ```sh
         pip --version
        ```
        - If not installed, visit this website to set up 'pip'
          - https://pip.pypa.io/en/stable/installation/
        - if installed:
          - Continue to install python virtual environment:
            ```sh
            pip install virtualenv
            ```
### Installation

Installing and setting up the app:

1. Clone the repo
   ```sh
   git clone https://github.com/JakeMartin336/CSCI-499-Capstone-Project.git
   ```
2. Set up a virtual environment:
   ```sh
     python3 -m venv venv
   ```
   Once that is complete:

   For Mac:
   ```sh
   source venv/bin/activate # Mac
   ```
   For Windows:
   ```sh
     .\venv\Scripts\Activate # Windows
   ```
   For more information on python virtual environment, visit: https://www.geeksforgeeks.org/creating-python-virtual-environment-windows-linux/
4. Once the virtual environment is activated, install all the required packages:
   ```sh
   pip install -r requirements.txt # if requirements.txt is not found, make sure to include the specific path to requirements.txt
   ```
5. Create a  `.env` file in your root of your project.
  - Copy the following template and fill in your own values:
     ```bash
     SUPABASE_URL="https://azjyjnshzkanmzbidmlb.supabase.co"
     SUPABASE_API_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6anlqbnNoemthbm16YmlkbWxiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjkwOTU1MzQsImV4cCI6MjA0NDY3MTUzNH0.nTzxoslmmR1A-dsomD9EP-sUeAlA0Zk-ViMsM9exN-A"
     OPENAI_API_KEY=your-openai-api-key
     ```
5. Once everything is set up, run this command:
   ```sh
   flask run
   ```
   This should run the application and you are able to access it on your local machine.
## or
 Run this deployed version of it:
  - [[https://csci-499-capstone-project.onrender.com](https://csci-499-capstone-project.onrender.com)](https://csci-499-capstone-project.onrender.com)
<p align="right">(<a href="#readme-top">back to top</a>)</p>

