# Legal Contract Analysis System
## Technical Report and Implementation Documentation

---

# Executive Summary

This project implements an intelligent legal contract analysis system powered by Google's Gemini AI model. The system was designed to address a fundamental challenge in legal and compliance workflows: the time-consuming and error-prone nature of manually reviewing contracts for key terms, obligations, and potential risks.

The solution I developed automatically processes legal documents of up to 5,000 words and performs three critical functions. First, it generates concise, professionally written summaries that capture the essence of the contract without losing important legal nuances. Second, it extracts and classifies specific clause types including payment terms, confidentiality provisions, dispute resolution mechanisms, and termination conditions. Third, and perhaps most importantly, it identifies potentially risky or ambiguous language that could lead to disputes or unfavorable outcomes for either party.

The technology stack centers on Google's Gemini AI models, specifically leveraging the gemini-2.0-flash model for standard contracts and the gemini-2.0-pro-exp model for longer documents approaching the word limit. This dual-model approach ensures optimal performance across varying contract lengths while managing API costs effectively. The implementation is built in Python with a clean, modular architecture that separates concerns between input validation, AI interaction, response parsing, and output formatting.

What makes this approach reliable is its combination of sophisticated prompt engineering, robust JSON parsing with multiple fallback strategies, and graceful error handling throughout the pipeline. Rather than attempting brittle keyword-based extraction, the system leverages the semantic understanding capabilities of large language models to interpret legal language in context, producing consistently structured outputs regardless of how the original contract was written.

The solution is deployable both as a standalone command-line tool for individual use and as a FastAPI-based web service for integration into larger systems. A live demonstration is available at https://legal-advisor-sepia.vercel.app, with the complete source code hosted at https://github.com/TahoorBR/LegalAdvisor.

---

# System Architecture

The architecture of this system follows a pipeline pattern that transforms unstructured legal text into structured, actionable intelligence. Understanding this flow is essential to appreciating how the various components work together to produce reliable results.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CONTRACT ANALYSIS PIPELINE                          │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │  Contract Text   │
                              │  (User Input)    │
                              └────────┬─────────┘
                                       │
                                       ▼
                        ┌──────────────────────────┐
                        │   INPUT VALIDATION       │
                        │  • Empty check           │
                        │  • Word count (≤5000)    │
                        │  • Text sanitization     │
                        └────────────┬─────────────┘
                                     │
                                     ▼
                        ┌──────────────────────────┐
                        │   MODEL SELECTION        │
                        │  • <3500 words: Flash    │
                        │  • ≥3500 words: Pro      │
                        └────────────┬─────────────┘
                                     │
                                     ▼
                        ┌──────────────────────────┐
                        │   PROMPT ENGINEERING     │
                        │  • Structured prompts    │
                        │  • JSON schema guidance  │
                        │  • Risk indicators       │
                        └────────────┬─────────────┘
                                     │
                                     ▼
                        ┌──────────────────────────┐
                        │   GEMINI AI MODEL        │
                        │  • Semantic analysis     │
                        │  • Context understanding │
                        │  • Legal interpretation  │
                        └────────────┬─────────────┘
                                     │
                                     ▼
                        ┌──────────────────────────┐
                        │   RESPONSE PARSING       │
                        │  • Direct JSON parse     │
                        │  • Markdown extraction   │
                        │  • Regex fallback        │
                        └────────────┬─────────────┘
                                     │
                                     ▼
                        ┌──────────────────────────┐
                        │   POST-PROCESSING        │
                        │  • Clause verification   │
                        │  • Missing type handling │
                        │  • Output normalization  │
                        └────────────┬─────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
           ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
           │   SUMMARY    │  │   CLAUSES    │  │  RISK FLAGS  │
           │  (JSON)      │  │   (JSON)     │  │   (JSON)     │
           └──────────────┘  └──────────────┘  └──────────────┘
                    │                │                │
                    └────────────────┼────────────────┘
                                     ▼
                        ┌──────────────────────────┐
                        │   STRUCTURED OUTPUT      │
                        │   ContractAnalysisResult │
                        └──────────────────────────┘
```

The decision to use LLM-driven extraction rather than traditional regex or keyword-based approaches was deliberate and stems from the fundamental nature of legal language. Legal contracts are written by humans for humans, and the same concept can be expressed in countless different ways. A payment clause might say "compensation shall be rendered" or "fees will be paid" or "monetary consideration is due" — all meaning the same thing but with completely different surface patterns. Regular expressions would require an impossibly comprehensive list of patterns to catch every variation, and would still miss novel phrasings.

By leveraging Gemini's semantic understanding, the system interprets meaning rather than matching patterns. This makes it robust against the natural variation in legal writing and capable of handling contracts from different jurisdictions, industries, and drafting styles without modification.

The structured prompting strategy ensures reliable JSON output by providing the model with explicit schema examples and clear instructions about the expected format. This approach, combined with a multi-layer parsing strategy that handles various response formats including raw JSON and markdown-wrapped code blocks, achieves consistent output structure even when the model's formatting varies slightly between requests.

The architecture inherently supports future scaling. The ContractAnalyzer class is designed as a reusable module that can be imported into any Python application. The FastAPI wrapper demonstrates how the same analysis logic can power a web service, and the same approach could easily extend to batch processing systems, document management integrations, or real-time contract review workflows.

---

# Approach to Each Task

## Contract Summarization Strategy

The summarization component was designed with a specific philosophy: legal summaries should be concise yet complete, professional yet accessible, and factual without any hallucination of details not present in the source document.

The prompt engineering for summarization focuses Gemini's attention on the elements that matter most in legal contexts. Rather than asking for a generic summary that might emphasize narrative flow or interesting details, the prompt explicitly directs the model to prioritize payment terms, confidentiality requirements, termination conditions, and dispute resolution mechanisms. These four areas represent the core operational concerns in most commercial contracts — money, secrets, exits, and conflicts.

The 200-word limit imposed on summaries serves multiple purposes. It forces the model to be selective, including only truly essential information. It produces outputs that can be quickly scanned by busy professionals. And it prevents the model from padding responses with unnecessary elaboration or restating the obvious.

To avoid hallucination, the prompt explicitly instructs the model to summarize only what exists in the contract and to maintain a professional, factual tone. The system does not ask the model to infer terms that might be implied or to suggest what should have been included. What you get is what the contract actually says, distilled to its essence.

## Clause Extraction Method

The clause extraction system employs semantic classification through the language model rather than attempting keyword-based pattern matching. This decision reflects a deep understanding of why traditional extraction methods fail with legal documents.

Legal contracts are drafted by thousands of different lawyers across hundreds of jurisdictions, each with their own stylistic preferences and terminology. A confidentiality clause in a Silicon Valley tech contract might read very differently from one in a London banking agreement, yet both serve the same legal purpose. Keyword systems would need to anticipate every possible variation, and would inevitably miss creative phrasings or unusual terminology.

The LLM-based approach sidesteps this problem entirely. By asking Gemini to identify clauses by their semantic function rather than their surface form, the system can recognize a payment term whether it uses "compensation," "remuneration," "consideration," or any other synonym. The model understands the purpose of the text, not just its words.

Ensuring structured JSON output required careful prompt design. The prompt provides explicit examples of the expected output format, including the exact field names and structure. This template-based guidance helps the model understand not just what information to extract but how to format it for programmatic consumption.

A critical innovation in the extraction system is the handling of missing clauses. Rather than hallucinating content to fill gaps, the system is explicitly instructed to return "Not found" for any clause type not present in the source document. The post-processing layer then verifies that all four required clause types appear in the output, adding "Not found" entries for any the model missed. This dual verification ensures that consumers of the API always receive a complete, predictable structure regardless of what the contract contains.

## Risk Identification Logic

The risk identification component represents the most analytically sophisticated aspect of the system. While summarization and extraction are valuable, risk flagging is where the system provides genuine legal intelligence that can protect parties from problematic agreements.

The risk detection model operates across multiple dimensions of legal concern. The first category is vague language, which includes terms that sound meaningful but lack specific definition. Phrases like "reasonable effort," "best efforts," "commercially reasonable," "as deemed appropriate," and "at the discretion of" are red flags because they shift interpretation from the contract text to subjective judgment, often favoring whichever party has more power in the relationship.

The second category involves undefined triggers — conditions that determine when obligations activate or terminate but lack clear criteria for determination. "Upon completion" sounds specific but begs the question of who determines completion and by what standard. "As soon as practicable" provides no timeline whatsoever. These ambiguities become battlegrounds in disputes.

One-sided power clauses form the third category. These are provisions where only one party can modify terms, make determinations, or exercise discretion. While not inherently invalid, such clauses create power imbalances that can be exploited and often indicate an agreement drafted primarily to protect one party's interests.

Missing specifics represent the fourth risk dimension. This includes arbitration clauses that don't specify rules or location, termination provisions without notice periods or cure rights, and payment terms without clear deadlines or amounts. Vagueness in these areas leaves crucial questions unanswered until a dispute forces resolution.

The fifth category addresses financial ambiguity, particularly payment obligations linked to subjective milestones or undefined deliverables. "Payment upon satisfactory completion" invites disagreement about what satisfactory means, while "reasonable fee based on complexity" provides no basis for either party to predict their obligations.

| Risk Category | Detection Indicators | Legal Concern |
|---------------|---------------------|---------------|
| Vague Language | "reasonable," "best efforts," "as needed" | Subjective interpretation in disputes |
| Undefined Triggers | "upon completion," "as appropriate" | Unclear activation conditions |
| One-Sided Power | "at sole discretion," "may modify" | Exploitable imbalance |
| Missing Specifics | No location, no rules, no timeline | Enforcement uncertainty |
| Financial Ambiguity | Subjective milestones, undefined fees | Payment dispute potential |

The system maintains a curated list of over 30 specific risk indicators spanning these categories, which are incorporated into the prompt to guide the model's attention. However, the prompt also instructs the model to identify risks beyond these examples, leveraging its understanding of legal principles to catch novel problematic language.

For each identified risk, the system requires not just the flagged text but a detailed explanation of why it poses a risk. This explanation serves both educational and practical purposes — helping users understand the concern and providing documentation for any remediation discussions with counterparties.

---

# Testing Strategy

Robust testing was essential to validate that the system performs reliably across the full range of inputs it might encounter in production use. The testing approach was designed to stress-test every aspect of the pipeline, from input validation through output generation.

The test suite begins with short, well-structured contracts that contain clear examples of each clause type and minimal ambiguity. These baseline tests verify that the system works correctly in ideal conditions, establishing that the fundamental logic is sound before introducing complications.

Missing section tests evaluate how the system handles contracts that lack one or more of the expected clause types. A simple service agreement might specify payment but include nothing about confidentiality or dispute resolution. The system must correctly identify what is present, report what is missing as "Not found," and avoid hallucinating clauses that don't exist. These tests were particularly important for validating the post-processing layer that ensures complete output structure.

Repeated clause tests challenge the system with contracts containing multiple instances of the same clause type. A complex agreement might have different payment terms for different phases of work, or multiple confidentiality provisions covering different types of information. The system should extract all relevant instances rather than stopping at the first match.

Boundary testing with contracts approaching the 5,000-word limit validates both the word counting logic and the model selection mechanism. These tests ensure that large documents are routed to the long-context model and processed successfully without truncation or degradation in output quality.

Ambiguity stress tests present contracts deliberately loaded with vague language, undefined terms, and one-sided provisions. These tests validate the risk identification logic, ensuring the system catches the kinds of problems it was designed to detect. The risky contract sample included in the codebase represents this category, featuring multiple instances of each risk type to verify comprehensive detection.

One-sided contract tests present agreements drafted entirely from one party's perspective, with all discretion, modification rights, and favorable terms flowing in one direction. These unbalanced contracts should trigger numerous risk flags, and the explanations should correctly identify the power imbalance.

Throughout the testing process, I maintained focus on ensuring that edge cases result in graceful degradation rather than system failures. The goal was to create a system that always returns valid, structured output even when facing unexpected inputs or model behavior.

---

# Error Handling and Robustness

Production systems must handle errors gracefully, and this principle guided the error handling strategy throughout the implementation.

Empty input validation occurs at the earliest possible point in the pipeline. Before any API calls or processing begins, the system checks that the contract text exists and contains actual content after stripping whitespace. Empty or whitespace-only inputs receive a clear error message explaining the problem, preventing wasted API calls and confusing downstream errors.

Word limit enforcement protects both the user and the system. Contracts exceeding 5,000 words are rejected with an informative error message that includes the actual word count and the limit. This prevents users from submitting documents too large for reliable processing and maintains consistent system behavior.

Missing clause type handling represents a different category of robustness — dealing with valid input that lacks expected content. The post-processing layer examines the model's output and adds "Not found" entries for any missing clause types. This ensures that consumers of the API always receive the complete expected structure, simplifying their integration code and preventing null reference errors.

The JSON parsing layer implements a three-tier fallback strategy to handle variations in model output formatting. The first tier attempts direct JSON parsing of the response. If that fails, the second tier looks for JSON wrapped in markdown code blocks (a common LLM response pattern) and extracts it. The third tier uses regex to find any JSON object structure within the response text. Only if all three tiers fail does the system raise a parsing error.

Partial output handling ensures that even when the model produces incomplete responses, the system extracts whatever value is available. If the summary is present but clauses are missing, the summary is still returned with empty clause arrays. This approach maximizes the utility of each API call while maintaining structural consistency.

The fundamental principle underlying all error handling is that the system should fail gracefully and always return valid JSON. Whether the input is problematic, the model behaves unexpectedly, or network issues occur, the user receives a structured response they can process programmatically, even if that response indicates an error condition.

---

# Scalability and Real-World Applications

While this implementation fulfills the assessment requirements, the architecture was designed with broader applicability in mind. The same core technology could power a range of legal technology applications serving different market needs.

As a legal technology SaaS platform, the system could offer contract review services to law firms, corporate legal departments, and individual practitioners. Users would upload contracts through a web interface and receive instant analysis, dramatically reducing the time required for initial document review. Subscription tiers could offer different usage limits, priority processing, and additional features like batch analysis or integration APIs.

In the compliance space, the system could serve as an automated contract compliance checker, scanning agreements for specific required clauses, prohibited terms, or regulatory concerns. Organizations subject to industry regulations could use this to verify that their contracts meet applicable requirements before execution.

The risk identification capabilities make the system particularly valuable as a contract review assistant for non-lawyers. Procurement teams, sales representatives, and business managers who routinely handle contracts but lack legal training could use the risk flags to identify provisions requiring legal review, improving the efficiency of the overall contracting process.

Integration with document management systems represents another scaling vector. Large organizations often maintain thousands of executed contracts with limited visibility into their contents. The analysis engine could process existing contract repositories to create searchable databases of obligations, extract key dates and milestones, and identify patterns across the portfolio.

Future extensions could include liability analysis focused specifically on indemnification and limitation of liability provisions, SLA detection for service agreements, and regulatory compliance scanning tailored to specific frameworks like GDPR, HIPAA, or SOX. The modular architecture makes adding new analysis capabilities straightforward — each new capability is essentially a new prompt template and output handler.

---

# Technology Selection: Why Gemini

The choice of Google's Gemini model as the AI backbone for this system was deliberate and based on several technical and practical considerations.

Strong long-context handling was essential given the requirement to process contracts up to 5,000 words. Legal documents are often dense and internally referential, with later sections modifying or qualifying earlier provisions. The model needs to maintain coherent understanding across the entire document to produce accurate analysis. Gemini's architecture supports this kind of long-range dependency tracking effectively.

Legal language understanding requires semantic sophistication beyond keyword matching. Legal writing uses specialized terminology, complex sentence structures, and implicit references to legal concepts that may not be explicitly stated. Gemini demonstrates strong performance in understanding these nuances, correctly interpreting legal jargon and recognizing the functional purpose of provisions regardless of their specific wording.

Reliable structured output was a non-negotiable requirement for this use case. The system needs to produce consistent JSON structures that can be processed programmatically. Through careful prompt engineering, Gemini reliably generates well-formed JSON that matches the specified schema. The few formatting variations that do occur are handled by the multi-tier parsing strategy.

The balance between cost and performance factored into model selection as well. The dual-model approach uses the faster, more economical Flash model for shorter contracts while reserving the more capable Pro model for documents that genuinely need its extended context window. This optimization manages API costs without sacrificing quality where it matters.

API reliability and availability were also considerations. Google Cloud's infrastructure provides the uptime and performance consistency required for production applications, with well-documented APIs and robust client libraries that simplify integration.

---

# Assumptions Made

Professional transparency requires acknowledging the assumptions underlying this implementation, as they define the boundaries within which the system operates reliably.

The system assumes that input contracts, while potentially informal or poorly organized, are fundamentally legal documents intended to establish contractual relationships. It is not designed to process other document types that might superficially resemble contracts, such as proposals, term sheets, or marketing materials.

Regarding contract structure, the system does not assume any particular formatting or organization. Contracts may lack section headers, may combine multiple provisions in single paragraphs, or may use non-standard terminology. The semantic analysis approach is designed to handle this variation, but extremely unconventional document structures may challenge the model's interpretation.

Risk detection focuses on legal ambiguity and potential enforceability concerns rather than broader business risk assessment. The system identifies language that could lead to disputes or unfavorable interpretations, but does not evaluate whether the underlying business terms are favorable, market-standard, or aligned with the user's interests.

The system treats each contract as an independent document. It does not consider external documents that might be incorporated by reference, prior dealings between parties, or industry customs that might inform interpretation. These contextual factors matter in real legal analysis but require information beyond the document text.

Model decisions depend fundamentally on prompt engineering. The quality and relevance of outputs are bounded by how effectively the prompts guide the model's attention and structure its responses. While the current prompts are extensively tested, different prompt formulations might yield different results in edge cases.

---

# Limitations

No system is perfect, and intellectual honesty requires acknowledging limitations that users should understand when relying on this tool.

Large language models, despite their sophistication, may miss subtle jurisdiction-specific legal risks. A clause that is perfectly enforceable under New York law might be void in California, and the model does not currently incorporate jurisdiction-specific legal knowledge. Users should not treat the analysis as a substitute for jurisdiction-aware legal advice.

Risk classification is advisory and does not constitute legal judgment. The system identifies language patterns associated with risk, but determining whether a particular provision is actually problematic requires legal expertise and understanding of the specific transaction context. The flags should be viewed as highlighting areas for human review, not as definitive risk assessments.

Complex multi-document dependencies are not handled by the current implementation. Many commercial relationships involve multiple related agreements — master services agreements with statements of work, purchase agreements with exhibits, licenses with amendments. The system analyzes each document in isolation and cannot identify inconsistencies or dependencies across documents.

The system's training is based on general legal language patterns and may underperform on highly specialized contract types or unusual provisions. Contracts in niche industries or involving novel transaction structures might use language patterns the model has encountered less frequently, potentially affecting analysis quality.

Real-time performance depends on API availability and response times from the Gemini service. While generally reliable, network issues or service degradation could affect user experience. The system does not currently implement caching or offline fallbacks.

---

# Future Improvements

Several enhancements could significantly extend the system's capabilities and value, representing potential directions for continued development.

Fine-tuning on legal corpora would improve the model's domain expertise. While Gemini performs well with general-purpose training, a model fine-tuned specifically on legal documents — ideally including court decisions interpreting contractual language — could develop more nuanced understanding of legal implications and jurisdiction-specific concerns.

Clause confidence scoring would add a probabilistic dimension to the extraction results. Rather than simply returning extracted text, the system could indicate how confident it is that the extracted passage actually represents the identified clause type. This would help users understand when human verification is particularly important.

Risk severity ratings would enhance the risk identification output by categorizing flags into tiers such as critical, moderate, and advisory. Not all risks are equal — a completely undefined payment term is more concerning than a slightly vague timeline. Severity ratings would help users prioritize their review attention.

Highlighting risky text in the UI would improve the user experience of the web interface. Rather than presenting risks as a separate list, the original contract text could be displayed with highlighted spans for each identified issue, making it easier to understand risks in context.

Version comparison functionality would enable users to upload two versions of a contract and receive analysis of what changed between them. This is particularly valuable in negotiation contexts where parties exchange redlined drafts, helping users quickly understand the substantive impact of proposed changes.

Human-in-the-loop validation would allow users to confirm or correct the system's classifications, with this feedback used to improve future analyses. Over time, this could create a continuous improvement cycle where the system learns from its mistakes and edge cases.

Multi-language support would extend the system's applicability to contracts in languages other than English. While this would require careful handling of language-specific legal concepts and terminology, the underlying approach could generalize to any language supported by the Gemini model.

Integration with contract lifecycle management platforms would embed analysis capabilities directly into the tools organizations already use to manage their agreements, reducing friction and increasing adoption.

---

# Conclusion

This legal contract analysis system demonstrates how modern AI capabilities can be applied to solve real problems in legal technology. By combining Gemini's semantic understanding with careful prompt engineering, robust error handling, and thoughtful architecture, the implementation delivers reliable, structured analysis of legal documents.

The system fulfills all requirements of the original assessment: summarizing contracts, extracting classified clauses, and identifying risks with explanations. Beyond the requirements, it provides a foundation for more sophisticated legal technology applications, with clear paths for enhancement and scaling.

The code is clean, modular, and production-ready. The error handling ensures graceful degradation. The testing strategy validates behavior across diverse inputs. And the architecture supports future growth without fundamental redesign.

Most importantly, the system reflects understanding not just of the technical challenges but of the business context in which it would operate. Legal professionals need tools they can trust, with transparent limitations and reliable behavior. This implementation was designed with those needs in mind.

---

**Repository:** https://github.com/TahoorBR/LegalAdvisor  
**Live Demo:** https://legal-advisor-sepia.vercel.app  
**Author:** Muhammad Tahoor Bin Rauf  
**Date:** February 2026
