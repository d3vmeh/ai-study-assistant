import streamlit as st
import os
from PIL import Image
from assistant_response import get_ai_response

def initialize_camera_session():
    """Initialize session state for camera functionality"""
    if "camera_active" not in st.session_state:
        st.session_state.camera_active = False
    if "captured_image" not in st.session_state:
        st.session_state.captured_image = None
    if "camera_messages" not in st.session_state:
        st.session_state.camera_messages = []
    if "current_image_path" not in st.session_state:
        st.session_state.current_image_path = None

def capture_image_from_camera():
    """Capture image from camera using Streamlit's camera_input"""
    img_bytes = st.camera_input("Take a picture of your study material")
    
    if img_bytes is not None:
        # Convert camera input to PIL Image
        image = Image.open(img_bytes)
        
        # Store in session state
        st.session_state.captured_image = image
        st.session_state.camera_active = True
        
        # Save to a stable location for later processing
        temp_path = "camera_capture_current.png"
        image.save(temp_path)
        st.session_state.current_image_path = temp_path
        
        return True
    
    return False

def process_camera_image(image_path, question):
    """Process captured camera image with AI"""
    try:
        with st.spinner("Analyzing your captured image..."):
            response = get_ai_response(question, image_path)
            
            if response:
                # Add to camera-specific message history
                st.session_state.camera_messages.append({
                    "role": "user",
                    "content": question,
                    "has_image": True
                })
                st.session_state.camera_messages.append({
                    "role": "assistant",
                    "content": response
                })
                
                return response
            else:
                return None
                
    except Exception as e:
        st.error(f"Error processing camera image: {str(e)}")
        return None

def display_camera_interface():
    """Display the camera interface in Streamlit"""
    st.title("📸 AI Study Assistant - Live Camera")
    initialize_camera_session()
    
    # Camera capture
    st.header("Capture Study Material")
    capture_image_from_camera()
    
    # Display captured image
    if st.session_state.captured_image:
        st.subheader("Captured Image:")
        st.image(st.session_state.captured_image, use_column_width=True)
        
        question = st.text_input("Ask a question about the captured image:")
        
        # Process button
        if st.button("Analyze Image", type="primary"):
            if question and hasattr(st.session_state, 'current_image_path'):
                response = process_camera_image(st.session_state.current_image_path, question)
                
                if response:
                    st.success("Analysis complete!")
                    
                    if response.get("answer"):
                        st.markdown("### Answer")
                        st.write(response["answer"].replace("<newline>", "\n\n"))
                    
                    if response.get("explanation"):
                        st.markdown("### Explanation")
                        st.write(response["explanation"].replace("<newline>", "\n\n"))
                    
                    if response.get("key_concepts"):
                        st.markdown("### Key Concepts")
                        st.write(response["key_concepts"].replace("<newline>", "\n\n"))
                    
                    if response.get("next_steps"):
                        st.markdown("### Next Steps")
                        st.write(response["next_steps"].replace("<newline>", "\n\n"))
            else:
                st.warning("Please enter a question before analyzing.")
    
    # Chat history
    if st.session_state.camera_messages:
        st.divider()
        st.subheader("Chat History")
        
        for message in st.session_state.camera_messages:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["content"])
                    if message.get("has_image"):
                        st.caption("📸 Image captured from camera")
                else:
                    content = message["content"]
                    if isinstance(content, dict):
                        if content.get("answer"):
                            st.markdown("**Answer:**")
                            st.write(content["answer"].replace("<newline>", "\n\n"))
                        if content.get("explanation"):
                            st.markdown("**Explanation:**")
                            st.write(content["explanation"].replace("<newline>", "\n\n"))
                        if content.get("key_concepts"):
                            st.markdown("**Key Concepts:**")
                            st.write(content["key_concepts"].replace("<newline>", "\n\n"))
                        if content.get("next_steps"):
                            st.markdown("**Next Steps:**")
                            st.write(content["next_steps"].replace("<newline>", "\n\n"))
                    else:
                        st.write(content)
    
    if st.button("Clear Camera Session"):
        # Clean up temporary file if it exists
        if hasattr(st.session_state, 'current_image_path') and st.session_state.current_image_path:
            if os.path.exists(st.session_state.current_image_path):
                os.remove(st.session_state.current_image_path)
        
        st.session_state.camera_active = False
        st.session_state.captured_image = None
        st.session_state.camera_messages = []
        st.session_state.current_image_path = None
        st.rerun()

def main():
    """Main function to run the camera interface"""
    if not os.getenv("OPENAI_API_KEY"):
        st.error("Please set your OPENAI_API_KEY environment variable!")
        st.stop()
    
    display_camera_interface()

if __name__ == "__main__":
    main()