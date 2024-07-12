import streamlit as st
import requests

st.title('Streamlit Library App')

# Initialize session state for token if it doesn't exist
if 'access_token' not in st.session_state:
    st.session_state['access_token'] = None
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None

def login():
    st.subheader('Login')
    # Input fields for username and password
    username = st.text_input('Username', key='user_login')
    password = st.text_input('Password', key='pass_login', type='password')

    # Handle the login button click
    if st.button('Login', key='login_button'):
        url = "http://localhost:3000/token"
        form_data = {'username': username, 'password': password}
        response = requests.post(url, data=form_data)
        if response.status_code == 200:
            token = response.json()
            st.session_state['access_token'] = token['access_token']
            st.session_state['role'] = token.get('role')
            st.success('Token has been saved')
        else:
            st.error('Invalid credentials')
            st.write(response.json())


def signup():
    st.subheader("Sign Up")

    username = st.text_input('Username', key='username')
    password = st.text_input('Password', key='password')
    email = st.text_input('Email', key='email')
    role = st.text_input('Role', key='role')

    if st.button('Signup', key='signup_button'):
        api_url = "http://localhost:3000/signup"
        params = {'username': username, 'password': password, 'email': email, 'role': role}
        response = requests.post(api_url, json=params)

        if response.status_code == 200:
            st.success('Signup successful')
        else:
            st.error('Signup failed')

col1, col2 = st.columns(2)
with col1:
    login()
with col2:
    signup()

st.title("Fetching Data")

# Parameters for the GET request
skip = st.number_input("Skip", min_value=0, value=0, step=1)
limit = st.number_input("Limit", min_value=1, value=100, step=1)

def fetch_authors():
    api_url = "http://localhost:3000/authors"
    params = {'skip': skip, 'limit': limit}
    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        authors = response.json()
        st.write(authors)
    else:
        st.write(f"Error: {response.status_code}")

def fetch_books():
    api_url = "http://localhost:3000/books"
    params = {'skip': skip, 'limit': limit}
    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        books = response.json()
        st.write(books)
    else:
        st.write(f"Error: {response.status_code}")

def fetch_categories():
    api_url = "http://localhost:3000/categories"
    params = {'skip': skip, 'limit': limit}
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        categories = response.json()
        return categories
    else:
        st.write(f"Error: {response.status_code}")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Fetch Authors", key="fetch_authors"):
        fetch_authors()
with col2:
    if st.button("Fetch Categories", key="fetch_categories"):
        categories = fetch_categories()
        st.write(categories)
with col3:
    if st.button("Fetch Books", key="fetch_books"):
        fetch_books()






if st.session_state['access_token']:
    st.title('Admin Panel')
    if st.session_state['role'] != 'admin':
        st.warning("You do not have permission to create an author.")
    else:
        def create_author():
            st.subheader("Create Author")
            # Input fields for author data
            first_name = st.text_input('First Name')
            last_name = st.text_input('Last Name')
            dob = st.date_input('Date of Birth')
            email = st.text_input('Email')
            gender = st.selectbox('Gender', ['Male', 'Female', 'Other'])
            country = st.text_input('Country')

            def format_date(date_obj):
                return date_obj.strftime('%Y-%m-%d')

            params = {
                'first_name': first_name,
                'last_name': last_name,
                'dob': format_date(dob),
                'email': email,
                'gender': gender,
                'country': country
            }
            headers = {
                'Authorization': f'Bearer {st.session_state["access_token"]}',
                'Content-Type': 'application/json'
            }

            if st.button('Create Author', key='create_author'):
                api_url = "http://localhost:3000/authors"
                response = requests.post(api_url, json=params, headers=headers)
                if response.status_code == 200:
                    st.success('Author created!')
                    author = response.json()
                    st.write(author)
                else:
                    st.write(f"Error: {response.status_code}")
                    st.write(response.json())

            author_id = st.text_input('Author ID', key='author_id')

            if st.button('Update Author', key='update_author'):
                api_url = f"http://localhost:3000/authors/{author_id}"
                response = requests.put(api_url, json=params, headers=headers)
                if response.status_code == 200:
                    st.success('Author updated!')
                else:
                    st.write(f"Error: {response.status_code}")
                    st.write(response.json())

            if st.button("Delete Author", key="delete_author"):
                api_url = f"http://localhost:3000/authors/{author_id}"
                response = requests.delete(api_url, headers=headers)
                if response.status_code == 200:
                    st.success('Author deleted!')
                else:
                    st.write(response.json())

        def create_book():
            st.subheader("Create Book")

            title = st.text_input('Title')
            summary = st.text_input('Summary')
            author_id = st.text_input('Author ID')
            json_categories = fetch_categories()
            categories = st.multiselect('Categories', [category['id'] for category in json_categories])

            params = {
                'title': title,
                'summary': summary,
                'author_id': author_id,
                'categories': categories,
            }
            headers = {
                'Authorization': f'Bearer {st.session_state["access_token"]}',
                'Content-Type': 'application/json'
            }

            if st.button("Create Book", key="create_book"):
                api_url = "http://localhost:3000/books"
                response = requests.post(api_url, json=params, headers=headers)
                if response.status_code == 200:
                    st.success('Book created!')
                else:
                    st.write(f"Error: {response.status_code}")

            book_id = st.text_input('Book ID', key='book_id')
            if st.button("Update Book", key="update_book"):
                api_url = f"http://localhost:3000/books/{book_id}"
                response = requests.put(api_url, json=params, headers=headers)
                if response.status_code == 200:
                    st.success('Book updated!')
                else:
                    st.write(f"Error: {response.status_code}")
                    st.write(response.json())
            if st.button("Delete Book", key="delete_book"):
                api_url = f"http://localhost:3000/books/{book_id}"
                response = requests.delete(api_url, headers=headers)
                if response.status_code == 200:
                    st.success('Book deleted!')
                else:
                    st.write(response.json())


        def create_category():
            st.subheader("Create Category")
            name = st.text_input('Name')
            description = st.text_input('Description')

            params = {
                'name': name,
                'description': description
            }
            headers = {
                'Authorization': f'Bearer {st.session_state["access_token"]}',
                'Content-Type': 'application/json'
            }

            if st.button("Create Category", key="create_category"):
                api_url = "http://localhost:3000/categories"

                response = requests.post(api_url, json=params, headers=headers)
                if response.status_code == 200:
                    st.success('Category created!')
                else:
                    st.write(f"Error: {response.status_code}")

            category_id = st.text_input('Category ID', key='category_id')
            if st.button("Update Category", key="update_category"):
                api_url = f"http://localhost:3000/categories/{category_id}"
                response = requests.put(api_url, json=params, headers=headers)
                if response.status_code == 200:
                    st.success('Category updated!')
                else:
                    st.write(f"Error: {response.status_code}")
                    st.write(response.json())

            if st.button("Delete Category", key="delete_category"):
                api_url = f"http://localhost:3000/categories/{category_id}"
                response = requests.delete(api_url, headers=headers)
                if response.status_code == 200:
                    st.success('Category deleted!')
                else:
                    st.write(response.json())


        col1, col2, col3 = st.columns(3)
        with col1:
            create_author()
        with col2:
            create_book()
        with col3:
            create_category()

