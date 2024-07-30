import ollama
import chromadb
import feedparser
import json

# Specify the path to your JSON file
file_path = "input_variables.json"

# Open the file in read mode
with open(file_path, "r") as file:
    data = json.load(file)

# Access the variables from the loaded data
rss_feed = data.get("rss_feed")

# read the feed

feed = feedparser.parse(url_file_stream_or_string = rss_feed)

# get the list of entries
entries = feed.entries

documents = []
metadatas = []
ids = []

for entry in entries:
    # title
    title = entry.title
    link = entry.link
    content = entry.summary
    # grab the "terms" in each of the tags and join them
    tags = ", ".join([t['terms'] for t in entry.tags])
    # in documents, follow the title by line feed and summary
    documents.append(f'# {title} \n {content} \n Tags: {tags}')
