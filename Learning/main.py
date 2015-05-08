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
CHANNEL_NAME = "sethbling"


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
    CHANNEL_RELEVANT = CHANNEL_NAME + "_rel.txt"
    CHANNEL_NOT_RELEVANT = CHANNEL_NAME + "_not_rel.txt"

    print("Please enter 1 for relevant and 2 for not relevant\n")
    with open(CHANNEL_RELEVANT, 'wb') as rel_file:
        with open(CHANNEL_NOT_RELEVANT, 'wb') as not_rel_file:
            for row in read_comment_data(COMMENTS_CSV):

                id = row[0].encode('utf-8', 'ignore')
                first = row[1].encode('utf-8', 'ignore')
                comment = row[2].encode('utf-8', 'ignore')
                if first == "author" and comment == "comment":
                    print("^^^^^Skipping this one!^^^^^\n")
                    continue

                print("Video id is {0}\ncomment: {1}".format(id, comment))
                try:
                    rel = int(raw_input("1=rel 2=not rel -1=STAHP"))
                    if rel == 1:
                        print(comment, file=rel_file)
                    elif rel == 2:
                        print(comment, file=not_rel_file)
                    elif rel == -1:
                        print("So long and thanks for all the fish!\n")
                        break
                    else:
                        print("Please enter only 1 or 2", file=sys.stderr)
                except ValueError:
                    print("Please enter only 1 or 2.", file=sys.stderr)