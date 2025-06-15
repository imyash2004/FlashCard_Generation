import streamlit as st
import pandas as pd
import json
from typing import List, Dict, Optional

def api_key_input() -> Optional[str]:
    """
    Create API key input field in sidebar.
    
    Returns:
        API key string or None if not provided
    """
    with st.sidebar:
        st.header("🔑 Configuration")
        api_key = st.text_input(
            "OpenAI API Key", 
            type="password", 
            help="Enter your OpenAI API key to generate flashcards"
        )
        
        if not api_key:
            st.warning("⚠️ Please enter your OpenAI API key")
            st.info("Get your API key from: https://platform.openai.com/api-keys")
            return None
        
        return api_key

def file_upload():
    """
    Create file upload widget.
    
    Returns:
        Uploaded file object or None
    """
    st.subheader("📁 File Upload")
    uploaded_file = st.file_uploader(
        "Upload a .txt or .pdf file",
        type=["txt", "pdf"],
        help="Upload educational content to generate flashcards from"
    )
    
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Show file info
        file_details = {
            "Filename": uploaded_file.name,
            "File Type": uploaded_file.type,
            "File Size": f"{uploaded_file.size} bytes"
        }
        
        with st.expander("File Details"):
            for key, value in file_details.items():
                st.write(f"**{key}:** {value}")
    
    return uploaded_file

def text_input() -> str:
    """
    Create text input area.
    
    Returns:
        Input text string
    """
    st.subheader("📝 Direct Text Input")
    text = st.text_area(
        "Or paste your educational content here:",
        height=200,
        placeholder="Enter textbook excerpts, lecture notes, or any educational material..."
    )
    
    if text:
        word_count = len(text.split())
        char_count = len(text)
        st.info(f"📊 Content: {word_count} words, {char_count} characters")
    
    return text

def subject_selection() -> Optional[str]:
    """
    Create subject selection dropdown.
    
    Returns:
        Selected subject or None
    """
    with st.sidebar:
        st.header("📚 Subject Selection")
        subjects = [
            "None", "Biology", "Chemistry", "Physics", "Mathematics", 
            "History", "Computer Science", "Literature", "Psychology", 
            "Economics", "Geography", "Philosophy"
        ]
        
        subject = st.selectbox(
            "Select subject (optional):",
            options=subjects,
            help="Choose a subject to optimize flashcard generation"
        )
        
        if subject == "None":
            return None
        
        st.success(f"🎯 Subject: {subject}")
        return subject

def generation_settings() -> Dict[str, any]:
    """
    Create settings for flashcard generation.
    
    Returns:
        Dictionary of settings
    """
    with st.sidebar:
        st.header("⚙️ Generation Settings")
        
        difficulty_filter = st.multiselect(
            "Include difficulty levels:",
            ["Easy", "Medium", "Hard"],
            default=["Easy", "Medium", "Hard"],
            help="Select which difficulty levels to include"
        )
        
        auto_difficulty = st.checkbox(
            "Auto-assign difficulty levels",
            value=True,
            help="Automatically assign difficulty levels to flashcards"
        )
        
        return {
            "difficulty_filter": difficulty_filter,
            "auto_difficulty": auto_difficulty
        }

def display_flashcards(flashcards: List[Dict[str, str]], settings: Dict[str, any]):
    """
    Display generated flashcards with various viewing options.
    
    Args:
        flashcards: List of flashcard dictionaries
        settings: Display settings
    """
    if not flashcards:
        st.info("No flashcards to display.")
        return
    
    # Filter by difficulty if enabled
    if settings.get("difficulty_filter"):
        flashcards = [
            card for card in flashcards 
            if card.get("difficulty", "Medium") in settings["difficulty_filter"]
        ]
    
    if not flashcards:
        st.warning("No flashcards match the selected difficulty levels.")
        return
    
    st.header(f"📚 Generated Flashcards ({len(flashcards)} cards)")
    
    # Display mode selection
    display_mode = st.radio(
        "Display mode:",
        ["🎴 Card View", "📊 Table View"],
        horizontal=True
    )
    
    if display_mode == "🎴 Card View":
        _display_card_view(flashcards)
    else:
        _display_table_view(flashcards)

def _display_card_view(flashcards: List[Dict[str, str]]):
    """Display flashcards in card format."""
    for i, card in enumerate(flashcards, 1):
        with st.container():
            # Card header
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader(f"Card {i}")
            with col2:
                if "difficulty" in card:
                    difficulty = card["difficulty"]
                    colors = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}
                    st.write(f"{colors.get(difficulty, '⚪')} {difficulty}")
            
            # Question
            st.write("**❓ Question:**")
            st.info(card["question"])
            
            # Answer (collapsible)
            with st.expander("💡 Show Answer"):
                st.success(card["answer"])
            
            st.divider()

def _display_table_view(flashcards: List[Dict[str, str]]):
    """Display flashcards in table format."""
    # Create DataFrame
    df = pd.DataFrame(flashcards)
    
    # Configure display
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "question": st.column_config.TextColumn("Question", width="medium"),
            "answer": st.column_config.TextColumn("Answer", width="large"),
            "difficulty": st.column_config.SelectboxColumn(
                "Difficulty",
                options=["Easy", "Medium", "Hard"],
                width="small"
            )
        }
    )

def download_buttons(flashcards: List[Dict[str, str]]):
    """
    Create download buttons for various formats.
    
    Args:
        flashcards: List of flashcard dictionaries
    """
    if not flashcards:
        return
    
    st.header("📤 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV Download
        csv_data = _create_csv(flashcards)
        st.download_button(
            label="📊 Download CSV",
            data=csv_data,
            file_name="flashcards.csv",
            mime="text/csv",
            help="Download as CSV for spreadsheet applications"
        )
    
    with col2:
        # JSON Download
        json_data = _create_json(flashcards)
        st.download_button(
            label="📋 Download JSON",
            data=json_data,
            file_name="flashcards.json",
            mime="application/json",
            help="Download as JSON for programmatic use"
        )
    
    with col3:
        # Anki Format Download
        anki_data = _create_anki_format(flashcards)
        st.download_button(
            label="🎴 Download Anki Format",
            data=anki_data,
            file_name="flashcards_anki.txt",
            mime="text/plain",
            help="Download in Anki-compatible format"
        )

def _create_csv(flashcards: List[Dict[str, str]]) -> str:
    """Create CSV format data."""
    df = pd.DataFrame(flashcards)
    return df.to_csv(index=False)

def _create_json(flashcards: List[Dict[str, str]]) -> str:
    """Create JSON format data."""
    return json.dumps(flashcards, indent=2, ensure_ascii=False)

def _create_anki_format(flashcards: List[Dict[str, str]]) -> str:
    """Create Anki-compatible format."""
    anki_lines = []
    for card in flashcards:
        question = card["question"].replace("\n", "<br>")
        answer = card["answer"].replace("\n", "<br>")
        difficulty = card.get("difficulty", "Medium")
        anki_lines.append(f"{question}\t{answer}\t{difficulty}")
    return "\n".join(anki_lines)

def display_statistics(flashcards: List[Dict[str, str]]):
    """
    Display statistics about generated flashcards.
    
    Args:
        flashcards: List of flashcard dictionaries
    """
    if not flashcards:
        return
    
    st.header("📊 Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cards", len(flashcards))
    
    with col2:
        easy_count = len([c for c in flashcards if c.get("difficulty") == "Easy"])
        st.metric("Easy Cards", easy_count)
    
    with col3:
        medium_count = len([c for c in flashcards if c.get("difficulty") == "Medium"])
        st.metric("Medium Cards", medium_count)
    
    with col4:
        hard_count = len([c for c in flashcards if c.get("difficulty") == "Hard"])
        st.metric("Hard Cards", hard_count)
    
    # Additional statistics
    if flashcards:
        avg_question_length = sum(len(card["question"].split()) for card in flashcards) / len(flashcards)
        avg_answer_length = sum(len(card["answer"].split()) for card in flashcards) / len(flashcards)
        
        col5, col6 = st.columns(2)
        with col5:
            st.metric("Avg Question Length", f"{avg_question_length:.1f} words")
        with col6:
            st.metric("Avg Answer Length", f"{avg_answer_length:.1f} words")

def show_error_message(error_msg: str):
    """
    Display error message with styling.
    
    Args:
        error_msg: Error message to display
    """
    st.error(f"❌ {error_msg}")

def show_success_message(success_msg: str):
    """
    Display success message with styling.
    
    Args:
        success_msg: Success message to display
    """
    st.success(f"✅ {success_msg}")

def show_warning_message(warning_msg: str):
    """
    Display warning message with styling.
    
    Args:
        warning_msg: Warning message to display
    """
    st.warning(f"⚠️ {warning_msg}")

def show_info_message(info_msg: str):
    """
    Display info message with styling.
    
    Args:
        info_msg: Info message to display
    """
    st.info(f"ℹ️ {info_msg}")