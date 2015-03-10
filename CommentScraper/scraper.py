#!/usr/bin/python
__author__ = 'Jonfor'


from googleapiclient.discovery import build
# from apiclient.discovery import build
import csv
import requests
import xml.etree.ElementTree as ET

DEVELOPER_KEY = "AIzaSyBKRXzSQsPZV65rBagqGYNuMnAHF6uuxxA"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
FREEBASE_SEARCH_URL = "https://www.googleapis.com/freebase/v1/search?%s"


def channel_search(channel):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    channels_response = youtube.channels().list(part="contentDetails", forUsername=channel).execute()

    for channel in channels_response["items"]:
        uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]

        print("Videos in list %s" % uploads_list_id)

        playlistitems_list_request = youtube.playlistItems().list(playlistId=uploads_list_id, part="snippet", maxResults=50)

        # channel_csv = '%s.csv' % channel
        # with open(channel_csv, 'wb') as csvfile:
        #     writer = csv.writer(csvfile)
        #     writer.writerow(['title', 'video_id'])
        comments_csv = '%s_comments.csv' % channel
        with open(comments_csv, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter="|")
            writer.writerow(['author', 'comment'])
            while playlistitems_list_request:
                playlistitems_list_response = playlistitems_list_request.execute()
                playlistitems_list_request = youtube.playlistItems().list_next(
                    playlistitems_list_request, playlistitems_list_response)
                print(playlistitems_list_response["items"])

                # Save to CSV file
                for playlist_item in playlistitems_list_response["items"]:
                    title = playlist_item["snippet"]["title"]
                    video_id = playlist_item["snippet"]["resourceId"]["videoId"]
                    url = "https://gdata.youtube.com/feeds/api/videos/%s/comments?orderby=published" % video_id
                    response = requests.get(url)
                    if response.status_code == 200:
                        root = ET.fromstring(response.text.encode('utf-8'))
                        comments = root.findall('{http://www.w3.org/2005/Atom}entry')

                        for comment in comments:
                            author = comment.find('{http://www.w3.org/2005/Atom}author').find('{http://www.w3.org/2005/Atom}name').text
                            content = comment.find('{http://www.w3.org/2005/Atom}content').text
                            # Apparently people like leaving blank comments and breaking my scraper
                            if author is None or content is None:
                                continue
                            else:
                                author = author.encode('utf-8')
                                content = content.encode('utf-8')

                            writer.writerow([author, content])
            #     writer.writerow([title, video_id])


if __name__ == "__main__":
    CHANNEL = "Ethoslab"

    channel_search(CHANNEL)