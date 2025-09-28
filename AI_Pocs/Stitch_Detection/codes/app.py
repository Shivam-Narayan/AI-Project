import streamlit as st
import time
import os
import cv2
import numpy as np
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw,ImageEnhance
import time
import pandas as pd
from datetime import datetime
from io import BytesIO
from PIL import Image
import base64
import shutil
from PIL import Image as PILImage
# from old_modelprediction import predict_on_new_image
from modelprediction import predict_image
import tkinter as tk
from tkinter import messagebox
import winsound
# from pyzbar.pyzbar import decode  # Or any other scanning method





# Main Content Area
st.title("Stitch Guard AI")

# Sidebar with 'Module Selection'
with st.sidebar:
    module_selection = st.radio("Choose Module", ("Training Module", "Detection Module"))

# Training Module Logic
if module_selection == "Training Module":
    option_1 = st.selectbox("Training Module", ("Home", "Upload Train Data"))

    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "upload"

    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []

    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0

    if 'captured_image' not in st.session_state:
        st.session_state.captured_image = None  # Store the captured image

    # Define a folder to save files
    SAVE_PATH = "saved_files"
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    # Function to delete files from the save path
    def delete_saved_files():
        for filename in os.listdir(SAVE_PATH):
            file_path = os.path.join(SAVE_PATH, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                st.error(f"Error deleting file: {file_path}. Reason: {e}")

    # Call the function to delete saved files when the page reloads
    delete_saved_files()

    # Function to capture an image from the webcam
    def capture_image():
        cap = cv2.VideoCapture(0)  # Open default camera
        if not cap.isOpened():
            st.error("Could not open camera.")
            return None

        ret, frame = cap.read()
        cap.release()

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame
        else:
            st.error("Failed to capture image.")
            return None

    # Resize function for images
    def resize_image(image, target_size=(200, 200)):
        return image.resize(target_size, Image.LANCZOS)  # Use LANCZOS for high-quality resizing

    # Page navigation logic
    if option_1 == "Home":
        st.write("\n\nThis application focuses on detecting stitching defects(specifically skipped stitch, broken stitch, andlooped stitch) from images and video feeds of industrial sewing machines. The primary aim is to build a machine learning model capable of identifying these defects in real-time, ensuring quality controlduring fabric stitching processes.\n\n\nThe application ensures improved quality control in industrial stitching processes by leveraging deep learning models.It offers both image and video-based detection, with the flexibility to integrate into existing production lines, helping manufacturers automate defect detection and reduce manual inspection costs.") 


    # Display the sentence

    elif option_1 == "Upload Train Data":
        if st.session_state.page == "upload":
            uploaded_files = ''
            st.markdown("Upload Train Data")
            selected_type = st.selectbox("Select", options=["Images","Videos"])
            if selected_type =="Images":
                uploaded_files = st.file_uploader("Choose image(s)", type=["jfif", "jpg", "jpeg","png"], accept_multiple_files=True)
            elif selected_type == "Videos":   
            

            # Upload files
                uploaded_files = st.file_uploader("Choose Videos...", type="mp4", accept_multiple_files=True)

            if uploaded_files:
                progress_bar = st.progress(0)

                for percent_complete in range(101):
                    time.sleep(0.01)  # Adjusted delay for progress bar
                    progress_bar.progress(percent_complete)

            col1, col2 = st.columns([2, 1])  # Create two columns for layout

            with col1:
                if st.button("Save"):
                    for uploaded_file in uploaded_files:
                        st.session_state.uploaded_files.append(uploaded_file)
                        with open(os.path.join(SAVE_PATH, uploaded_file.name), "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    st.success(f"Files saved to `{SAVE_PATH}`.")

                # Uncomment the following code if you want to capture a live image
                # if st.button("Capture Live Image"):
                #     # Capture a single image from the webcam
                #     captured_image = capture_image()
                #     if captured_image is not None:
                #         st.session_state.captured_image = captured_image  # Store the captured image in session state
                #         # Resize the captured image
                #         captured_img_resized = resize_image(Image.fromarray(captured_image))
                #         st.image(captured_img_resized, caption="Captured Image", use_column_width=True)
                #         # Save the captured image
                #         save_name = "captured_image.jpg"
                #         captured_img_resized.save(os.path.join(SAVE_PATH, save_name))
                #         st.success(f"Image captured and saved as `{save_name}`.")

            with col2:
                if st.button("Annotate"):
                    st.session_state.page = "annotate"

        elif st.session_state.page == "annotate":
            st.title("Annotate Uploaded Files")

            if st.session_state.uploaded_files:
                st.write("Here are the files you uploaded:")

                selected_files = []
                cols = st.columns(3)  # Create three columns for displaying files
                for index, file in enumerate(st.session_state.uploaded_files):
                    col = cols[index % 3]  # Select the column based on index
                    with col:
                        # Check for image formats to open them as PIL images
                        if file.name.endswith(("jpg", "jpeg", "jfif")):
                            img = Image.open(file)
                            img_resized = resize_image(img)  # Resize to uniform size
                            st.image(img_resized, caption=file.name)
                        elif file.name.endswith("mp4"):
                            st.video(file)

                        col1, col2 = st.columns(2)
                        with col1:
                            is_selected = st.checkbox(f" ", key=file.name)  # Updated checkbox label
                            if is_selected:
                                selected_files.append(file)

                        with col2:
                            delete_button = st.button(f"Delete ", key=f"delete_{file.name}")
                            if delete_button:
                                st.session_state.uploaded_files = [f for f in st.session_state.uploaded_files if f.name != file.name]
                                try:
                                    os.remove(os.path.join(SAVE_PATH, file.name))
                                    st.success(f"File '{file.name}' has been deleted.")
                                except FileNotFoundError:
                                    st.warning(f"File '{file.name}' was not found.")
                                st.experimental_rerun()

                # Check if the captured image is to be annotated
                if st.session_state.captured_image is not None:
                    captured_img = Image.fromarray(st.session_state.captured_image)
                    captured_img_resized = resize_image(captured_img)  # Resize to uniform size
                    st.image(captured_img_resized, caption="Captured Image", use_column_width=True)
                    col1, col2 = st.columns(2)  # Create columns for options

                    with col1:
                        # Allow selection of captured image
                        is_selected_captured = st.checkbox(" ", key="captured_image_checkbox")
                        if is_selected_captured:
                            selected_files.append(("Captured Image", st.session_state.captured_image))  # Include the captured image as selected

                    with col2:
                        # Allow deletion of captured image
                        delete_captured_button = st.button("Delete")
                        if delete_captured_button:
                            st.session_state.captured_image = None  # Remove the captured image from session state
                            st.success("Captured image deleted.")
                            st.experimental_rerun()

                col1, col2 = st.columns([2, 1])
                with col1:
                    if st.button("Start Annotate"):
                        if selected_files:
                            st.session_state.selected_files = selected_files
                            st.session_state.current_index = 0
                            st.session_state.page = "annotation_view"
                        else:
                            st.warning("No files selected for annotation.")

                with col2:
                    if st.button("Go Back"):
                        st.session_state.page = "upload"

        elif st.session_state.page == "annotation_view":
            st.title("Annotation View")

            # Check if files are selected for annotation
            if 'selected_files' in st.session_state and st.session_state.selected_files:
                current_file = st.session_state.selected_files[st.session_state.current_index]

                # Convert UploadedFile to PIL image for annotation
                if isinstance(current_file, tuple):  # If it's the captured image
                    image = Image.fromarray(current_file[1])
                    image_resized = resize_image(image)  # Resize for uniform display
                    st.image(image_resized, caption=current_file[0], use_column_width=True)
                else:  # Uploaded image
                    image = Image.open(current_file)
                    image_resized = resize_image(image)  # Resize for uniform display
                    st.image(image_resized, caption=current_file.name, use_column_width=True)

                # Use st_canvas for annotation
                canvas_result = st_canvas(
                    fill_color="rgba(255, 165, 0, 0.3)",  # Annotation color
                    stroke_width=2,
                    stroke_color="#000000",
                    background_image=image_resized,  # Display the uploaded image for annotation
                    update_streamlit=True,
                    height=image_resized.height,
                    width=image_resized.width,
                    drawing_mode="rect",
                    key="canvas"
                )

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.session_state.current_index > 0:
                        if st.button("Previous"):
                            st.session_state.current_index -= 1
                    else:
                        st.button("Previous", disabled=True)

                with col2:
                    if st.session_state.current_index < len(st.session_state.selected_files) - 1:
                        if st.button("Next"):
                            st.session_state.current_index += 1
                    else:
                        st.button("Next", disabled=True)

            else:
                st.warning("No files selected for annotation.")

            if st.button("Go Back"):
                st.session_state.page = "annotate"

            # Annotation tags
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            with col1:
                looped_stitch = st.checkbox("Looped Stitch")
            with col2:
                broken_stitch = st.checkbox("Broken Stitch")
            with col3:
                skipped_stitch = st.checkbox("Skipped Stitch")
            with col4:
                pinched_mark = st.checkbox("Pinched Mark")
            with col5:
                stain = st.checkbox("Stain")
            with col6:
                save = st.button("Save")

            # Save the annotated image
            if save:
                if canvas_result.json_data is not None:
                    # Convert the canvas drawing to an image
                    # Create a new image for the canvas marks
                    canvas_image = Image.new("RGBA", image.size)  # Use image.size for dimensions

                    # Extract the drawn objects (rectangles, etc.)
                    drawn_objects = canvas_result.json_data["objects"]
                    for obj in drawn_objects:
                        if obj["type"] == "rect":
                            # Draw rectangles on the canvas
                            rect = Image.new("RGBA", (obj["width"], obj["height"]), (255, 255, 255, 0))
                            # Use draw methods to draw the rectangle on the canvas
                            rect_draw = ImageDraw.Draw(rect)
                            rect_draw.rectangle([0, 0, obj["width"], obj["height"]], fill=(255, 165, 0, 128))  # Semi-transparent fill
                            canvas_image.paste(rect, (obj["left"], obj["top"]), rect)

                    # Save the annotated image with the checkbox name
                    SAVE_BASE_PATH = "path_to_base_folder"  # Set your base save path here
                    selected_checkbox_name = []

                    # Collect the selected checkbox names
                    if looped_stitch: selected_checkbox_name.append("Looped_Stitch")
                    if broken_stitch: selected_checkbox_name.append("Broken_Stitch")
                    if skipped_stitch: selected_checkbox_name.append("Skipped_Stitch")
                    if pinched_mark: selected_checkbox_name.append("Pinched_Mark")
                    if stain: selected_checkbox_name.append("Stain")

                    # Create a unique name for the annotated image based on selected checkboxes
                    if selected_checkbox_name:
                        annotated_image_name = "_".join(selected_checkbox_name) + ".png"
                    else:
                        annotated_image_name = "annotated_image.png"  # Default name if no checkbox is selected

                    # Save the final image in the appropriate folder based on the selected checkboxes
                    for checkbox_name in selected_checkbox_name:
                        # Create the folder path for the selected checkbox
                        folder_path = os.path.join(SAVE_BASE_PATH, checkbox_name)
                        
                        # Create the directory if it doesn't exist
                        os.makedirs(folder_path, exist_ok=True)
                        
                        # Construct the full path for the image
                        image_save_path = os.path.join(folder_path, annotated_image_name)

                        # Save the final image
                        final_image = Image.alpha_composite(image.convert("RGBA"), canvas_image)
                        final_image.save(image_save_path)
                        
                        # Provide feedback to the user
                        st.success(f"Annotated image saved as `{image_save_path}`.")

                        # Optionally, show the saved annotated image
                        st.image(final_image, caption="Annotated Image", use_column_width=True)














    
def download_image(image_path):
    """Function to download an image."""
    with open(image_path, "rb") as file:
        return file.read()

# # Prediction function (for demonstration purposes)
# def predict_image(image_path):
#     """
#     Function to make a prediction on a single image.
#     In this case, we assume that the model outputs either 0 or 1.
#     """
#     # Add your model prediction code here.
#     return 1  # Example: Always predicting 1 (Broken Stitch Detected)

# Detection Module logic
if module_selection == "Detection Module":
    option_2 = st.selectbox("Detection Module", ("Feeds", "Uploads"))

    


    # Start video capture logic
   
    # Define the folder where images will be saved
    output_folder = "captured_frames"  # Ensure this folder exists


    def show_alert(type, image_name):
        """Displays an alert when a defect is identified."""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        message = f"{type} Defect identified in Image {image_name}. Do you want to continue?"

        # Show the popup with Continue and Cancel buttons
        response = messagebox.askquestion("Defect Alert", message)
        root.destroy()  # Destroy the window after the popup is handled

        if response == 'yes':
            return True  # Continue
        else:
            return False  # Cancel

   

    # # Example frame processing logic
    # def predict_on_new_image(image_path):
        

    # Function to handle deleting an image
    def delete_image(image_name, output_folder):
        os.remove(os.path.join(output_folder, image_name))
        st.success(f"Deleted: {image_name}")
        st.experimental_rerun()  # Rerun the app after deletion to reflect changes

    # Store results in session state to persist between interactions
    if 'result' not in st.session_state:
        st.session_state.result = []

    # Process frames if the "Process" button is clicked
    if option_2 == "Feeds":
        if st.button("Process"):
            
            st.session_state["capture_video"] = True
            st.session_state["frame_type"] = "Video"

            # Create the output folder to save the frames if it doesn't exist
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # Capture video for 20 seconds and save all frames
            cap = cv2.VideoCapture(0)
            start_time = time.time()
            frame_count = 0  # Count of captured images

            video_placeholder = st.empty()  # Placeholder for showing video frames

            

            while time.time() - start_time < 5 and st.session_state["capture_video"]:
                ret, frame = cap.read()
                if not ret:
                    st.warning("Failed to capture video.")
                    break

                # Display the video frame
                video_placeholder.image(frame, channels="BGR")

                # Save each frame captured without displaying it
                frame_filename = os.path.join(output_folder, f"frame_{frame_count + 1}.jpg")
                cv2.imwrite(frame_filename, frame)  # Save the frame as an image
                frame_count += 1

                time.sleep(0.1)  # Small sleep to reduce CPU usage while looping

            cap.release()
            st.session_state["capture_video"] = False  # Stop video capture after 20 seconds
            st.success("Video processing completed. All frames captured.")
            with st.spinner("Processing image..."):
                # Now process the saved frames
                result = []  # List to store results for each frame
                for frame_file in os.listdir(output_folder):
                    if frame_file.endswith(('.png', '.jpg', '.jpeg')):
                        frame_path = os.path.join(output_folder, frame_file)

                        # Open the saved frame
                        image = Image.open(frame_path)

                        # Predict on the image using the prediction function
                        prediction,flag = predict_image(frame_path)

                    # Ensure results list exists in session state
                        if 'result' not in st.session_state:
                            st.session_state.result = []

                        # Function to convert image to base64
                        def convert_image_to_base64(image):
                            """Convert a PIL image to a base64 string."""
                            buffered = BytesIO()
                            image.save(buffered, format="PNG")
                            return base64.b64encode(buffered.getvalue()).decode()

                        # Process images (you might have this in your image processing section)

                
                        # frame_path = "path_to_your_image"  # Replace this with actual logic to get frame_path
                        frame_file = os.path.basename(frame_path)

                        image = PILImage.open(frame_path)
                        image_base64 = convert_image_to_base64(image)  # Convert to base64 string

                        # Append the result to the session state
                        st.session_state.result.append({
                            "Image Name": frame_file,
                            "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "Defect Detected": prediction,  # Replace with actual prediction
                            "name" : flag,
                            "Image": f'<img src="data:image/png;base64,{image_base64}" width="50" />',  # Store base64 image for HTML rendering
                        })

                # Convert results in session state into a DataFrame for display
                if st.session_state.result:
                    results_df = pd.DataFrame(st.session_state.result)

                    # Display the DataFrame in a tabular format
                    st.write("### Prediction Results")

                    # Add headers for the table
                    header_col1, header_col2, header_col3, header_col4, header_col5, header_col6 = st.columns([1.5, 2, 2, 1.5, 1.5, 1])
                    
                    with header_col1:
                        st.write("**Image Name**")
                    with header_col2:
                        st.write("**Defect Detected**")
                    with header_col3:
                        st.write("**Time**")
                    with header_col4:
                        st.write("**Download**")
                    with header_col5:
                        st.write("**False Positive**")
                    with header_col6:
                        st.write("**Image**")

                    # Iterate through the DataFrame and add custom buttons for each row
                    for i, row in results_df.iterrows():
                        st.markdown("---")  # Add separator line for each row

                        with st.container():
                            col1, col2, col3, col4, col5, col6 = st.columns([1.5, 1.5, 2, 1.5, 1.5, 1])  # Adjust layout

                            with col1:
                                st.write(f"{row['Image Name']}")
                            with col2:
                                st.write(f"{row['Defect Detected']}")
                            with col3:
                                st.write(f"{row['Time']}")

                            with col4:
                                # Download button
                                with open(os.path.join(output_folder, row["Image Name"]), "rb") as img_file:
                                    st.download_button(label="Download", data=img_file, file_name=row["Image Name"], key=f"download_{i}")

                            with col5:
                                # Yes checkbox
                                checkbox_response = st.checkbox("Yes", key=f"yes_{i}")
                                results_df.at[i, "False Positive"] = checkbox_response  # Store response in DataFrame

                            with col6:
                                # Display the image
                                st.markdown(row['Image'], unsafe_allow_html=True)

                # If there are no results, display a message
                else:
                    st.write("No defects detected.")


                results_df = pd.DataFrame(result)                

                # Button to download the entire results table as CSV
                csv = results_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download table as CSV",
                    data=csv,
                    file_name='prediction_results.csv',
                    mime='text/csv',
                )

                # Clear All Data button
                if st.button("Clear All Data"):
                    st.session_state.result = []  # Clear the captured data
                    st.experimental_rerun()  # Rerun the app to reflect the changes












    elif option_2 == "Uploads":
        # Function to capture frame and store it
        def capture_frame(frame, frame_type):
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(frame_rgb)
            image_name = f"frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            buffer = BytesIO()
            img_pil.save(buffer, format="PNG")
            buffer.seek(0)

            # Append captured data to session state with default values
            st.session_state["captured_data"].append({
                "Image Name": image_name,
                "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "Image Buffer": buffer,
                "Defect Detected": "_________",
                "Confidence": "100%",
                "Frame Type": frame_type,
            })


        def extract_frames_from_video(video_path, output_folder, interval=30):
    
            if not os.path.exists(video_path):
                print(f"Error: Video not found at path: {video_path}")
                return
            
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)  # Create output folder if not exists
            # else:
            #     shutil.rmtree(output_folder)  # Clean output folder
            #     os.makedirs(output_folder)

            # Capture video
            cap = cv2.VideoCapture(video_path)
            frame_count = 0
            saved_frame_count = 0

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Process every 'interval' frame
                if frame_count % interval == 0:
                    print(f"Processing frame {frame_count}...")
                    
                            
                    # Save the defective frame
                    frame_filename = os.path.join(output_folder, f"frame_{frame_count}.jpg")
                    cv2.imwrite(frame_filename, frame)
                    saved_frame_count += 1

                frame_count += 1

            cap.release()
            print(f"Processing complete. Saved {saved_frame_count} defective frames to {output_folder}")    

        st.title("UPLOAD PROCESSING")

        # Initialize session state variables
        if "capture_video" not in st.session_state:
            st.session_state["capture_video"] = False
        if "captured_data" not in st.session_state:
            st.session_state["captured_data"] = []
        if "frame_type" not in st.session_state:
            st.session_state["frame_type"] = None


            







        # Selection box for "Start Video", "Capture Image", "Upload Image"
        option_3 = st.selectbox("Select Option", ("Upload Image","Upload Video", "Capture Image"))



        # Initialize the results list in session state
        if "results" not in st.session_state:
            st.session_state["results"] = []

        
        # Define the output folder for captured images
        output_folder = "Capture_Images"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)       

        # Image capture logic
        if option_3 == "Capture Image":
            if st.button("Capture Image"):
                st.session_state["frame_type"] = "Captured Image"
                cap = cv2.VideoCapture(0)

                # Ensure the camera is opened properly
                if not cap.isOpened():
                    st.warning("Camera could not be accessed.")
                else:
                    # Wait a little to make sure the camera adjusts
                    time.sleep(1)

                    ret, frame = cap.read()
                    if ret:
                        st.image(frame, channels="BGR")  # Display the captured frame
                        img_path = os.path.join(output_folder, f"Captured_Image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                        Image.fromarray(frame).save(img_path)  # Save the captured image
                        st.success(f"Image captured and saved as {img_path}")

                        # Predict on the image using the prediction function
                        prediction, flag = predict_image(img_path)
                        print("+++++++++++++++++++++++++++++++++++++++++")
                        print(prediction, flag)
                        print("+++++++++++++++++++++++++++++++++++++++++")

                        # Append the result to the list in session state
                        st.session_state["results"].append({
                            "Image Name": os.path.basename(img_path),  # Use the name of the saved image
                            "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "Defect Detected": flag,
                            "name": prediction,
                            
                        })
                    else:
                        st.warning("Failed to capture image.")
                
                cap.release()  # Release the camera

            # Convert the list of results into a DataFrame for display
            if st.session_state["results"]:
                results_df = pd.DataFrame(st.session_state["results"])
                if st.button("start"):
                    with st.spinner("Processing image..."):

                        # Display the table in Streamlit
                        st.write("Defect Catalogue:")
                        st.dataframe(results_df)


                        # Download button for the CSV file
                        csv = results_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download Results as CSV",
                            data=csv,
                            file_name='prediction_results.csv',
                            mime='text/csv',
                        )


                        #  # Clear All Data button
                        if st.button("Clear All Data"):
                            st.session_state["results"] = []  # Clear the captured data
                            st.experimental_rerun()  # Rerun the app to reflect the changes

                







        # Upload image logic
        if option_3 == "Upload Image":
            results = []

            output_folder = "uploaded_Images"
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            uploaded_files = st.file_uploader("Upload an Image", accept_multiple_files=True, type=["png", "jpg", "jpeg"])



            if uploaded_files :
                # image_count=0
                for i in range(0, len(uploaded_files), 3):
                    cols = st.columns(3)  # Create 3 columns
                    for j in range(3):
                        if i + j < len(uploaded_files):
                            with cols[j]:
                                # Get the current file
                                uploaded_file = uploaded_files[i + j]
                                
                                # Open the image
                                image = Image.open(uploaded_file)
                                
                                # Generate a path to save the uploaded image
                                save_path = os.path.join(output_folder, uploaded_file.name)

                                # Save the image to the output folder
                                image.save(save_path)

                                # Display the image
                                st.image(image, caption=uploaded_file.name)

                                # Predict on the image using the prediction function
                                prediction, flag = predict_image(save_path)

                                

                                # Append the result to the list
                                results.append({
                                    "Image Name": uploaded_file.name,
                                    "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    "Defect Detected": flag,
                                    "Type": prediction,
                                })

            # Convert the list of results into a DataFrame for display
            results_df = pd.DataFrame(results)
            
            if st.button("Detect"):
                
                def apply_scanning_effect(image):
                    image_placeholder = st.empty()
                    scanning_image = image.copy()
                    width, height = scanning_image.size
                    
                    for y in range(0, height, 10):
                        scanning_overlay = scanning_image.copy()
                        draw = ImageDraw.Draw(scanning_overlay)
                        draw.line([(0, y), (width, y)], fill="lime", width=5)
                        scanning_overlay = scanning_overlay.convert("RGB")
                        enhancer = ImageEnhance.Brightness(scanning_overlay)
                        scanning_overlay = enhancer.enhance(1.2)
                        
                        image_placeholder.image(scanning_overlay, caption='Scanning Image...', width=100)
                        time.sleep(0.05)
                    
                    return image_placeholder
                for file in uploaded_files:
                    image = Image.open(file)    
                    apply_scanning_effect(image)



                with st.spinner("Processing image..."):


                    progress_bar = st.progress(0)

                    for percent_complete in range(101):
                        time.sleep(0.01)  # Adjusted delay for progress bar
                        progress_bar.progress(percent_complete)
                        
                   
                    # Display the table in Streamlit
                    st.write("Defect Catalogue:")
                    st.dataframe(results_df)
                    winsound.Beep(1000, 500)  # Frequency = 1000 Hz, Duration = 500 ms

                    # Display an alert popup with no button and no image name
                    st.markdown(
                        f"""
                        <div style="position: fixed; top: 20%; left: 30%; width: 40%; padding: 20px; 
                                    background-color: white; border: 2px solid red; border-radius: 10px; 
                                    box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.5); text-align: center; z-index: 9999;">
                            <h2 style='color: red;'>Alert: Prediction is { prediction}</h2>
                            <p style='font-size: 18px;'>Action is required!</p>
                        </div>
                        """,
                        unsafe_allow_html=True
        )

                    # Download button for the CSV file
                    csv = results_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Results as CSV",
                        data=csv,
                        file_name='prediction_results.csv',
                        mime='text/csv',
                )


                    # Clear All Data button
                    if st.button("Clear All Data"):
                        st.session_state["results"] = []  # Clear the captured data
                        st.experimental_rerun()  # Rerun the app to reflect the changes
                    # st.image(image)    
                    

                











        if option_3 == "Upload Video":




            # Create a folder to save the videos if it doesn't exist
            output_folder = "uploaded_videos"
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            uploaded_video = st.file_uploader("Upload a Video", type=["mp4", "avi", "mov"])
            if uploaded_video is not None:
                st.session_state["frame_type"] = "Uploaded Video"


                    # Save uploaded video to a specified folder in the current directory
                video_bytes = uploaded_video.read()  # Read the uploaded video file bytes
                video_save_path = os.path.join(output_folder, uploaded_video.name)  # Full path to save the file

                # Write the video to the folder
                with open(video_save_path, "wb") as f:
                    f.write(video_bytes)



              
               

                # Main function to extract frames, predict and display the results in a table
                if st.button("RUN"):
                    with st.spinner("Processing image..."):
                        # Assuming you have a function to extract frames from the video
                        # Function to extract frames from the video
                        extract_frames_from_video(video_save_path, output_folder, interval=50)

                        # List to store results for the table
                        results = []

                        # Get all frame files from the output folder
                        frame_files = [f for f in os.listdir(output_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

                        for frame_file in frame_files:
                            # Build the full path to the frame image
                            frame_path = os.path.join(output_folder, frame_file)

                            # Predict on the image using the prediction function
                            prediction, flag = predict_image(frame_path)

                            # Open the image with PIL
                            def convert_image_to_base64(image):
                                """Convert a PIL image to a base64 string."""
                                buffered = BytesIO()
                                image.save(buffered, format="PNG")
                                return base64.b64encode(buffered.getvalue()).decode()

                            # Only process images where defects are detected
                            if flag == 'Yes':
                                image = PILImage.open(frame_path)
                                image_base64 = convert_image_to_base64(image)  # Convert to base64 string
                                
                                results.append({
                                    "Image Name": frame_file,
                                    "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    "Defect Detected": flag,
                                    "Type": prediction,
                                    "Image": f'<img src="data:image/png;base64,{image_base64}" width="50" />',  # Store base64 image for HTML rendering
                                    "Download": f"<a href='data:image/png;base64,{image_base64}' download='{frame_file}'>Download</a>"  # Download link
                                })

                        # Display results if there are any after the loop
                        if results:
                            st.write("Defect Catalogue:")
                            
                            # Convert the list of results into a DataFrame for display
                            results_df = pd.DataFrame(results)


                            # Display the DataFrame with HTML rendering
                            st.markdown(results_df.to_html(escape=False), unsafe_allow_html=True)
                        else:
                            st.write("No defects detected.")

                            # Download button for each image
                    
                        # Download button for the CSV file
                        csv = results_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download Results as CSV",
                            data=csv,
                            file_name='defect_catalogue.csv',
                            mime='text/csv'
                        )

                        if st.button("Clear All Data"):
                            st.session_state["captured_data"] = []  # Clear the captured data
                            st.experimental_rerun()  # Rerun the app to reflect the changes
                                            