# BMM Beamline Profile Collection

This `.profile/` directory contains references to the original BMM profile collection startup files.

## Original Profile Collection

The original BMM profile collection is available at:
- Repository: `nsls_deployments/bmm-profile-collection/`
- Startup files: `nsls_deployments/bmm-profile-collection/startup/`

## Key Files

### Original Startup Files:
- `00-populate-namespace.py` - Base namespace population
- `BMM/` - Core BMM module with all device classes and plans
- `BMM_common/` - Common utilities and bot integration
- `BMM_configuration.ini` - Configuration settings
- `user_group_permissions.yaml` - Queue server permissions

### BITS Migration:
The BITS deployment has migrated these startup files into:
- Device configurations: `src/bmm_instrument/configs/devices.yml`
- Device classes: `src/bmm_instrument/devices/`
- Plan implementations: `src/bmm_instrument/plans/`
- Startup scripts: `src/bmm_instrument/startup.py` and `startup_nsls2.py`

## Core BMM Modules

The original BMM module contains:
- **Devices**: motors.py, detectors.py, dcm.py, pilatus.py, etc.
- **Plans**: xafs.py, linescans.py, raster.py, etc.
- **Utilities**: functions.py, utilities.py, metadata.py
- **User Interface**: user_ns/ with specialized namespaces

## Usage

To reference the original profile collection:
```bash
# View original startup files
ls ../../../nsls_deployments/bmm-profile-collection/startup/

# View BMM core modules
ls ../../../nsls_deployments/bmm-profile-collection/startup/BMM/

# Compare with BITS implementation
ls src/bmm_instrument/
```

## Testing

Both the original profile collection and BITS implementation can be tested:
- Original: Use the `startup/` files directly with IPython
- BITS: Use `test_devices.py`, `test_plans.py`, or `test.ipynb`