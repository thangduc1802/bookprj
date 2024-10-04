
# Requirements
- Install dependencies:  
  ```bash
  pip install -r requirements.txt
  ```
- List of installed packages:  
  ```
  pip list
  ```
  (Include versions of the modules listed in the `requirements.txt`)
- To check the installed version of pip and the environment path, run:  
  ```bash
  pip -V
  ```


# Who We Are
- **Duc Thang Phung** - [Link to profile]
- **Paul Willy** - [Link to profile]
- **Tim Roesch** - [Link to profile]

# Description

## How to Start
1. Clone the repository:
   ```bash
   git clone https://github.com/TimR04/1
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask app:
   ```bash
   python app.py
   ```
4. Open browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## What We Want to Show
- User Authentication: A secure system for user registration, login, and session management.
- Book Search Functionality: Users can search for books by entering their fields of interest and specific topics. The results are fetched from the Google Books API.
- Favorites System: Users can save their favorite books and view them later. Books can be categorized based on fields of interest.
- Reading Progress: The app allows users to save their current reading progress for each book.
- Learning Notes: Users can write and store personal learning notes for each book they have saved.
- Bookmarks: Users can bookmark books for future reference.
- Book Details: Each book includes title, author, ISBN, publication year, and a description.
- Book Recommendations: Users can add their favorite books to their collection and revisit them when needed.

## Special Operations
- Search Books by Topic: The app integrates with the Google Books API to retrieve books based on user preferences. The search is dynamic and includes fields such as interest and topic.
- Store Favorites in JSON: The user's favorite books are saved in a JSON file, allowing the user to easily manage and remove them later.
- Session Management: User sessions are managed through Flask's built-in session handling, ensuring secure access to user-specific data.
- Page Progress Update: Users can save their reading progress for each book. The app updates the page number of where the user left off reading.
- Learning Notes Storage: Personal notes for each book are stored and associated with the user’s account in the JSON file, so users can record important insights or information about books.
- Remove Favorites: Users can remove multiple selected favorites from their saved list in one operation.
- Authentication and Authorization: Secure login and session management are used to restrict access to user-specific actions like adding favorites or saving progress.

# Additional README Information
- The documentation is auto-generated from the code's docstrings using **mkdocs**. To build the docs, run:
  ```bash
  mkdocs build
  ```

--- 

