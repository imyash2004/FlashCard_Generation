import streamlit as st
import PyPDF2
import io
from agent import Agent
from ui import (
    api_key_input, file_upload, text_input, subject_selection,
    generation_settings, display_flashcards, download_buttons,
    display_statistics, show_error_message, show_success_message,
    show_warning_message, show_info_message
)

def main():
    """Main application function."""
    # Page configuration
    st.set_page_config(
        page_title="LLM-Powered Flashcard Generator",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Main title
    st.title("🧠 LLM-Powered Flashcard Generator")
    st.markdown("Transform your educational content into effective study flashcards using AI!")
    
    # Get API key
    api_key = api_key_input()
    if not api_key:
        show_warning_message("Please enter your OpenAI API key in the sidebar to continue.")
        return
    
    # Initialize agent
    try:
        agent = Agent(api_key)
    except Exception as e:
        show_error_message(f"Failed to initialize AI agent: {str(e)}")
        return
    
    # Get generation settings
    settings = generation_settings()
    
    # Get subject selection
    subject = subject_selection()
    
    # Input section
    st.header("📝 Input Your Educational Content")
    
    # Choose input method
    input_method = st.radio(
        "Choose input method:",
        ["📁 File Upload", "📝 Direct Text Input"],
        horizontal=True
    )
    
    text_content = ""
    
    if input_method == "📁 File Upload":
        uploaded_file = file_upload()
        if uploaded_file is not None:
            text_content = process_uploaded_file(uploaded_file)
    else:
        text_content = text_input()
    
    # Generate flashcards
    if st.button("🚀 Generate Flashcards", type="primary", use_container_width=True):
        if not text_content or not text_content.strip():
            show_error_message("Please provide educational content to generate flashcards.")
            return
        
        # Validate content length
        if len(text_content.strip()) < 50:
            show_warning_message("Content seems too short. Please provide more detailed educational material.")
            return
        
        # Generate flashcards
        with st.spinner("🔄 Generating flashcards... This may take a moment."):
            try:
                flashcards = agent.generate_flashcards(text_content, subject)
                
                if not flashcards:
                    show_error_message("Failed to generate flashcards. Please try again with different content.")
                    return
                
                # Assign difficulty levels if enabled
                if settings.get("auto_difficulty", True):
                    flashcards = agent.assign_difficulty_levels(flashcards)
                
                # Store in session state
                st.session_state.flashcards = flashcards
                st.session_state.settings = settings
                
                show_success_message(f"Successfully generated {len(flashcards)} flashcards!")
                
            except Exception as e:
                show_error_message(f"Error generating flashcards: {str(e)}")
                return
    
    # Display flashcards if they exist
    if 'flashcards' in st.session_state and st.session_state.flashcards:
        flashcards = st.session_state.flashcards
        stored_settings = st.session_state.get('settings', settings)
        
        # Display flashcards
        display_flashcards(flashcards, stored_settings)
        
        # Show statistics
        display_statistics(flashcards)
        
        # Download options
        download_buttons(flashcards)
        
        # Option to clear flashcards
        if st.button("🗑️ Clear Flashcards", type="secondary"):
            if 'flashcards' in st.session_state:
                del st.session_state.flashcards
            if 'settings' in st.session_state:
                del st.session_state.settings
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("💡 **Tips for better flashcards:**")
    st.markdown("""
    - Provide clear, well-structured educational content
    - Include key concepts, definitions, and explanations
    - Select the appropriate subject for optimized generation
    - Use content with sufficient detail (at least 100+ words)
    """)

def process_uploaded_file(uploaded_file) -> str:
    """
    Process uploaded file and extract text content.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Extracted text content
    """
    try:
        if uploaded_file.type == "text/plain":
            # Handle text files
            text_content = str(uploaded_file.read(), "utf-8")
            
        elif uploaded_file.type == "application/pdf":
            # Handle PDF files
            text_content = extract_text_from_pdf(uploaded_file)
            
        else:
            show_error_message(f"Unsupported file type: {uploaded_file.type}")
            return ""
        
        if text_content.strip():
            show_success_message(f"File processed successfully! Content length: {len(text_content)} characters")
            
            # Show preview
            with st.expander("📖 Preview Content"):
                preview_length = 500
                if len(text_content) > preview_length:
                    st.text(text_content[:preview_length] + "...")
                    st.caption(f"Showing first {preview_length} characters of {len(text_content)} total.")
                else:
                    st.text(text_content)
            
            return text_content
        else:
            show_error_message("No text content found in the uploaded file.")
            return ""
            
    except Exception as e:
        show_error_message(f"Error processing file: {str(e)}")
        return ""

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text from PDF file.
    
    Args:
        pdf_file: Uploaded PDF file object
        
    Returns:
        Extracted text content
    """
    try:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text.strip():
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page_text + "\n"
            except Exception as e:
                show_warning_message(f"Could not extract text from page {page_num + 1}: {str(e)}")
                continue
        
        if not text.strip():
            show_error_message("No text could be extracted from the PDF. The file might contain only images or be corrupted.")
            return ""
        
        return text.strip()
        
    except Exception as e:
        show_error_message(f"Error reading PDF file: {str(e)}")
        return ""

if __name__ == "__main__":
    main()