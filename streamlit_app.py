import streamlit as st
from openai import OpenAI
import pandas as pd
import plotly.express as px
import json

# Set a password (change 'your_password' to a strong password)
PASSWORD = "password"

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Password input for access
if not st.session_state.authenticated:
    st.title("🔒 Enter Password to Access")
    password = st.text_input("Password", type="password")
    
    if st.button("Submit"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("Incorrect password. Try again.")

else:
    # Access OpenAI API key directly from secrets
    openai_api_key = st.secrets["openai_api_key"]
    client = OpenAI(api_key=openai_api_key)

     # Create three tabs: "Upload CSV", "About Us", "Methodology"
    tab1, tab2, tab3 = st.tabs(["Main", "About Us", "Methodology"])
    
    with tab1:
        # Show title and description.
        st.title("💬 Chatbot with CSV File Upload and Visualization")
        st.write("This app lets you upload CSV or Excel files, visualize data, and interact with an AI chatbot using OpenAI's API.")

        # Upload CSV or XLSX file
        uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])
        if uploaded_file is not None:
            # Load the file based on format
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.write("File Loaded:")
            st.write(df.head())
            st.session_state["csv_data"] = df  # Store data for later use

        # Chatbot conversation
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask about your data or anything else..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Prepare prompt with data preview if uploaded
            if "csv_data" in st.session_state:
                csv_context = f"Here's the first few rows of the uploaded data:\n{st.session_state['csv_data'].head()}\n"
                prompt_with_data = f"{csv_context}\nUser question: {prompt}"
            else:
                prompt_with_data = prompt

            # Generate response
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages] + [{"role": "user", "content": prompt_with_data}],
                stream=True,
            )

            # Stream response
            with st.chat_message("assistant"):
                response_text = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

        # Visualization
        def plot_user_selection(df):
            if df is not None and not df.empty:
                st.write("### Customize Plot:")
                x_axis = st.selectbox("X-axis", options=df.columns)
                y_axis = st.selectbox("Y-axis", options=df.columns)
                plot_type = st.selectbox("Plot Type", ["Line Plot", "Bar Plot", "Scatter Plot", "Histogram"])
                plot_color = st.color_picker("Color", "#00f900")

                if x_axis and y_axis and plot_type:
                    if plot_type == "Line Plot":
                        fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}", color_discrete_sequence=[plot_color])
                    elif plot_type == "Bar Plot":
                        fig = px.bar(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}", color_discrete_sequence=[plot_color])
                    elif plot_type == "Scatter Plot":
                        fig = px.scatter(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}", color_discrete_sequence=[plot_color])
                    elif plot_type == "Histogram":
                        fig = px.histogram(df, x=x_axis, title=f"Histogram of {x_axis}", color_discrete_sequence=[plot_color])

                    if fig:
                        st.plotly_chart(fig)

        # Call visualization function if data exists
        if "csv_data" in st.session_state:
            df = pd.DataFrame(st.session_state["csv_data"])
            plot_user_selection(df)


    with tab2:
        st.header("About Us")
        
        # Adding structured content in paragraphs
        st.subheader("Project Scope")
        st.write(
            "Use LLM to do the aggregation, frequency analysis, and categorisation. For a holistic package, we also "
            "provide templates on Tableau or Qualtrics to help officers conduct surveys, then present the data, "
            "findings, and insights on a dashboard for their senior leaders. Databricks can be utilized to port Excel data "
            "into the product to simplify importing survey data into the platform."
        )
        
        st.subheader("Objectives")
        st.write(
            "To empower officers with a quick and easy overview of potential visualizations and leverage LLM "
            "capabilities to generate code and insights from the uploaded data sources with just a few clicks."
        )
        
        st.subheader("Data Sources")
        st.write(
            "In this proof of concept (POC), any open data sources can be used to quickly and easily show potential "
            "visualizations for use."
        )
        
        st.subheader("Features")
        st.write(
            "This app includes features such as file upload capabilities, visualization using Plotly, extraction "
            "of visualizations, and the use of LLM for further improvements and quick insights."
        )

    with tab3:
        st.header("Methodology")
        st.write("In this app, we use OpenAI's GPT-3.5 model to generate responses. "
                 "The methodology involves processing user inputs and integrating data from uploaded CSV files "
                 "to provide data-informed insights and responses.")