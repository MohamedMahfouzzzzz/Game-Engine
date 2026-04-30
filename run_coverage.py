#!/usr/bin/env python
"""Run tests with coverage reporting."""

import subprocess
import sys
import os

def main():
    """Run tests with coverage."""
    print("="*60)
    print("RUNNING TESTS WITH COVERAGE")
    print("="*60)
    
    # Install coverage if not available
    try:
        import coverage
    except ImportError:
        print("Installing coverage...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'coverage>=6.0'])
    
    # Run coverage
    print("\nRunning test coverage...")
    cov = coverage.Coverage(source=['engine'], omit=['*/tests/*', '*/benchmarks/*', '*/examples/*'])
    cov.start()
    
    # Import and run tests
    import unittest
    
    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    cov.stop()
    cov.save()
    
    # Generate reports
    print("\n" + "="*60)
    print("COVERAGE REPORT")
    print("="*60)
    
    # Terminal report
    cov.report()
    
    # HTML report
    try:
        cov.html_report(directory='coverage_html')
        print("\nHTML coverage report generated in 'coverage_html/' directory")
        print("Open 'coverage_html/index.html' in your browser to view")
    except Exception as e:
        print(f"Failed to generate HTML report: {e}")
    
    # XML report for CI
    try:
        cov.xml_report(outfile='coverage.xml')
        print("XML coverage report saved as 'coverage.xml'")
    except Exception as e:
        print(f"Failed to generate XML report: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("COVERAGE SUMMARY")
    print("="*60)
    
    total_lines = cov.report().files_covered
    if total_lines > 0:
        total_covered = cov.report().numbers.n_covered
        total_statements = cov.report().numbers.n_statements
        coverage_percent = (total_covered / total_statements * 100) if total_statements > 0 else 0
        
        print(f"Total statements: {total_statements}")
        print(f"Covered statements: {total_covered}")
        print(f"Coverage: {coverage_percent:.1f}%")
        
        if coverage_percent >= 80:
            print("✅ Good coverage!")
        elif coverage_percent >= 60:
            print("⚠️  Acceptable coverage")
        else:
            print("❌ Low coverage - add more tests!")
    
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    # Exit with error code if tests failed
    if result.failures or result.errors:
        sys.exit(1)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
