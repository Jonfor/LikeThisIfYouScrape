#!/usr/bin/python
__author__ = 'Jonfor'

import requests
from googleapiclient.discovery import build
import json
import os

DEVELOPER_KEY = "AIzaSyBKRXzSQsPZV65rBagqGYNuMnAHF6uuxxA"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
FREEBASE_SEARCH_URL = "https://www.googleapis.com/freebase/v1/search?%s"


def youtube_search():
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    channels_response = youtube.channels().list(part="contentDetails", forUsername="EthosLab").execute()

    for channel in channels_response["items"]:
        uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]

        print "Videos in list %s" % uploads_list_id

        next_page_token = ""
        file = open('workfile', 'w')
        while next_page_token is not None:
            play_list_items_response = youtube.playlistItems().list(playlistId=uploads_list_id, part="snippet",
                                                                    maxResults=50, pageToken=next_page_token).execute()
            json.dump(play_list_items_response, file)
            file.flush()
            os.fsync(file.fileno())

        for playlist_item in play_list_items_response["items"]:
            title = playlist_item["snippet"]["title"]
            video_id = playlist_item["snippet"]["resourceId"]["videoId"]
            print "%s (%s)" % (title, video_id)

        next_page_token = play_list_items_response.get("tokenPagination", {}).get("nextPageToken")

        print next_page_token

if __name__ == "__main__":

    youtube_search()
