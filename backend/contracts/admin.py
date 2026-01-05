from django.contrib import admin
from django.utils import timezone
from .models import Contract


def format_file_size(obj):
    """Helper function to format file size for admin display"""
    size_mb = obj.file_size_mb
    return f"{size_mb} MB" if size_mb is not None else "-"
format_file_size.short_description = "File Size"


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Contract model.
    This controls how contracts appear in Django's admin panel.
    """
    
    # Fields to display in the list view (main table)
    list_display = [
        'title',
        'file_type',
        'status',
        'uploaded_by',
        'uploaded_at',
        format_file_size,  # Using helper function to handle None values
    ]
    
    # Fields that are clickable links (navigate to detail view)
    list_display_links = ['title']
    
    # Filters in the right sidebar
    list_filter = [
        'status',
        'file_type',
        'uploaded_at',
        'analyzed_at',
    ]
    
    # Search fields (search bar at the top)
    search_fields = [
        'title',
        'description',
        'file_name',
        'uploaded_by__username',  # Search by username
    ]
    
    # Fields to show in the detail/edit form
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'uploaded_by')
        }),
        ('File Information', {
            'fields': ('file', 'file_name', 'file_type', 'file_size')
        }),
        ('Status & Analysis', {
            'fields': ('status', 'uploaded_at', 'analyzed_at', 'updated_at')
        }),
        ('Extracted Content', {
            'fields': ('extracted_text',),
            'classes': ('collapse',),  # Makes this section collapsible
        }),
    )
    
    # Read-only fields (can't be edited in admin)
    readonly_fields = [
        'uploaded_at',
        'updated_at',
        'file_size',
    ]
    # Note: analyzed_at is editable, but will be auto-set when status = 'analyzed'
    
    # Order by newest first
    ordering = ['-uploaded_at']
    
    # Date hierarchy (calendar navigation at the top)
    date_hierarchy = 'uploaded_at'
    
    def save_model(self, request, obj, form, change):
        """
        Override save to automatically set/clear analyzed_at based on status.
        """
        # If status is being set to 'analyzed' and analyzed_at is not set, set it now
        if obj.status == 'analyzed' and obj.analyzed_at is None:
            obj.analyzed_at = timezone.now()
        # If status is changed away from 'analyzed', clear analyzed_at
        # This ensures contracts with status != 'analyzed' don't show in "analyzed at" filters
        elif obj.status != 'analyzed' and obj.analyzed_at is not None:
            obj.analyzed_at = None
        
        # Call the parent save method to actually save the object
        super().save_model(request, obj, form, change)
