"""
Test Cases for Legal Contract Analysis System

This module contains sample contracts and expected outputs for testing
the ContractAnalyzer functionality.
"""

import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contract_analyzer import ContractAnalyzer, ContractAnalysisResult, format_output


# =============================================================================
# SAMPLE CONTRACTS
# =============================================================================

SAMPLE_CONTRACTS = {
    "basic_contract": {
        "description": "Basic service agreement with all key clause types",
        "text": """
        This agreement is between Company A and Company B. The payment for services 
        rendered shall be made in two equal installments, with the first payment due 
        on January 1, 2026, and the second due upon completion of the project. 
        Confidential information shared between the parties shall be kept confidential 
        for a period of 5 years from the termination of this agreement. Either party 
        may terminate this agreement with 30 days' notice. Dispute resolution will 
        occur via binding arbitration in New York.
        """,
        "expected_clause_types": ["Payment Terms", "Confidentiality", "Termination", "Dispute Resolution"],
        "expected_risk_areas": ["project completion ambiguity", "generic termination clause"]
    },
    
    "complex_contract": {
        "description": "More complex contract with multiple clauses and risks",
        "text": """
        SERVICE AGREEMENT

        This Service Agreement ("Agreement") is entered into as of February 1, 2026, 
        by and between TechCorp Inc. ("Service Provider") and GlobalEnterprises LLC ("Client").

        1. SERVICES AND PAYMENT
        The Service Provider agrees to provide software development services as described 
        in Exhibit A. The Client shall pay a total fee of $150,000, payable as follows:
        - Initial deposit of $50,000 due upon signing
        - $50,000 due upon completion of Phase 1 milestones
        - $50,000 due upon final delivery and acceptance
        
        Late payments shall incur a penalty of 1.5% per month. The Service Provider 
        reserves the right to suspend services if payment is more than 30 days overdue.

        2. CONFIDENTIALITY
        Each party agrees to maintain the confidentiality of any proprietary information 
        disclosed by the other party. This obligation shall continue for a period of 
        three (3) years following termination of this Agreement. Confidential information 
        does not include information that is publicly available or independently developed.

        3. INTELLECTUAL PROPERTY
        All intellectual property created during the course of this Agreement shall be 
        owned by the Client upon full payment. The Service Provider retains the right 
        to use general knowledge and skills acquired during the project.

        4. TERMINATION
        Either party may terminate this Agreement for cause with 15 days written notice 
        if the other party materially breaches any provision and fails to cure such breach 
        within the notice period. The Client may terminate for convenience with 30 days 
        notice, subject to payment of all work completed and reasonable wind-down costs.

        5. DISPUTE RESOLUTION
        Any disputes arising from this Agreement shall first be addressed through good 
        faith negotiation. If negotiation fails, disputes shall be resolved through 
        binding arbitration under the rules of the American Arbitration Association 
        in San Francisco, California. Each party shall bear its own costs.

        6. LIMITATION OF LIABILITY
        In no event shall either party be liable for any indirect, incidental, special, 
        or consequential damages. The Service Provider's total liability shall not 
        exceed the total fees paid under this Agreement.

        7. GENERAL PROVISIONS
        This Agreement constitutes the entire agreement between the parties. Any 
        modifications must be in writing and signed by both parties. This Agreement 
        shall be governed by the laws of the State of California.
        """,
        "expected_clause_types": ["Payment Terms", "Confidentiality", "Termination", "Dispute Resolution"],
        "expected_risk_areas": ["material breach", "good faith negotiation", "reasonable wind-down costs"]
    },
    
    "risky_contract": {
        "description": "Contract with multiple vague and risky clauses",
        "text": """
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
        
        NON-COMPETE
        The Consultant agrees not to work with any competitors of the Company for a 
        reasonable period after termination, in any geographic area where the Company 
        conducts business.
        
        INDEMNIFICATION
        The Consultant shall indemnify and hold harmless the Company from any and all 
        claims, damages, and expenses, without limitation, arising from the Consultant's 
        services.
        
        DISPUTE RESOLUTION
        Any disputes shall be resolved in a manner deemed appropriate by the Company.
        """,
        "expected_clause_types": ["Payment Terms", "Confidentiality", "Termination", "Dispute Resolution"],
        "expected_risk_areas": [
            "reasonably requested", "at the discretion of", "best efforts", 
            "reasonable fee", "reasonable time", "indefinite period", 
            "as deemed appropriate", "without limitation", "reasonable period"
        ]
    },
    
    "minimal_contract": {
        "description": "Minimal contract with few clauses",
        "text": """
        Agreement between Party A and Party B.
        
        Party A will provide services to Party B. 
        Party B will pay $10,000 for the services.
        This agreement is valid for one year from the date of signing.
        """,
        "expected_clause_types": ["Payment Terms"],
        "expected_risk_areas": ["no termination clause", "no dispute resolution", "no confidentiality"]
    },
    
    "employment_contract": {
        "description": "Employment agreement sample",
        "text": """
        EMPLOYMENT AGREEMENT
        
        This Employment Agreement is entered into between TechStartup Inc. ("Employer") 
        and John Smith ("Employee").
        
        1. POSITION AND DUTIES
        The Employee is hired as a Senior Software Engineer. Duties shall include software 
        development, code review, and mentoring junior developers. Additional duties may 
        be assigned as needed by the Employer.
        
        2. COMPENSATION
        Base Salary: $120,000 per year, paid bi-weekly
        Bonus: Discretionary annual bonus of up to 20% based on performance
        Equity: 10,000 stock options vesting over 4 years with a 1-year cliff
        
        3. BENEFITS
        The Employee shall be entitled to standard company benefits including health 
        insurance, 401(k) matching, and 20 days of paid time off annually.
        
        4. CONFIDENTIALITY
        The Employee agrees to maintain strict confidentiality regarding all proprietary 
        information, trade secrets, and business strategies of the Employer. This 
        obligation survives termination of employment indefinitely.
        
        5. INTELLECTUAL PROPERTY
        All inventions, discoveries, and works created by the Employee during employment 
        and related to the Employer's business shall be the sole property of the Employer.
        
        6. NON-COMPETE AND NON-SOLICITATION
        For a period of 12 months following termination, the Employee agrees not to:
        - Work for any direct competitor within a 50-mile radius
        - Solicit any employees or customers of the Employer
        
        7. TERMINATION
        Either party may terminate this Agreement with 2 weeks written notice. The 
        Employer may terminate immediately for cause, including but not limited to 
        misconduct, breach of this Agreement, or poor performance.
        
        8. DISPUTE RESOLUTION
        Any disputes shall be resolved through mediation, followed by binding arbitration 
        if mediation is unsuccessful. Venue shall be in San Francisco, California.
        
        9. GOVERNING LAW
        This Agreement shall be governed by the laws of the State of California.
        """,
        "expected_clause_types": ["Payment Terms", "Confidentiality", "Termination", "Dispute Resolution"],
        "expected_risk_areas": ["discretionary bonus", "as needed", "indefinitely", "including but not limited to"]
    }
}


def run_test_case(analyzer: ContractAnalyzer, contract_name: str, contract_data: dict) -> dict:
    """
    Run analysis on a single test case.
    
    Args:
        analyzer: The ContractAnalyzer instance
        contract_name: Name of the test case
        contract_data: Dictionary containing contract details
        
    Returns:
        Dictionary with test results
    """
    print(f"\n{'='*80}")
    print(f"TEST CASE: {contract_name}")
    print(f"Description: {contract_data['description']}")
    print(f"{'='*80}")
    
    try:
        result = analyzer.analyze_efficient(contract_data['text'])
        
        # Check clause types extracted
        extracted_types = [clause.get('type') for clause in result.clauses]
        expected_types = contract_data.get('expected_clause_types', [])
        
        print(f"\n📋 Summary Preview: {result.summary[:200]}...")
        print(f"\n📑 Extracted Clause Types: {extracted_types}")
        print(f"   Expected Types: {expected_types}")
        
        print(f"\n⚠️  Risks Identified: {len(result.risky_clauses)}")
        for i, risk in enumerate(result.risky_clauses[:3], 1):
            reason = risk.get('reason', '')[:100]
            print(f"   {i}. {reason}...")
        
        return {
            "status": "success",
            "result": result.to_dict(),
            "clause_types_found": extracted_types,
            "risks_count": len(result.risky_clauses)
        }
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


def run_all_tests(api_key: str = None) -> dict:
    """
    Run all test cases.
    
    Args:
        api_key: Google API key (optional, will use environment variable if not provided)
        
    Returns:
        Dictionary with all test results
    """
    print("\n" + "=" * 80)
    print("RUNNING ALL TEST CASES")
    print("=" * 80)
    
    try:
        analyzer = ContractAnalyzer(api_key=api_key)
    except ValueError as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        return {"status": "failed", "error": str(e)}
    
    results = {}
    for name, data in SAMPLE_CONTRACTS.items():
        results[name] = run_test_case(analyzer, name, data)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    success_count = sum(1 for r in results.values() if r.get("status") == "success")
    total_count = len(results)
    
    print(f"\n✅ Passed: {success_count}/{total_count}")
    
    for name, result in results.items():
        status = "✅" if result.get("status") == "success" else "❌"
        print(f"   {status} {name}")
    
    return results


def test_edge_cases(api_key: str = None) -> None:
    """
    Test edge cases and error handling.
    
    Args:
        api_key: Google API key
    """
    print("\n" + "=" * 80)
    print("TESTING EDGE CASES")
    print("=" * 80)
    
    try:
        analyzer = ContractAnalyzer(api_key=api_key)
    except ValueError as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        return
    
    # Test 1: Empty contract
    print("\n📝 Test: Empty contract")
    try:
        analyzer.analyze_efficient("")
        print("   ❌ Should have raised ValueError")
    except ValueError as e:
        print(f"   ✅ Correctly raised ValueError: {e}")
    
    # Test 2: Whitespace-only contract
    print("\n📝 Test: Whitespace-only contract")
    try:
        analyzer.analyze_efficient("   \n\t   ")
        print("   ❌ Should have raised ValueError")
    except ValueError as e:
        print(f"   ✅ Correctly raised ValueError: {e}")
    
    # Test 3: Very short contract
    print("\n📝 Test: Very short contract")
    try:
        result = analyzer.analyze_efficient("This is a contract.")
        print(f"   ✅ Handled gracefully: {result.summary[:50]}...")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    # Test 4: Contract with special characters
    print("\n📝 Test: Contract with special characters")
    try:
        result = analyzer.analyze_efficient(
            "Agreement between A & B: Payment of $10,000 @ 5% interest. "
            "Terms apply ©2026. Contact: test@email.com"
        )
        print(f"   ✅ Handled gracefully: {result.summary[:50]}...")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")


def save_results_to_file(results: dict, filename: str = "test_results.json") -> None:
    """
    Save test results to a JSON file.
    
    Args:
        results: Dictionary of test results
        filename: Output filename
    """
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📁 Results saved to {filename}")


if __name__ == "__main__":
    print("=" * 80)
    print("LEGAL CONTRACT ANALYSIS - TEST SUITE")
    print("=" * 80)
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n⚠️  GOOGLE_API_KEY environment variable not set.")
        api_key = input("Enter your Google API Key (or press Enter to skip tests): ").strip()
        if not api_key:
            print("\nNo API key provided. Showing sample contracts only.\n")
            for name, data in SAMPLE_CONTRACTS.items():
                print(f"\n{'='*60}")
                print(f"Contract: {name}")
                print(f"Description: {data['description']}")
                print(f"Expected Clause Types: {data['expected_clause_types']}")
                print(f"Expected Risk Areas: {data['expected_risk_areas']}")
                print(f"{'='*60}")
                print(f"Text Preview:\n{data['text'][:500]}...")
            sys.exit(0)
    
    # Run tests
    results = run_all_tests(api_key)
    
    # Test edge cases
    test_edge_cases(api_key)
    
    # Save results
    save_results_to_file(results)
    
    print("\n✅ All tests completed!")
