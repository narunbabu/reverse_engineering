# test_llm.py

import asyncio
from configs.llm_config import LLMConfig
from utils.llm_client import LLMClient
print_const=160
async def test_llm():
    # llm_config = LLMConfig()
    llm_config = {
      # 'ollama':LLMConfig.get('ollama') ,      # Primary LLM configuration
    'openai':LLMConfig.get('openai') , 
    # 'anthropic':LLMConfig.get('anthropic')  # Fallback LLM configuration
    }
    print('*'*print_const)
    for key in llm_config:
      async with LLMClient(llm_config[key]) as llm_client:
          prompt = "Hey! how are you?"        
          response_text, usage = await llm_client.ask_with_retry(prompt)
          print('='*print_const)
          print(f"With {key}: Response: {response_text} Input Tokens: {usage['input_tokens']}, Output Tokens: {usage['output_tokens']}")
          print('='*print_const)
    print('*'*print_const)
if __name__ == "__main__":
    asyncio.run(test_llm())

# folder_summary = {
#   "name": ".",
#   "files": [
#     "plotting.py",
#     "postprocessing.py",
#     "load_dumps.py",
#     "paperscraper.py"
#   ],
#   "subfolders": [
#     {
#       "name": "arxiv",
#       "files": [
#         "arxiv_papers.py",
#         "query_generator.py",
#         "__init__.py"
#       ],
#       "subfolders": [],
#       "purpose": "The folder contains scripts for fetching, processing, and dumping papers from arXiv based on given queries or keywords.",
#       "main_functionality": "The 'arxiv.py' script fetches papers from arXiv, processes them to extract relevant fields, and optionally dumps the data into a CSV file. The 'utils.py' script generates search query strings from a list of keywords. The '__init__.py' script imports functionalities from the arxiv module.",
#       "functions": [
#         {
#           "name": "get_arxiv_papers",
#           "description": "Fetches papers from arXiv based on a given query and processes them to extract specified fields.",
#           "signature": "def get_arxiv_papers(query: str, fields: List = ['title', 'authors', 'date', 'abstract', 'journal', 'doi'], max_results: int = 99999, client_options: Dict = {'num_retries': 10}, search_options: Dict = dict()) -> pd.DataFrame"
#         },
#         {
#           "name": "get_and_dump_arxiv_papers",
#           "description": "Generates a query from keywords, fetches papers using the query, processes them, and dumps the results to a specified file.",
#           "signature": "def get_and_dump_arxiv_papers(keywords: List[Union[str, List[str]]], output_filepath: str, fields: List = ['title', 'authors', 'date', 'abstract', 'journal', 'doi'], *args, **kwargs)"
#         },
#         {
#           "name": "get_query_from_keywords",
#           "description": "Constructs a search query from a list of keywords, where each keyword can be a string or a list of synonyms.",
#           "signature": "get_query_from_keywords(keywords: List[Union[str, List[str]]]) -> str"
#         }
#       ],
#       "interrelationships": "The 'arxiv.py' script uses functions from 'utils.py' to generate queries and dump papers. The '__init__.py' script imports functionalities from the arxiv module but does not add new functionality.",
#       "notes": "The 'arxiv.py' script maps arXiv-specific field names to more common ones and provides processing functions for certain fields like authors, date, journal, and DOI."
#     },
#     {
#       "name": "citations",
#       "files": [
#         "core.py",
#         "utils.py",
#         "__init__.py"
#       ],
#       "subfolders": [
#         {
#           "name": "tests",
#           "files": [
#             "test_self_references.py"
#           ],
#           "subfolders": [],
#           "purpose": "Contains unit tests for the self-references functionality in the paperscraper module.",
#           "main_functionality": "The scripts in this folder test the correctness of the self-references function, including handling single and multiple DOIs, managing not implemented errors, and comparing asynchronous and synchronous performance.",
#           "functions": [],
#           "interrelationships": "No interrelationships between files or subfolders are present in this folder.",
#           "notes": "The script uses pytest for testing and logging is disabled."
#         }
#       ],
#       "purpose": "The folder contains scripts for analyzing self-references in academic papers using DOIs and retrieving citations from titles.",
#       "main_functionality": "The core functionality includes fetching paper details via the Semantic Scholar API, calculating self-citations, and checking overlapping words between strings. The scripts support both synchronous and asynchronous execution.",
#       "functions": [
#         {
#           "name": "self_references",
#           "description": "Analyzes self-references for a list of inputs (either DOIs or text samples containing DOIs).",
#           "signature": "self_references(inputs: Union[str, Iterable[str]], relative: bool = False, verbose: bool = False) -> Dict[str, Dict[str, Union[float, int]]]"
#         },
#         {
#           "name": "self_references_paper",
#           "description": "Fetches and analyzes self-references for a single paper identified by its DOI.",
#           "signature": "self_references_paper(doi: str, relative: bool = False, verbose: bool = False) -> Dict[str, Union[float, int]]"
#         },
#         {
#           "name": "check_overlap",
#           "description": "Checks if two strings have overlapping words longer than one character.",
#           "signature": "check_overlap(n1: str, n2: str) -> bool"
#         }
#       ],
#       "interrelationships": "The `core.py` script uses functions from `utils.py` for checking overlaps and relies on the Semantic Scholar API. The `__init__.py` file imports functionalities from both `scholar` and `core` modules to provide a comprehensive citation analysis tool.",
#       "notes": "The `doi_pattern` regex pattern is defined in `utils.py` but not used within the provided functions."
#     },

#   ],
#   "purpose": "A collection of scripts for scraping, processing, and analyzing paper data from various databases.",
#   "main_functionality": "The folder contains scripts to scrape queries from different databases using keywords, process and analyze the scraped data, and handle file I/O operations. It includes functionalities for dumping and loading data in JSONL format, as well as generating visualizations and performing filtering based on specified criteria.",
#   "functions": [
#     {
#       "name": "dump_queries",
#       "description": "Dumps queries from various databases based on given keywords.",
#       "signature": "dump_queries(keywords: List[List[Union[str, List[str]]]], dump_root: str) -> None"
#     },
#     {
#       "name": "aggregate_data",
#       "description": "Aggregates data from different sources and performs post-processing tasks.",
#       "signature": "aggregate_data(data_sources: List[str], output_dir: str) -> None"
#     },
#     {
#       "name": "plot_counts",
#       "description": "Plots the counts of papers over time based on a DataFrame.",
#       "signature": "plot_counts(df: pd.DataFrame, save_path: str) -> None"
#     },
#     {
#       "name": "dump_papers",
#       "description": "Dumps a DataFrame of papers to a JSONL file.",
#       "signature": "dump_papers(papers: pd.DataFrame, filepath: str) -> None"
#     }
#   ],
#   "interrelationships": "The scripts interact by sharing data through files and directories. For example, 'paperscraper.py' scrapes data and dumps it into the 'data' subfolder, while 'postprocessing.py' loads this data for further processing. The 'plotting.py' script uses processed data to generate visualizations, which are saved in the 'logs' subfolder.",
#   "notes": "The folder includes logging configurations to manage output levels and handle warnings effectively. It also provides utility functions for asynchronous operations and type checking."
# }
# def extract_selective_info(folder_summary: dict, fields_to_extract=None) -> dict:
#     """
#     Recursively extract specified fields from a nested dictionary structure
#     while maintaining the original structure by including structural fields like 'subfolders'.
    
#     :param folder_summary: Input nested dictionary
#     :param fields_to_extract: List of field names to extract (e.g., ['purpose', 'main_functionality'])
#     :return: Filtered dictionary containing only specified fields and structural fields
#     """
#     # Default to empty list if no fields specified
#     if fields_to_extract is None:
#         fields_to_extract = []
    
#     # Define structural fields that should always be included to maintain hierarchy
#     structural_fields = ['subfolders']
    
#     def recursive_filter(data):
#         # If it's a dictionary
#         if isinstance(data, dict):
#             filtered = {}
            
#             # Include specified fields if they exist
#             for field in fields_to_extract:
#                 if field in data:
#                     filtered[field] = data[field]
            
#             # Always include structural fields
#             for field in structural_fields:
#                 if field in data:
#                     filtered_value = recursive_filter(data[field])
#                     if filtered_value:  # Only add if not empty
#                         filtered[field] = filtered_value
            
#             return filtered
        
#         # If it's a list, filter each item
#         elif isinstance(data, list):
#             filtered_list = []
#             for item in data:
#                 filtered_item = recursive_filter(item)
#                 if filtered_item:  # Only add if not empty
#                     filtered_list.append(filtered_item)
#             return filtered_list
        
#         # For other types, return as is
#         else:
#             return data
    
#     # Apply the recursive filter to the entire structure
#     return recursive_filter(folder_summary)

# # Usage examples:
# # 1. Extract specific fields
# result1 = extract_selective_info(folder_summary, ["purpose", "main_functionality"])

# # 2. Extract custom fields
# result2 = extract_selective_info(folder_summary, ["notes", "functions"])
# import json
# # 3. No fields specified (returns empty structure)
# # result3 = extract_selective_info(folder_summary)
# print("result1:", json.dumps(result1, indent=2))

# print("result2:", json.dumps(result2, indent=2))

# # print("\n result2:", result2)

# # prd = extract_prd_data(folder_summary)
# # print(prd)
# # prd will now contain all the nested information dynamically extracted