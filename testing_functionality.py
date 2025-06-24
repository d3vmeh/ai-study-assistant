import streamlit as st
import os
from assistant_response import get_assistant_response
import tempfile

st.set_page_config(page_title="AI Study Assistant", page_icon="🤖", layout="wide")

st.title("AI Study Assistant")
st.markdown("Upload an image of your homework, notes, or textbook page and ask questions!")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

with st.sidebar:
    st.header("Upload Study Material")
    uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        st.session_state.uploaded_image = uploaded_file
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        st.success("Image uploaded successfully!")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.markdown(f"**Answer:** {message['content']['answer']}")
            st.markdown(f"**Explanation:** {message['content']['explanation']}")
            if message['content'].get('key_concepts'):
                st.markdown(f"**Key Concepts:** {', '.join(message['content']['key_concepts'])}")
            if message['content'].get('next_steps'):
                st.markdown(f"**Next Steps:** {message['content']['next_steps']}")
        else:
            st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about the uploaded image..."):
    if st.session_state.uploaded_image is None:
        st.error("Please upload an image first")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Analyzing image and generating response..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    tmp_file.write(st.session_state.uploaded_image.getvalue())
                    tmp_file_path = tmp_file.name
                
                try:
                    response = get_assistant_response(prompt, tmp_file_path)
                    
                    if "error" in response:
                        st.error(f"Error: {response['error']}")
                    
                    st.markdown(f"**Answer:** {response['answer']}")
                    st.markdown(f"**Explanation:** {response['explanation']}")
                    if response.get('key_concepts'):
                        st.markdown(f"**Key Concepts:** {', '.join(response['key_concepts'])}")
                    if response.get('next_steps'):
                        st.markdown(f"**Next Steps:** {response['next_steps']}")
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response
                    })
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                finally:
                    os.unlink(tmp_file_path)