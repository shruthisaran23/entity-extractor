## Entity extraction (insurance PDFs)

Implements:
`extract_entities(document_url: str, topic_name: str, topic_def: str) -> dict`

### Approach
1. PDF ingestion: PDFs are converted to text deterministically using PyMuPDF.

2. Relevant section selection: The document is split into overlapping chunks. Chunks are scored and selected using keyword overlap from the topic definition. 

3. LLM-based extraction: An LLM is used as an extraction agent, conditioned on the topic definition provided at runtime. 

4. Structured output: Results are written to a JSON file.

### Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="your_api_key"
```
### Run
Using a local pdf: 
```bash
python examples/run_example.py data/Guardian_Accident.pdf CoveredInjuries
```
Using a remote PDF URL: 
```bash
python examples/run_example.py \
"https://cms3.revize.com/revize/seviercounty/Human%20Resources/Guardian%20Accident.pdf" \
HospitalBenefits
```
