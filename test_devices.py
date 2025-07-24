#!/usr/bin/env python3
"""
BMM Device Test Script

Test script to validate BMM device instantiation in mock mode.
This ensures all device classes can be created properly.
"""

import os
import sys
import logging

# Set mock mode environment variables
os.environ["BMM_MOCK_MODE"] = "YES"

# Add the src directory to Python path
sys.path.insert(0, "src")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_motor_devices():
    """Test motor device creation."""
    logger.info("Testing motor devices...")
    
    from bmm_instrument.devices import (
        BMMMotor, XAFSMotor, FMBOMotor, EndStationMotor, EncodedMotor
    )
    
    try:
        # Test basic motor
        motor1 = BMMMotor("XF:06BM-OP{Test}Mtr", name="test_motor")
        assert motor1.is_mock, "Motor should be in mock mode"
        logger.info("✓ BMMMotor created successfully")
        
        # Test XAFS motor
        xafs_motor = XAFSMotor(
            "XF:06BMA-BI{XAFS-Ax:LinX}Mtr", 
            name="xafs_x",
            default_llm=2,
            default_hlm=126
        )
        assert xafs_motor.is_mock, "XAFS motor should be in mock mode"
        logger.info("✓ XAFSMotor created successfully")
        
        # Test FMBO motor
        fmbo_motor = FMBOMotor("XF:06BM-OP{Mir:M1-Ax:YU}Mtr", name="m1_yu")
        assert fmbo_motor.is_mock, "FMBO motor should be in mock mode"
        logger.info("✓ FMBOMotor created successfully")
        
        # Test EndStation motor
        es_motor = EndStationMotor("XF:06BMA-BI{XAFS-Ax:Tbl_YU}Mtr", name="table_yu")
        assert es_motor.is_mock, "EndStation motor should be in mock mode"
        logger.info("✓ EndStationMotor created successfully")
        
        # Test Encoded motor
        enc_motor = EncodedMotor("XF:06BM-ES{MC:09-Ax:1}Mtr", name="det_y")
        assert enc_motor.is_mock, "Encoded motor should be in mock mode"
        logger.info("✓ EncodedMotor created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Motor device test failed: {e}")
        return False


def test_detector_devices():
    """Test detector device creation."""
    logger.info("Testing detector devices...")
    
    from bmm_instrument.devices import (
        BMMQuadEM, BMMIonChamber, BMMXspress3, BMMPilatus
    )
    
    try:
        # Test QuadEM
        quadem = BMMQuadEM("XF:06BM-BI{EM:1}EM180:", name="quadem1")
        assert quadem.is_mock, "QuadEM should be in mock mode"
        # In mock mode, we just verify the object was created
        assert hasattr(quadem, 'current1'), "QuadEM should have current1 component"
        logger.info("✓ BMMQuadEM created successfully")
        
        # Test Ion Chamber
        ic = BMMIonChamber("XF:06BM-BI{IC:0}EM180:", name="ic0")
        assert ic.is_mock, "Ion chamber should be in mock mode"
        logger.info("✓ BMMIonChamber created successfully")
        
        # Test Xspress3
        xspress3 = BMMXspress3("XF:06BM-ES{Xsp:1}:", name="xspress3", num_elements=7)
        assert xspress3.is_mock, "Xspress3 should be in mock mode"
        assert xspress3.num_elements == 7, "Xspress3 should have 7 elements"
        logger.info("✓ BMMXspress3 created successfully")
        
        # Test Pilatus
        pilatus = BMMPilatus("XF:06BMB-ES{Det:PIL100k}:", name="pilatus")
        assert pilatus.is_mock, "Pilatus should be in mock mode"
        logger.info("✓ BMMPilatus created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Detector device test failed: {e}")
        return False


def test_optics_devices():
    """Test optics device creation."""
    logger.info("Testing optics devices...")
    
    from bmm_instrument.devices import BMMMirror, BMMDCM, BMMSlits, BMMShutter
    
    try:
        # Test Mirror
        mirror = BMMMirror("XF:06BM-OP{Mir:M1-Ax:", name="m1")
        assert mirror.is_mock, "Mirror should be in mock mode"
        logger.info("✓ BMMMirror created successfully")
        
        # Test DCM
        dcm = BMMDCM("XF:06BMA-OP{Mono:DCM1-Ax:", name="dcm")
        assert dcm.is_mock, "DCM should be in mock mode"
        
        # Test energy conversion
        energy_ev = 8000
        bragg_angle = dcm.energy_to_bragg(energy_ev)
        back_energy = dcm.bragg_to_energy(bragg_angle)
        assert abs(back_energy - energy_ev) < 1, "Energy conversion should be reversible"
        logger.info("✓ BMMDCM created successfully")
        
        # Test Slits
        slits = BMMSlits("XF:06BMA-OP{Slt:01-Ax:", name="dm2_slits")
        assert slits.is_mock, "Slits should be in mock mode"
        logger.info("✓ BMMSlits created successfully")
        
        # Test Shutter
        shutter = BMMShutter("XF:06BMA-OP{FS:1}", name="fs1")
        assert shutter.is_mock, "Shutter should be in mock mode"
        logger.info("✓ BMMShutter created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Optics device test failed: {e}")
        return False


def test_sample_environment_devices():
    """Test sample environment device creation."""
    logger.info("Testing sample environment devices...")
    
    from bmm_instrument.devices import (
        BMMXAFSTable, BMMSampleStage, BMMReferenceStage, 
        BMMDetectorStage, BMMBeamStop
    )
    
    try:
        # Test XAFS Table
        table = BMMXAFSTable("XF:06BMA-BI{XAFS-Ax:Tbl_", name="xafs_table")
        assert table.is_mock, "XAFS table should be in mock mode"
        logger.info("✓ BMMXAFSTable created successfully")
        
        # Test Sample Stage
        sample_stage = BMMSampleStage("XF:06BMA-BI{XAFS-Ax:", name="sample_stage")
        assert sample_stage.is_mock, "Sample stage should be in mock mode"
        logger.info("✓ BMMSampleStage created successfully")
        
        # Test Reference Stage
        ref_stage = BMMReferenceStage("XF:06BMA-BI{XAFS-Ax:", name="reference_stage")
        assert ref_stage.is_mock, "Reference stage should be in mock mode"
        logger.info("✓ BMMReferenceStage created successfully")
        
        # Test Detector Stage
        det_stage = BMMDetectorStage("XF:06BM-ES{MC:09-Ax:", name="detector_stage")
        assert det_stage.is_mock, "Detector stage should be in mock mode"
        logger.info("✓ BMMDetectorStage created successfully")
        
        # Test Beam Stop
        beam_stop = BMMBeamStop("XF:06BM-ES{MC:09-Ax:", name="beam_stop")
        assert beam_stop.is_mock, "Beam stop should be in mock mode"
        logger.info("✓ BMMBeamStop created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Sample environment device test failed: {e}")
        return False


def test_temperature_devices():
    """Test temperature control device creation."""
    logger.info("Testing temperature control devices...")
    
    from bmm_instrument.devices import BMMLakeShore331, BMMLinkam
    
    try:
        # Test LakeShore 331
        lakeshore = BMMLakeShore331("XF:06BM-BI{LS:331-1}:", name="lakeshore331")
        assert lakeshore.is_mock, "LakeShore should be in mock mode"
        # In mock mode, we just verify the object was created
        assert hasattr(lakeshore, 'temp_a'), "LakeShore should have temp_a component"
        logger.info("✓ BMMLakeShore331 created successfully")
        
        # Test Linkam
        linkam = BMMLinkam("XF:06BM-ES:{LINKAM}:", name="linkam")
        assert linkam.is_mock, "Linkam should be in mock mode"
        logger.info("✓ BMMLinkam created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Temperature device test failed: {e}")
        return False


def test_device_lists():
    """Test device list creation from devices.yml configuration."""
    logger.info("Testing device list creation...")
    
    try:
        # Test motor list creation
        motors = [
            {"prefix": "XF:06BMA-BI{XAFS-Ax:LinX}Mtr", "name": "xafs_x"},
            {"prefix": "XF:06BMA-BI{XAFS-Ax:LinY}Mtr", "name": "xafs_y"},
            {"prefix": "XF:06BM-OP{Mir:M1-Ax:YU}Mtr", "name": "m1_yu"},
        ]
        
        from bmm_instrument.devices import BMMMotor
        motor_devices = []
        for config in motors:
            motor = BMMMotor(config["prefix"], name=config["name"])
            assert motor.is_mock, f"Motor {config['name']} should be in mock mode"
            motor_devices.append(motor)
        
        logger.info(f"✓ Created {len(motor_devices)} motors from configuration")
        
        return True
        
    except Exception as e:
        logger.error(f"Device list test failed: {e}")
        return False


def run_all_tests():
    """Run all device tests."""
    logger.info("="*60)
    logger.info("BMM Device Test Suite")
    logger.info("="*60)
    
    tests = [
        ("Motor Devices", test_motor_devices),
        ("Detector Devices", test_detector_devices),
        ("Optics Devices", test_optics_devices),
        ("Sample Environment Devices", test_sample_environment_devices),
        ("Temperature Devices", test_temperature_devices),
        ("Device Lists", test_device_lists),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info("")
        logger.info(f"Running {test_name} tests...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✓ {test_name} tests PASSED")
            else:
                logger.error(f"✗ {test_name} tests FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} tests FAILED with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("")
    logger.info("="*60)
    logger.info("Test Summary:")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name:.<40} {status}")
    
    logger.info("")
    logger.info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All tests passed! BMM devices are working correctly.")
        return True
    else:
        logger.error(f"❌ {total-passed} tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)