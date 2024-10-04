from flask import Flask, render_template, request, redirect, session, url_for
from backend import database, google_books_api, json_storage

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management

# Create tables if they do not exist
with app.app_context():
    database.create_tables()


@app.route('/')
def index():
    """Displays the homepage."""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
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
    """Handles user login."""
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
    """Handles user logout."""
    session.pop('user_id', None)
    return redirect('/')


@app.route('/search', methods=['GET', 'POST'])
def search():
    """Displays the search form and processes the user's search query."""
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
    """Displays the user's favorite books."""
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
    """Handles removing selected favorite books for a user."""
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
    """Adds selected books to the user's favorites."""
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


@app.route('/test_json_favorites', methods=['GET'])
def test_json_favorites():
    """Test route to display the contents of the favorites JSON file."""
    favorites_data = json_storage.load_all_favorites()
    return render_template('test_json.html', favorites_data=favorites_data)


@app.route('/bookmark', methods=['GET'])
def bookmark():
    """Displays the user's bookmarks."""
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    # Load all favorites and filter for the current user
    all_favorites = json_storage.load_all_favorites()
    favorites = all_favorites.get(str(user_id), [])

    return render_template('bookmarks.html', favorites=favorites)




@app.route('/update_favorite_page', methods=['POST'])
def update_favorite_page():
    """Updates the current page for a favorite book."""
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')  # User must be logged in

    # Get data from the form
    book_isbn = request.form['book_isbn']
    current_page = request.form['current_page']

    try:
        current_page = int(current_page)  # Ensure page number is a valid integer
    except ValueError:
        return "Invalid page number", 400

    # Update the current page in the JSON file
    json_storage.update_favorite_page(user_id, book_isbn, current_page)

    # Reload the page with the updated data
    favorites = json_storage.load_user_favorites(user_id)
    return render_template('bookmarks.html', favorites=favorites)



@app.route('/learnings', methods=['GET', 'POST'])
def learnings():
    """Displays and saves learning notes for a user's favorite books."""
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    if request.method == 'POST':
        book_isbn = request.form['book_isbn']
        learning = request.form['learning']

        json_storage.save_favorite_learning(user_id, book_isbn, learning)

        return redirect('/learnings')

    favorites = json_storage.load_user_favorites(user_id)

    return render_template('learnings.html', favorites=favorites)


if __name__ == '__main__':
    app.run(debug=True)
