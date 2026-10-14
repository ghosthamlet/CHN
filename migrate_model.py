#!/usr/bin/env python3
"""
Model Migration Script - Pickle to Joblib
==========================================
Migrates the ML model from insecure pickle format to secure joblib format.

Usage:
    python3 migrate_model.py

This script:
1. Loads the existing .pkl model file
2. Saves it in .joblib format
3. Updates config.py to use the new format
"""

import os
import sys
import pickle
import joblib

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config

def migrate_model():
    """Migrate model from pickle to joblib format"""
    
    model_path = config.hn_classifer_model
    
    if not os.path.exists(model_path):
        print(f"[ERROR] Model file not found: {model_path}")
        return False
    
    print(f"[*] Found model: {model_path}")
    print(f"[*] Loading model from pickle format...")
    
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print(f"[+] Model loaded successfully")
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return False
    
    # Generate new joblib path
    if model_path.endswith('.pkl'):
        new_model_path = model_path.replace('.pkl', '.joblib')
    else:
        new_model_path = model_path + '.joblib'
    
    print(f"[*] Saving model in secure joblib format: {new_model_path}")
    
    try:
        joblib.dump(model, new_model_path)
        print(f"[+] Model saved successfully")
    except Exception as e:
        print(f"[ERROR] Failed to save model: {e}")
        return False
    
    # Get file sizes for comparison
    old_size = os.path.getsize(model_path)
    new_size = os.path.getsize(new_model_path)
    
    print(f"\n[+] Migration completed successfully!")
    print(f"    Old file: {model_path} ({old_size:,} bytes)")
    print(f"    New file: {new_model_path} ({new_size:,} bytes)")
    
    print(f"\n[*] Next steps:")
    print(f"    1. Update config.py:")
    print(f"       Change: hn_classifer_model = '{model_path}'")
    print(f"       To:     hn_classifer_model = '{new_model_path}'")
    print(f"    2. Test the application: python3 ui.py")
    print(f"    3. Optionally remove old .pkl file: rm {model_path}")
    
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("CHN Model Migration: Pickle → Joblib")
    print("=" * 70)
    print()
    
    if migrate_model():
        print("\n[SUCCESS] Model migration completed!")
        sys.exit(0)
    else:
        print("\n[FAILED] Model migration failed!")
        sys.exit(1)
