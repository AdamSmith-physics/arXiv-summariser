from source.email_functions import EmailClient
from source.arxiv_functions import arxiv_search
from source.ollama_functions import rank_papers_individual, rank_papers_combined

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import json

from ollama import chat
from ollama import ChatResponse

import datetime
import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

email_client = EmailClient()

receiver_email = "adam.gammon-smith@nottingham.ac.uk"

with open("settings.json", 'r') as f:
    settings = json.load(f)

categories = settings['Categories']
authors = settings['Authors']
topics = settings['Topics']

# load previous IDs from text file. They are stored as a list
with open("previous_ids.dno", 'r') as f:
    previous_ids = f.read().splitlines()

arxiv_results = arxiv_search(categories, previous_ids, max_results=100, max_attempts=3)

# Rank papers using Ollama
relevant_results, paper_scores = rank_papers_individual(arxiv_results, settings)

ordered_relevant_results = rank_papers_combined(relevant_results, settings) 

# Print the titles of the top 3 ranked papers
for rank in range(3):
    paper = ordered_relevant_results[rank]
    print(f"Rank {rank + 1}: {paper.title} (ArXiv ID: {paper.get_short_id()})")


# Write the email content
message = email_client.write_email_content(ordered_relevant_results, receiver_email)

# Send the email
email_client.send_email(receiver_email, message)

# # Add new IDs to top of previous_ids file keeping up to 1000 entries
# with open("previous_ids.dno", 'w') as f:
#     new_ids = [result.get_short_id() for result in result_list]
#     all_ids = new_ids + previous_ids
#     all_ids = all_ids[:1000]  # Keep only the latest 1000 IDs
#     f.write("\n".join(all_ids))