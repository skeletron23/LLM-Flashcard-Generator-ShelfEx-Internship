# app.py
import streamlit as st
import io
from flashcard_model import flashcards_to_csv, flashcards_to_json
from content_parser import parse_input_content
from llm_service import LLMService

# --- UI Configuration ---
st.set_page_config(
    page_title="LLM-Powered Flashcard Generator",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 LLM-Powered Flashcard Generator")
st.write("Generate flashcards from your educational content using AI!")

# Initialize LLMService (only once for efficiency)
@st.cache_resource
def get_llm_service():
    try:
        return LLMService()
    except ValueError as e:
        st.error(f"Configuration Error: {e}. Please ensure your OPENAI_API_KEY is set in a .env file.")
        return None

llm_service = get_llm_service()

if llm_service is None:
    st.stop() # Stop the app if LLM service could not be initialized

# --- Input Section ---
st.header("1. Provide Your Educational Content")

input_method = st.radio(
    "Choose input method:",
    ("Upload File (.txt, .pdf)", "Paste Text Directly"),
    key="input_method"
)

content_text = ""
file_uploaded = False

if input_method == "Upload File (.txt, .pdf)":
    uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf"], key="file_uploader")
    if uploaded_file is not None:
        file_uploaded = True
        try:
            # Use io.BytesIO to pass file-like object to parser
            file_obj = io.BytesIO(uploaded_file.read())
            file_obj.name = uploaded_file.name # Preserve original filename for parser
            content_text = parse_input_content("file_upload", file_obj=file_obj)
        except ValueError as e:
            st.error(f"File processing error: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred while reading the file: {e}")
else: # Paste Text Directly
    direct_text = st.text_area(
        "Paste your educational content here:",
        height=300,
        placeholder="E.g., 'Photosynthesis is the process...' or notes from a lecture."
    )
    if direct_text:
        try:
            content_text = parse_input_content("direct_paste", direct_text=direct_text)
        except ValueError as e:
            st.error(f"Text processing error: {e}")

# Optional: Subject Type
subject_type = st.selectbox(
    "Optional: Select Subject Type (helps AI focus)",
    ["General", "Biology", "History", "Computer Science", "Physics", "Chemistry", "Mathematics", "Other"],
    index=0, # Default to General
    key="subject_type"
)

# --- Generate Flashcards Button ---
if st.button("Generate Flashcards", key="generate_button", type="primary"):
    if not content_text:
        st.warning("Please provide some content before generating flashcards.")
    else:
        with st.spinner("Generating flashcards... This may take a moment."):
            generated_flashcards = llm_service.generate_flashcards(content_text, subject_type=subject_type if subject_type != "General" else None)

            if generated_flashcards:
                st.session_state['flashcards'] = generated_flashcards
                st.session_state['content_provided'] = True
                st.success(f"Generated {len(generated_flashcards)} flashcards!")
            else:
                st.error("Failed to generate flashcards. Please try again with different content or check your API key.")
                st.session_state['flashcards'] = []
                st.session_state['content_provided'] = False

# --- Display Flashcards and Export Options ---
if 'flashcards' in st.session_state and st.session_state['flashcards']:
    st.header("2. Your Generated Flashcards")

    # Basic display of flashcards
    for i, card in enumerate(st.session_state['flashcards']):
        with st.expander(f"Flashcard {i+1}: {card.question}"):
            st.write(f"**Question:** {card.question}")
            st.write(f"**Answer:** {card.answer}")
            if card.topic:
                st.write(f"**Topic:** {card.topic}")
            # Optional: Add edit functionality here later if needed

    st.subheader("Export Options")
    col1, col2 = st.columns(2)

    with col1:
        csv_data = flashcards_to_csv(st.session_state['flashcards'])
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="flashcards.csv",
            mime="text/csv",
            key="download_csv"
        )
    with col2:
        json_data = flashcards_to_json(st.session_state['flashcards'])
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name="flashcards.json",
            mime="application/json",
            key="download_json"
        )

    st.info("You can refresh the page to generate new flashcards from different content.")

elif 'content_provided' in st.session_state and not st.session_state['flashcards'] and st.session_state['content_provided']:
    st.write("No flashcards were generated. Please check your input content and try again.")
