"""
Test runner for learning capabilities
Executes tests and generates detailed reports
"""

import pytest
import sys
from pathlib import Path
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

def run_tests():
    """Run all learning capability tests"""
    test_dir = Path(__file__).parent
    results_dir = test_dir / 'results'
    results_dir.mkdir(exist_ok=True)
    
    # Run tests and collect results
    result = pytest.main([
        str(test_dir / 'test_learning_capabilities.py'),
        '-v',
        '--html=' + str(results_dir / 'report.html'),
        '--self-contained-html',
        '--json=' + str(results_dir / 'results.json')
    ])
    
    return result == 0

def generate_performance_report(results_file):
    """Generate performance visualization from test results"""
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Extract metrics
    metrics = {
        'topic_modeling': results.get('topic_model_coherence', 0),
        'preference_learning': results.get('preference_learning_accuracy', 0),
        'semantic_search': results.get('semantic_search_precision', 0),
        'adaptation_rate': results.get('response_adaptation_rate', 0)
    }
    
    # Create visualization
    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(metrics.keys()), y=list(metrics.values()))
    plt.title('Learning System Performance Metrics')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save plot
    results_dir = Path(results_file).parent
    plt.savefig(results_dir / 'performance_metrics.png')

def main():
    """Main test execution function"""
    print("Starting learning capability tests...")
    
    success = run_tests()
    
    if success:
        print("\nTests completed successfully!")
        results_file = Path(__file__).parent / 'results' / 'results.json'
        if results_file.exists():
            generate_performance_report(results_file)
            print("Performance report generated.")
    else:
        print("\nSome tests failed. Check the HTML report for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
