from pymed import PubMed
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
pubmed = PubMed(tool="MyTool", email="disispavank@gmail.com")

def get_results(query: str):
    results = pubmed.query(query, max_results=30)
    return results

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
        "3. **Output format (strict JSON):**\n"
        "{\n"
        "  \"claim\": \"<the original claim string>\",\n"
        "  \"validity\": <contains a value: true, unverified, or vague>\n"
        "  \"question\": \"<A suggested follow-up question someone might ask a doctor based on this claim>\",\n"
        "  \"sources\": [\n"
        "    {\n"
        "      \"abstract_index\": <number>,\n"
        "      \"website_link\": \"<shows the link of this article (the url portion that is received)>\",\n"
        "      \"title\": \"title of article\",\n"
        "      \"reason\": \"<why this quote matters for evaluating the claim>\"\n"
        "    },\n"
        "    ...\n"
        "  ]\n"
        "}\n"
        "\n"
        "- If abstracts are too general or conflicting, choose a lower validity score and clearly explain why in the reason fields.\n"
        "- The `question` field should be practical, e.g., \"Could frequent headaches suggest a specific neurological condition in my case?\"\n"

        "- If no abstracts supply enough detail, category must be \"Vague\", with rationale explaining lack of specificity.\n\n"
        "4. **Edge-case handling:**\n"
        "   - If abstracts conflict, weigh the quality, recency, and sample size if mentioned; reflect conflicts in rationale.\n"
        "   - If abstracts mention that the symptom is common but not diagnostic, explicitly note that in rationale and choose Vague.\n"
    ]
    for art in articles_info:
        entry = f"Abstract {art['index']} (Website Link: {art['url']}): Title: {art['title']}\n{art['abstract']}\n"
        contents.append(entry)
    return contents

def generate_validation(query_text: str, articles_info: list) -> str:
    contents = format_abstract_contents(query_text, articles_info)
    response = genai.GenerativeModel("gemini-2.5-flash").generate_content(contents=contents)
    return response.text

#makes it safe to parse
def json_parse(text: str):
    try:
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(text)
    except json.JSONDecodeError as e:
        return None


#returns a python dict (CALL THIS FUNCTION)
def get_verification_info(query_text):
    results = get_results(query_text)

    articles_info = []
    
    #list of information regarding articles 
    for index, result in enumerate(results):
        info = result.toDict()
        title = info.get("title", "No title")
        abstract = info.get("abstract", "").replace("\n", " ")
        pub_date = info.get("publication_date")
        date_str = str(pub_date)
        
        raw_pmid = info.get('pubmed_id', '')  # use single quotes here
        # Sometimes pubmed_id may contain trailing newline or whitespace
        pmid = raw_pmid.split('\n')[0].strip() if raw_pmid else ""
        if pmid:
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        else:
            url = None
        
        articles_info.append({
            "index": index,
            "title": title,
            "abstract": abstract,
            "date": date_str,
            "url": url
        })
          
    response_text = generate_validation(query_text, articles_info)

    print(response_text, "***************")
    
    parsed_dict = json_parse(response_text)
    parsed_dict["type"] = "verif"
    parsed_dict["sources"] = parsed_dict['sources'][:2]

    return parsed_dict

print(get_verification_info("coughing is a sign of cancer"))

#returns in the below format
"""
{
    "claim": "",
    "validity": 1,
    "question": "",
    "sources": [
        "website_link"
        "reason"
    ],
    "
}
"""