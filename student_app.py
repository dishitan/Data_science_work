import streamlit as st
import mysql.connector
import requests
import json
import pandas as pd

# Page configuration
st.set_page_config(page_title="Student Database Query", page_icon="🎓", layout="wide")

# Initialize session state for API key and database credentials
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'db_connected' not in st.session_state:
    st.session_state.db_connected = False

# Sidebar for configuration
st.sidebar.header("⚙️ Configuration")

# API Key input
api_key = st.sidebar.text_input("SQL.AI API Key", type="password", value=st.session_state.api_key)
if api_key:
    st.session_state.api_key = api_key

# Database credentials
st.sidebar.subheader("MySQL Database")
db_host = st.sidebar.text_input("Host", value="localhost")
db_user = st.sidebar.text_input("Username", value="root")
db_password = st.sidebar.text_input("Password", type="password")
db_name = st.sidebar.text_input("Database Name", value="student_data")

# Function to connect to MySQL database
def connect_to_database(host, user, password, database):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return conn
    except mysql.connector.Error as err:
        st.error(f"Database connection error: {err}")
        return None

# Function to get database schema
def get_database_schema(conn):
    """Extract database schema in SQL.AI format"""
    cursor = conn.cursor()
    schema = []
    
    try:
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        for table in tables:
            # Get columns for each table
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            
            for column in columns:
                schema.append({
                    "table": table,
                    "column": column[0],
                    "type": column[1]
                })
        
        cursor.close()
        return schema
    except mysql.connector.Error as err:
        st.error(f"Error fetching schema: {err}")
        return []

# Function to call SQL.AI API
def text_to_sql(prompt, schema, api_key):
    """Convert natural language to SQL using SQL.AI API"""
    url = "https://api.sqlai.ai/api/public/v2"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "prompt": prompt,
        "engine": "mysql",
        "engineVersion": "8.0",
        "mode": "textToSQL",
        "dataSource": schema
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if 'query' in result:
            return result['query'], None
        elif 'error' in result:
            return None, result['error']
        else:
            return None, "Unexpected response format"
    except requests.exceptions.RequestException as e:
        return None, str(e)

# Function to execute SQL query
def execute_query(conn, query):
    """Execute SQL query and return results as DataFrame"""
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Fetch results
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        cursor.close()
        
        # Convert to DataFrame
        df = pd.DataFrame(results, columns=columns)
        return df, None
    except mysql.connector.Error as err:
        return None, str(err)

# Main app
st.title(" Database Query System")
#st.markdown("Ask questions about your student database in plain English!")

# Connect to database button
if st.sidebar.button("Connect to Database"):
    if not st.session_state.api_key:
        st.sidebar.error("Please enter your SQL.AI API key")
    elif not db_password:
        st.sidebar.error("Please enter database password")
    else:
        conn = connect_to_database(db_host, db_user, db_password, db_name)
        if conn:
            st.session_state.db_connected = True
            st.session_state.connection = conn
            st.session_state.schema = get_database_schema(conn)
            st.sidebar.success("✅ Connected to database!")
        else:
            st.session_state.db_connected = False

# Display connection status
if st.session_state.db_connected:
    st.success("✅ Database connected")
    
    # Display available tables
    with st.expander("📊 View Database Schema"):
        if 'schema' in st.session_state and st.session_state.schema:
            schema_df = pd.DataFrame(st.session_state.schema)
            st.dataframe(schema_df, use_container_width=True)
    
    # Query input
    st.markdown("---")
    st.subheader("💬 Ask a Question")
    
    # Example queries
    
    # Text input for custom query
    user_query = st.text_area(
        "Enter your question:",
        value=st.session_state.get('user_query', ''),
        height=100,
        placeholder="E.g., How many students have more than 18 hours of credit?"
    )
    
    if st.button("🔍 Search", type="primary"):
        if not user_query:
            st.warning("Please enter a question")
        else:
            with st.spinner("Converting to SQL..."):
                # Convert text to SQL
                sql_query, error = text_to_sql(
                    user_query,
                    st.session_state.schema,
                    st.session_state.api_key
                )
                
                if error:
                    st.error(f"Error generating SQL: {error}")
                elif sql_query:
                    # Display generated SQL
                    st.markdown("### Generated SQL Query:")
                    st.code(sql_query, language="sql")
                    
                    # Execute query
                    with st.spinner("Executing query..."):
                        results_df, exec_error = execute_query(
                            st.session_state.connection,
                            sql_query
                        )
                        
                        if exec_error:
                            st.error(f"Error executing query: {exec_error}")
                        elif results_df is not None:
                            st.markdown("### Results:")
                            if len(results_df) == 0:
                                st.info("No results found")
                            else:
                                st.dataframe(results_df, use_container_width=True)
                                
                                # Show summary statistics if applicable
                                if len(results_df.columns) == 1 and results_df.shape[0] == 1:
                                    st.metric(
                                        label="Result",
                                        value=results_df.iloc[0, 0]
                                    )
                                
                                # Download button
                                csv = results_df.to_csv(index=False)
                                st.download_button(
                                    label="📥 Download Results as CSV",
                                    data=csv,
                                    file_name="query_results.csv",
                                    mime="text/csv"
                                )
else:
    st.info("👈 Please configure your API key and database credentials in the sidebar, then click 'Connect to Database'")
    
    st.markdown("""
    ### Getting Started:
    1. Enter your **SQL.AI API Key** in the sidebar
    2. Configure your **MySQL database credentials**
    3. Click **Connect to Database**
    4. Start asking questions about your data!
        """)

# Footer
st.markdown("---")
