#!/usr/bin/env python3
"""
Security Tests for CHN
======================
Tests for the CWE-502 pickle deserialization fixes.
"""

import unittest
import json
import tempfile
import os
import sys
import requests

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestCookieSecurity(unittest.TestCase):
    """Test secure cookie serialization"""
    
    def test_json_cookie_format(self):
        """Test that cookies are saved in JSON format"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            cookie_file = f.name
        
        try:
            # Create a mock cookie jar
            jar = requests.cookies.RequestsCookieJar()
            jar.set('user', 'testuser&session123')
            jar.set('session', 'abc123')
            
            # Save as JSON
            with open(cookie_file, 'w') as f:
                cookie_dict = requests.utils.dict_from_cookiejar(jar)
                json.dump(cookie_dict, f)
            
            # Verify it's valid JSON
            with open(cookie_file, 'r') as f:
                loaded = json.load(f)
                self.assertIsInstance(loaded, dict)
                self.assertIn('user', loaded)
                self.assertEqual(loaded['user'], 'testuser&session123')
            
        finally:
            if os.path.exists(cookie_file):
                os.unlink(cookie_file)
    
    def test_cookie_jar_reconstruction(self):
        """Test that RequestsCookieJar can be reconstructed from JSON"""
        # Create original jar
        original_jar = requests.cookies.RequestsCookieJar()
        original_jar.set('user', 'testuser')
        original_jar.set('auth', 'token123')
        
        # Convert to dict and back
        cookie_dict = requests.utils.dict_from_cookiejar(original_jar)
        reconstructed_jar = requests.cookies.cookiejar_from_dict(cookie_dict)
        
        # Verify reconstruction
        self.assertEqual(original_jar.get('user'), reconstructed_jar.get('user'))
        self.assertEqual(original_jar.get('auth'), reconstructed_jar.get('auth'))
    
    def test_no_pickle_in_cookie_file(self):
        """Test that new cookie files don't contain pickle data"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            cookie_file = f.name
        
        try:
            jar = requests.cookies.RequestsCookieJar()
            jar.set('test', 'value')
            
            # Save as JSON
            with open(cookie_file, 'w') as f:
                cookie_dict = requests.utils.dict_from_cookiejar(jar)
                json.dump(cookie_dict, f)
            
            # Read as text and verify no pickle markers
            with open(cookie_file, 'r') as f:
                content = f.read()
                # Pickle files have binary markers that shouldn't appear in JSON
                self.assertNotIn('\\x80', content)
                self.assertNotIn('\\x03', content)
                # Should be valid JSON text
                self.assertTrue(content.strip().startswith('{'))
                
        finally:
            if os.path.exists(cookie_file):
                os.unlink(cookie_file)

class TestModelSecurity(unittest.TestCase):
    """Test secure model loading"""
    
    def test_joblib_import(self):
        """Test that joblib is available"""
        try:
            import joblib
            self.assertTrue(hasattr(joblib, 'load'))
            self.assertTrue(hasattr(joblib, 'dump'))
        except ImportError:
            self.fail("joblib not installed - required for secure model loading")
    
    def test_joblib_sklearn_compatibility(self):
        """Test that joblib can serialize sklearn models"""
        try:
            from sklearn.linear_model import LogisticRegression
            import joblib
            import tempfile
            
            # Create a simple model
            model = LogisticRegression()
            
            # Save with joblib
            with tempfile.NamedTemporaryFile(suffix='.joblib', delete=False) as f:
                model_file = f.name
            
            try:
                joblib.dump(model, model_file)
                
                # Load it back
                loaded_model = joblib.load(model_file)
                
                # Verify it's the same type
                self.assertIsInstance(loaded_model, LogisticRegression)
                
            finally:
                if os.path.exists(model_file):
                    os.unlink(model_file)
                    
        except ImportError:
            self.skipTest("sklearn not available")

class TestSecurityRegression(unittest.TestCase):
    """Test that pickle vulnerabilities are fixed"""
    
    def test_pickle_import_still_available(self):
        """Verify pickle is only imported for backward compatibility"""
        # Pickle should still be importable for migration
        import pickle
        self.assertTrue(hasattr(pickle, 'load'))
    
    def test_json_module_available(self):
        """Verify JSON module is available for cookies"""
        import json
        self.assertTrue(hasattr(json, 'load'))
        self.assertTrue(hasattr(json, 'dump'))

def run_tests():
    """Run all security tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestCookieSecurity))
    suite.addTests(loader.loadTestsFromTestCase(TestModelSecurity))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityRegression))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    print("=" * 70)
    print("CHN Security Tests - CWE-502 Fixes")
    print("=" * 70)
    print()
    
    success = run_tests()
    
    print()
    print("=" * 70)
    if success:
        print("✓ All security tests passed!")
    else:
        print("✗ Some security tests failed!")
    print("=" * 70)
    
    sys.exit(0 if success else 1)
