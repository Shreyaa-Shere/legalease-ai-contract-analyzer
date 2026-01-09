"""
Celery Tasks for Contract Processing

Background tasks for asynchronous contract analysis.
"""

from celery import shared_task
from django.utils import timezone
import logging
import time
from .models import Contract
from .utils import extract_text_from_file
from .clause_extractor import extract_all_clauses
from .ai_analyzer import analyze_clause_risks, generate_contract_summary, add_clause_summaries

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_contract_task(self, contract_id):
    """
    Process a contract asynchronously: extract text, clauses, and perform AI analysis.
    
    Args:
        contract_id: ID of the Contract to process
        
    Returns:
        dict: Processing status and metadata
        
    Note:
        Retries up to 3 times on failure with exponential backoff.
    """
    
    try:
        # Get the contract from database
        contract = Contract.objects.get(id=contract_id)
        
        logger.info(f"Starting background processing for contract {contract_id}: {contract.title}")
        
        # Update status to processing
        contract.status = 'processing'
        contract.save()
        
        # Step 1: Extract text from file
        if not contract.file or contract.file_type not in ['pdf', 'docx']:
            logger.warning(f"Contract {contract_id} has no file or unsupported file type")
            contract.status = 'error'
            contract.save()
            return {
                'status': 'error',
                'message': 'No file or unsupported file type'
            }
        
        try:
            file_path = contract.file.path
            logger.info(f"Extracting text from {contract.file_type} file: {file_path}")
            
            extracted_text = extract_text_from_file(file_path, contract.file_type)
            
            if not extracted_text:
                logger.warning(f"No text extracted from contract {contract_id}")
                contract.status = 'error'
                contract.save()
                return {
                    'status': 'error',
                    'message': 'No text could be extracted from file'
                }
            
            # Save extracted text immediately so frontend can show it
            contract.extracted_text = extracted_text
            contract.save(update_fields=['extracted_text'])  # Only update this field for speed
            logger.info(f"Successfully extracted {len(extracted_text)} characters from contract {contract_id}")
            
        except Exception as e:
            logger.error(f"Error extracting text from contract {contract_id}: {str(e)}", exc_info=True)
            contract.status = 'error'
            contract.save()
            # Re-raise exception to trigger retry
            raise
        
        # Step 2: Extract clauses
        try:
            logger.info(f"Extracting clauses from contract {contract_id}...")
            extracted_clauses = extract_all_clauses(extracted_text)
            logger.info(f"Found {len(extracted_clauses)} clause types in contract {contract_id}")
            
            # Save clauses immediately (without summaries) so frontend can show them
            contract.extracted_clauses = extracted_clauses
            contract.save(update_fields=['extracted_clauses'])
            logger.info(f"Saved {len(extracted_clauses)} clause types to database")
            
        except Exception as e:
            logger.error(f"Error extracting clauses from contract {contract_id}: {str(e)}", exc_info=True)
            raise
        
        # Step 3: Add GPT summaries to clauses (this takes time, but clauses already saved)
        try:
            logger.info(f"Generating clause summaries for contract {contract_id}...")
            start_time = time.time()
            extracted_clauses = add_clause_summaries(extracted_clauses)
            summary_time = round(time.time() - start_time, 2)
            logger.info(f"Generated summaries in {summary_time}s for contract {contract_id}")
            
            # Update clauses with summaries
            contract.extracted_clauses = extracted_clauses
            contract.save(update_fields=['extracted_clauses'])
            
        except Exception as e:
            logger.warning(f"Error generating clause summaries for contract {contract_id}: {str(e)}", exc_info=True)
            # Continue even if summaries fail (clauses are still saved without summaries)
        
        # Step 4: Analyze risks and generate summary
        analysis_start_time = time.time()
        
        try:
            logger.info(f"Analyzing risks for contract {contract_id}...")
            risk_assessment = analyze_clause_risks(extracted_clauses, extracted_text)
            
            logger.info(f"Generating summary for contract {contract_id}...")
            analysis_summary = generate_contract_summary(extracted_text, extracted_clauses)
            
            # Calculate processing time
            analysis_time = round(time.time() - analysis_start_time, 2)
            
            # Save all analysis results
            contract.extracted_clauses = extracted_clauses
            contract.risk_assessment = risk_assessment
            contract.analysis_summary = analysis_summary
            contract.analysis_metadata = {
                'processing_time_seconds': analysis_time,
                'clause_types_found': len(extracted_clauses),
                'total_clauses': sum(c['count'] for c in extracted_clauses),
                'overall_risk_level': risk_assessment.get('overall_risk_level', 'UNKNOWN') if risk_assessment else 'UNKNOWN',
            }
            contract.status = 'analyzed'
            contract.analyzed_at = timezone.now()
            contract.save()
            
            logger.info(
                f"Successfully analyzed contract {contract_id} in {analysis_time}s. "
                f"Found {len(extracted_clauses)} clause types."
            )
            
            return {
                'status': 'success',
                'contract_id': contract_id,
                'processing_time': analysis_time,
                'clause_types_found': len(extracted_clauses),
            }
            
        except Exception as e:
            logger.error(f"Error during AI analysis for contract {contract_id}: {str(e)}")
            # If analysis fails, save what we have (text and clauses)
            contract.extracted_clauses = extracted_clauses
            contract.status = 'error'
            contract.save()
            # Re-raise to trigger retry
            raise
    
    except Contract.DoesNotExist:
        logger.error(f"Contract {contract_id} not found")
        return {
            'status': 'error',
            'message': f'Contract {contract_id} not found'
        }
    
    except Exception as e:
        # Log the error
        logger.error(f"Error processing contract {contract_id}: {str(e)}", exc_info=True)
        
        # Try to update contract status
        try:
            contract = Contract.objects.get(id=contract_id)
            contract.status = 'error'
            contract.save()
        except:
            pass
        
        # Retry the task (Celery will handle retry logic)
        raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds

