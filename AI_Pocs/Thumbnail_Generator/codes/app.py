# import openai.openai_object
import streamlit as st
import dlib, yt_dlp, requests, os, time, shutil,random, face_recognition, pickle, re, stat
from PIL import Image
from io import BytesIO
import openai
from extractFrames import extract_frames
from filterFaces import filter_frames_with_dominant_face
from removeDuplicates import remove_duplicate_frames
from aiFaceEnhancer import process_image
import hashlib
import json

song_name = ''

def recognize_actors(image_path, actor_names):
    with open('encodings.pkl', 'rb') as f:
        known_encodings = pickle.load(f)
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)
    
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces([encoding for name, encoding in known_encodings], face_encoding)
        if any(matches):
            matched_actor = known_encodings[matches.index(True)][0]
            if matched_actor in actor_names:
                return True
    return False

def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_user(username, password):
    users = load_users()
    return username in users and users[username] == hash_password(password)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = hash_password(password)
    save_users(users)
    return True



def download_youtube_video(youtube_url, output_path):
    # Ensure the output directory exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Define the output file template
    output_file = os.path.join(output_path, 'video.mp4')

    # yt-dlp options
    ydl_opts = {
        'outtmpl': output_file,
        'format': 'bv*[height<=640]+ba/b[height<=640] / wv*+ba/w',
        'noplaylist': True,
    }

    try:
        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        
        print(f"Video downloaded successfully to {output_file}")
        return output_file
    
    except Exception as e:
        print(f"Failed to download video. Error: {str(e)}")
        return None

def main(video_url, output_path, frame_interval, face_size_threshold, cnn_model, video_type):
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.text("Downloading video...")
        
        ####### DOWNLOAD VIDEO ##################
        #########################################
        
        video_path = download_youtube_video(video_url, output_path)
        if not video_path:
            st.error("Failed to download video. Please try again...")
            return 0, 0
        frames_folder = os.path.join(output_path, "frames1")
        extract_frames(video_path, frames_folder, frame_interval)
        progress_bar.progress(20)

        ####### EXTRACT VIDEO ##################
        #########################################
        frames_folder = os.path.join(output_path, "frames1")

        status_text.text("Extracting frames from the video...") 
        extract_frames(video_path, frames_folder, frame_interval)

        progress_bar.progress(40)

        status_text.text("Detecting and analyzing faces in frames...")
        face_folder = os.path.join(output_path, "frames2")
        faces = filter_frames_with_dominant_face(frames_folder, face_folder, cnn_model, video_type, face_size_threshold)
        if not faces:
            st.warning("No faces detected in the video. Cannot generate thumbnails.")
            return 0, 0
        progress_bar.progress(60)

        status_text.text("Selecting thumbnail candidates...")
        unique_folder = os.path.join(output_path, "frames3")
        unique_thumbnails = remove_duplicate_frames(face_folder, unique_folder)

        progress_bar.progress(100)
        status_text.text("Thumbnails generation complete!")
        time.sleep(1)
        status_text.empty()
        progress_bar.empty()

        return unique_thumbnails

    except Exception as e:
        st.error(f"Something went wrong: Please retry the process....")
        print(str(e))
        return 0, 0


openai.api_key = "sk-proj-fKcIZYsf6Q8iuEIl5A2UT3BlbkFJCes8oljbs05oJ3Ek1DVp"

def get_actors_name(title):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that extracts actors' names from video titles."},
                {"role": "user", "content": f"Based on this YouTube video title, list the actors' names mentioned: \n\n{title}. Provide the actors' names in a comma-separated format."}
            ]
        )
        return response.choices[0].message['content'].strip().split(', ')
    except Exception as e:
        return f"Unable to generate summary: {str(e)}"

def summarize_description(description):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that creates concise song titles."},
                {"role": "user", "content": f"Based on this YouTube video description, provide a one-liner title for the song apart from the existing title, focusing on the main characters and central conflict:\n\n{description}"}
            ]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Unable to generate summary: {str(e)}"
 
def get_video_info(video_url):
    ydl_opts = {'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        pattern = r'Song\s*[:▶]*\s*(.*)'
        match = re.search(pattern, info['description'])
        if match:
            name = match.group(1).strip()
            return info['title'], info['description'], info['thumbnail'], name
        else:
            return info['title'], info['description'], info['thumbnail'], ''
        
def get_youtube_thumbnail(video_url):
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        thumbnail_url = info['thumbnail']
    response = requests.get(thumbnail_url)
    img = Image.open(BytesIO(response.content))
    img.save(f'../thumbnails/{st.session_state.username}/frames3/main_thumbnail.jpg')
    # img.save('../thumbnails/main_thumbnail.jpg')
    # shutil.copy('../thumbnails/main_thumbnail.jpg', '../thumbnails/frames3')
    return img

def remove_readonly(func, path, excinfo):
    # Change the permission to writable and retry
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clear_session(username):
    user_thumbnail_folder = f"../thumbnails/{username}/"

    if os.path.exists(user_thumbnail_folder):
        # Loop through and delete all files and folders inside the username folder
        for filename in os.listdir(user_thumbnail_folder):
            file_path = os.path.join(user_thumbnail_folder, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Remove file or symbolic link
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Remove directory and its contents

    # Ensure only 'youtube_url' is cleared, not other session state variables
    if 'youtube_url' in st.session_state:
        del st.session_state['youtube_url']

    # Preserve any login state or session variables related to login
    if 'logged_in' in st.session_state:
        st.session_state['logged_in'] = True  # Ensure login state is preserved

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.session_state['logged_in'] = True
                st.rerun()  # Changed from st.experimental_rerun()
            else:
                st.error("Invalid username or password")
    with col2:
        if st.button("Register"):
            if register_user(username, password):
                st.success("Registered successfully! Please login.")
            else:
                st.error("Username already exists")

    return username

def app():
    s = time.time()
    logo_path = "../templates/logo.jpg"
    image = Image.open(logo_path)
    st.logo(image)
    st.image(logo_path)
    genre = []
    actors_list = []
    output_path = f"../thumbnails/{st.session_state.username}" if 'username' in st.session_state else "../thumbnails"
    frame_interval = 6
    face_size_threshold = 0.02
    global song_name
    flag = True

    # Create user-specific folders
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if not os.path.exists(os.path.join(output_path, "frames1")):
        os.makedirs(os.path.join(output_path, "frames1"))
    if not os.path.exists(os.path.join(output_path, "frames2")):
        os.makedirs(os.path.join(output_path, "frames2"))
    unique_thumbnails_folder = os.path.join(output_path, "frames3")
    if not os.path.exists(unique_thumbnails_folder):
        os.makedirs(unique_thumbnails_folder)
    if not os.path.exists(os.path.join(output_path, "aiImages")):
        os.makedirs(os.path.join(output_path, "aiImages"))

    # Initialize session state for AI edit button and sliders
    if 'ai_edit_active' not in st.session_state:
        st.session_state.ai_edit_active = False

    # Initialize session state for sliders
    if 'brightness' not in st.session_state:
        st.session_state.brightness = 0.8
    if 'contrast' not in st.session_state:
        st.session_state.contrast = 2
    if 'hue' not in st.session_state:
        st.session_state.hue = 3
    if 'sharpness' not in st.session_state:
        st.session_state.sharpness = 1
    if 'color_enhance' not in st.session_state:
        st.session_state.color_enhance = 1
    
    if 'hdr' not in st.session_state:
        st.session_state.hdr = False
    if 'gray' not in st.session_state:
        st.session_state.gray = False
    if 'color' not in st.session_state:
        st.session_state.color = False
    if 'text' not in st.session_state:
        st.session_state.text = False
    if 'text_position' not in st.session_state or st.session_state.text_position not in ['Bottom', 'Right', 'Left']:
        st.session_state.text_position = 'Bottom'       

    # Load Dlib's CNN face detector model
    cnn_face_detector = dlib.cnn_face_detection_model_v1('../models/mmod_human_face_detector.dat')

    st.title("YouTube Thumbnail Generator")

    if 'youtube_url' not in st.session_state:
        st.session_state.youtube_url = ""

    video_type = st.selectbox("Video Type", ['Song', 'Movie', 'Others'])

    youtube_url = st.text_input("Enter YouTube URL", value=st.session_state.youtube_url)

    if '&' in str(youtube_url):
        ind = str(youtube_url).index('&')
        youtube_url = str(youtube_url)[:ind]

    if youtube_url != st.session_state.youtube_url:
        st.session_state.youtube_url = youtube_url

    if youtube_url:
        st.image(get_youtube_thumbnail(youtube_url), caption="YouTube Video Thumbnail", width=500)
        title, description, thumbnail_url, songName = get_video_info(youtube_url)
        print("SONG NAME1:", songName)
        global song_name
        song_name = songName
        summary = summarize_description(description)
        st.subheader("Video Title")
        st.write(title)
        st.subheader("Video Summary")
        st.write(summary)
        actors_list = get_actors_name(title)

    st.sidebar.header("Parameter Adjustments")
    fi = 25 if video_type == 'Movie' else 6
    frame_interval = st.sidebar.slider("Frame interval", 1, 30, fi)
    face_size_threshold = 0.02
    face_size_threshold = st.sidebar.slider("Face size threshold", 0.01, 0.1, 0.01, 0.02)
    similarity_threshold = st.sidebar.slider("Similarity threshold", 0.1, 0.99, 0.65, 0.01)

    if video_type != 'Song':
        st.sidebar.write('Choose Genre')
        if st.sidebar.checkbox('Comedy'):
            genre.append('Happy')
            genre.append('Surprise')
        st.sidebar.checkbox('Thriller')
        st.sidebar.checkbox('Action')

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Thumbnails"):
            st.cache_data.clear()
            st.cache_resource.clear()

            if youtube_url:
                unique_thumbnails = main(youtube_url, output_path, frame_interval, face_size_threshold, cnn_face_detector, video_type)

                if len(unique_thumbnails) > 0:
                    st.success("Thumbnails generated successfully!")
                else:
                    st.warning("No thumbnails were generated. Please check the video and parameters.")
            else:
                st.error("Please enter a YouTube URL")

    with col2:
        if st.button("Clear"):
            clear_session(st.session_state.username)
            st.cache_data.clear()
            st.cache_resource.clear()
            # Remove the following line:
            st.session_state.clear()
            st.success("Cleared YouTube URL and removed generated thumbnails.")
            st.rerun()
    save_folder = os.path.join(output_path, "saved_images")
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    dump_thumbnails_folder = os.path.join(output_path, "dump")
    if not os.path.exists(dump_thumbnails_folder):
        os.makedirs(dump_thumbnails_folder)

    if os.path.exists(unique_thumbnails_folder):
        thumbnails = [f for f in os.listdir(unique_thumbnails_folder) if f.endswith(('.jpg', '.png'))]
        selected_thumbnails = set()
        
        if st.button("Shuffle Thumbnails"):
            if len(os.listdir(unique_thumbnails_folder)) == 0:
                st.write("No more unique thumbnails to display...")
            else:
                for file_name in st.session_state.selected_thumbnails:
                    src_file = os.path.join(unique_thumbnails_folder, file_name)
                    dest_file = os.path.join(dump_thumbnails_folder, file_name)
                    shutil.move(src_file, dest_file)
                st.session_state.selected_thumbnails = []
                st.rerun() 

        if 'selected_thumbnails' not in st.session_state:
            st.session_state.selected_thumbnails = set()

        if not st.session_state.selected_thumbnails:
            if thumbnails:
                if os.path.exists(os.path.join(unique_thumbnails_folder, 'main_thumbnail.jpg')):
                    selected_thumbnails.update({'main_thumbnail.jpg'})
                if len(selected_thumbnails) == 0:
                    thumb_count = 12
                else:
                    thumb_count = 11

                if len(thumbnails) < thumb_count:
                    selected_thumbnails.update(set(thumbnails))
                else:
                    if video_type == 'Song':
                        selected_thumbnails.update(set(random.sample(thumbnails, min(thumb_count, len(thumbnails)))))
                    else:
                        mainActors = [f for f in os.listdir(unique_thumbnails_folder) if recognize_actors(os.path.join(unique_thumbnails_folder, f), actors_list)]
                        a = len(mainActors) if len(mainActors) <= 8 else 9
                        if a == 9:
                            selected_thumbnails.update(set(random.sample(mainActors, 9)))
                            selected_thumbnails.update(set(random.sample(thumbnails, thumb_count - a)))
                        else:
                            selected_thumbnails.update(set(random.sample(mainActors, a)))
                            selected_thumbnails.update(set(random.sample(thumbnails, thumb_count - a)))
                st.session_state.selected_thumbnails = selected_thumbnails

        cols = st.columns(3)
        cnt = 0
        selected_thumbnails = st.session_state.selected_thumbnails

        images = []

        for idx, photo in enumerate(selected_thumbnails):
            print("==================================")
            print("Entered Unique thumbnails folder")
            print("==================================")
            img = Image.open(os.path.join(unique_thumbnails_folder, photo))
            with cols[idx % 3]:
                st.image(img, use_column_width=True)
                unique_key = f"{photo}_{idx}"
                if st.checkbox(f"{photo}", key=unique_key):
                    images.append(photo)
                cnt += 1

        if st.session_state.selected_thumbnails:
            if st.button("AI Edit"):
                st.session_state.ai_edit_active = True

            # Display sliders if AI Edit is active
            if st.session_state.ai_edit_active:
                st.sidebar.text('---------------------------------')
                st.sidebar.text('Adjust Enhancing Parameters')
                # Use session state to store slider values
                st.session_state.brightness = st.sidebar.slider('Brightness', min_value=0.1, max_value=1.0, value=st.session_state.brightness, step=0.1)
                st.session_state.contrast = st.sidebar.slider('Contrast', 1, 5, st.session_state.contrast, 1)
                st.session_state.hue = st.sidebar.slider('Hue', 1, 10, st.session_state.hue, 1)
                st.session_state.sharpness = st.sidebar.slider('Sharpness', 1, 5, st.session_state.sharpness, 1)
                st.session_state.color_enhance = st.sidebar.slider('Color enhance', 1, 5, st.session_state.color_enhance, 1)
                st.session_state.hdr = st.sidebar.checkbox('HDR', st.session_state.hdr)
                st.session_state.gray = st.sidebar.checkbox('GrayScale', st.session_state.gray)
                st.session_state.color = st.sidebar.checkbox('Colorize', st.session_state.color)
                st.session_state.text = st.sidebar.text_input('Enter text to display on thumbnail')
                st.session_state.text_color = st.sidebar.radio('Choose text color', options=['White', 'Black', 'Red', 'Green', 'Blue', 'Yellow'])
                st.session_state.text_position = st.sidebar.selectbox('Select text position:', ['Bottom', 'Right', 'Left'], index=['Bottom', 'Right', 'Left'].index(st.session_state.text_position))
                cnt = 1
                if st.button("Submit"):
                    for i in images:
                        print("SONG NAME2:", song_name)
                        inp = os.path.join(unique_thumbnails_folder, i)
                        out = os.path.join(output_path, f'aiImages/aiImg_{cnt}.jpg')
                        if st.session_state.text: 
                            song_name = st.session_state.text
                        ai_image = process_image(inp, out, song_name, st.session_state.text_color,
                                        st.session_state.brightness, st.session_state.contrast, st.session_state.hue, st.session_state.sharpness, st.session_state.color_enhance,
                                        st.session_state.hdr, st.session_state.gray, st.session_state.color, st.session_state.text_position, '../templates/RACE1_Brannt_Plus_NCV.ttf', '../templates/HdLogo.jpg')
                        st.image(ai_image)
                        cnt += 1
                    st.success(f"Selected images are enhanced with AI and saved to '{os.path.join(output_path, 'aiImages')}' ")

            if st.button("Download Selected Images"):
                for i in images:
                    img = Image.open(os.path.join(unique_thumbnails_folder, i))
                    img.save(os.path.join(save_folder, i))
                st.success(f"Selected images have been saved to '{save_folder}'.")

            if st.button("Download All Images"):
                for thumbnail in selected_thumbnails:
                    img = Image.open(os.path.join(unique_thumbnails_folder, thumbnail))
                    img.save(os.path.join(save_folder, thumbnail))
                st.success(f"Images have been saved successfully.")

    e = time.time()
    print("Time:", (e-s))

def run_app():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
    else:
        app()

if __name__ == '__main__':
    run_app()
