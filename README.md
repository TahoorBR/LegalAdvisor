# Legal Contract Analysis and Risk Identification System

A Python-based system that uses the **Gemini AI model** to analyze legal contracts, extract key clauses, and identify potential risks.

## Features

- **Contract Summarization**: Generates concise summaries focusing on key elements
- **Clause Extraction & Classification**: Identifies and categorizes:
  - Payment Terms
  - Confidentiality Clauses
  - Dispute Resolution
  - Termination Clauses
- **Risk Identification**: Flags ambiguous or risky clauses with detailed explanations

## Requirements

- Python 3.8+
- Google Gemini API key

## Installation

1. **Clone or download** this repository

2. **Install dependencies**:
   ```bash
   pip install google-generativeai
   ```

3. **Set up your API key** (choose one method):
   
   **Option A**: Environment variable (recommended)
   ```bash
   # Windows
   set GOOGLE_API_KEY=your_api_key_here
   
   # Linux/Mac
   export GOOGLE_API_KEY=your_api_key_here
   ```
   
   **Option B**: Pass directly in code
   ```python
   analyzer = ContractAnalyzer(api_key="your_api_key_here")
   ```

## Quick Start

### Basic Usage

```python
from contract_analyzer import ContractAnalyzer

# Initialize the analyzer
analyzer = ContractAnalyzer()

# Sample contract text
contract = """
This agreement is between Company A and Company B. The payment for services 
rendered shall be made in two equal installments, with the first payment due 
on January 1, 2026, and the second due upon completion of the project. 
Confidential information shared between the parties shall be kept confidential 
for a period of 5 years from the termination of this agreement.
"""

# Perform full analysis (efficient single API call)
result = analyzer.analyze_efficient(contract)

# Access results
print(result.summary)
print(result.clauses)
print(result.risky_clauses)

# Get JSON output
print(result.to_json())
```

### Running the Main Script

```bash
python contract_analyzer.py
```

### Running Test Cases

```bash
python test_cases.py
```

## Output Format

### Summary Output
```json
{
  "summary": "This agreement outlines the terms between Company A and Company B..."
}
```

### Extracted Clauses Output
```json
{
  "clauses": [
    {
      "type": "Payment Terms",
      "clause": "The payment for services rendered shall be made..."
    },
    {
      "type": "Confidentiality",
      "clause": "Confidential information shared between the parties..."
    }
  ]
}
```

### Risk Flags Output
```json
{
  "risky_clauses": [
    {
      "clause": "Payment shall be made upon completion of the project.",
      "reason": "The term 'completion' is ambiguous and could lead to disputes..."
    }
  ]
}
```

## API Reference

### `ContractAnalyzer` Class

#### Constructor
```python
ContractAnalyzer(api_key: str = None, model_name: str = "gemini-3-flash-preview")
```
- `api_key`: Your Google API key (optional if set in environment)
- `model_name`: Gemini model to use (default:gemini-3-flash-preview)

#### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `summarize_contract(text)` | Generate a summary of the contract | `str` |
| `extract_clauses(text)` | Extract and classify clauses | `List[Dict]` |
| `identify_risks(text)` | Identify risky/ambiguous clauses | `List[Dict]` |
| `analyze(text)` | Full analysis (3 API calls) | `ContractAnalysisResult` |
| `analyze_efficient(text)` | Full analysis (1 API call) | `ContractAnalysisResult` |

### `ContractAnalysisResult` Class

#### Properties
- `summary`: Contract summary string
- `clauses`: List of extracted clauses
- `risky_clauses`: List of identified risks

#### Methods
- `to_json()`: Convert to JSON string
- `to_dict()`: Convert to dictionary

## Risk Detection Methodology

The system identifies risks by looking for:

1. **Vague Language Indicators**:
   - "reasonable effort", "best efforts"
   - "at the discretion of"
   - "as deemed appropriate"
   - "commercially reasonable"
   - "in a timely manner"

2. **Structural Issues**:
   - One-sided clauses favoring one party
   - Missing specifics (undefined deadlines, unclear conditions)
   - Open-ended obligations
   - Ambiguous completion criteria

3. **Legal Red Flags**:
   - Unlimited liability clauses
   - Indefinite confidentiality periods
   - Broad non-compete restrictions
   - Unlimited indemnification

## Test Cases Included

| Test Case | Description |
|-----------|-------------|
| `basic_contract` | Standard service agreement with all clause types |
| `complex_contract` | Multi-section contract with detailed terms |
| `risky_contract` | Contract loaded with vague/ambiguous language |
| `minimal_contract` | Bare-bones contract with few clauses |
| `employment_contract` | Employment agreement sample |

## Error Handling

The system handles:
- Empty or whitespace-only contracts (`ValueError`)
- Contracts exceeding 5,000 word limit (`ValueError`)
- Malformed or missing clauses (graceful degradation)
- API errors (informative error messages)

## Assumptions and Limitations

1. **Contract Language**: Assumes contracts are in English
2. **Word Limit**: Maximum 5,000 words per contract
3. **Clause Types**: Focuses on four main clause types; other types are not explicitly extracted
4. **Risk Detection**: Based on common patterns; may not catch domain-specific risks
5. **Legal Advice**: This tool provides analysis, not legal advice

## Project Structure

```
Assessment/
├── contract_analyzer.py  # Main analysis module
├── test_cases.py         # Test cases and sample contracts
├── README.md             # This documentation
└── requirements.txt      # Python dependencies
```

## License

This project is provided for assessment purposes.

## Author

Contract Analysis System - February 2026
