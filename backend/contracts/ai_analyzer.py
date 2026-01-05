"""
AI-Powered Contract Risk Analyzer

This module uses OpenAI's GPT models to analyze extracted clauses for risks.
It provides:
1. Risk assessment for each clause
2. Overall contract summary
3. Highlighted potential issues

BEGINNER EXPLANATION:
--------------------
After we extract clauses using pattern matching, we send them to OpenAI's GPT model
to analyze them for risks. GPT is trained on vast amounts of text and can understand
the legal implications of clauses better than simple keyword matching.

HOW IT WORKS:
1. We send the extracted clauses to OpenAI's API
2. GPT analyzes each clause and identifies risks
3. GPT generates a summary explaining the risks
4. We store the results in the database
"""

import logging
import re
from decouple import config
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not installed. AI analysis will not be available.")


def get_openai_client() -> Optional[Any]:
    """
    Create and return OpenAI client if API key is available.
    
    BEGINNER EXPLANATION:
    ---------------------
    This function creates a "client" object that we use to talk to OpenAI's API.
    Think of it like creating a connection to OpenAI's servers.
    
    RETURNS:
    --------
    OpenAI client object, or None if not available
    """
    if not OPENAI_AVAILABLE:
        logger.error("OpenAI library not installed")
        return None
    
    api_key = config('OPENAI_API_KEY', default=None)
    if not api_key:
        logger.error("OpenAI API key not found in environment variables")
        return None
    
    try:
        # Remove quotes if present (sometimes .env files have quotes)
        api_key = api_key.strip('"').strip("'")
        client = OpenAI(api_key=api_key)
        return client
    except Exception as e:
        logger.error(f"Error creating OpenAI client: {str(e)}")
        return None


def analyze_clause_risks(extracted_clauses: List[Dict[str, any]], contract_text: str) -> Dict[str, any]:
    """
    Analyze extracted clauses using OpenAI GPT for risk assessment.
    
    BEGINNER EXPLANATION:
    ---------------------
    This function sends clauses to GPT and asks it to analyze risks.
    GPT reads each clause and provides:
    - Risk level (low/medium/high/critical)
    - Explanation of why it's risky
    - What to watch out for
    - Recommendations
    
    PARAMETERS:
    -----------
    extracted_clauses: List of extracted clauses from clause_extractor
    contract_text: Full contract text (for context)
    
    RETURNS:
    --------
    Dictionary with:
    - 'risks': List of risk assessments for each clause
    - 'summary': Overall contract risk summary
    - 'overall_risk_level': Overall risk level (low/medium/high)
    """
    client = get_openai_client()
    if not client:
        logger.warning("OpenAI not available, returning basic risk assessment")
        return create_basic_risk_assessment(extracted_clauses)
    
    try:
        # Build prompt for GPT
        prompt = build_risk_analysis_prompt(extracted_clauses, contract_text)
        
        # Detect document type for system message
        text_lower = contract_text[:4000].lower()
        if any(keyword in text_lower for keyword in ['sanction letter', 'loan sanction', 'loan approval', 'home loan', 'housing finance']):
            doc_type_note = "This is a LOAN SANCTION LETTER or LOAN AGREEMENT. NEVER call it a 'lease agreement' in your analysis."
        elif any(keyword in text_lower for keyword in ['lease', 'landlord', 'tenant', 'demised premises']):
            doc_type_note = "This is a LEASE AGREEMENT. NEVER call it a 'loan sanction letter' in your analysis."
        else:
            doc_type_note = "Identify the document type correctly based on the content provided."
        
        # Call OpenAI API
        logger.info("Calling OpenAI API for risk analysis...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4o-mini for cost-effectiveness
            messages=[
                {
                    "role": "system",
                    "content": f"You are a precise legal contract analyst. You ONLY analyze information explicitly stated in the provided clauses. You never make assumptions, infer missing details, or hallucinate information. You provide concise, factual analysis based solely on the text provided. Keep all responses brief and focused. {doc_type_note} In the overall_summary field, you MUST use the correct document type name."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,  # Very low temperature for accuracy and consistency
            max_tokens=1500,  # Reduced to encourage conciseness
            response_format={"type": "json_object"}  # Force JSON output
        )
        
        # Parse response
        analysis_text = response.choices[0].message.content
        
        # Parse the structured response
        risk_assessment = parse_risk_analysis(analysis_text, extracted_clauses)
        
        logger.info("Successfully completed OpenAI risk analysis")
        return risk_assessment
        
    except Exception as e:
        logger.error(f"Error in OpenAI risk analysis: {str(e)}")
        # Fallback to basic risk assessment if OpenAI fails
        return create_basic_risk_assessment(extracted_clauses)


def build_risk_analysis_prompt(extracted_clauses: List[Dict[str, any]], contract_text: str) -> str:
    """
    Build the prompt to send to OpenAI for risk analysis.
    Improved to be more specific for lease agreements and contract types.
    
    BEGINNER EXPLANATION:
    ---------------------
    A "prompt" is the instructions we give to GPT. We need to be clear and specific
    about what we want GPT to do. This function creates that prompt.
    """
    # Detect document type for better context - improved to recognize loan documents
    text_lower = contract_text[:4000].lower()
    
    # Check for specific document type indicators first
    if any(keyword in text_lower for keyword in ['sanction letter', 'loan sanction', 'loan approval', 'home loan', 'housing finance']):
        contract_type = "loan sanction letter or loan agreement"
    elif any(keyword in text_lower for keyword in ['lease', 'landlord', 'tenant', 'demised premises']):
        contract_type = "lease agreement"
    elif any(keyword in text_lower for keyword in ['state', 'state of', 'agreement between', 'interstate', 'compact']):
        contract_type = "state agreement or intergovernmental agreement"
    elif any(keyword in text_lower for keyword in ['service agreement', 'service contract', 'vendor', 'provider', 'supplier']):
        contract_type = "service agreement"
    elif any(keyword in text_lower for keyword in ['employment', 'employee', 'employer']):
        contract_type = "employment agreement"
    else:
        contract_type = "contract or agreement"
    
    prompt_parts = [
        f"Analyze the following {contract_type} clauses for potential risks and provide a detailed risk assessment.",
        "",
        "CONTEXT:",
        f"This appears to be a {contract_type}. Focus on risks that are particularly relevant to this type of agreement.",
        "",
        "EXTRACTED CLAUSES:",
        ""
    ]
    
    # Add each clause type with its instances
    for clause_data in extracted_clauses:
        clause_type = clause_data['type'].replace('_', ' ').title()
        prompt_parts.append(f"\n{clause_type} ({clause_data['count']} instance(s)):")
        prompt_parts.append(f"Description: {clause_data['description']}")
        prompt_parts.append("Instances:")
        
        # Only show top 2 best instances per clause type for AI analysis
        # Prioritize instances with article numbers or longer, more complete text
        best_instances = sorted(
            clause_data['clauses'][:5],  # Look at top 5
            key=lambda x: (
                1 if x.get('article') else 0,  # Prefer article numbers
                len(x['text'])  # Then prefer longer text (more complete)
            ),
            reverse=True
        )[:2]  # Take only top 2
        
        for idx, clause_instance in enumerate(best_instances, 1):
            clause_text = clause_instance['text']
            # Include article number if available
            article_info = f" (Article {clause_instance.get('article', 'N/A')})" if clause_instance.get('article') else ""
            # Limit to first 400 chars - be concise for AI
            display_text = clause_text[:400] + "..." if len(clause_text) > 400 else clause_text
            prompt_parts.append(f"\n{idx}{article_info}: {display_text}")
        
        prompt_parts.append("")
    
    prompt_parts.extend([
        "",
        "TASK:",
        "1. For each clause type, assess the risk level (LOW, MEDIUM, HIGH, CRITICAL) based ONLY on the actual clause text provided",
        "2. Write a brief explanation (1-2 sentences max) of why this clause is risky or safe",
        "3. List 2-3 specific concerns using ONLY information explicitly stated in the clause text - do not make assumptions",
        "4. Provide ONE concise, actionable recommendation (1 sentence max)",
        f"5. Provide an overall risk summary (2-3 sentences max) for this {contract_type}",
        "",
        "CRITICAL RULES - READ CAREFULLY:",
        "- ONLY reference information that is explicitly stated in the clause text provided above",
        "- DO NOT make assumptions, infer information, or add details not present in the text",
        "- DO NOT hallucinate numbers, dates, or conditions that aren't in the clauses",
        "- If specific numbers/dates aren't mentioned, say 'amounts/dates not specified' rather than making them up",
        "- Be concise: keep explanations short and focused on actual risks",
        "- Focus on the most important risks only - don't list every minor concern",
        f"- CRITICAL: In the overall_summary, refer to this document as a '{contract_type}' - DO NOT call it a different document type",
        f"- If this is a loan sanction letter, say 'loan sanction letter' or 'loan agreement' - NEVER say 'lease agreement'",
        f"- If this is a lease agreement, say 'lease agreement' - NEVER say 'loan sanction letter'",
        "",
        "RESPONSE FORMAT (JSON only, no other text):",
        "{",
        '  "overall_risk_level": "LOW|MEDIUM|HIGH|CRITICAL",',
        f'  "overall_summary": "2-3 sentence summary for this {contract_type}, focusing on key risks only. Use the correct document type name.",',
        '  "clause_risks": [',
        '    {',
        '      "clause_type": "auto_renewal",',
        '      "risk_level": "MEDIUM",',
        '      "risk_explanation": "1-2 sentence explanation based on actual clause text",',
        '      "concerns": ["Only 2-3 specific concerns from actual clause text"],',
        '      "recommendations": "One concise actionable sentence"',
        '    }',
        '  ]',
        "}",
    ])
    
    return "\n".join(prompt_parts)


def parse_risk_analysis(analysis_text: str, extracted_clauses: List[Dict[str, any]]) -> Dict[str, any]:
    """
    Parse GPT's response into structured risk assessment.
    
    BEGINNER EXPLANATION:
    ---------------------
    GPT returns text, but we need structured data (dictionaries/lists).
    This function converts GPT's text response into a structured format we can use.
    """
    import json
    import re
    
    # Try to extract JSON from the response
    try:
        # Look for JSON-like structure in the response
        json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            # Clean up the JSON string
            json_str = json_str.replace('\\n', ' ')
            parsed = json.loads(json_str)
            # CRITICAL FIX: Post-process to fix document type if GPT got it wrong
            if 'overall_summary' in parsed:
                summary = parsed['overall_summary']
                # Check if it incorrectly says "lease agreement" but should be loan-related
                if 'lease agreement' in summary.lower() and not any(word in summary.lower() for word in ['landlord', 'tenant', 'rent', 'premises']):
                    # It says lease but has no lease keywords - likely a mistake, replace with loan
                    summary = re.sub(r'lease\s+agreement', 'loan sanction letter', summary, flags=re.IGNORECASE)
                    parsed['overall_summary'] = summary
            return parsed
    except Exception as e:
        logger.warning(f"Failed to parse JSON response: {str(e)}")
        pass
    except:
        pass
    
    # Fallback: Extract information using regex patterns
    risk_assessment = {
        'overall_risk_level': 'MEDIUM',
        'overall_summary': analysis_text[:500],  # Use first 500 chars as summary
        'clause_risks': [],
        'raw_analysis': analysis_text,
    }
    
    # Try to extract overall risk level
    risk_level_match = re.search(r'overall.*risk.*level.*?([A-Z]+)', analysis_text, re.IGNORECASE)
    if risk_level_match:
        risk_assessment['overall_risk_level'] = risk_level_match.group(1).upper()
    
    # CRITICAL FIX: Replace "lease agreement" with "loan sanction letter" if detected incorrectly
    if 'overall_summary' in risk_assessment:
        summary = risk_assessment['overall_summary']
        # Check if it incorrectly says "lease agreement" but should be loan-related
        if 'lease agreement' in summary.lower() and not any(word in summary.lower() for word in ['landlord', 'tenant', 'rent', 'premises']):
            # It says lease but has no lease keywords - likely a mistake
            summary = re.sub(r'lease\s+agreement', 'loan sanction letter', summary, flags=re.IGNORECASE)
            risk_assessment['overall_summary'] = summary
    
    # Map clause types to risks
    for clause_data in extracted_clauses:
        clause_type = clause_data['type']
        risk_assessment['clause_risks'].append({
            'clause_type': clause_type,
            'risk_level': clause_data.get('risk_level', 'medium').upper(),
            'risk_explanation': f"Found {clause_data['count']} instance(s) of {clause_data['description']}",
            'concerns': [],
            'recommendations': 'Review these clauses carefully with legal counsel.',
        })
    
    return risk_assessment


def create_basic_risk_assessment(extracted_clauses: List[Dict[str, any]]) -> Dict[str, any]:
    """
    Create a basic risk assessment without OpenAI (fallback).
    
    BEGINNER EXPLANATION:
    ---------------------
    If OpenAI is unavailable or fails, we still want to show some risk assessment.
    This function creates a basic assessment based on clause types and counts.
    """
    if not extracted_clauses:
        return {
            'overall_risk_level': 'LOW',
            'overall_summary': 'No key clauses detected. This contract appears standard, but review all terms carefully.',
            'clause_risks': [],
        }
    
    # Count high-risk clauses
    high_risk_types = ['indemnity', 'liability']
    high_risk_count = sum(1 for c in extracted_clauses if c['type'] in high_risk_types)
    medium_risk_count = sum(1 for c in extracted_clauses if c['risk_level'] == 'medium')
    
    # Determine overall risk
    if high_risk_count > 0:
        overall_risk = 'HIGH'
    elif medium_risk_count > 2:
        overall_risk = 'MEDIUM'
    else:
        overall_risk = 'LOW'
    
    # Build summary
    clause_types = [c['type'].replace('_', ' ').title() for c in extracted_clauses]
    summary = f"This contract contains {len(extracted_clauses)} key clause types: {', '.join(clause_types[:5])}."
    
    if high_risk_count > 0:
        summary += " High-risk clauses detected. Review carefully with legal counsel."
    
    # Build clause risks
    clause_risks = []
    for clause_data in extracted_clauses:
        risk_explanation = f"Found {clause_data['count']} instance(s). {clause_data['description']}."
        
        concerns = []
        if clause_data['type'] == 'auto_renewal':
            concerns.append("Contract may auto-renew without notice")
        elif clause_data['type'] == 'indemnity':
            concerns.append("You may be liable for damages")
        elif clause_data['type'] == 'termination':
            concerns.append("Review termination conditions carefully")
        
        clause_risks.append({
            'clause_type': clause_data['type'],
            'risk_level': clause_data['risk_level'].upper(),
            'risk_explanation': risk_explanation,
            'concerns': concerns,
            'recommendations': 'Review this clause carefully and consider negotiating terms.',
        })
    
    return {
        'overall_risk_level': overall_risk,
        'overall_summary': summary,
        'clause_risks': clause_risks,
    }


def generate_contract_summary(contract_text: str, extracted_clauses: List[Dict[str, any]]) -> str:
    """
    Generate an executive summary of the contract using OpenAI.
    
    BEGINNER EXPLANATION:
    ---------------------
    Creates a brief, easy-to-read summary of the contract highlighting key points.
    Useful for users who don't want to read 20 pages of legal jargon.
    """
    client = get_openai_client()
    if not client:
        # Fallback summary
        return generate_basic_summary(extracted_clauses)
    
    try:
        # CRITICAL FIX: Detect document type FIRST before generating summary
        text_lower = contract_text[:4000].lower()
        document_type_hint = ""
        
        # Detect document type explicitly
        if any(keyword in text_lower for keyword in ['sanction letter', 'loan sanction', 'letter of sanction', 'loan approval']):
            document_type_hint = "LOAN SANCTION LETTER"
            doc_type_description = "loan sanction letter or loan agreement"
        elif any(keyword in text_lower for keyword in ['lease', 'landlord', 'tenant', 'demised premises', 'residential lease']):
            document_type_hint = "LEASE AGREEMENT"
            doc_type_description = "lease agreement"
        elif any(keyword in text_lower for keyword in ['service agreement', 'service contract', 'vendor', 'provider']):
            document_type_hint = "SERVICE AGREEMENT"
            doc_type_description = "service agreement"
        elif any(keyword in text_lower for keyword in ['employment', 'employee', 'employer']):
            document_type_hint = "EMPLOYMENT AGREEMENT"
            doc_type_description = "employment agreement"
        else:
            document_type_hint = "CONTRACT OR AGREEMENT"
            doc_type_description = "contract or agreement"
        
        # Create a shorter prompt for summary - be very concise but informative
        summary_prompt = f"""
Analyze this contract document and create a brief executive summary (2-3 sentences) in plain English for a non-legal audience.

Contract text (excerpt):
{contract_text[:5000]}

Key clause types detected:
{', '.join([c['type'].replace('_', ' ').title() for c in extracted_clauses[:8]])}

CRITICAL: DOCUMENT TYPE DETECTION
Based on the document content, this appears to be a: {document_type_hint}
You MUST use this exact document type in your summary. DO NOT call it a different type.

INSTRUCTIONS:
1. Identify the EXACT document type - it should be: {doc_type_description}
   - If you see "Sanction Letter", "Loan Sanction", "Letter of Sanction" → It's a LOAN SANCTION LETTER (NOT a lease agreement)
   - If you see "Lease", "Landlord", "Tenant" → It's a LEASE AGREEMENT
   - NEVER confuse these two types
2. Identify the parties involved:
   - For loan: Look for lender (bank name) and borrower/applicant names
   - For lease: Look for landlord/owner and tenant/resident names
   - Format: "from [Lender/Bank] to [Borrower]" for loans OR "between [Landlord] and [Tenant]" for leases
3. Extract the most important terms:
   - Loan amount, rent amount, or contract value (with currency symbols like ₹, $, Rs.)
   - Interest rate (for loans) or payment terms
   - Duration/term (months, years, dates)
4. Write 2-3 clear, complete sentences
5. ONLY use information explicitly stated in the provided text
6. NEVER say "lease agreement" if the document is clearly a loan sanction letter

Example formats:
- Loan Sanction Letter: "This is a loan sanction letter from [Bank Name] to [Borrower Name]. The sanctioned loan amount is [amount] with an interest rate of [rate]% per annum, and a loan tenure of [duration] months, including a [X]-month moratorium period."
- Lease Agreement: "This is a lease agreement between [Landlord] and [Tenant]. The lease term is [duration] with monthly rent of [amount]."
- Service Agreement: "This is a service agreement between [Provider] and [Client]. The agreement covers [service type] with payment terms of [details]."

Provide your summary (use the correct document type: {doc_type_description}):
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a precise legal document analyzer. You ONLY explain information explicitly stated in contracts. You NEVER confuse document types - if you see 'Sanction Letter' or 'Loan Sanction', it's a LOAN SANCTION LETTER (NOT a lease agreement). If you see 'Lease' or 'Landlord/Tenant', it's a LEASE AGREEMENT. Always use the correct document type. Keep summaries brief (2-3 sentences max)."
                },
                {
                    "role": "user",
                    "content": summary_prompt
                }
            ],
            temperature=0.2,  # Even lower for more accuracy and consistency
            max_tokens=250,  # Slightly increased to allow complete sentences
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Error generating contract summary: {str(e)}")
        return generate_basic_summary(extracted_clauses)


def generate_basic_summary(extracted_clauses: List[Dict[str, any]]) -> str:
    """Generate a basic summary without OpenAI (fallback)."""
    if not extracted_clauses:
        return "This contract has been uploaded and analyzed. No key clauses were automatically detected. Please review all terms carefully."
    
    clause_types = [c['type'].replace('_', ' ').title() for c in extracted_clauses[:5]]
    summary = f"This contract contains {len(extracted_clauses)} key clause types including: {', '.join(clause_types)}."
    
    return summary


def summarize_clause_text(clause_text: str, clause_type: str, article_num: Optional[str] = None) -> str:
    """
    Use GPT to create a clear, complete summary sentence for a clause.
    
    This converts raw clause text into a readable, complete sentence that explains
    what the clause says, so users don't see truncated text like "Base Rent: As..."
    
    BEGINNER EXPLANATION:
    ---------------------
    Instead of showing raw text that gets cut off, we ask GPT to create a clear,
    complete sentence that explains what the clause means.
    """
    client = get_openai_client()
    if not client:
        # Fallback: return first complete sentence from the text
        sentences = re.split(r'[.!?]+', clause_text)
        complete_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        if complete_sentences:
            return complete_sentences[0] + "."
        return clause_text[:200] + "..." if len(clause_text) > 200 else clause_text
    
    try:
        article_info = f" from Article {article_num}" if article_num else ""
        clause_type_name = clause_type.replace('_', ' ').title()
        
        # CRITICAL FIX: For very long clauses, provide instruction to split or summarize better
        is_very_long = len(clause_text) > 600
        length_instruction = ""
        if is_very_long:
            length_instruction = "8. If the clause is very long, summarize the KEY points only - focus on numbers, dates, and main obligations."
        
        prompt = f"""Extract and summarize ONLY the {clause_type_name}-related information from the following clause text{article_info} into ONE focused, complete sentence.

Original clause text:
{clause_text[:1200]}

CRITICAL INSTRUCTIONS:
1. Focus ONLY on information related to "{clause_type_name}" - ignore unrelated topics in the text
2. Write ONE complete sentence (not a run-on combining multiple unrelated concepts)
3. Extract the ESSENTIAL {clause_type_name} information only
4. Include specific details if mentioned:
   - Dollar amounts (e.g., "₹45,00,000", "$15,000")
   - Percentages (e.g., "10.05%", "2% per month")
   - Dates (e.g., "December 1, 2010")
   - Durations (e.g., "134 months", "30 days")
5. Use clear, simple language
6. If the text contains multiple unrelated topics, extract ONLY what relates to {clause_type_name}
7. Do not combine different clause types into one sentence (e.g., don't mix "confidentiality" with "interest rate switching")
{length_instruction}
9. If you cannot find {clause_type_name}-specific information in the text, return "NONE" (do not make up information)

EXAMPLES:
- For Payment clause: "The interest rate is 10.05% per annum with an EMI of ₹56,002 due monthly on the 5th of each month."
- NOT: "The interest rate is 10.05% per annum with an EMI of ₹56,002 due monthly, and the sanction letter is confidential and cannot be shared." (mixing payment + confidentiality)

- For Confidentiality clause: "The sanction letter is confidential and cannot be communicated or used without prior written consent from HHFL."
- NOT: "Borrowers can switch interest rates while the sanction letter is confidential." (mixing two different topics)

- For Default Remedies: "Default penalties are set at 2% per month on overdue payments, and material changes in financial status must be disclosed."
- NOT: "Default penalties are 2% per month, jurisdiction is in New Delhi, and prepayment of 25% is allowed." (mixing default + jurisdiction + prepayment)

Now write your focused summary sentence (ONLY {clause_type_name}-related, or "NONE" if no relevant info found):"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert legal document analyst. Your job is to extract ONLY the information related to the specified clause type from legal text and rewrite it as ONE clear, focused sentence. You NEVER combine unrelated topics into one sentence. You ONLY use information explicitly stated in the provided text. You ensure sentences are grammatically complete and include relevant numbers, dates, and amounts when they relate to the clause type."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,  # Lower temperature for more consistent, accurate extraction
            max_tokens=180,  # Slightly reduced to encourage focus and prevent run-on sentences
        )
        
        summary = response.choices[0].message.content.strip()
        # Remove quotes if GPT adds them
        summary = summary.strip('"').strip("'")
        
        # CRITICAL FIX: Filter out fallback statements and "NONE" responses
        summary_lower = summary.lower()
        
        # Check if GPT said "NONE" or similar
        if summary_lower == 'none' or summary_lower.startswith('none'):
            return None
        
        # Check if summary contains phrases that indicate no data was found
        fallback_phrases = [
            'not explicitly stated',
            'not mentioned',
            'not provided',
            'not specified',
            'cannot find',
            'unable to find',
            'not found in',
            'no information',
            'not available',
            'does not contain',
            'lacks information'
        ]
        
        is_fallback = any(phrase in summary_lower for phrase in fallback_phrases)
        
        # If it's a fallback and we have actual clause text, extract real information instead
        if is_fallback and len(clause_text.strip()) > 100:
            # Try to extract actual information from the clause text
            # Look for numbers, dates, amounts in the text
            has_numbers = bool(re.search(r'\$?\d+[,\d]*(?:\.\d+)?%?', clause_text))
            has_dates = bool(re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d+\s+(january|february|march|april|may|june|july|august|september|october|november|december)', clause_text, re.IGNORECASE))
            
            # If we have actual data (numbers/dates), extract first meaningful sentence instead
            if has_numbers or has_dates:
                sentences = re.split(r'[.!?]+', clause_text)
                # Find first sentence with numbers/dates or meaningful content
                for sent in sentences:
                    sent = sent.strip()
                    if len(sent) > 30 and (re.search(r'\$?\d+|amount|fee|payment', sent, re.IGNORECASE) or len(sent) > 50):
                        # Return this sentence as the summary
                        return sent + "."
        
        # Only return fallback if we truly have no information
        if is_fallback:
            # Return None instead of fallback text - will be filtered out later
            return None
        
        return summary
        
    except Exception as e:
        logger.warning(f"Error summarizing clause text: {str(e)}")
        # Fallback: return first complete sentence with actual content
        sentences = re.split(r'[.!?]+', clause_text)
        complete_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        if complete_sentences:
            # Check if first sentence has meaningful content (numbers, dates, or sufficient length)
            first_sent = complete_sentences[0]
            has_content = bool(re.search(r'\$?\d+[,\d]*(?:\.\d+)?%?', first_sent)) or len(first_sent) > 50
            if has_content:
                return first_sent + "."
        # If no good sentence found, return None (will be filtered)
        return None


def add_clause_summaries(extracted_clauses: List[Dict[str, any]]) -> List[Dict[str, any]]:
    """
    Add GPT-generated summary sentences to each clause instance.
    
    This enhances the extracted_clauses structure by adding a 'summary' field
    to each clause instance with a clear, complete sentence explaining it.
    
    CRITICAL FIX: Filters out None summaries (fallback statements) and only keeps
    instances with real summaries to prevent contradictory statements.
    """
    enhanced_clauses = []
    
    for clause_group in extracted_clauses:
        enhanced_group = clause_group.copy()
        enhanced_instances = []
        
        # Only summarize the instances we'll display (top 2-3)
        instances_to_summarize = clause_group['clauses'][:3]
        
        for instance in instances_to_summarize:
            enhanced_instance = instance.copy()
            
            # Generate summary sentence
            summary = summarize_clause_text(
                instance['text'],
                clause_group['type'],
                instance.get('article')
            )
            
            # CRITICAL FIX: Only add summary if it's not None (no fallback)
            # If summary is None, use original text instead (no misleading fallback)
            if summary is not None:
                enhanced_instance['summary'] = summary
                enhanced_instances.append(enhanced_instance)
            else:
                # If no valid summary, still include the instance but without summary
                # Frontend will show the original text
                enhanced_instances.append(enhanced_instance)
        
        # Only keep clause group if it has at least one instance with valid summary
        # or if it has meaningful original text
        if enhanced_instances:
            enhanced_group['clauses'] = enhanced_instances
            enhanced_clauses.append(enhanced_group)
    
    return enhanced_clauses

