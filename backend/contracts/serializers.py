from rest_framework import serializers
from .models import Contract
from .utils import extract_text_from_file  # Import our text extraction function
from .clause_extractor import extract_all_clauses  # Import clause extraction
from .ai_analyzer import analyze_clause_risks, generate_contract_summary, add_clause_summaries  # Import AI analysis
from django.utils import timezone
import logging
import time

logger = logging.getLogger(__name__)


class ContractSerializer(serializers.ModelSerializer):
    """
    Serializer for Contract model.
    
    Serializers convert Django model instances to JSON (for API responses)
    and JSON to model instances (for API requests).
    
    Think of it as a translator between Python objects and JSON.
    """
    
    # Add computed/read-only fields
    file_size_mb = serializers.ReadOnlyField()
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = Contract
        fields = [
            'id',
            'title',
            'description',
            'file',
            'file_name',
            'file_size',
            'file_size_mb',
            'file_type',
            'status',
            'uploaded_at',
            'analyzed_at',
            'updated_at',
            'uploaded_by',
            'uploaded_by_username',
            'extracted_text',
            'analysis_summary',
            'extracted_clauses',
            'risk_assessment',
            'analysis_metadata',
        ]
        read_only_fields = [
            'id',
            'uploaded_at',
            'analyzed_at',
            'updated_at',
            'uploaded_by',
            'file_name',
            'file_size',
            'file_type',
            'extracted_text',
            'analysis_summary',
            'extracted_clauses',
            'risk_assessment',
            'analysis_metadata',
        ]
    
    def create(self, validated_data):
        """
        Override create method to set uploaded_by from request user
        and extract file metadata.
        """
        # Get the user from the request context
        user = self.context['request'].user
        
        # Get the uploaded file
        file = validated_data.get('file')
        
        # Create contract instance (don't save yet)
        contract = Contract(
            title=validated_data['title'],
            description=validated_data.get('description', ''),
            file=file,
            uploaded_by=user,
        )
        
        # Extract and set file metadata
        if file:
            contract.file_name = file.name
            contract.file_size = file.size
            
            # Determine file type
            file_extension = file.name.lower().split('.')[-1]
            if file_extension == 'pdf':
                contract.file_type = 'pdf'
            elif file_extension == 'docx':
                contract.file_type = 'docx'
        
        # Set initial status
        contract.status = 'uploaded'
        
        # Now save to database (we need to save first to get the file path)
        contract.save()
        
        # BEGINNER EXPLANATION:
        # ---------------------
        # Now that the contract is saved, we can extract text from the uploaded file.
        # The file has been saved to disk, so we can now read it and extract its text.
        
        # Extract text from the uploaded file
        if file and contract.file_type in ['pdf', 'docx']:
            try:
                # Get the full path to the uploaded file on the server's disk
                # contract.file.path gives us something like:
                # "/path/to/media/contracts/2024/01/15/contract.pdf"
                file_path = contract.file.path
                
                logger.info(f"Extracting text from {contract.file_type} file: {file_path}")
                
                # Extract text using our utility function
                # This reads the file and extracts all text from it
                extracted_text = extract_text_from_file(file_path, contract.file_type)
                
                # If text was successfully extracted, save it to the contract
                if extracted_text:
                    contract.extracted_text = extracted_text
                    contract.save()  # Save again with the extracted text
                    logger.info(f"Successfully extracted {len(extracted_text)} characters from contract {contract.id}")
                    
                    # BEGINNER EXPLANATION:
                    # ---------------------
                    # Now that we have the extracted text, we can analyze it!
                    # We'll:
                    # 1. Extract key clauses (auto-renewal, indemnity, etc.)
                    # 2. Analyze risks using OpenAI
                    # 3. Generate a summary
                    
                    # Update status to processing
                    contract.status = 'processing'
                    contract.save()
                    
                    try:
                        analysis_start_time = time.time()
                        
                        # Step 1: Extract key clauses
                        logger.info(f"Extracting clauses from contract {contract.id}...")
                        extracted_clauses = extract_all_clauses(extracted_text)
                        
                        # Step 1.5: Add GPT summaries to clauses (clear, complete sentences)
                        logger.info(f"Generating clause summaries for contract {contract.id}...")
                        extracted_clauses = add_clause_summaries(extracted_clauses)
                        
                        # Step 2: Analyze risks using OpenAI
                        logger.info(f"Analyzing risks for contract {contract.id}...")
                        risk_assessment = analyze_clause_risks(extracted_clauses, extracted_text)
                        
                        # Step 3: Generate contract summary
                        logger.info(f"Generating summary for contract {contract.id}...")
                        analysis_summary = generate_contract_summary(extracted_text, extracted_clauses)
                        
                        # Calculate processing time
                        analysis_time = round(time.time() - analysis_start_time, 2)
                        
                        # Save analysis results
                        contract.extracted_clauses = extracted_clauses
                        contract.risk_assessment = risk_assessment
                        contract.analysis_summary = analysis_summary
                        contract.analysis_metadata = {
                            'processing_time_seconds': analysis_time,
                            'clause_types_found': len(extracted_clauses),
                            'total_clauses': sum(c['count'] for c in extracted_clauses),
                            'overall_risk_level': risk_assessment.get('overall_risk_level', 'UNKNOWN'),
                        }
                        contract.status = 'analyzed'
                        contract.analyzed_at = timezone.now()
                        contract.save()
                        
                        logger.info(f"Successfully analyzed contract {contract.id} in {analysis_time}s. Found {len(extracted_clauses)} clause types.")
                        
                    except Exception as analysis_error:
                        # If analysis fails, log but don't crash
                        logger.error(f"Error during contract analysis for contract {contract.id}: {str(analysis_error)}")
                        contract.status = 'error'
                        contract.save()
                        # Contract still saved with extracted text, just without analysis
                else:
                    logger.warning(f"No text extracted from contract {contract.id}")
                    
            except Exception as e:
                # If text extraction fails, log the error but don't crash
                # The contract will still be saved, just without extracted text
                logger.error(f"Error extracting text from contract {contract.id}: {str(e)}")
                contract.status = 'error'
                contract.save()
        
        return contract


class ContractListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing contracts (fewer fields for performance).
    """
    file_size_mb = serializers.ReadOnlyField()
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = Contract
        fields = [
            'id',
            'title',
            'description',
            'file_type',
            'status',
            'file_size_mb',
            'uploaded_at',
            'analyzed_at',
            'uploaded_by_username',
        ]

