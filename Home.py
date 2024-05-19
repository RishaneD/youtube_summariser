import streamlit as st
import pandas as pd
from pytube import Playlist
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from openai import OpenAI
import time

st.header('📝 YouTube Summariser')

# Introduction copy
st.markdown("With the YouTube Summarizer app, you can quickly generate concise summaries of videos from any YouTube playlist using the OpenAI API. If you have any feedback, please email me at [rishanedassanayake@gmail.com](rishanedassanayake@gmail.com). I'd love to hear it!")


# Page 1: User Input
if 'page' not in st.session_state:
    st.session_state.page = 1

if st.session_state.page == 1:
    # Step 1: User enters their OpenAI API key
    api_key = st.text_input("🔑 Enter your OpenAI API key:", type="password", help = "Unfortunately, I'm not made of money so you'll have to enter your own API key :( ")

    if api_key == st.secrets.password.special_password:
        api_key = st.secrets.openai.api_key
    
    # Step 2: User enters the URL of a YouTube playlist in a textbox
    playlist_url = st.text_input("🧑🏽‍💻 Enter the YouTube playlist URL:", help='Enter the URL of the YouTube playlist you would like to make summaries of. Make sure this playlist is set to "Public".')
    
    # Step 3: User enters the topic(s) covered in the YouTube playlist in a textbox
    topic = st.text_input("🤓 Enter the topic covered in the playlist:", help = 'You can include multiple topics as well, if applicable. Make sure they are separated by a comma.')
    
    # Step 4: User chooses whether they want the default prompt or a custom prompt
    use_custom_prompt = st.checkbox("Use custom prompt", help = 'I have set a default prompt for the OpenAI model. If you would like to change this prompt because you would like to ask the model to answer more specific questions about the videos in your playlist, check this box and enter your custom prompt in the text area.')
    
    # Step 5: If custom prompt is chosen, user enters the custom prompt in a textbox
    custom_prompt = ""
    if use_custom_prompt:
        custom_prompt = st.text_area("Enter your custom prompt:", help = 'Please make sure your prompt is specific, clear, and well-structured.')

    # Step 6: User presses a button titled 'Create summaries'
    if st.button("Create summaries"):
        # Store inputs in session state
        st.session_state.api_key = api_key
        st.session_state.playlist_url = playlist_url
        st.session_state.topic = topic
        st.session_state.use_custom_prompt = use_custom_prompt
        st.session_state.custom_prompt = custom_prompt
    
        # switch to summary page
        st.session_state.page = 2
        st.rerun()

    st.markdown("""
    #### 💡 How to Use This App
    
    1. **Enter Your OpenAI API Key**
    
       - Input your OpenAI API key to access the summarization services. If you don't have an API key, you can get one from [OpenAI](https://www.openai.com/).
       - If you have a special password, you can enter that instead to use a predefined API key.
    
    2. **Provide the YouTube Playlist URL**
    
       - Paste the URL of the YouTube playlist you want to summarize. See [here](https://support.google.com/youtube/answer/57792?hl=en-GB&co=GENIE.Platform%3DAndroid) to find out how to create a YouTube playlist. 
    
    3. **Specify the Topic(s) Covered**
    
       - Describe the main topics or themes covered in the playlist to help tailor the summaries.
    
    4. **Choose a Custom Prompt (Optional)**
    
       - You can use a default prompt to generate summaries, or specify a custom prompt for more tailored results.
    
    5. **Generate Summaries**
    
       - Click the "Create Summaries" button to start the summarization process. The app will fetch video transcripts, process them, and display the summaries both individually and as DataFrame that can be downloaded as a .csv file. 
       - Processing a playlist with one hour worth of content will take approximately 45 seconds. Please be patient while the app generates your summaries.
    
    6. **Start Over**
    
        - If you want to summarize a different playlist, use the "Start Over" button to reset the app and enter new details.
    
    """)
    
    


if st.session_state.page == 2:
    # Check if inputs are available
    if 'api_key' not in st.session_state or 'playlist_url' not in st.session_state or 'topic' not in st.session_state:
        st.error("Please go back to the input page and provide the required inputs.")
    else:
        # Retrieve inputs from session state
        api_key = st.session_state.api_key
        playlist_url = st.session_state.playlist_url
        topic = st.session_state.topic
        use_custom_prompt = st.session_state.use_custom_prompt
        custom_prompt = st.session_state.custom_prompt
    
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
    
        # Define function to retrieve transcripts
        def fetch_transcript(video_id, title):
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                transcript_text = " ".join([line['text'] for line in transcript])
                return transcript_text
            except TranscriptsDisabled:
                return f"Transcripts are disabled for video: {title}"
            except NoTranscriptFound:
                return f"No transcript found for video: {title}"
            except Exception as e:
                return f"An error occurred for video {title}: {e}"
    
        # Define function to download playlist data
        def download_playlist_data(playlist_url):
            playlist = Playlist(playlist_url)
            video_info = {}
            for video in playlist.videos:
            
                # get the transcript and time
                start_time = time.time()
                result = fetch_transcript(video.video_id, video.title)
                end_time = time.time()
        
                # create dictionary entry for each video in playlist 
                if "An error occurred" not in result and "Transcripts are disabled" not in result and "No transcript found" not in result:
                    video_info[video.video_id] = {
                        "transcript": result,
                        "title": video.title,
                        'author': video.author,
                        "date_published": video.publish_date.strftime("%Y-%m-%d"),
                        "duration": video.length,
                        "transcript_fetch_time": round(end_time-start_time, 2)
                    }
        
            return video_info
    
        # Define function to get model response
        def get_model_response(user_prompt, system_prompt):
            response = client.chat.completions.create(
                model="gpt-4o-2024-05-13",
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": user_prompt}],
                max_tokens=750
            )
            return response.choices[0].message.content
    
        # Compile prompt based on transcript and topic
        def compile_prompt(user_prompt, transcript, topic):
            topic_and_transcript = f"Topic: {topic}\nTranscript: {transcript}"
            compiled_prompt = user_prompt + topic_and_transcript
            return compiled_prompt
    
        # Define the final function to summarize playlist
        def summarize_playlist(playlist_url, user_prompt, system_prompt, topic):
            playlist_data = download_playlist_data(playlist_url)
            summarized_data = {}
            for video_id, info in playlist_data.items():
                compiled_user_prompt = compile_prompt(user_prompt, info['transcript'], topic)
                start_time = time.time()
                summary = get_model_response(compiled_user_prompt, system_prompt)
                end_time = time.time()
                summarized_data[video_id] = {
                    "summary": summary,
                    "transcript": info['transcript'],
                    "title": info['title'],
                    "author": info['author'],
                    "date_published": info['date_published'],
                    "duration": info['duration'],
                    'transcript_fetch_time': info['transcript_fetch_time'],
                    'model_response_time': round(end_time-start_time, 2)
                }
            return summarized_data
    
    
        # Default system prompt
        system_prompt = """You are an expert at summarising YouTube videos on any topic. 
    Your job is to read and effectively summarise and answer questions about YouTube videos based on their transcripts. Do not hallucinate or fabricate any information. If some piece of information requested above is not found in the transcript, simply skip that part. Do not write things like "not found in transcript"."""
    
        # Determine user prompt
        user_prompt = custom_prompt if use_custom_prompt else "Generate a summary for the following transcript and topic."
    
        # Display loading message
        st.info("Loading summaries. A playlist with one hour worth of content will take around 45 seconds to load.")
    
        # Summarize playlist
        summaries = summarize_playlist(playlist_url, user_prompt, system_prompt, topic)
    
        # Convert summaries to DataFrame
        df = pd.DataFrame.from_dict(summaries, orient='index')
        df = df.reset_index().rename(columns={'index': 'video_id'})
        df = df[['video_id', 'title', 'author', 'summary', 'date_published', 'duration']]
    
        # Display raw titles and summaries in markdown format
        for _, row in df.iterrows():
            st.markdown(f"### {row['title']}\n**Author:** {row['author']}\n**Summary:**\n{row['summary']}\n")
    
        # Display summaries in DataFrame format
        st.subheader('DataFrame format')
        st.dataframe(df)

         # Add a reset button
        if st.button("Start Over"):
            # Reset session state variables
            st.session_state.page = 1
            st.session_state.api_key = None
            st.session_state.playlist_url = None
            st.session_state.topic = None
            st.session_state.use_custom_prompt = None
            st.session_state.custom_prompt = None
            st.rerun()
    
