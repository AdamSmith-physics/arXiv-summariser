import json
import arxiv
from ollama import chat
from ollama import ChatResponse

with open("settings.json", 'r') as f:
    settings = json.load(f)

categories = settings['Categories']
authors = settings['Authors']
topics = settings['Topics']

# load previous IDs from text file. They are stored as a list
with open("previous_ids.dno", 'r') as f:
    previous_ids = f.read().splitlines()

print(previous_ids)

client = arxiv.Client()
search = arxiv.Search(
  query = " AND ".join(categories),
  max_results = 10, # Get a larger batch to be safe
  sort_by = arxiv.SortCriterion.LastUpdatedDate, # Use SubmittedDate
  sort_order = arxiv.SortOrder.Descending
)

result_list = []
relevant_results = []

try:
    for result in client.results(search):

        arxiv_id = result.get_short_id()

        if arxiv_id not in previous_ids:
            result_list.append(result)
        else:
            print(f"Skipping previously processed paper: {arxiv_id}")
            print("-" * 40)
            continue

        print(f"Title: {result.title}")
        print(f"Authors: {[author.name for author in result.authors]}")
        print(f"Arxiv ID: {result.get_short_id()}")
        # print("-" * 40)

        prompt = f"""Tell me if the following arXiv paper abstract is relevant to my research interests or to any of the authors I follow. Please answer with a simple 'Yes' or 'No'. Do not provide any additional explanation.
        Research Interests: {', '.join(topics)}
        Authors I follow: {', '.join(authors)}

        Paper Title: {result.title}
        Paper Authors: {', '.join([author.name for author in result.authors])}
        Paper Abstract: {result.summary}
        """

        response: ChatResponse = chat(model='gemma3:27b', 
        messages=[
            {
            'role': 'user',
            'content': prompt,
            },
        ],
        options={
                'num_ctx': 2**10,  # Sets the context window to 1024 tokens
        })
        # ,think="low")

        stripped_response = response.message.content.strip().strip(".").lower()

        print(f"Relevance for {result.get_short_id()}: \n{stripped_response}\n")
        print("=" * 80)

        if 'yes' in stripped_response:
            relevant_results.append(result)


except Exception as e:
    print(f"An unexpected error occurred: {e}")

print(f"Found {len(relevant_results)} relevant papers out of {len(result_list)} new papers.")

combined_meassages = ""
# loop over enumerate relevant_results
for idx, result in enumerate(relevant_results):

    combined_meassages += f"{idx}: Title: {result.title}\n"
    combined_meassages += f"   Authors: {[author.name for author in result.authors]}\n"
    combined_meassages += f"   Arxiv ID: {result.get_short_id()}\n"
    combined_meassages += f"   Summary: {result.summary}\n"
    combined_meassages += "-" * 40 + "\n\n"

prompt = f"""Please rank the following arXiv papers in order of relevance to my research interests and the authors I follow. My research interests are: {', '.join(topics)}. The authors I follow are: {', '.join(authors)}. Provide the ranking as an ordered list of the indices corresponding to the paper, starting with the most relevant. Your response should be a simple comma-separated list of indices without any additional text. That is your answer should be something like "0, 3, 2, 1, 4" with no additional text!
\n\n{combined_meassages}"""

response: ChatResponse = chat(model='gemma3:27b',
messages=[
    {
    'role': 'user',
    'content': prompt,
    },
],
options={
        'num_ctx': 2**14,  # Sets the context window
})

ranked_indices_str = response.message.content.strip()
ranked_indices = [int(idx.strip()) for idx in ranked_indices_str.split(",")]    

# Print the titles of the top 3 ranked papers
for rank in range(min(3, len(ranked_indices))):
    paper_index = ranked_indices[rank]
    paper = relevant_results[paper_index]
    print(f"Rank {rank + 1}: {paper.title} (ArXiv ID: {paper.get_short_id()})")








stop



# Add new IDs to top of previous_ids file keeping up to 1000 entries
with open("previous_ids.dno", 'w') as f:
    new_ids = [result.get_short_id() for result in result_list]
    all_ids = new_ids + previous_ids
    all_ids = all_ids[:1000]  # Keep only the latest 1000 IDs
    f.write("\n".join(all_ids))