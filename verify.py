from pymed import PubMed
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

pubmed = PubMed(tool="MyTool", email="disispavank@gmail.")

def get_results(query: str):
    results = pubmed.query(query, max_results=30)
    return results

query_text = "coughing is only a symptom of bronchitis"
results = get_results(query_text)

articles_info = []
for index, result in enumerate(results):
    info = result.toDict()
    title = info.get("title", "No title")
    abstract = info.get("abstract", "").replace("\n", " ")
    pub_date = info.get("publication_date")
    date_str = str(pub_date)
    articles_info.append({
        "index": index,
        "title": title,
        "abstract": abstract,
        "date": date_str
    })

def format_abstract_contents(query_text: str, articles_info: list):
    """
    Build the 'contents' list for generate_content:
    - First two instructions entries
    - Then, for each abstract, a separate entry so we avoid a giant single string.
    """
    contents = [
        "The claim: " + query_text + "\n",
        "Categorize the following claim as one of: **Valid**, **Invalid**, or **Vague**, "
        "based on the provided abstracts. Use publication dates to judge relevance and timeliness.\n\n"
        "Instructions:\n"
        "1. **Definitions:**\n"
        "   - **Valid**: Abstracts supply clear, direct evidence that the claim holds true, "
        "including demonstration of causation or a highly specific link. Mere plausibility is not enough.\n"
        "   - **Invalid**: Abstracts contain evidence that directly contradicts the claim or show strong evidence against it.\n"
        "   - **Vague**: Abstracts do not provide sufficient evidence for a firm conclusion. "
        "This includes cases where the feature/symptom is common across many conditions and is not uniquely or reliably tied to the claim.\n\n"
        "2. **Evidence evaluation:**\n"
        "   - Check if any abstract demonstrates that the symptom or feature is uniquely or predominantly linked to the condition in question.\n"
        "   - If only correlation or common mention appears, but no indication of specificity or diagnostic reliability, treat as Vague.\n"
        "   - Consider publication date: prioritize recent, high-quality studies; older abstracts may be noted but weighed appropriately.\n\n"
        "3. **Output format (strict JSON):\n"
        "{\n"
        "  \"category\": \"<Valid|Invalid|Vague>\",\n"
        "  \"confidence\": <float 0.0–1.0>,\n"
        "  \"rationale\": \"Brief summary of how evidence supports this category, citing publication dates or key phrases.\",\n"
        "  \"key_evidence\": [\n"
        "    {\n"
        "      \"abstract_index\": <number>,\n"
        "      \"quote\": \"…\",\n"
        "      \"date\": \"YYYY-MM-DD\",\n"
        "      \"reason\": \"Why this snippet matters\"\n"
        "    },\n"
        "    ...\n"
        "  ]\n"
        "}\n"
        "- If no abstracts supply enough detail, category must be \"Vague\", with rationale explaining lack of specificity.\n\n"
        "4. **Edge-case handling:**\n"
        "   - If abstracts conflict, weigh the quality, recency, and sample size if mentioned; reflect conflicts in rationale.\n"
        "   - If abstracts mention that the symptom is common but not diagnostic, explicitly note that in rationale and choose Vague.\n"
    ]
    for art in articles_info:
        entry = f"Abstract {art['index']} (Date: {art['date']}): Title: {art['title']}\n{art['abstract']}\n"
        contents.append(entry)
    return contents

def generate_validation(query_text: str, articles_info: list) -> str:
    contents = format_abstract_contents(query_text, articles_info)
    response = genai.GenerativeModel("gemini-2.5-flash").generate_content(contents=contents)
    
    return response.text



print(generate_validation(query_text=query_text, articles_info=articles_info))
