#!/usr/bin/python
__author__ = 'Jonfor'

import csv
import os.path
import sys

from googleapiclient.discovery import build

if not os.path.isfile("api_key"):
    print("Error: Please have your YouTube API key in a file named 'api_key'.", file=sys.stderr)
    exit(1)
with open("api_key") as api_key_file:
    DEVELOPER_KEY = api_key_file.read()
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
FREEBASE_SEARCH_URL = "https://www.googleapis.com/freebase/v1/search?%s"
CHANNEL_NAME = "jblow888"


def channel_search():
    """
    Get all the videos for a channel, given in CHANNEL_NAME, and write their titles and video IDs to a csv.
    """
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    channels_response = youtube.channels().list(part="contentDetails", forUsername=CHANNEL_NAME).execute()

    for channel in channels_response["items"]:
        uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]

        print("Videos in list %s" % uploads_list_id)

        playlistitems_list_request = youtube.playlistItems().list(playlistId=uploads_list_id, part="snippet",
                                                                  maxResults=50)

        channel_csv = '%s.csv' % CHANNEL_NAME
        with open(channel_csv, 'wt') as csvfile:
            writer = csv.writer(csvfile, delimiter="|")
            writer.writerow(['title', 'video_id'])
            # Gets 50 videos at a time; keep making requests until we get all of the videos.
            while playlistitems_list_request:
                playlistitems_list_response = playlistitems_list_request.execute()
                playlistitems_list_request = youtube.playlistItems().list_next(
                    playlistitems_list_request, playlistitems_list_response)
                print(playlistitems_list_response["items"])

                # Save to CSV file
                for playlist_item in playlistitems_list_response["items"]:
                    title = playlist_item["snippet"]["title"]
                    video_id = playlist_item["snippet"]["resourceId"]["videoId"]
                    writer.writerow([title, video_id])


if __name__ == "__main__":
    channel_search()
    print("Successfully finished outputting data to %s.csv." % CHANNEL_NAME)
