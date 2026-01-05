from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import json


class Contract(models.Model):
    """
    Model to store uploaded legal contracts and their analysis results.
    
    This model represents a contract document that users upload for analysis.
    It stores metadata about the contract and will later store AI analysis results.
    """
    
    # Status choices for the contract analysis process
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),           # Just uploaded, not processed yet
        ('processing', 'Processing'),       # Currently being analyzed
        ('analyzed', 'Analyzed'),           # Analysis complete
        ('error', 'Error'),                 # Error during processing
    ]
    
    # Basic Information
    title = models.CharField(
        max_length=200,
        help_text="Name or title of the contract"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description or notes about the contract"
    )
    
    # File Storage
    file = models.FileField(
        upload_to='contracts/%Y/%m/%d/',
        help_text="Upload PDF or DOCX contract file"
    )
    
    # File Metadata
    file_name = models.CharField(
        max_length=255,
        help_text="Original name of the uploaded file"
    )
    
    file_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Size of the file in bytes (auto-calculated from uploaded file)"
    )
    
    file_type = models.CharField(
        max_length=10,
        choices=[
            ('pdf', 'PDF'),
            ('docx', 'DOCX'),
        ],
        help_text="Type of the uploaded file"
    )
    
    # Status Tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='uploaded',
        help_text="Current status of the contract analysis"
    )
    
    # Timestamps
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the contract was uploaded"
    )
    
    analyzed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the analysis was completed"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last time this contract was updated"
    )
    
    # User Association
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contracts',
        help_text="User who uploaded this contract"
    )
    
    # Extracted Text (for future AI processing)
    extracted_text = models.TextField(
        blank=True,
        null=True,
        help_text="Text extracted from the contract document"
    )
    
    # AI Analysis Results (stored as JSON)
    analysis_summary = models.TextField(
        blank=True,
        null=True,
        help_text="AI-generated executive summary of the contract"
    )
    
    extracted_clauses = models.JSONField(
        default=list,
        blank=True,
        help_text="List of extracted key clauses (auto-renewal, indemnity, termination, etc.)"
    )
    
    risk_assessment = models.JSONField(
        default=dict,
        blank=True,
        help_text="Risk analysis results with identified risks and their severity"
    )
    
    analysis_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Metadata about the analysis (model used, timestamp, processing time, etc.)"
    )
    
    class Meta:
        """
        Meta options for the Contract model.
        """
        ordering = ['-uploaded_at']  # Newest contracts first
        verbose_name = 'Contract'
        verbose_name_plural = 'Contracts'
    
    def __str__(self):
        """
        String representation of the Contract object.
        Shows in Django admin and when printing the object.
        """
        return f"{self.title} ({self.file_type.upper()})"
    
    @property
    def file_size_mb(self):
        """
        Property to get file size in megabytes (MB).
        Usage: contract.file_size_mb  (no parentheses needed)
        Returns None if file_size is not set.
        """
        if self.file_size is None:
            return None
        return round(self.file_size / (1024 * 1024), 2)
    
    def mark_as_analyzed(self):
        """
        Helper method to mark contract as analyzed.
        Sets status to 'analyzed' and records the analysis time.
        """
        self.status = 'analyzed'
        self.analyzed_at = timezone.now()
        self.save()
