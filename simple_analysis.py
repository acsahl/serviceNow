"""
Simple analysis of ServiceNow data without external dependencies
"""

import csv
import json
from collections import Counter, defaultdict
import re
from datetime import datetime

def load_csv_data(filename):
    """Load CSV data into a list of dictionaries"""
    data = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def extract_technologies(description):
    """Extract technology keywords from description"""
    if not description:
        return []
    
    tech_keywords = [
        'ServiceNow', 'ITSM', 'ITOM', 'ITAM', 'CSM', 'HR', 'SPM', 'FSM',
        'AI', 'Machine Learning', 'Analytics', 'Reporting', 'Dashboard',
        'Workflow', 'Automation', 'Integration', 'API', 'Mobile',
        'Security', 'Compliance', 'RBAC', 'SSO', 'MFA',
        'Cloud', 'AWS', 'Azure', 'GCP', 'SaaS', 'PaaS',
        'Database', 'CMDB', 'Discovery', 'Event Management',
        'Virtual Agent', 'Chatbot', 'Knowledge Management',
        'Service Catalog', 'Incident Management', 'Change Management'
    ]
    
    found_techs = []
    description_lower = description.lower()
    
    for tech in tech_keywords:
        if tech.lower() in description_lower:
            found_techs.append(tech)
    
    return found_techs

def categorize_complexity(description):
    """Categorize request complexity based on description"""
    if not description:
        return 'Medium'
    
    description_lower = description.lower()
    
    # High complexity indicators
    high_complexity_keywords = [
        'enterprise', 'comprehensive', 'integration', 'migration', 
        'automation', 'workflow', 'security', 'compliance'
    ]
    
    # Low complexity indicators  
    low_complexity_keywords = [
        'simple', 'basic', 'quick', 'easy', 'guidance', 'overview'
    ]
    
    high_count = sum(1 for keyword in high_complexity_keywords if keyword in description_lower)
    low_count = sum(1 for keyword in low_complexity_keywords if keyword in description_lower)
    
    if high_count >= 2:
        return 'High'
    elif low_count >= 2:
        return 'Low'
    else:
        return 'Medium'

def analyze_requests():
    """Analyze the request data"""
    print("Loading request data...")
    requests = load_csv_data('csv/u_hack.csv')
    
    print(f"Loaded {len(requests)} requests")
    
    # Basic analysis
    capabilities = [req['capability'] for req in requests]
    companies = [req['company'] for req in requests]
    categories = [req['primary_category'] for req in requests]
    
    # Technology analysis
    all_technologies = []
    complexity_dist = Counter()
    
    for req in requests:
        techs = extract_technologies(req['description'])
        all_technologies.extend(techs)
        
        complexity = categorize_complexity(req['description'])
        complexity_dist[complexity] += 1
    
    tech_counts = Counter(all_technologies)
    
    # Company standardization
    company_standardized = {}
    for company in companies:
        # Remove common suffixes
        standardized = re.sub(r'(Group|Services|Solutions|Corp|Inc\.?|Ltd\.?)$', '', company).strip()
        company_standardized[company] = standardized
    
    # Count standardized companies
    std_company_counts = Counter(company_standardized.values())
    
    return {
        'total_requests': len(requests),
        'unique_capabilities': len(set(capabilities)),
        'unique_companies': len(set(company_standardized.values())),
        'top_capabilities': dict(Counter(capabilities).most_common(10)),
        'top_companies': dict(std_company_counts.most_common(10)),
        'category_distribution': dict(Counter(categories)),
        'technology_trends': dict(tech_counts.most_common(15)),
        'complexity_distribution': dict(complexity_dist)
    }

def analyze_accelerators():
    """Analyze the accelerator catalog"""
    print("Loading accelerator data...")
    accelerators = load_csv_data('csv/accelerators.csv')
    
    print(f"Loaded {len(accelerators)} accelerators")
    
    # Extract categories from accelerator names/descriptions
    categories = []
    for acc in accelerators:
        name = acc['name'].lower()
        desc = acc['description'].lower()
        
        if 'ai' in name or 'ai' in desc:
            categories.append('AI/ML')
        elif 'security' in name or 'security' in desc:
            categories.append('Security')
        elif 'analytics' in name or 'analytics' in desc:
            categories.append('Analytics')
        elif 'workflow' in name or 'workflow' in desc:
            categories.append('Workflow')
        elif 'integration' in name or 'integration' in desc:
            categories.append('Integration')
        elif 'mobile' in name or 'mobile' in desc:
            categories.append('Mobile')
        else:
            categories.append('Other')
    
    return {
        'total_accelerators': len(accelerators),
        'category_distribution': dict(Counter(categories)),
        'accelerator_names': [acc['name'] for acc in accelerators]
    }

def identify_gaps(requests_analysis, accelerators_analysis):
    """Identify gaps between requests and current accelerators"""
    print("Identifying gaps...")
    
    # Get request capabilities
    request_capabilities = set(requests_analysis['top_capabilities'].keys())
    
    # Get accelerator categories
    accelerator_categories = set(accelerators_analysis['category_distribution'].keys())
    
    # Simple gap analysis - capabilities that appear frequently in requests
    # but don't have corresponding accelerators
    gaps = []
    
    for capability, count in requests_analysis['top_capabilities'].items():
        if count >= 3:  # Only consider if significant demand
            # Check if this capability is covered by current accelerators
            capability_lower = capability.lower()
            covered = False
            
            for acc_category in accelerator_categories:
                if acc_category.lower() in capability_lower:
                    covered = True
                    break
            
            if not covered:
                gaps.append({
                    'capability': capability,
                    'request_count': count,
                    'gap_type': 'Missing Accelerator'
                })
    
    return gaps

def generate_recommendations(gaps):
    """Generate accelerator recommendations based on gaps"""
    print("Generating recommendations...")
    
    recommendations = []
    
    for gap in gaps:
        recommendation = {
            'accelerator_name': f"{gap['capability']} Accelerator",
            'capability': gap['capability'],
            'description': f"Comprehensive solution for {gap['capability'].lower()} challenges",
            'market_potential': gap['request_count'] * 50000,  # $50K per request estimate
            'priority_score': min(gap['request_count'] / 10, 1.0),
            'request_count': gap['request_count']
        }
        recommendations.append(recommendation)
    
    # Sort by priority score
    recommendations.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return recommendations

def main():
    """Main analysis function"""
    print("🚀 ServiceNow Technical Accelerators Analysis")
    print("=" * 50)
    
    try:
        # Analyze requests
        requests_analysis = analyze_requests()
        
        # Analyze accelerators
        accelerators_analysis = analyze_accelerators()
        
        # Identify gaps
        gaps = identify_gaps(requests_analysis, accelerators_analysis)
        
        # Generate recommendations
        recommendations = generate_recommendations(gaps)
        
        # Compile results
        results = {
            'requests_analysis': requests_analysis,
            'accelerators_analysis': accelerators_analysis,
            'gaps_identified': len(gaps),
            'gaps': gaps,
            'recommendations': recommendations,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Save results
        with open('servicenow_analysis_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 50)
        
        print(f"📈 Data Analyzed:")
        print(f"   • {requests_analysis['total_requests']} Access to Experts requests")
        print(f"   • {accelerators_analysis['total_accelerators']} current accelerators")
        print(f"   • {requests_analysis['unique_companies']} unique companies")
        print(f"   • {requests_analysis['unique_capabilities']} unique capabilities")
        
        print(f"\n🔍 Analysis Results:")
        print(f"   • {len(gaps)} gaps identified")
        print(f"   • {len(recommendations)} accelerator recommendations")
        
        print(f"\n🏆 Top 3 Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec['accelerator_name']}")
            print(f"      Priority Score: {rec['priority_score']:.2f}")
            print(f"      Market Potential: ${rec['market_potential']:,}")
            print(f"      Request Count: {rec['request_count']}")
            print()
        
        print(f"\n📈 Key Insights:")
        print(f"   • Most requested capability: {max(requests_analysis['top_capabilities'], key=requests_analysis['top_capabilities'].get)}")
        print(f"   • Most active company: {max(requests_analysis['top_companies'], key=requests_analysis['top_companies'].get)}")
        print(f"   • Top technology trend: {max(requests_analysis['technology_trends'], key=requests_analysis['technology_trends'].get)}")
        
        print(f"\n✅ Analysis complete! Results saved to servicenow_analysis_results.json")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
