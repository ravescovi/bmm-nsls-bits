"""
BMM NSLS-II Nexus data file writer callback.

This module provides callbacks for writing BMM data to Nexus data files
adapted for NSLS-II without APS dependencies.
"""

import logging
import os
from pathlib import Path

from apsbits.utils.config_loaders import get_config

logger = logging.getLogger(__name__)

# Get the configuration
iconfig = get_config()

# Use standard NXWriter (not APS-specific version)
try:
    from apstools.callbacks import NXWriter
except ImportError:
    logger.warning("apstools not available - NXWriter callback disabled")
    NXWriter = None


class BMMNXWriter(NXWriter if NXWriter else object):
    """BMM-specific NeXus writer for NSLS-II."""

    def __init__(self, *args, **kwargs):
        if NXWriter is None:
            logger.error("NXWriter not available - cannot create BMM NXWriter")
            return
            
        super().__init__(*args, **kwargs)
        
        # BMM-specific metadata
        self.beamline_name = "BMM"
        self.facility_name = "NSLS-II"
        
    def get_sample_title(self):
        """
        Get the sample title from BMM metadata.
        
        Returns:
        --------
        str
            Sample title for the NeXus file
        """
        # Try to get sample name from metadata
        if hasattr(self, 'metadata') and self.metadata:
            sample_name = self.metadata.get('sample_name', 'unknown_sample')
            return f"BMM_{sample_name}"
        else:
            return "BMM_sample"
    
    def get_file_name(self, start_doc):
        """
        Generate BMM-specific file name.
        
        Parameters:
        -----------
        start_doc : dict
            Bluesky start document
            
        Returns:
        --------
        str
            NeXus file name
        """
        scan_id = start_doc.get('scan_id', 0)
        sample_name = start_doc.get('sample_name', 'sample')
        plan_name = start_doc.get('plan_name', 'scan')
        
        # Clean sample name for filename
        clean_sample = sample_name.replace(' ', '_').replace('/', '_')
        
        return f"bmm_{scan_id:04d}_{clean_sample}_{plan_name}.h5"
    
    def prepare_file_path(self, start_doc):
        """
        Prepare the full file path for BMM data.
        
        Parameters:
        -----------
        start_doc : dict
            Bluesky start document
            
        Returns:
        --------
        Path
            Full path for the NeXus file
        """
        from datetime import datetime
        
        # Get timestamp from start document
        timestamp = datetime.fromtimestamp(start_doc['time'])
        year = timestamp.strftime('%Y')
        month = timestamp.strftime('%m')
        day = timestamp.strftime('%d')
        
        # BMM data directory structure
        base_path = Path(iconfig.get('NEXUS_DATA_FILES', {}).get('FILE_PATH', '/nsls2/data/bmm/shared/'))
        data_path = base_path / year / month / day
        
        # Ensure directory exists
        data_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = self.get_file_name(start_doc)
        
        return data_path / filename


def nxwriter_init(RE):
    """
    Initialize BMM NeXus writer and attach to RunEngine.
    
    Parameters:
    -----------
    RE : bluesky.RunEngine
        The Bluesky RunEngine instance
        
    Returns:
    --------
    BMMNXWriter or None
        The initialized NeXus writer instance
    """
    if NXWriter is None:
        logger.warning("NXWriter not available - skipping NeXus callback initialization")
        return None
        
    try:
        # Create BMM-specific NXWriter
        nxwriter = BMMNXWriter()
        
        # Configure for BMM
        nxwriter.file_path = iconfig.get('NEXUS_DATA_FILES', {}).get('FILE_PATH', '/nsls2/data/bmm/shared/')
        nxwriter.file_extension = iconfig.get('NEXUS_DATA_FILES', {}).get('FILE_EXTENSION', 'h5')
        
        # Subscribe to RunEngine
        RE.subscribe(nxwriter.receiver)
        
        logger.info("BMM NeXus writer initialized successfully")
        return nxwriter
        
    except Exception as e:
        logger.error(f"Failed to initialize BMM NeXus writer: {e}")
        return None


# For backward compatibility, create the standard init function
def init_nexus_writer(RE):
    """Backward compatibility wrapper."""
    return nxwriter_init(RE)