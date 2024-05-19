import os
import pandas as pd
import streamlit as st
from utilities.icon import page_icon

st.set_page_config(
    page_title="Chat Archive",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_messages(filename):
    return pd.read_csv(filename, parse_dates=["Time"])


def main():
    page_icon("💬")
    st.subheader("Chat Archive", divider="red", anchor=False)

    archive_folder = "archive"
    all_files = os.listdir(archive_folder)
    all_files.sort(reverse=True)  # Sorting files by timestamp, latest first

    if not all_files:
        st.info("No chat archives found.", icon="📂")
        return

    selected_file = st.selectbox("Select a chat archive:", all_files)
    if selected_file:
        st.write(f"Selected Chat Archive: {selected_file}")
        messages = load_messages(os.path.join(archive_folder, selected_file))
        st.write(messages)
    if selected_file:
        st.write(f"Selected Chat Archive: {selected_file}")
        messages = load_messages(os.path.join(archive_folder, selected_file))

        for index, row in messages.iterrows():
            avatar = "🤖" if row.get("Role") == "assistant" else "😎"
            with st.container():
                st.markdown(f"**{row.get('Role', '')}**", unsafe_allow_html=True)
                st.markdown(row.get("content", ""))
                

if __name__ == "__main__":
    main()


