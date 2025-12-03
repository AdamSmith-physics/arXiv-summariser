from ollama import chat
from ollama import ChatResponse

from .constants import PROMPT_INDIVIDUAL, SYSTEM_PROMPT_INDIVIDUAL, PROMPT_COMBINED, SYSTEM_PROMPT_COMBINED

def rank_papers_individual(arxiv_results, settings):

    authors = settings['Authors']
    topics = settings['Topics']
    model = settings['Model']

    relevant_results = []
    paper_scores = []
    system_instructions = SYSTEM_PROMPT_INDIVIDUAL

    for result in arxiv_results:

        print(f"Title: {result.title}")
        print(f"Authors: {[author.name for author in result.authors]}")
        print(f"Arxiv ID: {result.get_short_id()}")

        prompt = f"""
        Paper Title: {result.title}
        Paper Authors: {', '.join([author.name for author in result.authors])}
        Paper Abstract: {result.summary}

        ---------
        
        My research Interests: {', '.join(topics)}
        Authors I follow: {', '.join(authors)}

        ----------

        """

        prompt += PROMPT_INDIVIDUAL

        response: ChatResponse = chat(
            model=model, 
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

    print(f"Found {len(relevant_results)} relevant papers out of {len(arxiv_results)} new papers.") 

    return relevant_results, paper_scores


def rank_papers_combined(relevant_results, settings, max_attempts=3):

    authors = settings['Authors']
    topics = settings['Topics']
    model = settings['Model']

    system_instructions = SYSTEM_PROMPT_COMBINED


    combined_meassages = ""
    # loop over enumerate relevant_results
    for idx, result in enumerate(relevant_results):

        combined_meassages += f"{idx}: Title: {result.title}\n"
        combined_meassages += f"   Authors: {[author.name for author in result.authors]}\n"
        combined_meassages += f"   Arxiv ID: {result.get_short_id()}\n"
        combined_meassages += f"   Summary: {result.summary}\n"
        combined_meassages += "-" * 40 + "\n\n"

    prompt = f"""{combined_meassages}
    
    ---------
    
    My research Interests: {', '.join(topics)}
    Authors I follow: {', '.join(authors)}

    ----------

    """

    prompt += PROMPT_COMBINED

    for attempt in range(max_attempts):
        try:
            response: ChatResponse = chat(model=model,
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

            # check that we have all indices
            if set(ranked_indices) != set(range(len(relevant_results))):
                raise Exception(f"Ranked indices do not match expected indices. Got: {ranked_indices}")
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < max_attempts - 1:
                print("Retrying...")
            else:
                print("Max attempts reached. Could not get top 10 ordering. Defaulting to individual rankings.")
                return relevant_results 

    # Reorder relevant_results based on ranked_indices
    ordered_relevant_results = [relevant_results[i] for i in ranked_indices]

    return ordered_relevant_results