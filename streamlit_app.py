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

# if st.session_state['access_token']:
#     chatapp_button = st.button("Go to Chat App")
#     if chatapp_button:
#         chatapp_url = "http://localhost:8502/"
#         st.write(f'<iframe src="{chatapp_url}" width=700 height=600></iframe>', unsafe_allow_html=True)

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

if 'selected_session' not in st.session_state:
    st.session_state.selected_session = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

def icon_with_text():
    col4, col5, col6 = st.columns([1, 2, 1])
    with col4:
        st.write("")
    with col5:
        st.markdown(
            """
            <div style="text-align: center;">
                <img src="icons8-guide-48.png" style='width:30px;'/>
                <p style="margin: 0;">Guides</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col6:
        st.write("")
def default_page():
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
            <h2>I will answer your questions</h2>
            <p>Get started with blabla</p>
        </div>
        """, unsafe_allow_html=True)
    st.write("")
    st.write("")
    st.write("")
    col1, col2, col3 = st.columns(3)
    with col1:
        icon_with_text()
        with st.container(border=True):
            st.markdown("Lorem ipsum " * 3)
        with st.container(border=True):
            st.markdown("Lorem ipsum " * 3)
    with col2:
        icon_with_text()
        with st.container(border=True):
            st.markdown("Lorem ipsum " * 3)
        with st.container(border=True):
            st.markdown("Lorem ipsum " * 3)
    with col3:
        icon_with_text()
        with st.container(border=True):
            st.markdown("Lorem ipsum " * 3)
        with st.container(border=True):
            st.markdown("Lorem ipsum " * 3)

prompt = st.chat_input("Type your text here and magic will happen")

def create_session(prompt):
    user_id = get_curr_user()
    st.session_state['user_id'] = user_id
    params = {
        'name': prompt,
        'user_id': user_id
    }
    headers = {
        'Authorization': f'Bearer {st.session_state["access_token"]}',
        'Content-Type': 'application/json'
    }

    api_url = f"http://localhost:3000/sessions"
    response = requests.post(api_url, json=params, headers=headers)
    if response.status_code == 200:
        # st.write(response.json()['name'])
        return fetch_session(response.json()['name'])
    else:
        st.error("Error")

def fetch_session(session_name):
    api_url = f"http://localhost:3000/sessions/{session_name}"
    params = {'name': session_name}
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        return response.json()['id']
    else:
        st.write(f"Error: {response.status_code}")

def fetch_all_sessions():
    api_url = f"http://localhost:3000/sessions"
    params = {'skip': skip, 'limit': limit}
    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        sessions = response.json()
        return sessions
    else:
        st.write(f"Error: {response.status_code}")

def fetch_chat(session_id):
    api_url = f"http://localhost:3000/chat/{session_id}"
    params = {'session_id': session_id}
    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        chats = response.json()
        return chats
    else:
        st.write(f"Error: {response.status_code}")

def new_chat(session_id):
    if not session_id:
        session_id = create_session(prompt)
        print(f"I am making session {session_id}")
        st.session_state.selected_session = session_id

    with st.chat_message("user"):
        st.markdown(prompt)

    params = {
        'sent': prompt,
        'session_id': session_id
    }

    api_url = f"http://localhost:3000/chat/{prompt}"

    response = requests.post(api_url, json=params)
    if response.status_code == 200:
        return response.json()['receive']
    else:
        st.error("ERROR")

def get_curr_user():
    api_url = f"http://localhost:3000/users/me"
    headers = {
        'Authorization': f'Bearer {st.session_state["access_token"]}',
        'Content-Type': 'application/json'
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()["id"]
    else:
        st.error("Error fetching curr user, please log in")


with st.sidebar:
    st.write("History....")
    sessions = fetch_all_sessions()
    if sessions:
        for session in sessions:
            if st.sidebar.button(session['name'], key=session['id']):
                st.session_state.selected_session = session['id']

if st.button("New chat", key="new_chat"):
    # st.write(st.session_state.selected_session)
    st.session_state.selected_session = None

if 'selected_session' in st.session_state and st.session_state.get('selected_session'):
    st.write("Select a session from the sidebar to start chatting")
    if st.session_state.selected_session:
        chats = fetch_chat(st.session_state.selected_session)
        if chats:
            for message in chats:
                with st.chat_message("user"):
                    st.markdown(message['sent'])
                with st.chat_message("assistant"):
                    st.markdown(message['receive'])
        if prompt:
            output = new_chat(st.session_state.selected_session)
            if output:
                with st.chat_message("assistant"):
                    st.markdown(output)
            else:
                with st.chat_message("assistant"):
                    st.error("Error")
else:
    # st.write(prompt)
    if prompt:
        output = new_chat(session_id=None)
        if output:
            with st.chat_message("assistant"):
                st.markdown(output)
        else:
            with st.chat_message("assistant"):
                st.error("Error")
    else:
        default_page()

