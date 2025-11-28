from ollama import chat
from ollama import ChatResponse

def rank_papers_individual(arxiv_results, settings):

    categories = settings['Categories']
    authors = settings['Authors']
    topics = settings['Topics']

    result_list = []
    relevant_results = []
    paper_scores = []
    system_instructions = """
    You are an expert research assistant specialised in academic literature review.
    Your task is to evaluate the relevance of academic papers based on their titles, authors, and abstracts.
    When I provide you with the details you should respond with a relevance score out of 100, where a higher score indicates greater relevance to my research interests and the authors I follow. 
    I will consider any score below 50 as not relevant. 
    Please answer with just the score, no additional text.
    """

    for result in arxiv_results:

        arxiv_id = result.get_short_id()

        print(f"Title: {result.title}")
        print(f"Authors: {[author.name for author in result.authors]}")
        print(f"Arxiv ID: {result.get_short_id()}")
        # print("-" * 40)

        prompt = f"""
        Paper Title: {result.title}
        Paper Authors: {', '.join([author.name for author in result.authors])}
        Paper Abstract: {result.summary}


        Tell me if the above arXiv paper abstract is relevant to my research interests or to any of the authors I follow. 
        Research Interests: {', '.join(topics)}
        Authors I follow: {', '.join(authors)}
        """

        # prompt += """
        
        # Please answer with a simple 'Yes' or 'No'. Do not provide any additional explanation.
        # """

        # Change to using scores to give an initial ranking.
        prompt += """
        Please score the paper out of 100 for relevance. I will consider any score below 50 as not relevant. Please answer with just the score, no additional text."""  

        response: ChatResponse = chat(
            model='gemma3:27b', 
            messages=[
                {
                'role': 'system',
                'content': system_instructions,
                },
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

        try:
            relevance_score = int(stripped_response)
        except ValueError:
            # I would like to implement having a retry mechanism here, but for now just raise an exception
            raise Exception(f"Could not parse relevance score from response: {stripped_response}")

        if relevance_score >= 50:
            relevant_results.append(result)
            paper_scores.append(relevance_score)

    # sort relevant_results based on paper_order scores. Do this by first getting the indices that would sort paper_order
    sorted_indices = sorted(range(len(paper_scores)), key=lambda k: paper_scores[k], reverse=True)
    paper_scores = [paper_scores[i] for i in sorted_indices]
    relevant_results = [relevant_results[i] for i in sorted_indices]

    # Check the ordering
    print("Ordered relevance scores of relevant papers:")
    for i, result in enumerate(relevant_results):
        print(f"{paper_scores[i]} : {result.title}")

    print(f"Found {len(relevant_results)} relevant papers out of {len(result_list)} new papers.") 

    return relevant_results, paper_scores


def rank_papers_combined(relevant_results, settings):

    authors = settings['Authors']
    topics = settings['Topics']

    system_instructions = """
    You are an expert research assistant specialised in academic literature review.
    Your task is to evaluate the relevance of academic papers based on their titles, authors, and abstracts.
    When I provide you with the details you should respond with an ordering based on the relevance to my research interests and the authors I follow. 
    Provide the ranking as an ordered list of the indices corresponding to the paper, starting with the most relevant. 
    Your response should be a simple comma-separated list of indices without any additional text. 
    That is your answer should be something like "0, 3, 2, 1, 4" with no additional text!
    """


    combined_meassages = ""
    # loop over enumerate relevant_results
    for idx, result in enumerate(relevant_results):

        combined_meassages += f"{idx}: Title: {result.title}\n"
        combined_meassages += f"   Authors: {[author.name for author in result.authors]}\n"
        combined_meassages += f"   Arxiv ID: {result.get_short_id()}\n"
        combined_meassages += f"   Summary: {result.summary}\n"
        combined_meassages += "-" * 40 + "\n\n"

    prompt = f"""{combined_meassages}\n\nPlease rank the above arXiv papers in order of relevance to my research interests and the authors I follow. My research interests are: {', '.join(topics)}. The authors I follow are: {', '.join(authors)}. Provide the ranking as an ordered list of the indices corresponding to the paper, starting with the most relevant. Your response should be a simple comma-separated list of indices without any additional text. That is your answer should be something like "0, 3, 2, 1, 4" with no additional text!"""

    response: ChatResponse = chat(model='gemma3:27b',
    messages=[
        {
        'role': 'system',
        'content': system_instructions,
        },
        {
        'role': 'user',
        'content': prompt,
        },
    ],
    options={
            'num_ctx': 2**15,  # Sets the context window
    })

    ranked_indices_str = response.message.content.strip()
    ranked_indices = [int(idx.strip()) for idx in ranked_indices_str.split(",")]

    # Reorder relevant_results based on ranked_indices
    ordered_relevant_results = [relevant_results[i] for i in ranked_indices]

    return ordered_relevant_results