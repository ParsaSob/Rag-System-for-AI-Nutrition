import streamlit as st
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

# Must be the first Streamlit command
st.set_page_config(
    page_title="Market Mine Bot",
    page_icon="📊",
    layout="wide"
)

from src.ui import UI

def main():
    """Main function to run the Streamlit app."""
    ui = UI()
    ui.run()

if __name__ == "__main__":
    main()
