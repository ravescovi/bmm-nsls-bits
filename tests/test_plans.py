#!/usr/bin/env python3
"""
BMM Plans Test Script

Test script to validate BMM plan imports and basic functionality.
This ensures all plan modules can be imported properly.
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


def test_plan_imports():
    """Test that all plan modules can be imported."""
    logger.info("Testing plan module imports...")
    
    try:
        # Test individual module imports
        from bmm_instrument.plans import basic_plans
        logger.info("✓ basic_plans imported successfully")
        
        from bmm_instrument.plans import xafs_plans
        logger.info("✓ xafs_plans imported successfully")
        
        from bmm_instrument.plans import scanning_plans
        logger.info("✓ scanning_plans imported successfully")
        
        from bmm_instrument.plans import alignment_plans
        logger.info("✓ alignment_plans imported successfully")
        
        from bmm_instrument.plans import utility_plans
        logger.info("✓ utility_plans imported successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Plan import test failed: {e}")
        return False


def test_plan_discovery():
    """Test plan discovery functions."""
    logger.info("Testing plan discovery functions...")
    
    try:
        from bmm_instrument.plans import list_plans, get_plan_info, find_plans_by_keyword
        
        # Test list_plans
        all_categories = list_plans()
        logger.info(f"✓ Found {len(all_categories)} plan categories")
        
        basic_plans = list_plans('basic')
        logger.info(f"✓ Found {len(basic_plans)} basic plans")
        
        # Test get_plan_info
        plan_info = get_plan_info('move')
        logger.info(f"✓ Plan info for 'move': {plan_info}")
        
        # Test find_plans_by_keyword
        scan_plans = find_plans_by_keyword('scan')
        logger.info(f"✓ Found {len(scan_plans)} plans with 'scan' keyword")
        
        return True
        
    except Exception as e:
        logger.error(f"Plan discovery test failed: {e}")
        return False


def test_plan_metadata():
    """Test plan metadata and categories."""
    logger.info("Testing plan metadata...")
    
    try:
        from bmm_instrument.plans import PLAN_CATEGORIES, ALL_PLANS
        
        logger.info(f"✓ Total plans available: {len(ALL_PLANS)}")
        
        for category, plans in PLAN_CATEGORIES.items():
            logger.info(f"✓ {category}: {len(plans)} plans")
        
        # Check for expected categories
        expected_categories = ['basic', 'xafs', 'scanning', 'alignment', 'utility', 'bits']
        for category in expected_categories:
            if category in PLAN_CATEGORIES:
                logger.info(f"✓ Category '{category}' found")
            else:
                logger.warning(f"✗ Category '{category}' missing")
        
        return True
        
    except Exception as e:
        logger.error(f"Plan metadata test failed: {e}")
        return False


def test_plan_function_access():
    """Test that plan functions can be accessed."""
    logger.info("Testing plan function access...")
    
    try:
        from bmm_instrument.plans import move, count_plan, line_scan, transmission_xafs
        
        # Check if functions are callable
        if callable(move):
            logger.info("✓ 'move' plan is callable")
        else:
            logger.warning("✗ 'move' plan is not callable")
        
        if callable(count_plan):
            logger.info("✓ 'count_plan' plan is callable")
        else:
            logger.warning("✗ 'count_plan' plan is not callable")
        
        if callable(line_scan):
            logger.info("✓ 'line_scan' plan is callable")
        else:
            logger.warning("✗ 'line_scan' plan is not callable")
        
        if callable(transmission_xafs):
            logger.info("✓ 'transmission_xafs' plan is callable")
        else:
            logger.warning("✗ 'transmission_xafs' plan is not callable")
        
        return True
        
    except Exception as e:
        logger.error(f"Plan function access test failed: {e}")
        return False


def run_all_tests():
    """Run all plan tests."""
    logger.info("="*60)
    logger.info("BMM Plans Test Suite")
    logger.info("="*60)
    
    tests = [
        ("Plan Imports", test_plan_imports),
        ("Plan Discovery", test_plan_discovery),
        ("Plan Metadata", test_plan_metadata),
        ("Plan Function Access", test_plan_function_access),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info("")
        logger.info(f"Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✓ {test_name} test PASSED")
            else:
                logger.error(f"✗ {test_name} test FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} test FAILED with exception: {e}")
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
        logger.info("🎉 All tests passed! BMM plans are working correctly.")
        return True
    else:
        logger.error(f"❌ {total-passed} tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)