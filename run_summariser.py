from source.email_functions import EmailClient
from source.arxiv_functions import arxiv_search
from source.ollama_functions import rank_papers_individual, rank_papers_combined

import json
import os

# Set working directory to the script's directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

user_settings_path = "settings/user_settings"  # where the user settings json files are stored

email_client = EmailClient()  # Initialize email client

for filename in os.listdir(user_settings_path):

    if filename.endswith(".json"):
        with open(user_settings_path + "/" + filename, 'r') as f:
            settings = json.load(f)

    user_name = settings["Name"]
    receiver_email = settings["Email"]
    categories = settings['Categories']
    authors = settings['Authors']
    topics = settings['Topics']

    print("\n\n" + "=" * 80)
    print(f"Running summariser for {user_name} ({receiver_email})")
    print("=" * 80 + "\n")

    # load previous IDs from text file. They are stored as a list
    if not os.path.exists("previous_ids.dno"):
        previous_ids = []
    else:
        with open("previous_ids.dno", 'r') as f:
            previous_ids = f.read().splitlines()


    #####################################
    ## Main Code

    arxiv_results = arxiv_search(categories, previous_ids, max_results=20, max_attempts=3)

    # Rank papers using Ollama
    relevant_results, paper_scores = rank_papers_individual(arxiv_results, settings)

    # Look at the top 10 relevant results and re-rank them by comparison
    num_relevant = len(relevant_results)
    top_num = min(10, num_relevant)

    ordered_relevant_results = rank_papers_combined(relevant_results[:top_num], settings) 

    relevant_results[:top_num] = ordered_relevant_results

    #####################################


    # Print the titles of the top 3 ranked papers
    for rank in range(3):
        paper = ordered_relevant_results[rank]
        print(f"Rank {rank + 1}: {paper.title} (ArXiv ID: {paper.get_short_id()})")

    # Write the email content
    message = email_client.write_email_content(ordered_relevant_results, receiver_email)

    # Send the email
    email_client.send_email(receiver_email, message)

    # Add new IDs to top of previous_ids file keeping up to 1000 entries
    # with open("previous_ids.dno", 'w') as f:
    #     new_ids = [result.get_short_id() for result in arxiv_results]
    #     all_ids = new_ids + previous_ids
    #     all_ids = all_ids[:1000]  # Keep only the latest 1000 IDs
    #     f.write("\n".join(all_ids))