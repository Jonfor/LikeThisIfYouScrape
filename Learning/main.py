from __future__ import print_function

try:
    import unicodecsv as csv
except ImportError:
    import warnings

    warnings.warn("can't import `unicodecsv` encoding errors may occur")
    import csv
from collections import namedtuple
import sys
import os

fields = ("video_id", "author", "comment")
CHANNEL_NAME = "jblow888"


# See https://districtdatalabs.silvrback.com/simple-csv-data-wrangling-with-python
class CommentRecord(namedtuple('CommentRecord_', fields)):
    @classmethod
    def parse(cls, row):
        row = list(row)  # Make row mutable
        return cls(*row)

    def __str__(self):
        return "{1} with comment {2}".format(self.author, self.comment)


def read_comment_data(path):
    with open(path, 'rU') as data:
        data.readline()  # Skip the header
        reader = csv.reader(data, delimiter='|')  # Create a regular tuple reader
        for row in map(CommentRecord.parse, reader):
            yield row


if __name__ == "__main__":
    COMMENTS_CSV = os.path.realpath(CHANNEL_NAME + "_comments.csv")
    CHANNEL_RELEVANT = CHANNEL_NAME + "_rel.csv"
    CHANNEL_NOT_RELEVANT = CHANNEL_NAME + "_not_rel.txt"

    with open(CHANNEL_RELEVANT, 'wb') as rel_file:
        writer = csv.writer(rel_file, delimiter="|")
        writer.writerow(['video_id', 'author', 'comment', 'helpfulness', 'length_of_text'])
        lens = []
        counter = 0
        for row in read_comment_data(COMMENTS_CSV):
            author = row[1].encode('utf-8', 'ignore')
            comment = row[2].encode('utf-8', 'ignore')
            print("\n\n")
            print("Curr video: {0}\ncomment: {1}".format(row[0], comment))
            print("\n\n")

            if author == "author" and comment == "comment":
                print("^^^^^Skipping this one!^^^^^\n")
                continue

            try:
                rel = int(raw_input("1=rel 2=not rel -1=STAHP"))
                lens.insert(counter, len(row[2]))
                counter += 1
                if rel != -1:
                    writer.writerow([row[0], row[1], row[2], rel, len(row[2])])
                elif rel == -1:
                    print("So long and thanks for all the fish!\n")
                    break
                else:
                    print("Please enter only 1 or 2", file=sys.stderr)
            except ValueError:
                print("Please enter only 1 or 2.", file=sys.stderr)
