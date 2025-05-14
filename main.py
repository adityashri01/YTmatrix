import os
import pickle
import re
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

def authenticate_youtube():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build("youtube", "v3", credentials=creds)

youtube = authenticate_youtube()

def extract_playlist_id(url):
    match = re.search(r"(?:list=)([a-zA-Z0-9_-]+)", url)
    return match.group(1) if match else None

def convert_duration_to_time_format(duration):
    # YouTube duration format: PT#H#M#S
    regex = r"PT(\d+H)?(\d+M)?(\d+S)?"
    match = re.match(regex, duration)
    hours = minutes = seconds = 0

    if match:
        hours = int(match.group(1)[:-1]) if match.group(1) else 0
        minutes = int(match.group(2)[:-1]) if match.group(2) else 0
        seconds = int(match.group(3)[:-1]) if match.group(3) else 0

    # Format into hh:mm:ss
    formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}"
    total_hours = hours + (minutes / 60) + (seconds / 3600)
    return formatted_duration, total_hours

def fetch_playlist_videos(playlist_input, sort_by="None", max_videos=None, max_duration=None):
    try:
        playlist_id = extract_playlist_id(playlist_input) or playlist_input
        videos = []
        nextPageToken = None

        while True:
            request = youtube.playlistItems().list(
                playlistId=playlist_id,
                part="snippet",
                maxResults=50,
                pageToken=nextPageToken
            )
            response = request.execute()
            for item in response["items"]:
                title = item["snippet"]["title"]
                video_id = item["snippet"]["resourceId"]["videoId"]
                published_at = item["snippet"]["publishedAt"]

                video_details_request = youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id=video_id
                )
                video_details_response = video_details_request.execute()
                duration = video_details_response["items"][0]["contentDetails"]["duration"]
                view_count = video_details_response["items"][0]["statistics"]["viewCount"]  # Fetch view count
                duration_formatted, duration_hours = convert_duration_to_time_format(duration)
                
                if max_duration and duration_hours > max_duration:
                    continue  # Skip this video if it's longer than the max_duration specified

                published_at_datetime = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
                published_date = published_at_datetime.strftime("%b %d, %Y %I:%M %p")

                videos.append({
                    "title": title,
                    "published": published_date,
                    "duration": duration_formatted,
                    "raw_duration": duration_hours,
                    "view_count": view_count,  # Add view count to the video data
                    "published_datetime": published_at_datetime
                })

                if max_videos and len(videos) >= max_videos:
                    break

            if "nextPageToken" not in response or (max_videos and len(videos) >= max_videos):
                break
            nextPageToken = response["nextPageToken"]

        if sort_by == "Duration":
            videos.sort(key=lambda x: x["raw_duration"])
        elif sort_by == "Published Date":
            videos.sort(key=lambda x: x["published_datetime"])

        return videos
    except Exception as e:
        print(f"❌ Error fetching playlist videos: {e}")
        return []


def fetch_video_details(video_url):
    try:
        match = re.search(r"v=([a-zA-Z0-9_-]+)", video_url)
        if not match:
            print("❌ Invalid video URL format.")
            return None
        video_id = match.group(1)
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",  # Include statistics part for view count
            id=video_id
        )
        response = request.execute()
        items = response.get("items", [])
        if not items:
            print("⚠ No video found.")
            return None
        snippet = items[0]["snippet"]
        title = snippet["title"]
        published_at = snippet["publishedAt"]
        duration = items[0]["contentDetails"]["duration"]
        view_count = items[0]["statistics"]["viewCount"]  # Fetch view count
        duration_formatted, duration_hours = convert_duration_to_time_format(duration)

        published_at_datetime = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
        published_date = published_at_datetime.strftime("%b %d, %Y %I:%M %p")

        return [{
            "title": title,
            "published": published_date,
            "duration": duration_formatted,
            "raw_duration": duration_hours,
            "view_count": view_count,  # Add view count to the video data
            "published_datetime": published_at_datetime
        }]
    except Exception as e:
        print(f"❌ Error fetching video details: {e}")
        return None
