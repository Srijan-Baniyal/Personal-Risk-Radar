import streamlit as st

# Set page config
st.set_page_config(page_title="Personal Risk Radar", page_icon="🎯", layout="wide")

# Title
st.title(body="🎯 Personal Risk Radar")

# Sidebar
st.sidebar.header(body="Settings")
st.sidebar.write("Configure your preferences here")

# Main content
st.header(body="Welcome to Personal Risk Radar!")
st.write("This is your starting point. Start building your app here.")

# Example: Add some interactive elements
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Risk Level", value="Low", delta="-5%")

with col2:
    st.metric(label="Total Alerts", value="12", delta="2")

with col3:
    st.metric(label="Status", value="Active", delta="")

# Example: Text input
user_input: str = st.text_input(
    label="Enter your data:", placeholder="Type something..."
)

if user_input:
    st.success(body=f"You entered: {user_input}")

# Example: Button
if st.button(label="Click me!"):
    st.balloons()
    st.write("Button clicked! 🎉")
