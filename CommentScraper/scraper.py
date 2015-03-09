#!/usr/bin/python
__author__ = 'Jonfor'


from googleapiclient.discovery import build
# from apiclient.discovery import build
import csv

DEVELOPER_KEY = "AIzaSyBKRXzSQsPZV65rBagqGYNuMnAHF6uuxxA"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
FREEBASE_SEARCH_URL = "https://www.googleapis.com/freebase/v1/search?%s"


def youtube_search():
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    channels_response = youtube.channels().list(part="contentDetails", forUsername="EthosLab").execute()

    for channel in channels_response["items"]:
        uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]

        print("Videos in list %s" % uploads_list_id)

        playlistitems_list_request = youtube.playlistItems().list(playlistId=uploads_list_id, part="snippet", maxResults=50)

        with open('etho.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['title', 'video_id'])

            while playlistitems_list_request:
                playlistitems_list_response = playlistitems_list_request.execute()
                playlistitems_list_request = youtube.playlistItems().list_next(
                    playlistitems_list_request, playlistitems_list_response)
                print(playlistitems_list_response["items"])

                # Print information about each video.
                for playlist_item in playlistitems_list_response["items"]:
                    title = playlist_item["snippet"]["title"]
                    video_id = playlist_item["snippet"]["resourceId"]["videoId"]
                    writer.writerow([title, video_id])


if __name__ == "__main__":

    youtube_search()
