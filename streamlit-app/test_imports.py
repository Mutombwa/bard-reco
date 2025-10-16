"""
Test imports to diagnose localhost issues
"""
import sys
import os

print("=" * 60)
print("DIAGNOSTIC TEST - FNB Workflow Ultra Fast")
print("=" * 60)

# Test 1: Basic imports
print("\n1. Testing basic imports...")
try:
    import streamlit as st
    print("   ✅ streamlit imported")
except Exception as e:
    print(f"   ❌ streamlit failed: {e}")

try:
    import pandas as pd
    print("   ✅ pandas imported")
except Exception as e:
    print(f"   ❌ pandas failed: {e}")

try:
    from fuzzywuzzy import fuzz
    print("   ✅ fuzzywuzzy imported")
except Exception as e:
    print(f"   ❌ fuzzywuzzy failed: {e}")

# Test 2: Component imports
print("\n2. Testing component imports...")
try:
    from components.fnb_workflow import FNBWorkflow
    print("   ✅ FNBWorkflow imported")
except Exception as e:
    print(f"   ❌ FNBWorkflow failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Ultra fast engine import
print("\n3. Testing ultra fast engine import...")
try:
    from components.fnb_workflow_ultra_fast import UltraFastFNBReconciler
    print("   ✅ UltraFastFNBReconciler imported")

    # Try to instantiate
    reconciler = UltraFastFNBReconciler()
    print("   ✅ UltraFastFNBReconciler instantiated")
except Exception as e:
    print(f"   ❌ UltraFastFNBReconciler failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check file paths
print("\n4. Checking file paths...")
print(f"   Current directory: {os.getcwd()}")
print(f"   Components directory exists: {os.path.exists('components')}")
print(f"   fnb_workflow.py exists: {os.path.exists('components/fnb_workflow.py')}")
print(f"   fnb_workflow_ultra_fast.py exists: {os.path.exists('components/fnb_workflow_ultra_fast.py')}")

print("\n" + "=" * 60)
print("DIAGNOSTIC TEST COMPLETE")
print("=" * 60)
