#!/usr/bin/python
__author__ = 'Jonfor'

import csv
import requests
import xml.etree.ElementTree as eleTree
import time
import logging
from collections import namedtuple
from multiprocessing import Queue, Pool, Process, Event, cpu_count

fields = ("title", "video_id")
PROCESSES = cpu_count() - 1  # Leave one for the writer process
CHANNEL_NAME = "Ethoslab"


class ChannelRecord(namedtuple('ChannelRecord_', fields)):

    @classmethod
    def parse(cls, row):
        row = list(row)  # Make row mutable
        return cls(*row)

    def __str__(self):
        return "%s with video id %s" % (self.title, self.video_id)


def read_channel_data(path):
    with open(path, 'rU') as data:
        data.readline()            # Skip the header
        reader = csv.reader(data, delimiter='|')  # Create a regular tuple reader
        for row in map(ChannelRecord.parse, reader):
            yield row


def get_data(url):
    time.sleep(0.1)  # Too fast for the Google
    response = requests.get(url)
    if response.status_code == 200:
        logging.info("Received response, inserting into queue")
        response_queue.put(response)
    elif response.status_code >= 400:
        logging.warning("Got status code {0} when hitting {1}".format(response.status_code, url))


def comment_search(response_queue, url_finish_event):

    while not url_finish_event.is_set():
        while not response_queue.empty():
            logging.info("Waiting for responses")
            response = response_queue.get()
            logging.info("Dequeued a response")
            comments_csv = '%s_comments.csv' % CHANNEL_NAME
            with open(comments_csv, 'wb') as csvfile:
                writer = csv.writer(csvfile, delimiter="|")
                writer.writerow(['author', 'comment'])

                root = eleTree.fromstring(response.text.encode('utf-8'))
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


if __name__ == "__main__":
    VIDEOS = CHANNEL_NAME + ".csv"  # This CSV contains the video IDs
    response_queue = Queue()

    urls = []
    for row in read_channel_data(VIDEOS):
        url = "https://gdata.youtube.com/feeds/api/videos/%s/comments?orderby=published" % row[1]
        urls.append(url)

    url_finish_event = Event()
    write_process = Process(target=comment_search, args=(response_queue, url_finish_event))
    write_process.start()

    pool = Pool(processes=PROCESSES)
    pool.map(get_data, urls)
    pool.close()
    pool.join()
    url_finish_event.set()

    write_process.join()
    logging.info("Set the event flag, finished program.")
