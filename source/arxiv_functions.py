import arxiv

def arxiv_search(categories, previous_ids, max_results=100, max_attempts=3):
    
    client = arxiv.Client()
    search = arxiv.Search(
      query = " AND ".join(categories),
      max_results = max_results,
      sort_by = arxiv.SortCriterion.LastUpdatedDate,
      sort_order = arxiv.SortOrder.Descending
    )

    result_list = []

    for attempt in range(max_attempts):
        try:
            temp_list = []
            for result in client.results(search):
                arxiv_id = result.get_short_id()

                if arxiv_id not in previous_ids:
                    temp_list.append(result)
                else:
                    print(f"Skipping previously processed paper: {arxiv_id}")
                    continue
            
            result_list = temp_list
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < max_attempts - 1:
                print("Retrying...")
            else:
                print("Max attempts reached. Could not retrieve results.")
                raise e

    return result_list