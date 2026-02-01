"""
Legal Contract Analysis using Gemini AI.
Summarizes contracts, extracts clauses, and identifies risks.
"""

import os
import json
import re
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import google.generativeai as genai
except ImportError:
    print("=" * 60)
    print("ERROR: Required package 'google-generativeai' not found!")
    print("=" * 60)
    print("\nPlease install it using:")
    print("  pip install google-generativeai")
    print("\nThen run this script again.")
    sys.exit(1)


class ClauseType(Enum):
    """Clause types to extract."""
    PAYMENT_TERMS = "Payment Terms"
    CONFIDENTIALITY = "Confidentiality"
    DISPUTE_RESOLUTION = "Dispute Resolution"
    TERMINATION = "Termination"
    OTHER = "Other"


@dataclass
class ExtractedClause:
    type: str
    clause: str


@dataclass
class RiskyClause:
    clause: str
    reason: str


@dataclass
class ContractAnalysisResult:
    """Complete analysis result for a contract."""
    summary: str
    clauses: List[Dict[str, str]]
    risky_clauses: List[Dict[str, str]]
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def get_summary_json(self) -> str:
        return json.dumps({"summary": self.summary}, indent=2)
    
    def get_clauses_json(self) -> str:
        return json.dumps({"clauses": self.clauses}, indent=2)
    
    def get_risks_json(self) -> str:
        return json.dumps({"risky_clauses": self.risky_clauses}, indent=2)


class ContractAnalyzer:
    """Analyzes legal contracts using Gemini AI."""
    
    DEFAULT_MODEL = "gemini-3-flash-preview"
    LONG_CONTEXT_MODEL = "gemini-3-pro-preview"
    LONG_CONTRACT_THRESHOLD = 3500
    MAX_WORDS = 5000
    
    REQUIRED_CLAUSE_TYPES = [
        "Payment Terms",
        "Confidentiality",
        "Dispute Resolution",
        "Termination"
    ]
    
    RISK_INDICATORS = [
        # Vague effort terms
        "reasonable effort", "reasonable efforts", "best effort", "best efforts",
        "commercially reasonable efforts",
        
        # Discretionary terms
        "at the discretion of", "in its sole discretion", "as deemed appropriate",
        "at its option", "may elect to",
        
        # Undefined time terms
        "reasonable time", "timely manner", "as soon as practicable",
        "promptly", "without undue delay",
        
        # Modification/change terms
        "may be modified", "subject to change", "reserves the right to modify",
        
        # Scope limiters
        "without limitation", "including but not limited to",
        "and/or", "etc.",
        
        # Vague standards
        "material breach", "substantially similar", "good faith",
        "to the extent possible", "materially adverse",
        
        # Force majeure
        "force majeure", "act of God", "circumstances beyond control",
        
        # One-sided terms
        "sole remedy", "exclusive remedy", "waives all claims",
        "indemnify and hold harmless",
    ]
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """Initialize with API key (or uses GOOGLE_API_KEY env var)."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "API key is required. Provide it as an argument or set "
                "GOOGLE_API_KEY environment variable."
            )
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Store custom model name if provided
        self._custom_model_name = model_name
        
        # Initialize models for dynamic selection
        self.default_model = genai.GenerativeModel(self.DEFAULT_MODEL)
        self.long_context_model = genai.GenerativeModel(self.LONG_CONTEXT_MODEL)
        
        self.max_words = self.MAX_WORDS
    
    def _get_word_count(self, text: str) -> int:
        return len(text.split())
    
    def _get_model_for_contract(self, contract_text: str) -> tuple:
        """Select model based on contract length."""
        if self._custom_model_name:
            return genai.GenerativeModel(self._custom_model_name), self._custom_model_name
        
        word_count = self._get_word_count(contract_text)
        
        if word_count >= self.LONG_CONTRACT_THRESHOLD:
            return self.long_context_model, self.LONG_CONTEXT_MODEL
        else:
            return self.default_model, self.DEFAULT_MODEL
    
    def _validate_contract(self, contract_text: str) -> int:
        """Validate contract and return word count."""
        if not contract_text or not contract_text.strip():
            raise ValueError("Contract text cannot be empty.")
        
        word_count = self._get_word_count(contract_text)
        
        if word_count > self.max_words:
            raise ValueError(
                f"Contract exceeds maximum word limit of {self.max_words} words. "
                f"Current word count: {word_count}. "
                f"Please reduce the contract length and try again."
            )
        
        return word_count
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from model response, handling markdown code blocks."""
        text = response_text.strip()
        
        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Handle ```json ... ``` format
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if json_match:
            text = json_match.group(1).strip()
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON object
        json_pattern = re.search(r'(\{[\s\S]*\})', text)
        if json_pattern:
            try:
                return json.loads(json_pattern.group(1))
            except json.JSONDecodeError:
                pass
        
        # If all else fails, raise error
        raise json.JSONDecodeError("Could not parse JSON from response", text, 0)
    
    def _ensure_all_clause_types(self, clauses: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Ensure all required clause types are present (adds 'Not found' for missing)."""
        found_types = {clause.get("type") for clause in clauses}
        result = list(clauses)
        
        for clause_type in self.REQUIRED_CLAUSE_TYPES:
            if clause_type not in found_types:
                result.append({
                    "type": clause_type,
                    "clause": "Not found"
                })
        
        type_order = {t: i for i, t in enumerate(self.REQUIRED_CLAUSE_TYPES)}
        result.sort(key=lambda x: type_order.get(x.get("type"), 999))
        
        return result
    
    def summarize_contract(self, contract_text: str) -> str:
        """Generate a concise summary of the contract."""
        self._validate_contract(contract_text)
        model, _ = self._get_model_for_contract(contract_text)
        
        prompt = f"""You are a legal contract analyst. Analyze the following contract and provide a concise summary.

Focus on these key elements:
- Payment terms and conditions
- Confidentiality requirements
- Termination conditions
- Dispute resolution mechanisms
- Any other critical terms

Contract:
{contract_text}

Provide your response as a JSON object with this exact structure:
{{"summary": "Your concise summary here"}}

Keep the summary clear, professional, and under 200 words."""
        
        try:
            response = model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            return result.get("summary", "Unable to generate summary.")
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw text cleaned up
            return response.text.strip()
        except Exception as e:
            raise RuntimeError(f"Error generating summary: {str(e)}")
    
    def extract_clauses(self, contract_text: str) -> List[Dict[str, str]]:
        """Extract and classify clauses from the contract."""
        self._validate_contract(contract_text)
        model, _ = self._get_model_for_contract(contract_text)
        
        prompt = f"""You are a legal contract analyst. Extract and classify the following types of clauses from this contract:

1. Payment Terms: Terms related to payments, deadlines, penalties, amounts, installments
2. Confidentiality: Terms defining confidentiality, its duration, and restrictions
3. Dispute Resolution: How disputes will be resolved (arbitration, litigation, mediation)
4. Termination: Conditions under which the contract can be terminated

Contract:
{contract_text}

Provide your response as a JSON object with this exact structure:
{{
  "clauses": [
    {{"type": "Payment Terms", "clause": "exact text from contract OR 'Not found' if not present"}},
    {{"type": "Confidentiality", "clause": "exact text from contract OR 'Not found' if not present"}},
    {{"type": "Dispute Resolution", "clause": "exact text from contract OR 'Not found' if not present"}},
    {{"type": "Termination", "clause": "exact text from contract OR 'Not found' if not present"}}
  ]
}}

CRITICAL INSTRUCTIONS:
- Extract the EXACT text from the contract for each clause
- If a clause type is NOT found in the contract, you MUST include it with "clause": "Not found"
- DO NOT hallucinate or invent clauses that don't exist in the contract
- ALL FOUR clause types must appear in the output
- You may include multiple clauses of the same type if present"""
        
        try:
            response = model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            clauses = result.get("clauses", [])
            return self._ensure_all_clause_types(clauses)
        except json.JSONDecodeError:
            return [{"type": t, "clause": "Not found"} for t in self.REQUIRED_CLAUSE_TYPES]
        except Exception as e:
            raise RuntimeError(f"Error extracting clauses: {str(e)}")
    
    def identify_risks(self, contract_text: str) -> List[Dict[str, str]]:
        """Identify risky or ambiguous clauses."""
        self._validate_contract(contract_text)
        model, _ = self._get_model_for_contract(contract_text)
        sample_indicators = ", ".join(f'"{ind}"' for ind in self.RISK_INDICATORS[:8])
        
        prompt = f"""You are a legal risk analyst. Analyze this contract and identify risky or ambiguous clauses.

Look for these risk categories:

1. VAGUE LANGUAGE: Terms like {sample_indicators}
2. ONE-SIDED TERMS: Clauses heavily favoring one party
3. MISSING SPECIFICS: Undefined deadlines, unclear conditions, missing amounts
4. AMBIGUOUS CRITERIA: Unclear completion milestones or performance standards
5. LACK OF REMEDIES: No specified penalties or resolution for breaches
6. OPEN-ENDED OBLIGATIONS: Unlimited duration or scope
7. SUBJECTIVE STANDARDS: Terms requiring interpretation
8. MISSING CLAUSES: Important protections that should be present but aren't

Contract:
{contract_text}

Provide your response as a JSON object:
{{
  "risky_clauses": [
    {{
      "clause": "exact risky clause text from contract",
      "reason": "detailed explanation of the legal risk and potential consequences"
    }}
  ]
}}

RULES:
- Extract EXACT text from the contract for each risky clause
- Provide SPECIFIC explanations of why each clause is risky
- Consider legal implications and dispute potential
- If no risky clauses found, return empty array: {{"risky_clauses": []}}"""
        
        try:
            response = model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            return result.get("risky_clauses", [])
        except json.JSONDecodeError:
            return []
        except Exception as e:
            raise RuntimeError(f"Error identifying risks: {str(e)}")
    
    def analyze(self, contract_text: str) -> ContractAnalysisResult:
        """Perform complete analysis (3 API calls). Use analyze_efficient() for single call."""
        self._validate_contract(contract_text)
        
        summary = self.summarize_contract(contract_text)
        clauses = self.extract_clauses(contract_text)
        risky_clauses = self.identify_risks(contract_text)
        
        return ContractAnalysisResult(
            summary=summary,
            clauses=clauses,
            risky_clauses=risky_clauses
        )
    
    def analyze_efficient(self, contract_text: str) -> ContractAnalysisResult:
        """Perform complete analysis in single API call (recommended)."""
        word_count = self._validate_contract(contract_text)
        model, model_name = self._get_model_for_contract(contract_text)
        sample_indicators = ", ".join(f'"{ind}"' for ind in self.RISK_INDICATORS[:6])
        
        prompt = f"""You are an expert legal contract analyst. Perform a comprehensive analysis of this contract.

Contract:
{contract_text}

Provide your analysis as a JSON object with this EXACT structure:
{{
  "summary": "A concise summary (under 200 words) covering payment terms, confidentiality, termination, and dispute resolution",
  "clauses": [
    {{"type": "Payment Terms", "clause": "exact text OR 'Not found'"}},
    {{"type": "Confidentiality", "clause": "exact text OR 'Not found'"}},
    {{"type": "Dispute Resolution", "clause": "exact text OR 'Not found'"}},
    {{"type": "Termination", "clause": "exact text OR 'Not found'"}}
  ],
  "risky_clauses": [
    {{
      "clause": "exact risky clause text",
      "reason": "detailed explanation of the risk"
    }}
  ]
}}

CRITICAL INSTRUCTIONS:

1. SUMMARY:
   - Focus on key business terms
   - Keep under 200 words
   - Be professional and clear

2. CLAUSES:
   - Extract EXACT text from the contract
   - If a clause type is NOT present, use "Not found"
   - DO NOT invent clauses - only extract what exists
   - ALL FOUR types MUST appear in output

3. RISKS:
   - Look for vague terms like: {sample_indicators}
   - Flag one-sided or ambiguous clauses
   - Explain WHY each clause is risky
   - Consider legal disputes and enforcement issues
   - If no risks found, use empty array

Return ONLY valid JSON, no additional text."""
        
        try:
            response = model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            clauses = self._ensure_all_clause_types(result.get("clauses", []))
            
            return ContractAnalysisResult(
                summary=result.get("summary", "Unable to generate summary."),
                clauses=clauses,
                risky_clauses=result.get("risky_clauses", [])
            )
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse model response: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Analysis failed: {str(e)}")
    
    def get_contract_info(self, contract_text: str) -> Dict[str, Any]:
        """Get contract info (word count, model) without analyzing."""
        word_count = self._get_word_count(contract_text)
        _, model_name = self._get_model_for_contract(contract_text)
        
        return {
            "word_count": word_count,
            "max_words": self.max_words,
            "is_valid": word_count <= self.max_words and word_count > 0,
            "model_to_use": model_name,
            "is_long_context": word_count >= self.LONG_CONTRACT_THRESHOLD
        }


def format_output(result: ContractAnalysisResult, show_full_json: bool = True) -> None:
    """Print analysis result in formatted manner."""
    print("\n" + "=" * 80)
    print("CONTRACT ANALYSIS RESULTS")
    print("=" * 80)
    
    # Summary
    print("\n📋 SUMMARY:")
    print("-" * 40)
    print(json.dumps({"summary": result.summary}, indent=2, ensure_ascii=False))
    
    # Clauses
    print("\n📑 EXTRACTED CLAUSES:")
    print("-" * 40)
    print(json.dumps({"clauses": result.clauses}, indent=2, ensure_ascii=False))
    
    # Risks
    print("\n⚠️  RISK FLAGS:")
    print("-" * 40)
    if result.risky_clauses:
        print(json.dumps({"risky_clauses": result.risky_clauses}, indent=2, ensure_ascii=False))
    else:
        print(json.dumps({"risky_clauses": []}, indent=2))
        print("  (No risky clauses identified)")
    
    # Full JSON output
    if show_full_json:
        print("\n" + "=" * 80)
        print("COMPLETE JSON OUTPUT:")
        print("=" * 80)
        print(result.to_json())


def get_api_key() -> str:
    """Get API key from environment or prompt user."""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if api_key:
        print("✅ Using API key from GOOGLE_API_KEY environment variable")
        return api_key
    
    print("\n⚠️  GOOGLE_API_KEY environment variable not set.")
    print("Please enter your Google API Key below.")
    print("(You can get one from: https://makersuite.google.com/app/apikey)")
    print()
    
    try:
        api_key = input("Enter your Google API Key: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n\n❌ Cancelled by user.")
        sys.exit(1)
    
    if not api_key:
        print("\n❌ No API key provided. Exiting.")
        sys.exit(1)
    
    return api_key


SAMPLE_CONTRACTS = {
    "example_contract": """
This agreement is between Company A and Company B. The payment for services 
rendered shall be made in two equal installments, with the first payment due 
on January 1, 2026, and the second due upon completion of the project. 
Confidential information shared between the parties shall be kept confidential 
for a period of 5 years from the termination of this agreement. Either party 
may terminate this agreement with 30 days' notice. Dispute resolution will 
occur via binding arbitration in New York.
""",
    
    "risky_contract": """
CONSULTING AGREEMENT

This Agreement is made between ABC Consulting ("Consultant") and XYZ Corp ("Company").

SCOPE OF WORK
The Consultant shall provide consulting services as reasonably requested by the 
Company. The specific tasks will be determined at the discretion of the Company's 
management team. The Consultant shall use best efforts to complete all assignments 
in a timely manner.

COMPENSATION
The Company shall pay the Consultant a reasonable fee for services rendered, to 
be determined based on the complexity of work performed. Payment shall be made 
within a reasonable time after invoice submission.

CONFIDENTIALITY
The Consultant agrees to keep all Company information confidential for an 
indefinite period. What constitutes confidential information shall be determined 
by the Company as deemed appropriate.

TERMINATION
Either party may terminate this Agreement at any time, with or without cause, 
effective immediately upon verbal or written notice.
""",
    
    "minimal_contract": """
Agreement between Party A and Party B.
Party A will provide services to Party B. 
Party B will pay $10,000 for the services.
This agreement is valid for one year from the date of signing.
"""
}


def get_contract_from_terminal() -> str:
    """Get contract text from user via terminal (end with double Enter)."""
    print("\n" + "=" * 80)
    print("ENTER YOUR CONTRACT TEXT")
    print("=" * 80)
    print("Paste or type your contract below.")
    print("When finished, press Enter twice (empty line) to submit.")
    print("Or press Ctrl+C to cancel.")
    print("-" * 80)
    
    lines = []
    empty_line_count = 0
    
    try:
        while True:
            line = input()
            if line == "":
                empty_line_count += 1
                if empty_line_count >= 2:
                    break
                lines.append(line)
            else:
                empty_line_count = 0
                lines.append(line)
    except EOFError:
        pass
    except KeyboardInterrupt:
        print("\n\n❌ Input cancelled.")
        return ""
    
    contract_text = "\n".join(lines).strip()
    return contract_text


def main():
    """Run the contract analyzer interactively."""
    print("=" * 80)
    print("LEGAL CONTRACT ANALYSIS SYSTEM")
    print("Using Gemini AI Model")
    print("=" * 80)
    print()
    print("This tool analyzes legal contracts to:")
    print("  • Generate concise summaries")
    print("  • Extract and classify key clauses")
    print("  • Identify risky or ambiguous language")
    print()
    
    # Get API key (from env or prompt)
    api_key = get_api_key()
    
    try:
        # Initialize the analyzer
        print("\n🔄 Initializing Contract Analyzer...")
        analyzer = ContractAnalyzer(api_key=api_key)
        print(f"   Using models: {analyzer.DEFAULT_MODEL} / {analyzer.LONG_CONTEXT_MODEL}")
        print(f"   Max words: {analyzer.max_words}")
        
        # Main loop - allow multiple analyses
        while True:
            # Menu
            print("\n" + "=" * 80)
            print("OPTIONS:")
            print("  1. Enter/paste a contract to analyze")
            print("  2. Use sample contract (example)")
            print("  3. Use sample contract (risky)")
            print("  4. Use sample contract (minimal)")
            print("  5. Exit")
            print("=" * 80)
            
            try:
                choice = input("\nSelect option (1-5): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\n👋 Goodbye!")
                break
            
            if choice == "5":
                print("\n👋 Goodbye!")
                break
            elif choice == "1":
                # Get contract from user input
                contract = get_contract_from_terminal()
                if not contract:
                    print("No contract text entered. Please try again.")
                    continue
            elif choice == "2":
                contract = SAMPLE_CONTRACTS["example_contract"]
                print("\n📄 Using example contract:")
                print("-" * 40)
                print(contract.strip())
            elif choice == "3":
                contract = SAMPLE_CONTRACTS["risky_contract"]
                print("\n📄 Using risky contract sample:")
                print("-" * 40)
                print(contract.strip())
            elif choice == "4":
                contract = SAMPLE_CONTRACTS["minimal_contract"]
                print("\n📄 Using minimal contract sample:")
                print("-" * 40)
                print(contract.strip())
            else:
                print("❌ Invalid option. Please select 1-5.")
                continue
            
            # Validate and show contract info
            try:
                info = analyzer.get_contract_info(contract)
                print(f"\n📊 Contract Info:")
                print(f"   Word count: {info['word_count']} / {info['max_words']}")
                print(f"   Model: {info['model_to_use']}")
                
                if not info['is_valid']:
                    print(f"\n❌ Contract exceeds {info['max_words']} word limit!")
                    continue
                
            except Exception as e:
                print(f"\n❌ Error: {e}")
                continue
            
            # Analyze
            print("\n🔍 Analyzing contract...")
            try:
                result = analyzer.analyze_efficient(contract)
                
                # Display results
                format_output(result)
                
                print("\n" + "=" * 80)
                print("✅ Analysis complete!")
                print("=" * 80)
                
            except Exception as e:
                print(f"\n❌ Analysis failed: {e}")
                continue
            
            # Ask if user wants to continue
            try:
                again = input("\n🔄 Analyze another contract? (y/n): ").strip().lower()
                if again != 'y' and again != 'yes':
                    print("\n👋 Goodbye!")
                    break
            except (EOFError, KeyboardInterrupt):
                print("\n\n👋 Goodbye!")
                break
        
    except ValueError as e:
        print(f"\n❌ Validation Error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\n❌ Runtime Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
