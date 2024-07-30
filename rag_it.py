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
collection_name = data.get("collection_name")

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
    tags = ", ".join([t['term'] for t in entry.tags])
    # in documents, follow the title by line feed and summary
    documents.append(f'# {title} \n {content} \n Tags: {tags}')
    metadatas.append({"title": title, "link": link, "tags": tags})
    # here links are the unique identifier
    ids.append(link)


# Currently the context window is increasing day by day with the language
# models, however this approach is not optimized, hence loads of resources
# would be used up, which will lead to increase in cost.
# Hence using a vector database is about optimization and especially
# with local, which may use local llm which is having less context window


# create the chroma db using client
# this is not using persistent [creation in local system]
client = chromadb.Client()

collection = client.get_or_create_collection(name = collection_name)

collection.add(
    documents = documents,
    metadatas = metadatas,
    ids = ids
)

prompt = "List top 3 most interesting AI related news with summaries and reference link"

query_result = collection.query(
                                # conext to find similar documents
                                query_texts = [prompt]
)
context_result = query_result['documents'][0]

stream = ollama.chat(
    model='phi3',
    messages=[
        {
            "role": "system",
            "content": f"Answer the questions based on the news feed given here only. If you do not know the answer, say I do not know. The news feed content is here:\n\n------------------------------------------------\n\n{context_result}\n\n------------------------------------------------\n\n"
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    stream=True
)

for chunk in stream:
    print(chunk['message']['content'], end='')

# response = ollama.chat(
#     model='phi3',
#     messages=[
#         {
#             "role": "system",
#             "content": f"Answer the questions based on the news feed given here only. If you do not know the answer, say I do not know. The news feed content is here:\n\n------------------------------------------------\n\n{context_result}\n\n------------------------------------------------\n\n"
#         },
#         {
#             "role": "user",
#             "content": prompt
#         }
#     ]
# )

# print(response['message']['content'])