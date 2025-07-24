# BMM NSLS-II BITS Instrument Package

BITS (Bluesky Instrument Toolkit System) package for the BMM (Beamline for Materials Measurement) beamline at NSLS-II.

## Overview

This package provides a BITS-compliant implementation for the BMM beamline, migrated from the original profile collection to use modern Bluesky patterns including:

- ophyd-async devices
- Structured YAML configuration
- Enhanced error handling and mock mode support
- Modern plan implementations
- BITS framework integration

## Installation

```bash
pip install -e .
```

## Usage

### Starting the Instrument

```python
from bmm_instrument.startup import *
```

### Running Demo Plans

```python
RE(sim_print_plan())
RE(sim_count_plan())
RE(sim_rel_scan_plan())
```

## Configuration

Configuration files are located in `src/bmm_instrument/configs/`:

- `devices.yml` - Device PV mappings and configurations
- `iconfig.yml` - Instrument configuration
- `extra_logging.yml` - Logging configuration

## Development

This package was generated using the BITS framework and follows BITS conventions for beamline instrument packages.

## License

BSD-3-Clause