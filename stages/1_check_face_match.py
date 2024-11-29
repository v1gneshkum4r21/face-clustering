import face_recognition
import streamlit as st

def check_if_faces_match(face_1_encoding, face_2_encoding):
    results = face_recognition.compare_faces([face_1_encoding], face_2_encoding)
    distance = face_recognition.face_distance([face_1_encoding], face_2_encoding)[0]
    
    match_status = "Match" if results[0] else "No match"
    confidence = (1 - distance) * 100
    
    return {
        "is_match": results[0],
        "confidence": confidence,
        "distance": distance
    }

def demo_face_matching():
    st.title("Face Matching Demo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        img1 = st.file_uploader("Upload first face", type=['jpg', 'jpeg', 'png'])
    with col2:
        img2 = st.file_uploader("Upload second face", type=['jpg', 'jpeg', 'png'])
        
    if img1 and img2:
        try:
            # Process first image
            face1 = face_recognition.load_image_file(img1)
            face1_encoding = face_recognition.face_encodings(face1)[0]
            
            # Process second image
            face2 = face_recognition.load_image_file(img2)
            face2_encoding = face_recognition.face_encodings(face2)[0]
            
            # Compare faces
            result = check_if_faces_match(face1_encoding, face2_encoding)
            
            # Display results
            if result["is_match"]:
                st.success(f"Match found! Confidence: {result['confidence']:.2f}%")
            else:
                st.warning(f"No match. Confidence: {result['confidence']:.2f}%")
                
        except Exception as e:
            st.error(f"Error processing images: {str(e)}")

if __name__ == "__main__":
    demo_face_matching()