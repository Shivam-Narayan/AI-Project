import os, cv2, datetime
import streamlit as st

def extract_frames(video_path, output_path, frame_interval):
    
    # Ensure the output directory exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # Open the video file
    video = cv2.VideoCapture(video_path)
    
    if not video.isOpened():
        print(f"Error opening video file: {video_path}")
        return
    
    frame_count = 0
    extracted_frame_count = 0
    fps = video.get(cv2.CAP_PROP_FPS)
    lst = []
    # Create placeholders for displaying images
    placeholder_col1 = st.empty()
    placeholder_col2 = st.empty()
    placeholder_col3 = st.empty()
    
    while True:
        success, frame = video.read()

        if not success:
            break
        
        timestamp = frame_count / fps
        timestamp_str = str(datetime.timedelta(seconds=int(timestamp)))
 
        # Save the frame at the specified interval
        if frame_count % frame_interval == 0:
            frame_filename = os.path.join(output_path, f"frame_{timestamp_str.replace(':', '_')}.jpg")
            cv2.imwrite(frame_filename, frame)
            # print(f"Extracted frame {extracted_frame_count}: {frame_filename}")
            extracted_frame_count += 1

            lst.append(frame_filename)

            if len(lst) >= 3:
                
                with placeholder_col1:
                        st.image(lst[-3], width=150)
                # with placeholder_col2:
                #         st.image(lst[-2], width=150)
                # with placeholder_col3:
                #         st.image(lst[-1], width=150)
                
                # Clear the list after displaying
                lst = []
            
        frame_count += 1
    video.release()
    # Handle any remaining images that weren't displayed
    # if lst:
    #     # Create new columns for remaining images
    #     cols = st.columns(len(lst))
    #     for i, img_path in enumerate(lst):
    #         with cols[i]:
    #             st.image(img_path, use_column_width=True)
    # Release the video capture object
    placeholder_col1.empty()
    placeholder_col2.empty()
    placeholder_col3.empty()
    print("Frame extraction complete.")