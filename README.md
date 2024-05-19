# 📝 YouTube Summariser

With the YouTube Summariser app, you can quickly generate concise summaries of videos from any YouTube playlist using the OpenAI API. This tool is ideal for students, researchers, or anyone who wants to save time by summarizing video content. 

I built this app because I wanted to quickly summarise content from Machine Learning lectures on YouTube. 

You can use the app [here](https://youtubesummariser-rishane-d.streamlit.app/s). If you have any feedback, please email me at [rishanedassanayake@gmail.com](rishanedassanayake@gmail.com). I'd love to hear it!

## Overview and Features

- Enter your OpenAI API key or use a special password to use a predefined API key.
- Provide the URL of a YouTube playlist to summarize.
- Specify the topic(s) covered in the playlist.
- Option to use a default prompt or provide a custom prompt for the summaries.
- Generates and displays summaries in a DataFrame format.
- Download the summaries as a CSV file.
- Easy to reset and start over with a different playlist.

## Libraries 

To run this app, you need the following Python libraries:

- `pandas`
- `numpy`
- `pytube`
- `youtube-transcript-api`
- `openai`
- `ipython`
- `requests`
- `charset_normalizer`
- `streamlit`

You can install these libraries using pip:

```bash
pip install pandas numpy pytube youtube-transcript-api openai ipython requests charset_normalizer streamlit
```

## Setup Instructions

#### 1. Clone this repository

First, clone this repository to your local machine. 

```bash
git clone https://github.com/RishaneD/youtube_summariser.git
cd your-repo-name
```

#### 2. Create a new virtual environment

Next, create a new virtual environment.

```bash
conda create --name my_env python=3.9
```

#### 3. Install dependencies

Install the required python packages using pip.

```bash
pip install -r requirements.txt
```

#### 4. Run the app

Run the streamlit app using the following command: 

```bash
streamlit run summariser_app.py
```

## Licensing

This project is licensed under the MIT License. See the `LICENSE` file for more details.




