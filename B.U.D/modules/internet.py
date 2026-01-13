from duckduckgo_search import DDGS

def search_web(query):
    """
    Searches the web and returns a summary of the top result.
    """
    print(f">> EXECUTING: SEARCHING FOR '{query}'")
    try:
        results = DDGS().text(query, max_results=1)
        if results:
            # We get a list of dicts. We just want the first 'body' (summary).
            first_result = results[0]
            summary = first_result.get('body', 'No summary available.')
            return summary
        else:
            return "I couldn't find any information on the web."
    except Exception as e:
        print(f"Search Error: {e}")
        return "I encountered an error while trying to access the internet."