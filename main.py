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
        from data_processor import DataProcessor
        print("🔍 Running ServiceNow data analysis...")
        processor = DataProcessor()
        
        # Check if actual data files exist
        if not os.path.exists("csv/u_hack.csv") or not os.path.exists("csv/accelerators.csv"):
            print("❌ Error: ServiceNow data files not found in csv/ directory.")
            print("Please ensure csv/u_hack.csv and csv/accelerators.csv exist.")
            sys.exit(1)
        
        results = processor.run_complete_analysis()
        
        if "error" not in results:
            processor.save_results(results, args.output_file)
            processor.print_summary(results)
            print("✅ Analysis complete!")
        else:
            print(f"❌ Analysis failed: {results['error']}")
            sys.exit(1)
        
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
        print("🚀 Running full pipeline with actual ServiceNow data...")
        
        # Check if actual data files exist
        if not os.path.exists("csv/u_hack.csv") or not os.path.exists("csv/accelerators.csv"):
            print("❌ Error: ServiceNow data files not found in csv/ directory.")
            print("Please ensure csv/u_hack.csv and csv/accelerators.csv exist.")
            sys.exit(1)
        
        # Run analysis on actual data
        print("Step 1: Analyzing ServiceNow data...")
        from data_processor import DataProcessor
        processor = DataProcessor()
        results = processor.run_complete_analysis()
        
        if "error" not in results:
            processor.save_results(results, args.output_file)
            processor.print_summary(results)
            
            print("✅ Full pipeline complete!")
            print(f"📊 Results saved to: {args.output_file}")
            print(f"🌐 To start API: python main.py api")
            print(f"📈 To start dashboard: python main.py dashboard")
        else:
            print(f"❌ Pipeline failed: {results['error']}")
            sys.exit(1)

if __name__ == "__main__":
    main()
