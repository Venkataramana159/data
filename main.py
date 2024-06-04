import streamlit as st
import pyrebase
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import uuid
import json

# Firebase configuration
firebaseConfig = {
    'apiKey': "AIzaSyC809oPeczPZZ0lBVavBgZggheNOOn48HU",
    'authDomain': "dataviz-94075.firebaseapp.com",
    'databaseURL': "https://dataviz-94075-default-rtdb.firebaseio.com",
    'projectId': "dataviz-94075",
    'storageBucket': "dataviz-94075.appspot.com",
    'messagingSenderId': "323856315390",
    'appId': "1:323856315390:web:862d6729304307bc0886af",
    'measurementId': "G-9D2TV7CFZK"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

def extract_serializable_state(session_state):
    serializable_state = {}
    for key, value in session_state.items():
        try:
            json.dumps(value)  # Test if the value is JSON serializable
            serializable_state[key] = value
        except TypeError:
            pass  # Ignore non-serializable values
    return serializable_state

def save_draft(user_id, data):
    serializable_data = extract_serializable_state(data)
    db.child("drafts").child(user_id).set(serializable_data)

def retrieve_draft(user_id):
    draft = db.child("drafts").child(user_id).get()
    return draft.val() if draft.val() else {}

def main():
    # Initialize session state variables if not already done
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.email = ""
        st.session_state.username = ""
        st.session_state.user = None
        st.session_state.signup_mode = False  # Initialize signup mode

    # Check the logged-in state to determine the current page
    if st.session_state.logged_in:
        home()
    else:
        auth_page()

def auth_page():
    if st.session_state.signup_mode:
        signup()
    else:
        login()

def set_login_background():
    login_background_css = """
        <style>
            [data-testid="stAppViewContainer"] {
                background-image: url('https://i.postimg.cc/VLLpdC6q/login.png');
                background-size: cover;
            }
            [data-testid="stHeader"]{
                background-color: rgba(0,0,0,0);
            }
        </style>
    """
    st.markdown(login_background_css, unsafe_allow_html=True)

def set_signup_background():
    signup_background_css = """
        <style>
            [data-testid="stAppViewContainer"] {
                background-image: url('https://i.postimg.cc/x8XhbMPp/download-1.png');
                background-size: cover;
            }
            [data-testid="stHeader"]{
                background-color: rgba(0,0,0,0);
            }
        </style>
    """
    st.markdown(signup_background_css, unsafe_allow_html=True)

def set_main_page_background():
    main_page_background_css = """
        <style>
            [data-testid="stAppViewContainer"] {
                background-image: url('https://i.postimg.cc/y8nDNvms/download-4.png');
                background-size: cover;
            }
            [data-testid="stHeader"]{
                background-color: rgba(0,0,0,0);
            }
        </style>
    """
    st.markdown(main_page_background_css, unsafe_allow_html=True)

def sidebar_page_background():
    sidebar_page_background_css = """
        <style>
            [data-testid="stSidebar"] > div:first-child {
                background-image: url("https://i.postimg.cc/W1YdM6qL/download-4.png");
                background-size: cover;
            }
        </style>
    """
    st.markdown(sidebar_page_background_css, unsafe_allow_html=True)

def login():
    set_login_background()

    st.markdown("<h2 style='text-decoration: underline;'>Login</h2>", unsafe_allow_html=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.success(f"Successfully logged in as {email}")
            st.balloons()
            st.session_state.logged_in = True
            st.session_state.email = email
            st.session_state.user = user
            user_info = db.child("users").child(user['localId']).get()
            if user_info.val():
                st.session_state.username = user_info.val().get("username", "")

            # Retrieve and load draft data
            draft_data = retrieve_draft(user['localId'])
            for key, value in draft_data.items():
                st.session_state[key] = value

            st.experimental_rerun()  # Rerun the script after login
        except Exception as e:
            st.error("Invalid Email or Password")
            st.error(str(e))

    st.write("If you don't have an account:")
    if st.button("Sign Up"):
        st.session_state.signup_mode = True
        st.experimental_rerun()  # Rerun the script to switch to signup mode

def signup():
    set_signup_background()

    st.markdown("<h2 style='text-decoration: underline;'>Sign Up</h2>", unsafe_allow_html=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    username = st.text_input("Username")

    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("Passwords do not match.")
        else:
            try:
                user = auth.create_user_with_email_and_password(email, password)
                st.success(f"Successfully signed up as {email}")
                st.balloons()
                st.session_state.logged_in = True
                st.session_state.email = email
                st.session_state.user = user

                # Save the username to the database
                db.child("users").child(user['localId']).set({"username": username})
                st.session_state.username = username

                st.experimental_rerun()  # Rerun the script after signup
            except Exception as e:
                st.error("Failed to sign up. Please try again.")
                st.error(str(e))

    st.write("If you already have an account:")
    if st.button("Back to Login"):
        st.session_state.signup_mode = False
        st.experimental_rerun()  # Rerun the script to switch to login mode

def home():
    set_main_page_background()
    sidebar_page_background()

    st.sidebar.header("Dashboard :rocket:")
    st.sidebar.success(f"Welcome, {st.session_state.username}")
    st.header("Welcome To")
    
    if st.sidebar.button("Logout"):
        # Reset session state variables
        st.session_state.logged_in = False
        st.session_state.email = ""
        st.session_state.username = ""
        st.session_state.user = None
        st.experimental_rerun()

    st.title('Data Visualization :bar_chart:')

    st.sidebar.header('Upload Excel file')
    uploaded_file = st.sidebar.file_uploader('', type=['xlsx', 'xls'])

    if uploaded_file is not None:
        header_row = st.sidebar.number_input('Header Row (1-based index)', min_value=1, value=st.session_state.get('header_row', 4))
        st.session_state.header_row = header_row
        df = load_data(uploaded_file, header_row)

        st.subheader('Data Frame')
        st.dataframe(df)

        # Firebase Storage
        file_path = f"uploads/{str(uuid.uuid4())}_{uploaded_file.name}"
        storage.child(file_path).put(uploaded_file)
        st.success("File uploaded successfully!")
        # Update database with file path
        db.child("files").child(st.session_state.user['localId']).push({"file_name": uploaded_file.name, "file_path": file_path})

        st.sidebar.header('Dashboard')
        selected_columns = st.sidebar.multiselect('Select Columns', df.columns, default=st.session_state.get('selected_columns', []))
        st.session_state.selected_columns = selected_columns

        if selected_columns:
            visualization_options = [
                'Bar chart', 'Pie chart', 'Scatter plot', 'Area chart', 'Bubble chart', 'Heatmap',
                'Line chart', 'Funnel chart', 'Boxplot', 'Donut chart', 'Gantt chart', 'Histogram',
                'Waterfall chart', 'Bullet graph', 'Line graph', 'Radar chart', 'Stacked bar graph',
                'Table', 'Treemaps', 'Column chart', 'Venn diagram', 'Word cloud', 'Choropleth map', 'Gauge'
            ]
            default_visualizations = st.session_state.get('selected_visualizations', [])
            selected_visualizations = st.sidebar.multiselect(
                'Select Visualization Format', 
                visualization_options, 
                default=[v for v in default_visualizations if v in visualization_options]
            )
            st.session_state.selected_visualizations = selected_visualizations

            x_column = st.sidebar.selectbox('X Axis', selected_columns, index=st.session_state.get('x_column_index', 0))
            st.session_state.x_column_index = selected_columns.index(x_column)
            y_column = st.sidebar.selectbox('Y Axis', selected_columns, index=st.session_state.get('y_column_index', 1))
            st.session_state.y_column_index = selected_columns.index(y_column)
            color_column = st.sidebar.selectbox('Color', [None] + selected_columns, index=0)
            st.session_state.color_column = color_column

            visualize(df, selected_visualizations, x_column, y_column, color_column)
            
            # Save draft
            if st.sidebar.button('Save Draft'):
                save_draft(st.session_state.user['localId'], st.session_state)
                st.success("Draft saved successfully!")

    # Add "Contact us" button at the bottom of the sidebar
    st.sidebar.write("---")
    contact_us_button()

def contact_us_button():
    st.sidebar.markdown("""
        <form action="https://contactio.streamlit.app" target="_blank">
            <button type="submit" style="
                background-color:transparent;
                color: white;
                border: none;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 12px;
            ">
                Contact us
            </button>
        </form>
    """, unsafe_allow_html=True)

def load_data(file, header_row):
    df = pd.read_excel(file, header=header_row-1)
    return df

def visualize(df, selected_visualizations, x_column, y_column, color_column):
    for viz in selected_visualizations:
        try:
            if viz == 'Bar chart':
                st.subheader('Bar Chart')
                fig = px.bar(df, x=x_column, y=y_column, color=color_column)
                st.plotly_chart(fig)

            elif viz == 'Pie chart':
                st.subheader('Pie Chart')
                fig = px.pie(df, names=x_column, values=y_column)
                st.plotly_chart(fig)

            elif viz == 'Scatter plot':
                st.subheader('Scatter Plot')
                fig = px.scatter(df, x=x_column, y=y_column, color=color_column)
                st.plotly_chart(fig)

            elif viz == 'Area chart':
                st.subheader('Area Chart')
                fig = px.area(df, x=x_column, y=y_column, color=color_column)
                st.plotly_chart(fig)

            elif viz == 'Bubble chart':
                st.subheader('Bubble Chart')
                if pd.api.types.is_numeric_dtype(df[y_column]):
                    fig = px.scatter(df, x=x_column, y=y_column, size=y_column, color=color_column)
                    st.plotly_chart(fig)
                else:
                    st.warning(f"Cannot create Bubble Chart because '{y_column}' is not numeric.")

            elif viz == 'Heatmap':
                st.subheader('Heatmap')
                fig = px.density_heatmap(df, x=x_column, y=y_column, z=color_column)
                st.plotly_chart(fig)

            elif viz == 'Line chart':
                st.subheader('Line Chart')
                fig = px.line(df, x=x_column, y=y_column, color=color_column)
                st.plotly_chart(fig)

            elif viz == 'Funnel chart':
                st.subheader('Funnel Chart')
                fig = px.funnel(df, x=x_column, y=y_column, color=color_column)
                st.plotly_chart(fig)

            elif viz == 'Boxplot':
                st.subheader('Boxplot')
                fig = px.box(df, x=x_column, y=y_column, color=color_column)
                st.plotly_chart(fig)

            elif viz == 'Donut chart':
                st.subheader('Donut Chart')
                fig = px.pie(df, names=x_column, values=y_column, hole=0.3)
                st.plotly_chart(fig)

            elif viz == 'Gantt chart':
                st.subheader('Gantt Chart')
                st.write("Gantt Chart visualization is not implemented yet.")

            elif viz == 'Histogram':
                st.subheader('Histogram')
                fig = px.histogram(df, x=x_column, y=y_column, color=color_column)
                st.plotly_chart(fig)

            elif viz == 'Waterfall chart':
                st.subheader('Waterfall Chart')
                fig = go.Figure(go.Waterfall(x=df[x_column], y=df[y_column]))
                st.plotly_chart(fig)

            elif viz == 'Bullet graph':
                st.subheader('Bullet Graph')
                st.write("Bullet Graph visualization is not implemented yet.")

            elif viz == 'Line graph':
                st.subheader('Line Graph')
                fig = px.line(df, x=x_column, y=y_column, color=color_column)
                st.plotly_chart(fig)

            elif viz == 'Radar chart':
                st.subheader('Radar Chart')
                st.write("Radar Chart visualization is not implemented yet.")

            elif viz == 'Stacked bar graph':
                st.subheader('Stacked Bar Graph')
                fig = px.bar(df, x=x_column, y=y_column, color=color_column, barmode='stack')
                st.plotly_chart(fig)

            elif viz == 'Table':
                st.subheader('Table')
                st.table(df[[x_column, y_column]])

            elif viz == 'Treemaps':
                st.subheader('Treemaps')
                st.write("Treemaps visualization is not implemented yet.")

            elif viz == 'Column chart':
                st.subheader('Column Chart')
                fig = px.bar(df, x=x_column, y=y_column, color=color_column)
                st.plotly_chart(fig)

            elif viz == 'Venn diagram':
                st.subheader('Venn Diagram')
                st.write("Venn Diagram visualization is not implemented yet.")

            elif viz == 'Word cloud':
                st.subheader('Word Cloud')
                st.write("Word Cloud visualization is not implemented yet.")

            elif viz == 'Choropleth map':
                st.subheader('Choropleth Map')
                st.write("Choropleth Map visualization is not implemented yet.")

            elif viz == 'Gauge':
                st.subheader('Gauge')
                st.write("Gauge visualization is not implemented yet.")
        except Exception as e:
            st.error(f"Error generating {viz}: {str(e)}")

if __name__ == '__main__':
    main()
