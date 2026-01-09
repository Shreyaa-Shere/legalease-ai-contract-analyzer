"""
Clause Extraction Utility

Extracts key clauses from contract text using pattern matching and regex.
Identifies common legal clauses including auto-renewal, indemnity, termination,
confidentiality, payment terms, liability limitations, dispute resolution, etc.
"""

import re
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


# Define clause patterns - these are regex patterns that match common legal clauses
CLAUSE_PATTERNS = {
    'auto_renewal': {
        'keywords': [
            r'auto.*renew',
            r'automatic.*renewal',
            r'shall.*automatically.*renew',
            r'self.*renew',
            r'evergreen',
            r'renew.*automatically',
        ],
        'description': 'Auto-renewal clauses that automatically extend the contract',
        'risk_level': 'medium',
    },
    'indemnity': {
        'keywords': [
            r'indemnif',
            r'hold.*harmless',
            r'assume.*liability',
            r'defend.*indemnif',
            r'indemnification',
        ],
        'description': 'Indemnity clauses that transfer liability',
        'risk_level': 'high',
    },
    'termination': {
        'keywords': [
            r'terminat',
            r'cancel',
            r'expir',
            r'end.*contract',
            r'breach.*terminat',
            r'early.*terminat',
        ],
        'description': 'Termination and early termination clauses',
        'risk_level': 'medium',
    },
    'confidentiality': {
        'keywords': [
            r'confidential',
            r'non.*disclosure',
            r'nda',
            r'proprietary.*information',
            r'trade.*secret',
        ],
        'description': 'Confidentiality and non-disclosure clauses',
        'risk_level': 'low',
    },
    'payment': {
        'keywords': [
            r'payment.*term',
            r'invoice',
            r'due.*date',
            r'late.*fee',
            r'payment.*schedule',
            r'recurring.*payment',
            r'base.*rent',
            r'monthly.*installment',
            r'rent.*payable',
            r'annual.*rent',
            r'\$\s*\d+.*per',  # Dollar amounts with "per"
            r'payment.*of.*\$\d+',  # Payment of $X
            r'fee.*of.*\$\d+',  # Fee of $X
            r'compensation',  # General compensation
            r'reimbursement',  # Reimbursement terms
            r'cost.*sharing',  # Cost sharing
            r'budget.*allocation',  # Budget allocations
            # Loan-specific payment terms
            r'emi.*payment',  # EMI (Equated Monthly Installment)
            r'equated.*monthly.*installment',
            r'installment.*payment',
            r'loan.*installment',
            r'deviation.*charge',  # Deviation charges in loans
            r'processing.*charge',  # Processing charges
        ],
        'description': 'Payment terms, fees, rent schedules, and financial obligations',
        'risk_level': 'low',
    },
    'security_deposit': {
        'keywords': [
            r'security.*deposit',
            r'security\s+deposit',  # More specific pattern
        ],
        'description': 'Security deposit and refund terms',
        'risk_level': 'low',
    },
    'rent_increase': {
        'keywords': [
            r'rent.*increas',
            r'escalat',
            r'rent.*adjust',
            r'annual.*increas',
            r'year.*over.*year',
        ],
        'description': 'Rent escalation and increase clauses',
        'risk_level': 'medium',
    },
    'subletting': {
        'keywords': [
            r'assignment.*subletting',
            r'article\s+\d+.*assignment.*sublet',
            r'sublet.*premises',
            r'assign.*lease',
            r'consent.*sublet',
            r'consent.*assignment',
        ],
        'description': 'Subletting and assignment restrictions',
        'risk_level': 'medium',
    },
    'default_remedies': {
        'keywords': [
            r'default.*under.*lease',
            r'default.*breach',
            r'default.*remed',
            r'article\s+\d+.*default',  # Article-specific
            r'default.*terminat',
            r'remedies.*default',
        ],
        'description': 'Default, breach, and remedy provisions',
        'risk_level': 'high',
    },
    'liability': {
        'keywords': [
            r'limitation.*liability',
            r'exclude.*liability',
            r'no.*liability',
            r'liability.*cap',
            r'consequential.*damages',
            r'indirect.*damages',
        ],
        'description': 'Liability limitation clauses',
        'risk_level': 'medium',
    },
    'dispute_resolution': {
        'keywords': [
            r'dispute.*resolution',
            r'arbitration',
            r'mediation',
            r'jurisdiction',
            r'governing.*law',
            r'venue',
        ],
        'description': 'Dispute resolution and jurisdiction clauses',
        'risk_level': 'medium',
    },
    'force_majeure': {
        'keywords': [
            r'force.*majeure',
            r'act.*god',
            r'unforeseeable.*circumstance',
            r'natural.*disaster',
        ],
        'description': 'Force majeure clauses for unforeseeable circumstances',
        'risk_level': 'low',
    },
    'intellectual_property': {
        'keywords': [
            r'intellectual.*property',
            r'ip.*rights',
            r'copyright',
            r'trademark',
            r'patent',
            r'ownership.*work',
        ],
        'description': 'Intellectual property and ownership clauses',
        'risk_level': 'medium',
    },
    'warranty': {
        'keywords': [
            r'warrant',
            r'guarantee',
            r'warranty.*period',
            r'as.*is',
            r'no.*warranty',
            r'disclaim.*warranty',
        ],
        'description': 'Warranty and guarantee clauses',
        'risk_level': 'medium',
    },
    # Additional patterns for broader document types
    'duration_term': {
        'keywords': [
            r'term.*of.*\d+',
            r'duration.*\d+',
            r'commencement.*date',
            r'expiration.*date',
            r'effective.*date',
            r'period.*of.*performance',
            r'agreement.*period',
            r'contract.*term',
            r'lease.*term',
        ],
        'description': 'Contract duration, term, and effective dates',
        'risk_level': 'low',
    },
    'obligations_duties': {
        'keywords': [
            r'obligation',
            r'shall.*provide',
            r'shall.*perform',
            r'responsibility',
            r'duty.*to',
            r'must.*deliver',
            r'required.*to',
            r'shall.*maintain',
        ],
        'description': 'Key obligations and duties of parties',
        'risk_level': 'medium',
    },
    'modifications_amendments': {
        'keywords': [
            r'amendment',
            r'modification',
            r'amend.*this.*agreement',
            r'change.*to.*agreement',
            r'revised.*agreement',
            r'supplement.*to',
        ],
        'description': 'Amendment and modification procedures',
        'risk_level': 'low',
    },
    'data_information': {
        'keywords': [
            r'data.*provide',
            r'information.*submit',
            r'report.*requirement',
            r'annual.*report',
            r'data.*collection',
            r'information.*sharing',
        ],
        'description': 'Data submission and reporting requirements',
        'risk_level': 'low',
    },
    'calculation_methodology': {
        'keywords': [
            r'calculation.*method',
            r'formula',
            r'compute',
            r'weighted.*average',
            r'methodology',
            r'determine.*by',
        ],
        'description': 'Calculation methods and formulas',
        'risk_level': 'low',
    },
    'interest_rate': {
        'keywords': [
            r'rate.*of.*interest',
            r'interest.*rate',
            r'floating.*rate',
            r'fixed.*rate',
            r'eblr',  # External Benchmark Lending Rate
            r'base.*rate',
            r'spread.*over',
            r'interest.*linked',
            r'rate.*linked.*to',
            r'percent.*per.*annum',
            r'%.*per.*annum',
            r'%.*p\.?a\.?',  # % p.a. or % pa
            r'annual.*percentage.*rate',
            r'apr',
            r'simple.*rate.*interest',
            r'compound.*interest',
            r'rate.*reset',
            r'rate.*review',
        ],
        'description': 'Interest rate, floating/fixed rates, and rate calculation methods',
        'risk_level': 'medium',
    },
    'loan_tenure': {
        'keywords': [
            r'loan.*tenure',
            r'loan.*term',
            r'tenure.*of.*loan',
            r'term.*of.*loan',
            r'repayment.*period',
            r'loan.*duration',
            r'loan.*period',
            r'tenor.*of.*loan',
            r'repayment.*tenure',
            r'\d+\s*months.*repayment',  # "216 months" repayment
            r'\d+\s*years.*repayment',
        ],
        'description': 'Loan tenure, repayment period, and loan duration',
        'risk_level': 'low',
    },
    'moratorium': {
        'keywords': [
            r'moratorium.*period',
            r'moratorium',
            r'grace.*period',
            r'repayment.*holiday',
            r'payment.*holiday',
            r'deferment.*period',
            r'interest.*only.*period',
            r'course.*period',  # For education loans - course + moratorium
            r'course.*and.*moratorium',
        ],
        'description': 'Moratorium period, grace period, and payment deferment',
        'risk_level': 'medium',
    },
    'penal_interest': {
        'keywords': [
            r'penal.*interest',
            r'penalty.*interest',
            r'overdue.*interest',
            r'default.*interest',
            r'penal.*charge',
            r'penalty.*charge',
            r'overdue.*charge',
            r'default.*charge',
            r'%.*on.*overdue',  # "% on overdue"
            r'penal.*@.*\d+%',  # "penal @ 2%"
            r'penalty.*@.*\d+%',
        ],
        'description': 'Penal interest, penalty charges, and overdue/default charges',
        'risk_level': 'high',
    },
    'security_collateral': {
        'keywords': [
            r'security.*document',
            r'collateral',
            r'mortgage',
            r'secured.*loan',
            r'security.*deposit',
            r'hypothecat',  # Hypothecation (for movable assets)
            r'pledge',
            r'guarantor',
            r'guarantee',
            r'collateral.*coverag',
            r'margin.*money',
            r'property.*mortgag',
            r'security.*for.*loan',
            r'documents.*to.*be.*execut',  # "documents to be executed"
            r'simple.*mortgage',
            r'mortgage.*deed',
        ],
        'description': 'Security, collateral, mortgage, and guarantee requirements',
        'risk_level': 'medium',
    },
    'prepayment': {
        'keywords': [
            r'prepayment',
            r'pre.*payment',
            r'pre.*payment.*charge',
            r'prepayment.*charge',
            r'early.*payment',
            r'early.*repayment',
            r'part.*prepayment',
            r'full.*prepayment',
            r'foreclosur',  # Foreclosure of loan
            r'switchover',  # Rate switchover charges
            r'pre.*payment.*penalty',
            r'foreclosure.*charge',
        ],
        'description': 'Prepayment charges, foreclosure charges, and early repayment terms',
        'risk_level': 'low',
    },
    'insurance_requirement': {
        'keywords': [
            r'life.*insurance',
            r'insurance.*policy',
            r'insurance.*requirement',
            r'term.*life.*insurance',
            r'insurance.*premium',
            r'policy.*assign',
            r'insurance.*coverag',
            r'insurance.*mandatory',
            r'compulsory.*insurance',
            r'health.*insurance',  # For education loans
            r'medical.*insurance',
        ],
        'description': 'Insurance requirements, life insurance, and policy assignment',
        'risk_level': 'medium',
    },
    'disbursement': {
        'keywords': [
            r'disbursement',
            r'disburse.*loan',
            r'release.*of.*loan',
            r'loan.*disbursement',
            r'disbursement.*condition',
            r'disbursement.*stage',
            r'staged.*disbursement',
            r'disbursement.*to.*institution',
            r'payment.*to.*vendor',
            r'demand.*draft',  # DD for disbursement
            r'neft',  # NEFT transfer
            r'rtgs',  # RTGS transfer
        ],
        'description': 'Loan disbursement conditions, stages, and payment methods',
        'risk_level': 'low',
    },
}


def extract_clause_context(text: str, pattern: str, context_chars: int = 500) -> List[Dict[str, str]]:
    """
    Extract clauses matching a pattern with surrounding context.
    Improved to extract complete sentences/paragraphs around matches.
    
    BEGINNER EXPLANATION:
    ---------------------
    When we find a clause keyword (like "auto-renewal"), we don't just want
    that one word - we want the entire sentence or paragraph that explains it.
    
    IMPROVEMENTS:
    - Tries to extract complete sentences
    - Looks for article headers to provide better context
    - Centers the snippet around the actual clause content
    
    PARAMETERS:
    -----------
    text: The contract text to search in
    pattern: Regex pattern to search for
    context_chars: How many characters before/after to include (default 500)
    
    RETURNS:
    --------
    List of dictionaries, each containing:
    - 'text': The extracted clause with context
    - 'match': The exact match found
    - 'position': Where in the document it was found
    - 'article': Article number if found nearby
    """
    matches = []
    
    # Find all matches (case-insensitive)
    for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
        start_pos = match.start()
        end_pos = match.end()
        
        # Try to find the start of the sentence
        sentence_start = start_pos
        # Look backwards for sentence start (period, newline, or article header)
        for i in range(max(0, start_pos - context_chars), start_pos):
            if text[i] in '.!\n':
                # Found sentence boundary, move a bit forward to skip the punctuation
                sentence_start = i + 1
                break
            # Also check for article headers
            if i > 0 and text[i-1:i+20].upper().startswith('ARTICLE'):
                sentence_start = i - 1
                break
        
        # Try to find the end of the sentence/paragraph
        # CRITICAL FIX: Better boundary detection to stop at section breaks, numbered items
        sentence_end = end_pos
        search_end = min(len(text), end_pos + context_chars)
        
        # Look for natural stopping points (section breaks, numbered items)
        for i in range(end_pos, search_end):
            # Stop at numbered list items (e.g., "6. Resident agrees" or "7.")
            if i < len(text) - 2:
                # Check for numbered list pattern: digit followed by period and space
                if text[i].isdigit() and i > 0 and text[i-1] in '.)\n' and i+1 < len(text) and text[i+1] in '. ':
                    # Found numbered item - stop before it
                    sentence_end = i - 1
                    # Find the last sentence end before this
                    for j in range(i-1, max(end_pos, i-100), -1):
                        if text[j] in '.!':
                            sentence_end = j + 1
                            break
                    break
            
            # Stop at section headers (all caps words followed by colon) - but only if we've got enough context
            if i < len(text) - 20 and i > end_pos + 30:
                # Look for patterns like "PAYMENT:", "TERM:", "Special Terms and Conditions:", etc.
                # Check for section headers (all caps followed by colon or specific section markers)
                section_header_patterns = [
                    r'[A-Z\s]{5,}:',  # All caps section headers like "PAYMENT:", "SPECIAL TERMS:"
                    r'Special\s+Terms',  # "Special Terms and Conditions"
                    r'Pre\s+Disbursment',  # "Pre Disbursment" section
                    r'Post\s+Disbursment',  # "Post Disbursment" section
                ]
                found_section_header = False
                for pattern in section_header_patterns:
                    if re.search(pattern, text[i:i+40], re.IGNORECASE):
                        # Found section header - stop before it
                        sentence_end = i
                        # Find the last sentence end
                        for j in range(i-1, max(end_pos, i-50), -1):
                            if text[j] in '.!':
                                sentence_end = j + 1
                                break
                        found_section_header = True
                        break
                if found_section_header:  # If we found a section header, break out of loop
                    break
            
            # Original sentence end detection
            if text[i] in '.\n':
                # Found sentence boundary
                sentence_end = i + 1
                # If it's a period, check if next char is capital (likely end of sentence)
                if i + 1 < len(text) and text[i+1].isspace():
                    if i + 2 < len(text) and text[i+2].isupper():
                        sentence_end = i + 1
                        break
        
        # Extract the clause text
        clause_text = text[sentence_start:sentence_end].strip()
        
        # If we got a very short snippet, expand it with more context
        if len(clause_text) < 100:
            context_start = max(0, start_pos - context_chars)
            context_end = min(len(text), end_pos + context_chars)
            clause_text = text[context_start:context_end].strip()
        
        # Remove page number markers and table of contents patterns
        clause_text = re.sub(r'---\s*Page\s+\d+\s*---', '', clause_text, flags=re.IGNORECASE)
        clause_text = re.sub(r'^\s*\|\s*ARTICLE\s+\d+\.\s*\|\s*[A-Z\s]+\s*\|\s*\d+\s*\|\s*$', '', clause_text, flags=re.IGNORECASE | re.MULTILINE)
        
        # CRITICAL FIX: Clean up stray numbers and punctuation that got included from poor boundaries
        # Remove leading standalone numbers (e.g., "6. Resident agrees" -> "Resident agrees")
        clause_text = re.sub(r'^\s*\d+\.\s+', '', clause_text)
        # Remove trailing incomplete fragments (e.g., "submitted.6." -> "submitted.")
        clause_text = re.sub(r'\.(\d+)\.\s*$', '.', clause_text)
        
        # CRITICAL FIX: Remove incomplete text at the end (section headers, table markers, etc.)
        # Remove text ending with incomplete section headers like "SP-ecial Terms" or "Pre Disbursment S."
        clause_text = re.sub(r'\s+SP[-\s]?ecial\s+Terms.*$', '', clause_text, flags=re.IGNORECASE)
        clause_text = re.sub(r'\s+Pre\s+Disbursment.*$', '', clause_text, flags=re.IGNORECASE)
        clause_text = re.sub(r'\s+Post\s+Disbursment.*$', '', clause_text, flags=re.IGNORECASE)
        # Remove incomplete sentences ending with single letters (like "S." from "Pre Disbursment S.")
        clause_text = re.sub(r'\s+[A-Z]\.\s*$', '', clause_text)
        # Remove "The aforesaid sanction" type phrases that appear at the start of new sections
        if re.search(r'^The\s+aforesaid\s+sanction.*terms\s+and\s+conditions:', clause_text, re.IGNORECASE):
            # This is usually a section header, not part of the clause
            clause_text = re.sub(r'^The\s+aforesaid\s+sanction.*terms\s+and\s+conditions:.*?\n', '', clause_text, flags=re.IGNORECASE | re.DOTALL)
        
        # CRITICAL FIX: Remove loan application details that shouldn't be in prepayment clauses
        # These patterns indicate loan application/approval details, not prepayment terms
        loan_detail_patterns = [
            r'RIZONA\s+STATE\s+UNIVERSITY.*?GUJARAT',  # University/course details
            r'Purpose\s+of\s+loan.*?GUJARAT',  # Purpose of loan section
            r'Loan\s+Tenure\s+\d+.*?Moratorium\s+Period\s+\d+',  # Loan tenure table
            r'Interest\s+Type.*?Processing\s+charges',  # Interest/charges table
        ]
        for pattern in loan_detail_patterns:
            clause_text = re.sub(pattern, '', clause_text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove any remaining table-like structures or loan application details
        # Look for patterns that suggest we've captured too much (e.g., loan application form fields)
        if re.search(r'Applicant|Co-applicant|Guarantor|Nature\s+of\s+loan|Sanction\s+Amount', clause_text, re.IGNORECASE):
            # This looks like loan application details - try to extract only the prepayment-related part
            # Find the last sentence that mentions prepayment/foreclosure/switchover
            prepayment_sentences = []
            sentences = re.split(r'[.!?]\s+', clause_text)
            for sentence in sentences:
                if re.search(r'prepayment|foreclosur|switchover|fixed\s+rate|floating\s+rate', sentence, re.IGNORECASE):
                    prepayment_sentences.append(sentence)
            if prepayment_sentences:
                # Keep only sentences related to prepayment
                clause_text = '. '.join(prepayment_sentences) + '.'
        
        # Remove fragments that start mid-sentence (e.g., "amount which shall" -> should be filtered)
        if len(clause_text) > 0 and not clause_text[0].isupper() and not clause_text[0].isdigit():
            # If it doesn't start with capital or number, check if it's a complete thought
            # Look for proper sentence start indicators
            if not re.match(r'^(the|a|an|this|that|resident|management|landlord|tenant|borrower)', clause_text[:20], re.IGNORECASE):
                # Might be a fragment - try to find a better start
                first_cap = re.search(r'[A-Z]', clause_text)
                if first_cap and first_cap.start() > 0:
                    # Remove everything before first capital letter
                    clause_text = clause_text[first_cap.start():]
        
        # Clean up whitespace (multiple spaces/newlines become single, but preserve structure)
        clause_text = re.sub(r'[ \t]+', ' ', clause_text)  # Multiple spaces -> single
        clause_text = re.sub(r'\n\s*\n+', '\n\n', clause_text)  # Multiple newlines -> double
        clause_text = clause_text.strip()
        
        # Try to extract article number if nearby
        article_match = re.search(r'ARTICLE\s+(\d+)', text[max(0, start_pos-200):start_pos+100], re.IGNORECASE)
        article_num = article_match.group(1) if article_match else None
        
        # Limit text length but ensure we capture complete sentences
        # Increased to 1200 to capture more context for better summarization
        if len(clause_text) > 1200:
            # Try to find a good breaking point (sentence end)
            truncated = clause_text[:1200]
            last_period = truncated.rfind('.')
            if last_period > 900:  # If we have a period reasonably close to the end
                clause_text = truncated[:last_period + 1]
            else:
                # If no period found, look for newline as paragraph break
                last_newline = truncated.rfind('\n')
                if last_newline > 900:
                    clause_text = truncated[:last_newline]
                else:
                    clause_text = truncated + "..."
        
        matches.append({
            'text': clause_text,
            'match': match.group(),
            'position': start_pos,
            'article': article_num,
        })
    
    return matches


def extract_all_clauses(contract_text: str) -> List[Dict[str, any]]:
    """
    Extract all key clauses from contract text.
    
    BEGINNER EXPLANATION:
    ---------------------
    This is the main function that finds all important clauses in a contract.
    
    HOW IT WORKS:
    1. Goes through each clause type (auto-renewal, indemnity, etc.)
    2. For each type, searches for matching keywords
    3. Extracts the clause text with context
    4. Returns a list of all found clauses
    
    PARAMETERS:
    -----------
    contract_text: The full extracted text from the contract
    
    RETURNS:
    --------
    List of dictionaries, each containing:
    - 'type': Type of clause (e.g., 'auto_renewal')
    - 'description': Human-readable description
    - 'risk_level': Risk level (low/medium/high)
    - 'clauses': List of found clause instances with text
    - 'count': Number of times this clause type appears
    """
    if not contract_text:
        logger.warning("Empty contract text provided for clause extraction")
        return []
    
    extracted_clauses = []
    
    # Go through each clause type
    for clause_type, clause_info in CLAUSE_PATTERNS.items():
        found_clauses = []
        
        # Search for each keyword pattern for this clause type
        for keyword_pattern in clause_info['keywords']:
            # Compile pattern with word boundaries to avoid partial matches
            # e.g., "renew" won't match "renewable" unless we want it to
            pattern = r'\b' + keyword_pattern + r'\b'
            
            # Extract all matches with context
            matches = extract_clause_context(contract_text, pattern)
            
            # Add to found clauses (avoid duplicates and filter irrelevant ones)
            for match in matches:
                # Filter out irrelevant matches
                if not is_relevant_clause(match, clause_type):
                    continue
                
                # Check if we already have this clause (improved duplicate detection)
                is_duplicate = False
                for existing in found_clauses:
                    # Check if texts are very similar (fuzzy duplicate detection)
                    if texts_similar(existing['text'], match['text'], threshold=0.7):
                        is_duplicate = True
                        break
                    # Also check if positions are very close (same clause mentioned twice)
                    if abs(existing['position'] - match['position']) < 200:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    found_clauses.append(match)
        
        # Sort by article number (prioritize article-based matches) and limit instances
        found_clauses = prioritize_and_limit_clauses(found_clauses, clause_type)
        
        # Only add if we found at least one instance
        if found_clauses:
            extracted_clauses.append({
                'type': clause_type,
                'description': clause_info['description'],
                'risk_level': clause_info['risk_level'],
                'clauses': found_clauses,
                'count': len(found_clauses),
            })
    
    logger.info(f"Extracted {len(extracted_clauses)} clause types with {sum(c['count'] for c in extracted_clauses)} total clauses")
    
    return extracted_clauses


def is_relevant_clause(match: Dict[str, str], clause_type: str) -> bool:
    """
    Filter out irrelevant clause matches.
    
    CRITICAL FIX: Enhanced filtering to detect and handle addendums/riders better.
    
    Filters:
    - Table of contents entries
    - Page numbers only
    - Very short snippets
    - Cross-references without context
    - Definition-only mentions
    - Addendum/rider-specific clauses that may not be core terms
    """
    text = match['text'].lower()
    original_text = match['text']  # Keep original for better checking
    
    # Filter out table of contents patterns
    if re.search(r'^\s*article\s+\d+\.\s*\w+\s+\d+\s*$', text, re.IGNORECASE):
        return False
    
    # Filter out if it's just a page number reference
    if re.search(r'^(page|p\.?)\s*\d+$', text.strip()):
        return False
    
    # Filter out very short snippets (likely just a mention, not the actual clause)
    if len(text.strip()) < 50:
        return False
    
    # Filter out if it's just a section number reference (e.g., "Section 3.02" without context)
    if re.match(r'^\s*section\s+\d+\.\d+\.?\s*$', text.strip(), re.IGNORECASE):
        return False
    
    # Filter out if text is mostly just article titles without content
    if re.match(r'^\s*article\s+\d+\.\s*[A-Z\s]+$', text, re.IGNORECASE):
        return False
    
    # CRITICAL FIX: Detect addendum/rider-specific clauses
    # These are often too specific and may not be core contract terms
    addendum_keywords = [
        r'valet\s+trash',
        r'bicycle.*rider',
        r'storage.*unit',
        r'pet.*addendum',
        r'pool.*area',
        r'amenity.*space',
        r'parking.*permit',
        r'garage.*space',
        r'containers?.*trash',  # Trash container rules
        r'rider.*bicycle',  # Bicycle rider addendum
    ]
    
    # Check if this looks like an addendum-specific clause
    # If it's a very specific addendum clause AND doesn't have core contract terms, filter it
    is_addendum_specific = any(re.search(pattern, text, re.IGNORECASE) for pattern in addendum_keywords)
    
    if is_addendum_specific:
        # Only keep if it also contains core contract information (amounts, dates, obligations)
        # AND the clause type matches (e.g., payment for fees, liability for damages)
        has_core_info = bool(
            re.search(r'\$\s*\d+|amount|fee|deposit|rent|term|obligation|liability', text, re.IGNORECASE) or
            re.search(r'\d+\s*(month|year|day)', text, re.IGNORECASE) or
            len(original_text) > 200  # Long enough to contain substantial info
        )
        
        # Additional check: for very specific addendums (bicycle, trash), be more strict
        is_very_specific = bool(
            re.search(r'bicycle|rider.*bicycle|trash.*container', text, re.IGNORECASE)
        )
        if is_very_specific:
            # Only keep if it has significant financial/legal implications
            has_significant_impact = bool(
                re.search(r'\$\s*\d+|liability|damage|responsible|obligation', text, re.IGNORECASE) and
                len(original_text) > 100
            )
            if not has_significant_impact:
                return False
        
        if not has_core_info:
            return False
    
    # For certain clause types, require more specific context
    if clause_type == 'security_deposit':
        # Security deposit should mention amount or refund
        if not re.search(r'\$\s*\d+|amount|refund|deposit', text, re.IGNORECASE):
            return False
    
    if clause_type == 'rent_increase':
        # Rent increase should mention percentage, dollar amount, or escalation
        if not re.search(r'\d+%|increas|escalat|\$\s*\d+.*per|annum|annual', text, re.IGNORECASE):
            return False
    
    if clause_type == 'duration_term':
        # Duration/term should have actual dates, months, or time periods
        # CRITICAL FIX: Exclude payment-related text from duration clauses
        has_payment_keywords = bool(
            re.search(r'payment|fee|amount.*disclose|invoice|due.*date', text, re.IGNORECASE)
        )
        
        has_duration = bool(
            re.search(r'\d+\s*(month|year|day)', text, re.IGNORECASE) or
            re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text) or
            re.search(r'commenc|start|begin|end|expir|terminat', text, re.IGNORECASE)
        )
        
        # If it has payment keywords but no duration, it's likely not a duration clause
        if has_payment_keywords and not has_duration:
            return False
        
        if not has_duration:
            return False
    
    if clause_type == 'payment':
        # Payment clauses should have amounts, fees, or payment terms
        # CRITICAL FIX: Exclude warranty/guarantee text from payment clauses
        is_warranty_text = bool(
            re.search(r'\bwarrant\b(?!.*fee)|\bguarantee\b(?!.*payment)', text, re.IGNORECASE) or
            re.search(r'fair.*reasonable.*compensation', text, re.IGNORECASE)
        )
        # But allow if it's clearly about payment-related fees
        has_fee_in_warranty = bool(
            re.search(r'(late\s+fee|reversal\s+fee|nsf\s+charge|payment.*fee)', text, re.IGNORECASE)
        )
        
        has_payment_info = bool(
            re.search(r'[\$\₹]\s*\d+|amount|fee|payment|rent|installment|emi', text, re.IGNORECASE) or
            re.search(r'per\s+month|monthly|annual|due\s+date', text, re.IGNORECASE) or
            re.search(r'deviation.*charge|processing.*charge', text, re.IGNORECASE)
        )
        
        # If it's warranty text without payment context, exclude it
        if is_warranty_text and not has_fee_in_warranty:
            return False
        
        if not has_payment_info:
            return False
    
    if clause_type == 'warranty':
        # CRITICAL FIX: Exclude payment/late fee text and trash/fine rules from warranty clauses
        # Warranty clauses should be about guarantees/warranties, not payment terms or rules
        
        # Exclude payment-related text
        is_payment_text = bool(
            re.search(r'late\s+fee|reversal\s+fee|nsf\s+charge|payment.*due|invoice', text, re.IGNORECASE) and
            not re.search(r'\bwarrant\b|\bguarantee\b', text, re.IGNORECASE)
        )
        
        # Exclude trash container/fine rules (common false positives)
        is_trash_fine_rule = bool(
            re.search(r'containers?.*trash|trash.*container|fine.*per.*bag|violation.*fine', text, re.IGNORECASE)
        )
        
        # Ensure it's actually about warranties/guarantees
        # Look for actual warranty/guarantee language, not just the word "warrant" in other contexts
        has_warranty_language = bool(
            re.search(r'\bwarrant(?:y|ies)\b', text, re.IGNORECASE) or  # "warranty" or "warranties"
            re.search(r'\bguarantee\b', text, re.IGNORECASE) or
            re.search(r'\bwarrant\b.*\b(?:product|service|workmanship|condition)', text, re.IGNORECASE) or  # "warrant product/service"
            re.search(r'(?:no|disclaim).*warrant', text, re.IGNORECASE) or  # "no warranty", "disclaim warranty"
            re.search(r'as.*is.*warrant', text, re.IGNORECASE)  # "as is" warranty
        )
        
        # If it's payment-related, trash rules, or doesn't have actual warranty language, exclude it
        if is_payment_text or is_trash_fine_rule:
            return False
        
        # Only keep if it has actual warranty/guarantee language
        if not has_warranty_language:
            return False
    
    if clause_type == 'interest_rate':
        # Interest rate clauses should mention rates, percentages, or rate calculation
        has_rate_info = bool(
            re.search(r'\d+\.?\d*%|percent|rate.*of.*interest|interest.*rate|eblr|spread', text, re.IGNORECASE) or
            re.search(r'floating|fixed.*rate', text, re.IGNORECASE)
        )
        if not has_rate_info:
            return False
    
    if clause_type == 'loan_tenure':
        # Loan tenure should mention duration, months, years, or repayment period
        has_tenure_info = bool(
            re.search(r'\d+\s*(month|year)', text, re.IGNORECASE) or
            re.search(r'tenure|term.*of.*loan|repayment.*period', text, re.IGNORECASE)
        )
        if not has_tenure_info:
            return False
    
    if clause_type == 'moratorium':
        # Moratorium clauses should mention moratorium, grace period, or deferment
        has_moratorium_info = bool(
            re.search(r'moratorium|grace.*period|deferment|payment.*holiday', text, re.IGNORECASE) or
            re.search(r'\d+\s*(month|year).*moratorium', text, re.IGNORECASE)
        )
        if not has_moratorium_info:
            return False
    
    if clause_type == 'penal_interest':
        # Penal interest should mention penalty, overdue, or default charges
        has_penal_info = bool(
            re.search(r'penal.*interest|penalty.*interest|overdue|default.*interest', text, re.IGNORECASE) or
            re.search(r'\d+%.*overdue|\d+%.*penal', text, re.IGNORECASE)
        )
        if not has_penal_info:
            return False
    
    if clause_type == 'security_collateral':
        # Security/collateral should mention security, mortgage, collateral, or guarantee
        has_security_info = bool(
            re.search(r'security|collateral|mortgage|hypothecat|guarantor|guarantee', text, re.IGNORECASE) or
            re.search(r'security.*document|mortgage.*deed', text, re.IGNORECASE)
        )
        # Exclude if it's just a mention in a different context (e.g., "security deposit" for leases)
        if clause_type == 'security_collateral' and re.search(r'security.*deposit.*refund', text, re.IGNORECASE):
            # This is likely a lease security deposit, not loan collateral
            if not re.search(r'loan|mortgage|collateral', text, re.IGNORECASE):
                return False
        if not has_security_info:
            return False
    
    if clause_type == 'prepayment':
        # Prepayment should mention prepayment, foreclosure, or early repayment
        has_prepayment_info = bool(
            re.search(r'prepayment|foreclosur|early.*repayment|switchover', text, re.IGNORECASE) or
            re.search(r'pre.*payment.*charge', text, re.IGNORECASE)
        )
        if not has_prepayment_info:
            return False
    
    if clause_type == 'insurance_requirement':
        # Insurance should mention insurance, policy, or premium
        has_insurance_info = bool(
            re.search(r'insurance|policy|premium', text, re.IGNORECASE) or
            re.search(r'life.*insurance|term.*life', text, re.IGNORECASE)
        )
        if not has_insurance_info:
            return False
    
    if clause_type == 'disbursement':
        # Disbursement should mention disbursement, release, or payment stages
        has_disbursement_info = bool(
            re.search(r'disbursement|release.*loan|disburse', text, re.IGNORECASE) or
            re.search(r'staged.*disbursement|demand.*draft|neft|rtgs', text, re.IGNORECASE)
        )
        if not has_disbursement_info:
            return False
    
    return True


def texts_similar(text1: str, text2: str, threshold: float = 0.7) -> bool:
    """
    Check if two texts are similar (fuzzy duplicate detection).
    Uses simple word overlap to determine similarity.
    """
    # Normalize texts
    words1 = set(re.findall(r'\w+', text1.lower()))
    words2 = set(re.findall(r'\w+', text2.lower()))
    
    if not words1 or not words2:
        return False
    
    # Calculate Jaccard similarity (intersection over union)
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    similarity = intersection / union if union > 0 else 0
    
    return similarity >= threshold


def prioritize_and_limit_clauses(clauses: List[Dict[str, any]], clause_type: str) -> List[Dict[str, any]]:
    """
    Prioritize clauses with article numbers and limit the number returned.
    
    Prioritization:
    1. Clauses with article numbers (actual article sections)
    2. Longer, more detailed clauses (more context)
    3. Limit to top 3-4 most relevant instances (reduced for cleaner UI)
    """
    if not clauses:
        return []
    
    # Separate clauses with and without article numbers
    with_article = [c for c in clauses if c.get('article')]
    without_article = [c for c in clauses if not c.get('article')]
    
    # Sort by article number for those with articles
    with_article.sort(key=lambda x: (int(x['article']) if x.get('article') and x['article'].isdigit() else 999, x['position']))
    
    # Sort without articles by text length (longer = more context)
    without_article.sort(key=lambda x: len(x['text']), reverse=True)
    
    # Combine: article-based first, then others
    prioritized = with_article + without_article
    
    # Limit to top instances - REDUCED for cleaner display
    limits = {
        'default_remedies': 3,
        'subletting': 2,
        'security_deposit': 2,
        'payment': 3,
        'indemnity': 2,
        'liability': 2,
        'rent_increase': 2,
        'dispute_resolution': 2,
        'warranty': 2,
        'duration_term': 2,
        'obligations_duties': 3,
        'modifications_amendments': 2,
        'data_information': 2,
        'calculation_methodology': 2,
        # Loan-specific clauses
        'interest_rate': 2,
        'loan_tenure': 2,
        'moratorium': 2,
        'penal_interest': 2,
        'security_collateral': 3,
        'prepayment': 2,
        'insurance_requirement': 2,
        'disbursement': 2,
    }
    
    limit = limits.get(clause_type, 3)  # Default to 3 max
    return prioritized[:limit]


def get_clause_summary(extracted_clauses: List[Dict[str, any]]) -> str:
    """
    Generate a simple text summary of extracted clauses.
    
    BEGINNER EXPLANATION:
    ---------------------
    Converts the structured clause data into a readable text summary.
    This is useful for displaying in the UI or for AI analysis.
    """
    if not extracted_clauses:
        return "No key clauses detected in this contract."
    
    summary_parts = []
    
    for clause_data in extracted_clauses:
        clause_type = clause_data['type'].replace('_', ' ').title()
        count = clause_data['count']
        risk = clause_data['risk_level'].upper()
        
        summary_parts.append(f"- {clause_type}: Found {count} instance(s) (Risk: {risk})")
    
    return "\n".join(summary_parts)

