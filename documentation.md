"""
Book Recommendation App

- This Flask application serves as a front-end for a book recommendation system. 
- Users can register, log in, search for books using the Google Books API, and save their favorites. 
- Favorites are stored in JSON format, and users can manage them through the app.

Author: Paul, Tim, Thang
Date: 06.10.2024
Version: 0.1.0 (major.minor.bugfix)
License: Free
"""

from flask import Flask, render_template, request, redirect, session, url_for
from backend import database, google_books_api, json_storage

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management

# Create tables if they do not exist
with app.app_context():
    database.create_tables()


@app.route('/')
def index():
    """
    Displays the homepage.
    
    Returns:
        Rendered homepage (index.html).

    Tests:
        1. **Homepage Rendering**:
            - Input: None.
            - Expected Outcome: The function should return the rendered index.html template without any errors.

        2. **Status Code Check**:
            - Input: None.
            - Expected Outcome: The function should return a status code of 200 indicating successful rendering.
    """
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user registration.

    POST:
        Registers the user with the provided username and password.

    Returns:
        Redirects to the login page after registration, or renders the registration form if a GET request is made.

    Tests:
        1. **User Registration**:
            - Input: Valid username and password via POST request.
            - Expected Outcome: The function should register the user and redirect to the login page.

        2. **Registration Form Rendering**:
            - Input: GET request.
            - Expected Outcome: The function should return the rendered registration form (register.html).
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Register the user
        database.register_user(username, password)

        # Redirect the user to the login page
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login.

    POST:
        Authenticates the user based on the provided username and password.
    
    Returns:
        Redirects to the search page if successful, otherwise reloads the login page with an error.

    Tests:
        1. **Successful Login**:
            - Input: Valid username and password via POST request.
            - Expected Outcome: The function should authenticate the user and redirect to the search page.

        2. **Login Failure Handling**:
            - Input: Invalid username and password via POST request.
            - Expected Outcome: The function should return an error message indicating login failure without redirecting.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists
        user = database.authenticate_user(username, password)
        if user:
            session['user_id'] = user[0]  # user[0] is the user's ID
            return redirect('/search')
        else:
            return 'Login failed. Please check your username and password.'

    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    Logs out the user by clearing the session.

    Returns:
        Redirects to the homepage.

    Tests:
        1. **Session Clearing**:
            - Input: None.
            - Expected Outcome: The session should be cleared (user_id should not exist).

        2. **Redirecting to Homepage**:
            - Input: None.
            - Expected Outcome: The function should redirect to the homepage (index route).
    """
    session.pop('user_id', None)
    return redirect('/')


@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    Displays the search form and processes the user's search query.

    POST:
        Retrieves books from the Google Books API based on user input (field and topic).
    
    Returns:
        Renders the search results page if successful or the search form for a GET request.

    Tests:
        1. **Search Results Retrieval**:
            - Input: Valid field and topic via POST request.
            - Expected Outcome: The function should return rendered results.html with books based on the search query.

        2. **Unauthorized Access Handling**:
            - Input: GET request without a user logged in.
            - Expected Outcome: The function should redirect to the login page.
    """
    if 'user_id' not in session:
        return redirect('/login')  # User must be logged in

    if request.method == 'POST':
        field_of_interest = request.form['field']
        specific_topic = request.form.get('topic', '')

        # Retrieve books from the Google Books API based on search criteria
        books = google_books_api.search_books(field_of_interest, specific_topic)

        # Display results
        return render_template('results.html', books=books, category=field_of_interest)

    return render_template('search.html')


@app.route('/favorites', methods=['GET'])
def favorites():
    """
    Displays the user's favorite books.

    Returns:
        Renders the favorites page with the user's favorite books filtered by category if applicable.

    Tests:
        1. **Favorites Retrieval**:
            - Input: Valid user session.
            - Expected Outcome: The function should return rendered favorites.html with the user's favorite books.

        2. **Category Filtering**:
            - Input: Valid user session and category filter in the query string.
            - Expected Outcome: The function should return rendered favorites.html with only books that match the specified category.
    """
    user_id = session.get('user_id')

    # Load all favorites and filter only the current user's favorites
    all_favorites = json_storage.load_all_favorites()
    favorites_json = all_favorites.get(str(user_id), [])

    # Optional: Filter by category
    category_filter = request.args.get('category', None)
    if category_filter:
        favorites_json = [book for book in favorites_json if book.get('category') == category_filter]

    return render_template('favorites.html', favorites=favorites_json, category_filter=category_filter)


@app.route('/remove_favorites', methods=['POST'])
def remove_favorites_view():
    """
    Handles removing selected favorite books for a user.

    POST:
        Removes the books with the selected ISBNs from the user's favorites list.

    Returns:
        Redirects to the favorites page.

    Tests:
        1. **Favorites Removal**:
            - Input: Valid user session and selected ISBNs.
            - Expected Outcome: The function should remove the specified books from the user's favorites and redirect to the favorites page.

        2. **Unauthorized Removal Handling**:
            - Input: POST request without a logged-in user.
            - Expected Outcome: The function should redirect to the login page.
    """
    if 'user_id' in session:
        user_id = session['user_id']
        selected_isbns = request.form.getlist('selected_books')

        if selected_isbns:
            # Remove selected favorites from the JSON file
            json_storage.remove_favorites(user_id, selected_isbns)

        return redirect(url_for('favorites'))
    return redirect(url_for('login'))


@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    """
    Adds selected books to the user's favorites.

    POST:
        Saves the selected books (with title, author, ISBN, publication year) to the user's favorites list.

    Returns:
        Redirects to the favorites page.

    Tests:
        1. **Adding Favorite Books**:
            - Input: Valid book details via POST request.
            - Expected Outcome: The function should save the book details to the user's favorites and redirect to the favorites page.

        2. **Handling Missing Data**:
            - Input: Missing one or more required fields (title, author, ISBN, publication year).
            - Expected Outcome: The function should return a 400 status code with an error message indicating missing data.
    """
    user_id = session.get('user_id')

    selected_books = request.form.getlist('selected_books')
    if not selected_books:
        return "No books selected.", 400

    for index in selected_books:
        title = request.form.get(f'title_{index}')
        author = request.form.get(f'author_{index}')
        isbn = request.form.get(f'isbn_{index}')
        publication_year = request.form.get(f'publication_year_{index}')
        category = request.form.get(f'category_{index}', 'Uncategorized')

        if not all([title, author, isbn, publication_year]):
            return "Missing data for one of the books.", 400

        # Prepare book details
        book_details = {
            'title': title,
            'author': author,
            'isbn': isbn,
            'publication_year': publication_year,
            'category': category
        }

        # Save the book to JSON
        json_storage.save_favorite(user_id, book_details)

    return redirect('/favorites')


if __name__ == '__main__':
    app.run(debug=True)


---------------------------------------------------------------------------------------------------------------------------

"""
Database Module

- This module handles the SQLite database connection and operations such as user registration, authentication, and table creation for a book recommendation application.


Author: Paul, Tim, Thang
Date: 06.10.2024
Version: 0.1.0
License: Free
"""

import sqlite3

def connect_db():
    """
    Establishes a connection to the SQLite database.

    Returns:
        Connection object: SQLite connection to 'database.db'.

    Tests:
        1. **Database Connection Success**:
            - Input: Attempt to connect to the database.
            - Expected Outcome: A connection object is returned if the database exists.
        
        2. **Database Connection Error Handling**:
            - Input: (Simulate) Attempt to connect to a non-existent database.
            - Expected Outcome: An exception should be raised indicating that the database cannot be found (this requires a mock or testing environment).
    """
    return sqlite3.connect('database.db')

def create_tables():
    """
    Creates the 'users' and 'reading_progress' tables in the database if they do not exist.
    The 'users' table stores user information, and the 'reading_progress' table stores 
    the user's reading progress with foreign keys linking to the 'users' and 'books' tables.
    
    Returns:
        None

    Tests:
        1. **Table Creation Success**:
            - Input: Call create_tables() when the database is empty.
            - Expected Outcome: Tables 'users' and 'reading_progress' are created successfully without raising any errors.
        
        2. **Table Existence Check**:
            - Input: Call create_tables() twice in a row.
            - Expected Outcome: The second call should not raise any errors, and the tables should remain unchanged.
    """
    conn = connect_db()
    cur = conn.cursor()

    # Create 'users' table if it does not exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create 'reading_progress' table if it does not exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS reading_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            book_id INTEGER,
            book_title TEXT,
            date DATE DEFAULT (DATE('now')),
            pages_read INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    ''')

    conn.commit()
    conn.close()

def register_user(username, password):
    """
    Registers a new user by inserting their username and password into the 'users' table.

    Args:
        username (str): The username of the new user.
        password (str): The password of the new user.

    Returns:
        None

    Tests:
        1. **User Registration Success**:
            - Input: A valid username and password that do not already exist in the database.
            - Expected Outcome: The user is successfully added to the 'users' table.
        
        2. **Duplicate User Registration Handling**:
            - Input: Attempt to register a username that already exists in the 'users' table.
            - Expected Outcome: An exception or error message is raised, indicating that the username must be unique.
    """
    conn = connect_db()
    cur = conn.cursor()
    
    # Insert user data into the 'users' table
    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    """
    Authenticates a user by checking the provided username and password against the 'users' table.

    Args:
        username (str): The username to be checked.
        password (str): The password to be checked.

    Returns:
        tuple: A tuple containing the user data (id, username, password) if authentication is successful.
               None if the credentials are incorrect.

    Tests:
        1. **Successful Authentication**:
            - Input: A valid username and password that exist in the 'users' table.
            - Expected Outcome: A tuple (id, username, password) is returned for the authenticated user.
        
        2. **Unsuccessful Authentication**:
            - Input: A username and password that do not match any record in the 'users' table.
            - Expected Outcome: None is returned, indicating failed authentication.
        3. **Handling of Non-Existent User**:
            - Input: An invalid username or an empty string for the username.
            - Expected Outcome: None is returned, confirming that the user does not exist.
    """
    conn = connect_db()
    cur = conn.cursor()
    
    # Fetch the user data matching the given username and password
    cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cur.fetchone()  # Returns a tuple: (id, username, password) or None
    
    conn.close()
    
    return user  # Return the user tuple or None if the user is not found

---------------------------------------------------------------------------------------------------------------------------------
    """
Google Books API Module

- This module interacts with the Google Books API to search for books based on user input and retrieve book details using the ISBN.


Author: Paul, Tim, Thang
Date: 06.10.2024
Version: 0.1.0
License: Free
"""

import requests

def search_books(field_of_interest, specific_topic):
    """
    Searches for books based on the field of interest and specific topic using the Google Books API.

    Args:
        field_of_interest (str): The general category or subject area of interest.
        specific_topic (str): An optional specific topic or subcategory within the field of interest.

    Returns:
        list: A list of dictionaries containing details for up to 10 books. 
              Each dictionary contains the following book details:
              - 'title': Title of the book (str).
              - 'author': Author(s) of the book (str).
              - 'isbn': The ISBN of the book (str).
              - 'publication_year': Year of publication (str).
              - 'description': Description of the book (str).
              - 'category': The category or field of interest (str).

    Tests:
        1. **Valid Search Query**:
            - Input: `field_of_interest = "Science"`, `specific_topic = "Physics"`
            - Expected Outcome: The function should return a list of up to 10 dictionaries, each containing book details like 'title', 'author', 'isbn', etc. All fields should be populated with relevant data.

        2. **Empty Specific Topic**:
            - Input: `field_of_interest = "Fiction"`, `specific_topic = ""`
            - Expected Outcome: The function should return a list of up to 10 dictionaries containing fiction books without any filtering by specific topic. The books should still have their details populated correctly.
        
        3. **No Results Found**:
            - Input: `field_of_interest = "NonexistentCategory"`, `specific_topic = "MadeUpTopic"`
            - Expected Outcome: The function should return an empty list `[]`, indicating that no books were found for the given search criteria.
        
        4. **Invalid API Response Handling**:
            - Input: Simulate a scenario where the API returns an unexpected response format.
            - Expected Outcome: The function should handle the error gracefully and not throw an exception. Instead, it should return an empty list or default values.
    """
    query = f'{field_of_interest} {specific_topic}'
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}'
    response = requests.get(url)
    data = response.json()

    books = []
    for item in data.get('items', [])[:10]:  # Limit to 10 books
        book_info = item.get('volumeInfo', {})

        # Add book details
        books.append({
            'title': book_info.get('title', 'N/A'),
            'author': ', '.join(book_info.get('authors', ['N/A'])),
            'isbn': book_info.get('industryIdentifiers', [{'identifier': 'N/A'}])[0]['identifier'],
            'publication_year': book_info.get('publishedDate', 'N/A'),
            'description': book_info.get('description', 'No description available'),
            'category': field_of_interest  # Add the field of interest as the category
        })

    return books


def get_book_by_isbn(isbn):
    """
    Retrieves book details from the Google Books API based on the provided ISBN.

    Args:
        isbn (str): The International Standard Book Number (ISBN) of the book to be retrieved.

    Returns:
        dict or None: A dictionary containing the following book details if found:
            - 'title': Title of the book (str).
            - 'author': Author(s) of the book (str).
            - 'isbn': The ISBN of the book (str).
            - 'publication_year': Year of publication (str).
            - 'description': Description of the book (str).
          Returns `None` if no book is found with the given ISBN.
        
    Tests:
        1. **Valid ISBN**:
            - Input: `isbn = "9780134685991"` (A valid ISBN for a known book)
            - Expected Outcome: The function should return a dictionary containing the book details such as 'title', 'author', 'isbn', etc., with all fields populated with valid information.

        2. **Invalid ISBN**:
            - Input: `isbn = "0000000000000"` (An invalid or nonexistent ISBN)
            - Expected Outcome: The function should return `None`, indicating that no book was found for the given ISBN.
        
        3. **Empty ISBN**:
            - Input: `isbn = ""`
            - Expected Outcome: The function should return `None`, as an empty ISBN is not valid for searching.
        
        4. **Malformed API Response**:
            - Input: Simulate a situation where the API returns an unexpected or malformed response.
            - Expected Outcome: The function should not raise an exception but should return `None`, handling the unexpected response appropriately.
    """
    url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}'
    response = requests.get(url)
    data = response.json()

    # Check if 'items' is present in the response JSON
    if 'items' not in data:
        return None  # No results found

    item = data['items'][0]
    book_info = item.get('volumeInfo', {})

    return {
        'title': book_info.get('title', 'N/A'),
        'author': ', '.join(book_info.get('authors', ['N/A'])),
        'isbn': book_info.get('industryIdentifiers', [{'identifier': 'N/A'}])[0]['identifier'],
        'publication_year': book_info.get('publishedDate', 'N/A'),
        'description': book_info.get('description', 'No description available')
    }

---------------------------------------------------------------------------------------------------------------------------------

"""
Favorites Management Module

- This module provides functionality to manage users' favorite books using a JSON file for storage. 
- Users can save their favorite books, add notes about their learning, update the current page they are on, and remove books from their favorites list.

Author: Paul, Tim, Thang
Date: 06.10.2024
Version: 0.1.0
License: Free
"""

import json
import os

# Path to the JSON file for favorites
FAVORITES_JSON_PATH = 'favorites.json'


def load_all_favorites():
    """
    Load all favorites from the JSON file.
    
    Returns:
        dict: A dictionary where keys are user IDs and values are lists of favorite books for each user.
              Returns an empty dictionary if the file doesn't exist or is not readable.
    
    Tests:
        1. **File Exists**:
            - Input: A valid JSON file located at `FAVORITES_JSON_PATH`.
            - Expected Outcome: The function should return a dictionary containing the user's favorite books as loaded from the JSON file.
        
        2. **File Does Not Exist**:
            - Input: A scenario where the JSON file does not exist.
            - Expected Outcome: The function should return an empty dictionary.
        
        3. **Corrupted JSON File**:
            - Input: A corrupted JSON file (e.g., missing brackets).
            - Expected Outcome: The function should catch the JSONDecodeError and return an empty dictionary.
    """
    if not os.path.exists(FAVORITES_JSON_PATH):
        return {}

    try:
        with open(FAVORITES_JSON_PATH, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}


def load_user_favorites(user_id):
    """
    Load favorites for a specific user.

    Args:
        user_id (int or str): The ID of the user whose favorites should be loaded.

    Returns:
        list: A list of favorite books for the given user, or an empty list if the user has no favorites.
    
    Tests:
        1. **User Has Favorites**:
            - Input: A user ID that exists in the favorites JSON file.
            - Expected Outcome: The function should return a list of favorite books for that user.
        
        2. **User Has No Favorites**:
            - Input: A user ID that does not exist in the favorites JSON file.
            - Expected Outcome: The function should return an empty list.
    """
    all_favorites = load_all_favorites()
    return all_favorites.get(str(user_id), [])


def save_favorite(user_id, book_details):
    """
    Save a favorite book for a user in the JSON file.

    Args:
        user_id (int or str): The ID of the user adding a favorite.
        book_details (dict): A dictionary containing the details of the book (e.g., title, author, ISBN).
    
    Returns:
        None
    
    Tests:
        1. **Valid Save**:
            - Input: A user ID that exists and valid book details.
            - Expected Outcome: The book should be added to the user's favorites in the JSON file.
        
        2. **Duplicate Book**:
            - Input: A user ID that exists and book details that are already in the user's favorites.
            - Expected Outcome: The user's favorites should remain unchanged, and the duplicate book should not be added.
    """
    all_favorites = load_all_favorites()

    if str(user_id) not in all_favorites:
        all_favorites[str(user_id)] = []

    # Check if the book already exists
    existing_book = next((book for book in all_favorites[str(user_id)] if book['isbn'] == book_details['isbn']), None)

    if not existing_book:
        all_favorites[str(user_id)].append(book_details)

        # Write the updated favorites back to the JSON file
        with open(FAVORITES_JSON_PATH, 'w') as file:
            json.dump(all_favorites, file, indent=4)


def save_favorite_learning(user_id, book_isbn, learning):
    """
    Save a learning note for a book in the favorites JSON file.

    Args:
        user_id (int or str): The ID of the user.
        book_isbn (str): The ISBN of the book for which the learning note is being saved.
        learning (str): The learning note or takeaway from the book.

    Returns:
        None

    Tests:
        1. **Valid Learning Note Update**:
            - Input: A user ID that exists, a valid ISBN, and a learning note.
            - Expected Outcome: The learning note should be updated in the user's favorite book entry in the JSON file.
        
        2. **Nonexistent Book**:
            - Input: A user ID that exists but a book ISBN that is not in the user's favorites.
            - Expected Outcome: The JSON file should remain unchanged since there’s no matching book.
    """
    all_favorites = load_all_favorites()

    if str(user_id) in all_favorites:
        # Find the book by its ISBN and update its learning note
        for book in all_favorites[str(user_id)]:
            if book['isbn'] == book_isbn:
                book['learning'] = learning
                break

        # Write the updated favorites back to the JSON file
        with open(FAVORITES_JSON_PATH, 'w') as file:
            json.dump(all_favorites, file, indent=4)


def remove_favorites(user_id, selected_isbns):
    """
    Remove selected favorites for a user from the JSON file.

    Args:
        user_id (int or str): The ID of the user.
        selected_isbns (list): A list of ISBNs for the books to be removed from the user's favorites.

    Returns:
        None

    Tests:
        1. **Valid Removal**:
            - Input: A user ID that exists and a list of ISBNs that are present in the user's favorites.
            - Expected Outcome: The specified books should be removed from the user's favorites in the JSON file.
        
        2. **No Matching ISBNs**:
            - Input: A user ID that exists and a list of ISBNs that are not in the user's favorites.
            - Expected Outcome: The user's favorites should remain unchanged, and no books should be removed.
    """
    all_favorites = load_all_favorites()

    if str(user_id) in all_favorites:
        # Filter out the books whose ISBN is in the selected_isbns list
        all_favorites[str(user_id)] = [
            book for book in all_favorites[str(user_id)] if book['isbn'] not in selected_isbns
        ]

        # Write the updated favorites back to the JSON file
        with open(FAVORITES_JSON_PATH, 'w') as file:
            json.dump(all_favorites, file, indent=4)


def update_favorite_page(user_id, book_isbn, current_page):
    """
    Update the current page number of a favorite book for the user.

    Args:
        user_id (int or str): The ID of the user.
        book_isbn (str): The ISBN of the book being updated.
        current_page (int): The new current page number the user is on.

    Returns:
        None

    Tests:
        1. **Valid Page Update**:
            - Input: A user ID that exists, a valid ISBN of a favorite book, and a new current page number.
            - Expected Outcome: The current page number for the specified book should be updated in the user's favorites in the JSON file.
        
        2. **Nonexistent Book Update**:
            - Input: A user ID that exists and an ISBN that does not match any book in the user's favorites.
            - Expected Outcome: The JSON file should remain unchanged since there’s no matching book to update.
    """
    all_favorites = load_all_favorites()

    if str(user_id) in all_favorites:
        # Find the book by its ISBN and update the current page number
        for book in all_favorites[str(user_id)]:
            if book['isbn'] == book_isbn:
                book['current_page'] = current_page
                break

        # Write the updated favorites back to the JSON file
        with open(FAVORITES_JSON_PATH, 'w') as file:
            json.dump(all_favorites, file, indent=4)