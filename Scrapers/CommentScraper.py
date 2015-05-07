#!/usr/bin/python
__author__ = 'Jonfor'

try:
    import unicodecsv as csv
except ImportError:
    import warnings

    warnings.warn("can't import `unicodecsv` encoding errors may occur")
    import csv
import xml.etree.ElementTree as eleTree
import time
import logging
from collections import namedtuple
from multiprocessing import Queue, Pool, Process, Event, cpu_count

import requests


fields = ("title", "video_id")
PROCESSES = cpu_count() - 1  # Leave one for the writer process
CHANNEL_NAME = "jblow888"


# See https://districtdatalabs.silvrback.com/simple-csv-data-wrangling-with-python
class ChannelRecord(namedtuple('ChannelRecord_', fields)):
    @classmethod
    def parse(cls, row):
        row = list(row)  # Make row mutable
        return cls(*row)

    def __str__(self):
        return "%s with video id %s" % (self.title, self.video_id)


def read_channel_data(path):
    with open(path, 'rU') as data:
        data.readline()  # Skip the header
        reader = csv.reader(data, delimiter='|')  # Create a regular tuple reader
        for row in map(ChannelRecord.parse, reader):
            yield row


def get_data(url):
    """
    Scrape the given URL and enqueue the response.
    :param url: The url to scrape
    """
    time.sleep(2.5)  # Too fast for the Google
    response = requests.get(url)
    if response.status_code == 200:
        logging.info("Received response, inserting into queue")
        response_queue.put(response)
        ids_queue.put(url.split('/')[6])
    elif response.status_code >= 400:
        logging.warning("Got status code {0} with content {1}".format(response.status_code, response.content))


def comment_search(response_queue, url_finish_event, ids_queue):
    """
    While the scraping processes are going, wait for responses to be queued.
    As soon as a response is queued, retrieve the author and comment from the response
    Write the results to the comments CSV.
    Repeat until the scraping processes indicate (through url_finish_event) that all requests have finished.
    :param response_queue: The queue of responses that have been received.
    :param url_finish_event: Event that indicates the scraping processes have all finished.
    """

    comments_csv = '%s_comments.csv' % CHANNEL_NAME
    ATOM = '{http://www.w3.org/2005/Atom}'  # Some XML thing from every XML element returned by the YouTube API
    with open(comments_csv, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter="|")
        writer.writerow(['video_id', 'author', 'comment'])
        while not url_finish_event.is_set():
            while not response_queue.empty():
                logging.info("Waiting for responses")
                response = response_queue.get()
                id = ids_queue.get()
                logging.info("Dequeued a response")

                root = eleTree.fromstring(response.text.encode('utf-8'))
                comments = root.findall(ATOM + 'entry')

                for comment in comments:
                    author = comment.find(ATOM + 'author').find(ATOM + 'name').text
                    content = comment.find(ATOM + 'content').text
                    # Apparently people like leaving blank comments and breaking my scraper
                    if author is None or content is None:
                        continue
                    else:
                        author = author.encode('utf-8')
                        content = content.encode('utf-8')

                    writer.writerow([id, author, content])


if __name__ == "__main__":
    VIDEOS = CHANNEL_NAME + ".csv"  # This CSV contains the video IDs received from the ChannelScraper.
    response_queue = Queue()
    ids_queue = Queue()

    #  Create the list of URLs for the scraper processes to start working on
    urls = []
    for row in read_channel_data(VIDEOS):
        video_id = row[1]
        url = "https://gdata.youtube.com/feeds/api/videos/%s/comments?orderby=published" % video_id
        urls.append(url)

    url_finish_event = Event()
    write_process = Process(target=comment_search, args=(response_queue, url_finish_event, ids_queue))
    write_process.start()

    pool = Pool(processes=PROCESSES)
    pool.map(get_data, urls)
    pool.close()
    pool.join()
    url_finish_event.set()

    write_process.join()
    logging.info("Set the event flag, finished program.")
