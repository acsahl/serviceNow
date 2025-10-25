"""
Main application entry point for ServiceNow Technical Accelerators Request Analysis Agent
"""

import argparse
import sys
import os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="ServiceNow Technical Accelerators Request Analysis Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py generate-data          # Generate sample data
  python main.py analyze               # Run analysis on existing data
  python main.py api                   # Start API server
  python main.py dashboard             # Start dashboard
  python main.py full-pipeline         # Run complete pipeline
        """
    )
    
    parser.add_argument(
        'command',
        choices=['generate-data', 'analyze', 'api', 'dashboard', 'full-pipeline'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--companies-file',
        default='companies.csv',
        help='Companies data file (default: companies.csv)'
    )
    
    parser.add_argument(
        '--requests-file', 
        default='requests.csv',
        help='Requests data file (default: requests.csv)'
    )
    
    parser.add_argument(
        '--catalog-file',
        default='catalog.csv', 
        help='Catalog data file (default: catalog.csv)'
    )
    
    parser.add_argument(
        '--output-file',
        default='analysis_results.json',
        help='Output file for analysis results (default: analysis_results.json)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port for API server (default: 8000)'
    )
    
    args = parser.parse_args()
    
    if args.command == 'generate-data':
        from data_generator import DataGenerator
        print("🚀 Generating sample data...")
        generator = DataGenerator()
        companies, requests, catalog = generator.save_data()
        print("✅ Data generation complete!")
        
    elif args.command == 'analyze':
        from request_analyzer import RequestAnalyzer
        print("🔍 Running request analysis...")
        analyzer = RequestAnalyzer()
        
        # Check if data files exist
        for file_path in [args.companies_file, args.requests_file, args.catalog_file]:
            if not os.path.exists(file_path):
                print(f"❌ Error: {file_path} not found. Run 'python main.py generate-data' first.")
                sys.exit(1)
        
        results = analyzer.run_complete_analysis(
            args.companies_file,
            args.requests_file,
            args.catalog_file
        )
        
        analyzer.save_results(results, args.output_file)
        print("✅ Analysis complete!")
        
    elif args.command == 'api':
        import uvicorn
        from api.main import app
        print(f"🌐 Starting API server on port {args.port}...")
        uvicorn.run(app, host="0.0.0.0", port=args.port)
        
    elif args.command == 'dashboard':
        import subprocess
        print("📊 Starting dashboard...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard/app.py"])
        
    elif args.command == 'full-pipeline':
        print("🚀 Running full pipeline...")
        
        # Step 1: Generate data
        print("Step 1: Generating sample data...")
        from data_generator import DataGenerator
        generator = DataGenerator()
        companies, requests, catalog = generator.save_data()
        
        # Step 2: Run analysis
        print("Step 2: Running analysis...")
        from request_analyzer import RequestAnalyzer
        analyzer = RequestAnalyzer()
        results = analyzer.run_complete_analysis(
            args.companies_file,
            args.requests_file,
            args.catalog_file
        )
        analyzer.save_results(results, args.output_file)
        
        print("✅ Full pipeline complete!")
        print(f"📊 Results saved to: {args.output_file}")
        print(f"🌐 To start API: python main.py api")
        print(f"📈 To start dashboard: python main.py dashboard")

if __name__ == "__main__":
    main()
