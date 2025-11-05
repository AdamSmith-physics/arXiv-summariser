import arxiv

client = arxiv.Client()
search = arxiv.Search(
  query = "cat:quant-ph",
  max_results = 10, # Get a larger batch to be safe
  sort_by = arxiv.SortCriterion.LastUpdatedDate, # Use SubmittedDate
  sort_order = arxiv.SortOrder.Descending
)

try:
    for result in client.results(search):

        submission_time = result.updated

        print(f"Title: {result.title}")
        print(f"Authors: {[author.name for author in result.authors]}")
        print(f"Published: {result.published}")
        print(f"Updated: {result.updated}")
        print(f"URL: {result.entry_id}")
        print(f"Arxiv ID: {result.get_short_id()}")
        print(f"Summary: {result.summary}")
        print("-" * 40)

        # downlad the PDF
        pdf_path = result.download_pdf(filename = f"downloads/{result.get_short_id()}.pdf")
        print(f"Downloaded PDF to: {pdf_path}\n")


except Exception as e:
    print(f"An unexpected error occurred: {e}")

