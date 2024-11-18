import os
import sys
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize
from tqdm.asyncio import tqdm_asyncio
from docx import Document
from multiprocessing import Pool, cpu_count
import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_KEY = os.getenv('API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')                 
SEARCH_RESULTS = 5                                       # Number of search results to retrieve per query
CONCURRENT_REQUESTS = 5                                  # Number of concurrent API requests per process
RATE_LIMIT_DELAY = 1                                     # Delay in seconds between batches to respect rate limits

# Paths for report templates
TEMPLATE_DIR = 'templates'
HTML_TEMPLATE = 'report_template.html'

def download_nltk_data():
    """
    Download necessary NLTK data files.
    """
    nltk_data_files = ['punkt']
    for file in tqdm_asyncio(nltk_data_files, desc="Downloading NLTK data files"):
        nltk.download(file, quiet=True)

def read_target_document(file_path):
    """
    Read the target document (.txt or .docx) and tokenize it into sentences.
    """
    try:
        _, file_extension = os.path.splitext(file_path)
        if file_extension.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        elif file_extension.lower() == '.docx':
            doc = Document(file_path)
            text = '\n'.join([para.text for para in doc.paragraphs])
        else:
            print("Unsupported file format. Please provide a .txt or .docx file.")
            sys.exit(1)
        sentences = sent_tokenize(text)
        return sentences
    except Exception as e:
        print(f"Error reading target document: {e}")
        sys.exit(1)

async def google_search(session, query, api_key, cse_id, num_results=5):
    """
    Perform a Google Custom Search for the given query asynchronously.
    """
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': api_key,
        'cx': cse_id,
        'num': num_results,
        'lr': 'lang_en',  # Restrict results to English
    }
    try:
        async with session.get(search_url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                text = await response.text()
                print(f"Google Search API Error: {response.status} - {text}")
                return None
    except asyncio.TimeoutError:
        print(f"Google Search API Timeout for query: {query}")
        return None
    except Exception as e:
        print(f"Google Search API Exception for query '{query}': {e}")
        return None

def extract_snippet(item):
    """
    Extract snippet from search result item.
    """
    return item.get('snippet', '')

def compute_similarity(text1, text2):
    """
    Compute cosine similarity between two texts using TF-IDF Vectorization.
    """
    vectorizer = TfidfVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    if vectors.shape[0] < 2:
        return 0.0
    similarity = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
    return similarity

async def process_sentence(session, sentence, api_key, cse_id, num_results):
    """
    Process a single sentence: perform search and compute similarity.
    """
    query = f'"{sentence}"'
    search_results = await google_search(session, query, api_key, cse_id, num_results)
    if search_results and 'items' in search_results:
        snippets = [extract_snippet(item) for item in search_results['items']]
        combined_snippets = ' '.join(snippets)
        similarity = compute_similarity(sentence, combined_snippets) * 100  # Percentage
        return {
            'sentence': sentence,
            'similarity': similarity,
            'matches': len(search_results['items']),
            'snippets': snippets
        }
    else:
        return {
            'sentence': sentence,
            'similarity': 0.0,
            'matches': 0,
            'snippets': []
        }

async def process_sentences_async(sentences, api_key, cse_id, num_results, concurrent_requests, rate_limit_delay):
    """
    Asynchronously process a list of sentences.
    """
    results = []
    connector = aiohttp.TCPConnector(limit=concurrent_requests)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for sentence in sentences:
            task = asyncio.create_task(process_sentence(session, sentence, api_key, cse_id, num_results))
            tasks.append(task)
        for f in tqdm_asyncio.as_completed(tasks, desc="Checking sentences", total=len(tasks)):
            result = await f
            results.append(result)
            await asyncio.sleep(rate_limit_delay)  # Adjust based on API rate limits
    return results

def process_sentences(sentences_chunk, api_key, cse_id, num_results, concurrent_requests, rate_limit_delay):
    """
    Worker function to process a chunk of sentences.
    """
    return asyncio.run(process_sentences_async(
        sentences=sentences_chunk,
        api_key=api_key,
        cse_id=cse_id,
        num_results=num_results,
        concurrent_requests=concurrent_requests,
        rate_limit_delay=rate_limit_delay
    ))

def split_into_chunks(sentences, num_chunks):
    """
    Split the list of sentences into specified number of chunks.
    """
    avg = len(sentences) / float(num_chunks)
    chunks = []
    last = 0.0

    while last < len(sentences):
        chunks.append(sentences[int(last):int(last + avg)])
        last += avg

    return chunks

def display_report(results, threshold):
    """
    Display the plagiarism report based on the results.
    """
    potential_plagiarism = [res for res in results if res['similarity'] >= threshold]
    total_sentences = len(results)
    plagiarized_sentences = len(potential_plagiarism)
    plagiarism_percentage = (plagiarized_sentences / total_sentences) * 100 if total_sentences > 0 else 0.0

    print("\n=== Plagiarism Report ===")
    print(f"Total Sentences Checked: {total_sentences}")
    print(f"Potentially Plagiarized Sentences: {plagiarized_sentences} ({plagiarism_percentage:.2f}%)\n")

    if potential_plagiarism:
        print(f"Sentences with Similarity >= {threshold}%:\n")
        for idx, res in enumerate(potential_plagiarism, 1):
            print(f"{idx}. Sentence: {res['sentence']}")
            print(f"   Similarity: {res['similarity']:.2f}%")
            print(f"   Number of Matches: {res['matches']}")
            print(f"   Snippets from Web:")
            for snippet in res['snippets']:
                print(f"      - {snippet}")
            print()
    else:
        print(f"No significant plagiarism detected (No similarity >= {threshold}%).")

def export_to_csv(results, filename='plagiarism_report.csv'):
    """
    Export plagiarism report to a CSV file.
    """
    if not results:
        print("No results to export.")
        return

    df = pd.DataFrame(results)
    # Expand snippets into a single string separated by semicolons
    df['snippets'] = df['snippets'].apply(lambda x: '; '.join(x))
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"Report exported to {filename}")

def export_to_html(report_data, filename='plagiarism_report.html'):
    """
    Export plagiarism report to an HTML file using Jinja2 templating.
    """
    if not report_data['results']:
        print("No results to export.")
        return

    # Set up Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(searchpath=TEMPLATE_DIR),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(HTML_TEMPLATE)

    # Render the template with results and additional data
    html_content = template.render(
        total_sentences=report_data['total_sentences'],
        plagiarized_sentences=report_data['plagiarized_sentences'],
        plagiarism_percentage=report_data['plagiarism_percentage'],
        potential_plagiarism=report_data['potential_plagiarism'],
        threshold=report_data['threshold']
    )

    # Write to HTML file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Report exported to {filename}")

def setup_templates():
    """
    Create the HTML template if it doesn't exist.
    """
    if not os.path.exists(TEMPLATE_DIR):
        os.makedirs(TEMPLATE_DIR)
    
    template_path = os.path.join(TEMPLATE_DIR, HTML_TEMPLATE)
    if not os.path.isfile(template_path):
        # Create a basic HTML template
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Plagiarism Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ccc; padding: 10px; text-align: left; vertical-align: top; }
        th { background-color: #f2f2f2; }
        .high { background-color: #ffdddd; }
        ul { margin: 0; padding-left: 20px; }
    </style>
</head>
<body>
    <h1>Plagiarism Report</h1>
    <p><strong>Total Sentences Checked:</strong> {{ total_sentences }}</p>
    <p><strong>Potentially Plagiarized Sentences:</strong> {{ plagiarized_sentences }} ({{ plagiarism_percentage }}%)</p>
    {% if potential_plagiarism %}
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Sentence</th>
                <th>Similarity (%)</th>
                <th>Number of Matches</th>
                <th>Snippets from Web</th>
            </tr>
        </thead>
        <tbody>
            {% for res in potential_plagiarism %}
            <tr class="{% if res.similarity >= 50 %}high{% endif %}">
                <td>{{ loop.index }}</td>
                <td>{{ res.sentence }}</td>
                <td>{{ "%.2f"|format(res.similarity) }}</td>
                <td>{{ res.matches }}</td>
                <td>
                    <ul>
                        {% for snippet in res.snippets %}
                        <li>{{ snippet }}</li>
                        {% endfor %}
                    </ul>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p>No significant plagiarism detected (No similarity >= {{ threshold }}%).</p>
    {% endif %}
</body>
</html>
""")
        print(f"HTML template created at {template_path}")

def export_reports(results, threshold):
    """
    Export plagiarism reports to CSV and HTML.
    """
    # Export CSV
    export_to_csv(results, filename='plagiarism_report.csv')

    # Filter potential plagiarism for HTML report
    potential_plagiarism = [res for res in results if res['similarity'] >= threshold]
    # Prepare data for the HTML template
    report_data = {
        'results': results,
        'potential_plagiarism': potential_plagiarism,
        'total_sentences': len(results),
        'plagiarized_sentences': len(potential_plagiarism),
        'plagiarism_percentage': f"{(len(potential_plagiarism)/len(results)*100):.2f}" if results else "0.00",
        'threshold': threshold
    }
    # Export HTML
    export_to_html(report_data, filename='plagiarism_report.html')

def main():
    print("=== Internet-Based Plagiarism Checker ===\n")

    # Input path
    target_path = input("Enter the path to the target research paper (e.g., target_paper.txt or target_paper.docx): ").strip()
    print(f"Debug: Target path entered: {target_path}")

    # Validate target path
    if not os.path.isfile(target_path):
        print(f"Error: The file '{target_path}' does not exist.")
        sys.exit(1)

    # Setup HTML templates
    setup_templates()

    # Download NLTK data
    download_nltk_data()

    # Read and tokenize target document
    sentences = read_target_document(target_path)
    print(f"Debug: Total sentences to check: {len(sentences)}\n")

    # Determine number of processes (use number of CPU cores)
    num_processes = cpu_count()
    print(f"Debug: Using {num_processes} processes for multiprocessing.")

    # Split sentences into chunks for each process
    sentence_chunks = split_into_chunks(sentences, num_processes)

    # Prepare arguments for each process
    args = [
        (
            chunk,
            API_KEY,
            SEARCH_ENGINE_ID,
            SEARCH_RESULTS,
            CONCURRENT_REQUESTS,
            RATE_LIMIT_DELAY
        )
        for chunk in sentence_chunks
    ]

    # Initialize multiprocessing Pool
    with Pool(processes=num_processes) as pool:
        # Map the process_sentences function to the chunks
        all_results = pool.starmap(process_sentences, args)

    # Flatten the list of results
    flat_results = [item for sublist in all_results for item in sublist]

    # Analyze and display results
    threshold = 30.0  # Similarity threshold in percentage
    display_report(flat_results, threshold)

    # Export reports
    export_reports(flat_results, threshold)

if __name__ == "__main__":
    main()
