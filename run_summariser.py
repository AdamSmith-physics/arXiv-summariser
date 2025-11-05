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

        prompt = f"""Tell me if the following arXiv paper abstract is relevant to my research interests or to any of the authors I follow. Please answer with a simple 'Yes' or 'No'.
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
                'num_ctx': 2*10,  # Sets the context window to 32768 tokens
        })
        # ,think="low")

        stripped_response = response.message.content.strip().strip(".").lower()

        print(f"Relevance for {result.get_short_id()}: \n{stripped_response}\n")
        print("=" * 80)

        if 'yes' in stripped_response:
            relevant_results.append(result)


except Exception as e:
    print(f"An unexpected error occurred: {e}")


for relevant_result in relevant_results:
    



# Add new IDs to top of previous_ids file keeping up to 1000 entries
with open("previous_ids.dno", 'w') as f:
    new_ids = [result.get_short_id() for result in result_list]
    all_ids = new_ids + previous_ids
    all_ids = all_ids[:1000]  # Keep only the latest 1000 IDs
    f.write("\n".join(all_ids))