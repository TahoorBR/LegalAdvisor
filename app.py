"""
FastAPI Application for Legal Contract Analysis
"""

import os
from pathlib import Path
from typing import Optional

# Load environment variables from .env.local (for local development)
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env.local"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not required in production

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from contract_analyzer import ContractAnalyzer, ContractAnalysisResult

# Initialize FastAPI app
app = FastAPI(
    title="Legal Contract Analyzer",
    description="Analyze legal contracts using Gemini AI",
    version="1.0.0"
)

# Initialize the analyzer with API key from .env.local
analyzer: Optional[ContractAnalyzer] = None

def get_analyzer() -> ContractAnalyzer:
    """Get or create the ContractAnalyzer instance."""
    global analyzer
    if analyzer is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="GOOGLE_API_KEY not found in .env.local"
            )
        analyzer = ContractAnalyzer(api_key=api_key)
    return analyzer


# Pydantic models for API
class ContractInput(BaseModel):
    """Input model for contract analysis."""
    contract_text: str
    
class AnalysisMetadata(BaseModel):
    """Metadata about the analysis."""
    word_count: int
    model_used: str
    is_long_context: bool
    
class AnalysisResponse(BaseModel):
    """Response model for contract analysis."""
    summary: str
    clauses: list
    risky_clauses: list
    metadata: AnalysisMetadata


# HTML Template for the UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legal Contract Analyzer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #a0a0a0;
            font-size: 1.1rem;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        @media (max-width: 1024px) {
            .main-content {
                grid-template-columns: 1fr;
            }
        }
        
        .input-section, .output-section {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .section-title {
            font-size: 1.3rem;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .section-title .icon {
            font-size: 1.5rem;
        }
        
        textarea {
            width: 100%;
            height: 400px;
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 12px;
            padding: 15px;
            color: #fff;
            font-family: 'Consolas', monospace;
            font-size: 0.95rem;
            resize: vertical;
            transition: border-color 0.3s;
        }
        
        textarea:focus {
            outline: none;
            border-color: #00d4ff;
        }
        
        textarea::placeholder {
            color: #666;
        }
        
        .btn-group {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }
        
        .btn {
            padding: 14px 28px;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #00d4ff, #7c3aed);
            color: #fff;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0,212,255,0.3);
        }
        
        .btn-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-secondary {
            background: rgba(255,255,255,0.1);
            color: #fff;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .btn-secondary:hover {
            background: rgba(255,255,255,0.2);
        }
        
        .output-section {
            min-height: 500px;
        }
        
        .tabs {
            display: flex;
            gap: 5px;
            margin-bottom: 20px;
            background: rgba(0,0,0,0.2);
            padding: 5px;
            border-radius: 10px;
        }
        
        .tab {
            padding: 12px 20px;
            background: transparent;
            border: none;
            color: #a0a0a0;
            cursor: pointer;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .tab.active {
            background: rgba(0,212,255,0.2);
            color: #00d4ff;
        }
        
        .tab:hover:not(.active) {
            background: rgba(255,255,255,0.05);
        }
        
        .tab-content {
            display: none;
            animation: fadeIn 0.3s;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .result-box {
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 20px;
            min-height: 350px;
            max-height: 450px;
            overflow-y: auto;
        }
        
        .summary-text {
            line-height: 1.8;
            color: #e0e0e0;
        }
        
        .clause-item {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #00d4ff;
        }
        
        .clause-type {
            font-weight: 600;
            color: #00d4ff;
            margin-bottom: 8px;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .clause-text {
            color: #c0c0c0;
            line-height: 1.6;
        }
        
        .risk-item {
            background: rgba(255,87,87,0.1);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #ff5757;
        }
        
        .risk-clause {
            color: #ff8a8a;
            margin-bottom: 10px;
            font-style: italic;
        }
        
        .risk-reason {
            color: #c0c0c0;
            line-height: 1.6;
        }
        
        .risk-label {
            display: inline-block;
            background: #ff5757;
            color: #fff;
            padding: 3px 10px;
            border-radius: 5px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 50px;
        }
        
        .loading.active {
            display: block;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255,255,255,0.1);
            border-top-color: #00d4ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .empty-state {
            text-align: center;
            padding: 50px;
            color: #666;
        }
        
        .empty-state .icon {
            font-size: 4rem;
            margin-bottom: 20px;
        }
        
        .sample-contracts {
            margin-top: 20px;
        }
        
        .sample-btn {
            padding: 8px 16px;
            background: rgba(124,58,237,0.2);
            border: 1px solid rgba(124,58,237,0.5);
            border-radius: 8px;
            color: #a78bfa;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.3s;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        
        .sample-btn:hover {
            background: rgba(124,58,237,0.4);
        }
        
        .stats {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-item {
            background: rgba(0,0,0,0.2);
            padding: 15px 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #00d4ff;
        }
        
        .stat-label {
            font-size: 0.8rem;
            color: #888;
            text-transform: uppercase;
        }
        
        .json-output {
            font-family: 'Consolas', monospace;
            font-size: 0.85rem;
            white-space: pre-wrap;
            color: #a0e0a0;
        }
        
        .error-message {
            background: rgba(255,87,87,0.2);
            border: 1px solid #ff5757;
            border-radius: 10px;
            padding: 20px;
            color: #ff8a8a;
            text-align: center;
        }
        
        .metadata-banner {
            display: flex;
            gap: 20px;
            align-items: center;
            background: rgba(0,212,255,0.1);
            border: 1px solid rgba(0,212,255,0.3);
            border-radius: 10px;
            padding: 12px 20px;
            margin-bottom: 20px;
        }
        
        .metadata-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .metadata-label {
            color: #a0a0a0;
            font-size: 0.9rem;
        }
        
        .metadata-item span:last-child:not(.badge) {
            color: #00d4ff;
            font-weight: 600;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .badge-info {
            background: rgba(124,58,237,0.3);
            color: #b794f4;
            border: 1px solid rgba(124,58,237,0.5);
        }
        
        .badge-warning {
            background: rgba(255,170,0,0.2);
            color: #ffb347;
            border: 1px solid rgba(255,170,0,0.4);
        }
        
        .clause-not-found {
            background: rgba(255,170,0,0.15);
            border-left: 3px solid #ffaa00;
        }
        
        .clause-not-found .clause-text {
            color: #ffb347;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚖️ Legal Contract Analyzer</h1>
            <p class="subtitle">AI-powered contract analysis using Gemini</p>
        </header>
        
        <div class="main-content">
            <div class="input-section">
                <h2 class="section-title">
                    <span class="icon">📄</span>
                    Contract Input
                </h2>
                <textarea id="contractText" placeholder="Paste your legal contract here...

Example:
This agreement is between Company A and Company B. The payment for services rendered shall be made in two equal installments..."></textarea>
                
                <div class="btn-group">
                    <button class="btn btn-primary" id="analyzeBtn" onclick="analyzeContract()">
                        🔍 Analyze Contract
                    </button>
                    <button class="btn btn-secondary" onclick="clearAll()">
                        🗑️ Clear
                    </button>
                </div>
                
                <div class="sample-contracts">
                    <p style="color: #888; margin-bottom: 10px; font-size: 0.9rem;">Load sample contract:</p>
                    <button class="sample-btn" onclick="loadSample('basic')">Basic Agreement</button>
                    <button class="sample-btn" onclick="loadSample('complex')">Complex Contract</button>
                    <button class="sample-btn" onclick="loadSample('risky')">Risky Contract</button>
                </div>
            </div>
            
            <div class="output-section">
                <h2 class="section-title">
                    <span class="icon">📊</span>
                    Analysis Results
                </h2>
                
                <div class="stats" id="stats" style="display: none;">
                    <div class="stat-item">
                        <div class="stat-value" id="clauseCount">0</div>
                        <div class="stat-label">Clauses Found</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value" id="riskCount">0</div>
                        <div class="stat-label">Risks Identified</div>
                    </div>
                </div>
                
                <div class="tabs">
                    <button class="tab active" onclick="showTab('summary')">Summary</button>
                    <button class="tab" onclick="showTab('clauses')">Clauses</button>
                    <button class="tab" onclick="showTab('risks')">Risks</button>
                    <button class="tab" onclick="showTab('json')">JSON</button>
                </div>
                
                <div id="loading" class="loading">
                    <div class="spinner"></div>
                    <p>Analyzing contract with Gemini AI...</p>
                </div>
                
                <div id="emptyState" class="empty-state">
                    <div class="icon">📝</div>
                    <p>Enter a contract and click "Analyze" to see results</p>
                </div>
                
                <div id="errorState" class="error-message" style="display: none;"></div>
                
                <!-- Metadata Banner -->
                <div id="metadataBanner" class="metadata-banner" style="display: none;">
                    <div class="metadata-item">
                        <span class="metadata-label">📝 Words:</span>
                        <span id="wordCount">0</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">🤖 Model:</span>
                        <span id="modelUsed">-</span>
                    </div>
                    <div class="metadata-item" id="longContextBadge" style="display: none;">
                        <span class="badge badge-info">Long Context Mode</span>
                    </div>
                </div>
                
                <div id="tab-summary" class="tab-content">
                    <div class="result-box">
                        <div id="summaryContent" class="summary-text"></div>
                    </div>
                </div>
                
                <div id="tab-clauses" class="tab-content">
                    <div class="result-box" id="clausesContent"></div>
                </div>
                
                <div id="tab-risks" class="tab-content">
                    <div class="result-box" id="risksContent"></div>
                </div>
                
                <div id="tab-json" class="tab-content">
                    <div class="result-box">
                        <pre id="jsonContent" class="json-output"></pre>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const sampleContracts = {
            basic: `This agreement is between Company A and Company B. The payment for services rendered shall be made in two equal installments, with the first payment due on January 1, 2026, and the second due upon completion of the project. Confidential information shared between the parties shall be kept confidential for a period of 5 years from the termination of this agreement. Either party may terminate this agreement with 30 days' notice. Dispute resolution will occur via binding arbitration in New York.`,
            
            complex: `SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into as of February 1, 2026, by and between TechCorp Inc. ("Service Provider") and GlobalEnterprises LLC ("Client").

1. SERVICES AND PAYMENT
The Service Provider agrees to provide software development services as described in Exhibit A. The Client shall pay a total fee of $150,000, payable as follows:
- Initial deposit of $50,000 due upon signing
- $50,000 due upon completion of Phase 1 milestones
- $50,000 due upon final delivery and acceptance

Late payments shall incur a penalty of 1.5% per month. The Service Provider reserves the right to suspend services if payment is more than 30 days overdue.

2. CONFIDENTIALITY
Each party agrees to maintain the confidentiality of any proprietary information disclosed by the other party. This obligation shall continue for a period of three (3) years following termination of this Agreement.

3. TERMINATION
Either party may terminate this Agreement for cause with 15 days written notice if the other party materially breaches any provision and fails to cure such breach within the notice period.

4. DISPUTE RESOLUTION
Any disputes arising from this Agreement shall first be addressed through good faith negotiation. If negotiation fails, disputes shall be resolved through binding arbitration in San Francisco, California.`,
            
            risky: `CONSULTING AGREEMENT

This Agreement is made between ABC Consulting ("Consultant") and XYZ Corp ("Company").

SCOPE OF WORK
The Consultant shall provide consulting services as reasonably requested by the Company. The specific tasks will be determined at the discretion of the Company's management team. The Consultant shall use best efforts to complete all assignments in a timely manner.

COMPENSATION
The Company shall pay the Consultant a reasonable fee for services rendered, to be determined based on the complexity of work performed. Payment shall be made within a reasonable time after invoice submission.

CONFIDENTIALITY
The Consultant agrees to keep all Company information confidential for an indefinite period. What constitutes confidential information shall be determined by the Company as deemed appropriate.

TERMINATION
Either party may terminate this Agreement at any time, with or without cause, effective immediately upon verbal or written notice.

INDEMNIFICATION
The Consultant shall indemnify and hold harmless the Company from any and all claims, damages, and expenses, without limitation, arising from the Consultant's services.

DISPUTE RESOLUTION
Any disputes shall be resolved in a manner deemed appropriate by the Company.`
        };
        
        function loadSample(type) {
            document.getElementById('contractText').value = sampleContracts[type];
        }
        
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById('tab-' + tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        function clearAll() {
            document.getElementById('contractText').value = '';
            document.getElementById('emptyState').style.display = 'block';
            document.getElementById('stats').style.display = 'none';
            document.getElementById('errorState').style.display = 'none';
            document.getElementById('metadataBanner').style.display = 'none';
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById('summaryContent').innerHTML = '';
            document.getElementById('clausesContent').innerHTML = '';
            document.getElementById('risksContent').innerHTML = '';
            document.getElementById('jsonContent').textContent = '';
        }
        
        async function analyzeContract() {
            const contractText = document.getElementById('contractText').value.trim();
            
            if (!contractText) {
                alert('Please enter a contract to analyze');
                return;
            }
            
            // Show loading
            document.getElementById('loading').classList.add('active');
            document.getElementById('emptyState').style.display = 'none';
            document.getElementById('errorState').style.display = 'none';
            document.getElementById('stats').style.display = 'none';
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById('analyzeBtn').disabled = true;
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ contract_text: contractText })
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Analysis failed');
                }
                
                const result = await response.json();
                displayResults(result);
                
            } catch (error) {
                document.getElementById('loading').classList.remove('active');
                document.getElementById('errorState').style.display = 'block';
                document.getElementById('errorState').textContent = '❌ Error: ' + error.message;
            } finally {
                document.getElementById('analyzeBtn').disabled = false;
            }
        }
        
        function displayResults(result) {
            // Hide loading
            document.getElementById('loading').classList.remove('active');
            
            // Show metadata banner
            if (result.metadata) {
                document.getElementById('metadataBanner').style.display = 'flex';
                document.getElementById('wordCount').textContent = result.metadata.word_count.toLocaleString();
                document.getElementById('modelUsed').textContent = result.metadata.model_used;
                
                if (result.metadata.is_long_context) {
                    document.getElementById('longContextBadge').style.display = 'block';
                } else {
                    document.getElementById('longContextBadge').style.display = 'none';
                }
            }
            
            // Show stats
            document.getElementById('stats').style.display = 'flex';
            
            // Count only found clauses
            const foundClauses = result.clauses.filter(c => c.clause !== 'Not found').length;
            const notFoundClauses = result.clauses.filter(c => c.clause === 'Not found').length;
            document.getElementById('clauseCount').textContent = foundClauses + (notFoundClauses > 0 ? ` (${notFoundClauses} not found)` : '');
            document.getElementById('riskCount').textContent = result.risky_clauses.length;
            
            // Summary
            document.getElementById('summaryContent').innerHTML = result.summary;
            
            // Clauses - with special handling for "Not found"
            let clausesHtml = '';
            if (result.clauses.length === 0) {
                clausesHtml = '<p style="color: #888;">No clauses extracted</p>';
            } else {
                result.clauses.forEach(clause => {
                    const isNotFound = clause.clause === 'Not found';
                    const itemClass = isNotFound ? 'clause-item clause-not-found' : 'clause-item';
                    const clauseText = isNotFound 
                        ? '<em>⚠️ Not found in contract</em>' 
                        : clause.clause;
                    
                    clausesHtml += `
                        <div class="${itemClass}">
                            <div class="clause-type">${clause.type}${isNotFound ? ' <span class="badge badge-warning">Missing</span>' : ''}</div>
                            <div class="clause-text">${clauseText}</div>
                        </div>
                    `;
                });
            }
            document.getElementById('clausesContent').innerHTML = clausesHtml;
            
            // Risks
            let risksHtml = '';
            if (result.risky_clauses.length === 0) {
                risksHtml = '<p style="color: #4ade80;">✓ No significant risks identified</p>';
            } else {
                result.risky_clauses.forEach(risk => {
                    risksHtml += `
                        <div class="risk-item">
                            <span class="risk-label">⚠️ RISK</span>
                            <div class="risk-clause">"${risk.clause}"</div>
                            <div class="risk-reason"><strong>Why it's risky:</strong> ${risk.reason}</div>
                        </div>
                    `;
                });
            }
            document.getElementById('risksContent').innerHTML = risksHtml;
            
            // JSON
            document.getElementById('jsonContent').textContent = JSON.stringify(result, null, 2);
            
            // Show summary tab
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelector('.tab').classList.add('active');
            document.getElementById('tab-summary').classList.add('active');
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main UI."""
    return HTML_TEMPLATE


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_contract(input_data: ContractInput):
    """
    Analyze a legal contract.
    
    Args:
        input_data: ContractInput with the contract text
        
    Returns:
        AnalysisResponse with summary, clauses, risky clauses, and metadata
    """
    try:
        contract_analyzer = get_analyzer()
        
        # Calculate word count and determine model
        word_count = len(input_data.contract_text.split())
        is_long_context = word_count >= contract_analyzer.LONG_CONTRACT_THRESHOLD
        model_used = contract_analyzer.LONG_CONTEXT_MODEL if is_long_context else contract_analyzer.DEFAULT_MODEL
        
        result = contract_analyzer.analyze_efficient(input_data.contract_text)
        
        return AnalysisResponse(
            summary=result.summary,
            clauses=result.clauses,
            risky_clauses=result.risky_clauses,
            metadata=AnalysisMetadata(
                word_count=word_count,
                model_used=model_used,
                is_long_context=is_long_context
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    api_key = os.getenv("GOOGLE_API_KEY")
    return {
        "status": "healthy",
        "api_key_configured": bool(api_key)
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting Legal Contract Analyzer API...")
    print("Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
