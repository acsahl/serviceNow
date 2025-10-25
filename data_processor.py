"""
Data Processor for ServiceNow Technical Accelerators
Processes the actual CSV data and synthesizes insights for the analysis agent
"""

import pandas as pd
import numpy as np
from collections import Counter
import re
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class DataProcessor:
    """
    Processes the actual ServiceNow CSV data and prepares it for analysis
    """
    
    def __init__(self):
        self.requests_df = None
        self.accelerators_df = None
        self.processed_data = {}
        
    def load_data(self, requests_file: str = "csv/u_hack.csv", accelerators_file: str = "csv/accelerators.csv"):
        """Load the actual CSV data files"""
        print("Loading actual ServiceNow data...")
        
        try:
            self.requests_df = pd.read_csv(requests_file)
            self.accelerators_df = pd.read_csv(accelerators_file)
            
            print(f"✅ Loaded {len(self.requests_df)} requests and {len(self.accelerators_df)} accelerators")
            
            # Basic data cleaning
            self._clean_data()
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
        
        return True
    
    def _clean_data(self):
        """Clean and standardize the data"""
        # Remove any rows with missing critical data
        self.requests_df = self.requests_df.dropna(subset=['capability', 'description'])
        
        # Standardize company names (remove duplicates like "Acme Financial Group" vs "Acme Financial Services")
        self.requests_df['company_standardized'] = self.requests_df['company'].str.replace(
            r'(Group|Services|Solutions|Corp|Inc\.?|Ltd\.?)$', '', regex=True
        ).str.strip()
        
        # Extract key technologies from descriptions
        self.requests_df['technologies'] = self.requests_df['description'].apply(self._extract_technologies)
        
        # Categorize requests by complexity based on description length and keywords
        self.requests_df['complexity'] = self.requests_df['description'].apply(self._categorize_complexity)
        
        # Extract business impact keywords
        self.requests_df['business_impact'] = self.requests_df['description'].apply(self._extract_business_impact)
        
        # Generate synthetic company data
        self._generate_company_metadata()
    
    def _extract_technologies(self, description: str) -> List[str]:
        """Extract technology keywords from request descriptions"""
        if pd.isna(description):
            return []
        
        # Common ServiceNow and IT technologies
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
    
    def _categorize_complexity(self, description: str) -> str:
        """Categorize request complexity based on description"""
        if pd.isna(description):
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
    
    def _extract_business_impact(self, description: str) -> str:
        """Extract business impact level from description"""
        if pd.isna(description):
            return 'Medium'
        
        description_lower = description.lower()
        
        # High impact indicators
        high_impact_keywords = [
            'critical', 'security', 'compliance', 'enterprise', 'strategic',
            'business continuity', 'risk', 'audit', 'governance'
        ]
        
        # Low impact indicators
        low_impact_keywords = [
            'convenience', 'nice to have', 'improvement', 'enhancement'
        ]
        
        high_count = sum(1 for keyword in high_impact_keywords if keyword in description_lower)
        low_count = sum(1 for keyword in low_impact_keywords if keyword in description_lower)
        
        if high_count >= 2:
            return 'High'
        elif low_count >= 1:
            return 'Low'
        else:
            return 'Medium'
    
    def _generate_company_metadata(self):
        """Generate additional company metadata for analysis"""
        # Create company size based on request volume
        company_request_counts = self.requests_df['company_standardized'].value_counts()
        
        def categorize_company_size(count):
            if count >= 20:
                return 'Enterprise'
            elif count >= 10:
                return 'Large'
            elif count >= 5:
                return 'Medium'
            else:
                return 'Small'
        
        self.requests_df['company_size'] = self.requests_df['company_standardized'].map(
            lambda x: categorize_company_size(company_request_counts.get(x, 0))
        )
        
        # Generate industry based on company name patterns
        def infer_industry(company_name):
            name_lower = company_name.lower()
            if any(word in name_lower for word in ['financial', 'bank', 'credit']):
                return 'Financial Services'
            elif any(word in name_lower for word in ['tech', 'software', 'digital']):
                return 'Technology'
            elif any(word in name_lower for word in ['health', 'medical', 'care']):
                return 'Healthcare'
            elif any(word in name_lower for word in ['manufacturing', 'industrial']):
                return 'Manufacturing'
            else:
                return 'Other'
        
        self.requests_df['industry'] = self.requests_df['company_standardized'].apply(infer_industry)
    
    def analyze_request_patterns(self) -> Dict:
        """Analyze patterns in the actual request data"""
        print("Analyzing request patterns...")
        
        # Capability analysis
        capability_counts = self.requests_df['capability'].value_counts()
        top_capabilities = capability_counts.head(10)
        
        # Company analysis
        company_counts = self.requests_df['company_standardized'].value_counts()
        top_companies = company_counts.head(10)
        
        # Category analysis
        category_counts = self.requests_df['primary_category'].value_counts()
        
        # Technology analysis
        all_technologies = []
        for tech_list in self.requests_df['technologies']:
            all_technologies.extend(tech_list)
        tech_counts = Counter(all_technologies)
        top_technologies = dict(tech_counts.most_common(15))
        
        # Complexity analysis
        complexity_counts = self.requests_df['complexity'].value_counts()
        
        # Business impact analysis
        impact_counts = self.requests_df['business_impact'].value_counts()
        
        # Industry analysis
        industry_counts = self.requests_df['industry'].value_counts()
        
        patterns = {
            'top_capabilities': top_capabilities.to_dict(),
            'top_companies': top_companies.to_dict(),
            'category_distribution': category_counts.to_dict(),
            'technology_trends': top_technologies,
            'complexity_distribution': complexity_counts.to_dict(),
            'impact_distribution': impact_counts.to_dict(),
            'industry_distribution': industry_counts.to_dict(),
            'total_requests': len(self.requests_df),
            'unique_companies': self.requests_df['company_standardized'].nunique(),
            'unique_capabilities': self.requests_df['capability'].nunique()
        }
        
        return patterns
    
    def identify_emerging_needs(self) -> List[Dict]:
        """Identify emerging needs and gaps based on actual data"""
        print("Identifying emerging needs...")
        
        # Get current accelerator categories
        accelerator_categories = set()
        for desc in self.accelerators_df['description']:
            # Extract key terms from accelerator descriptions
            if 'AI' in desc:
                accelerator_categories.add('AI/ML Implementation')
            if 'Security' in desc:
                accelerator_categories.add('Security Enhancement')
            if 'Analytics' in desc:
                accelerator_categories.add('Data Analytics')
            if 'Workflow' in desc:
                accelerator_categories.add('Process Automation')
            if 'Integration' in desc:
                accelerator_categories.add('Integration')
            if 'Mobile' in desc:
                accelerator_categories.add('Mobile Development')
        
        # Analyze request capabilities not covered by current accelerators
        request_capabilities = set(self.requests_df['capability'].unique())
        
        # Find gaps
        gaps = []
        for capability in request_capabilities:
            if capability not in accelerator_categories:
                capability_requests = self.requests_df[self.requests_df['capability'] == capability]
                
                if len(capability_requests) >= 3:  # Only consider if significant demand
                    gap_analysis = {
                        'capability': capability,
                        'request_count': len(capability_requests),
                        'companies': capability_requests['company_standardized'].nunique(),
                        'industries': capability_requests['industry'].value_counts().to_dict(),
                        'technologies': self._get_tech_for_capability(capability),
                        'complexity_distribution': capability_requests['complexity'].value_counts().to_dict(),
                        'impact_distribution': capability_requests['business_impact'].value_counts().to_dict(),
                        'priority_score': self._calculate_capability_priority(capability_requests)
                    }
                    gaps.append(gap_analysis)
        
        # Sort by priority score
        gaps.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return gaps
    
    def _get_tech_for_capability(self, capability: str) -> Dict:
        """Get technology distribution for a specific capability"""
        capability_requests = self.requests_df[self.requests_df['capability'] == capability]
        all_techs = []
        for tech_list in capability_requests['technologies']:
            all_techs.extend(tech_list)
        return dict(Counter(all_techs).most_common(10))
    
    def _calculate_capability_priority(self, capability_requests: pd.DataFrame) -> float:
        """Calculate priority score for a capability based on various factors"""
        # Factors: request count, company diversity, complexity, business impact
        
        request_count_score = min(len(capability_requests) / 10, 1.0)  # Max 1.0 for 10+ requests
        company_diversity_score = min(capability_requests['company_standardized'].nunique() / 5, 1.0)  # Max 1.0 for 5+ companies
        
        # Complexity score (higher complexity = higher priority)
        complexity_scores = {'Low': 0.3, 'Medium': 0.6, 'High': 1.0}
        avg_complexity = capability_requests['complexity'].map(complexity_scores).mean()
        
        # Impact score
        impact_scores = {'Low': 0.3, 'Medium': 0.6, 'High': 1.0}
        avg_impact = capability_requests['business_impact'].map(impact_scores).mean()
        
        # Weighted priority score
        priority_score = (
            request_count_score * 0.3 +
            company_diversity_score * 0.2 +
            avg_complexity * 0.3 +
            avg_impact * 0.2
        )
        
        return priority_score
    
    def generate_recommendations(self, emerging_needs: List[Dict]) -> List[Dict]:
        """Generate accelerator recommendations based on emerging needs"""
        print("Generating accelerator recommendations...")
        
        recommendations = []
        
        for need in emerging_needs:
            # Generate accelerator name
            accelerator_name = f"{need['capability']} Accelerator"
            
            # Determine complexity based on request complexity distribution
            complexity_dist = need['complexity_distribution']
            if complexity_dist.get('High', 0) > complexity_dist.get('Low', 0):
                accelerator_complexity = 'Complex'
                duration_weeks = 8
            elif complexity_dist.get('Low', 0) > complexity_dist.get('High', 0):
                accelerator_complexity = 'Simple'
                duration_weeks = 4
            else:
                accelerator_complexity = 'Medium'
                duration_weeks = 6
            
            # Calculate market potential
            market_size = need['request_count'] * 50000  # Estimate $50K per request
            
            # Success probability based on priority score
            success_probability = min(0.95, 0.7 + need['priority_score'] * 0.25)
            
            # Generate description
            description = f"Comprehensive solution for {need['capability'].lower()} challenges, addressing the needs of {need['companies']} companies across multiple industries."
            
            recommendation = {
                'accelerator_name': accelerator_name,
                'capability': need['capability'],
                'description': description,
                'complexity': accelerator_complexity,
                'duration_weeks': duration_weeks,
                'estimated_market_size': market_size,
                'success_probability': success_probability,
                'priority_score': need['priority_score'],
                'request_count': need['request_count'],
                'target_companies': need['companies'],
                'target_industries': list(need['industries'].keys())[:3],
                'key_technologies': list(need['technologies'].keys())[:5],
                'business_justification': self._generate_business_justification(need)
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_business_justification(self, need: Dict) -> str:
        """Generate business justification for accelerator recommendation"""
        industries = ', '.join(list(need['industries'].keys())[:2])
        techs = ', '.join(list(need['technologies'].keys())[:3])
        
        return f"""
        High demand for {need['capability']} solutions with {need['request_count']} requests from {need['companies']} companies. 
        Strong presence in {industries} industries with technologies including {techs}. 
        Priority score of {need['priority_score']:.2f} indicates significant business opportunity.
        """
    
    def generate_insights(self) -> Dict:
        """Generate comprehensive insights from the data"""
        print("Generating insights...")
        
        # Request volume by capability
        capability_volume = self.requests_df['capability'].value_counts()
        
        # Company engagement analysis
        company_engagement = self.requests_df.groupby('company_standardized').agg({
            'capability': 'count',
            'complexity': lambda x: x.value_counts().to_dict(),
            'business_impact': lambda x: x.value_counts().to_dict()
        }).rename(columns={'capability': 'request_count'})
        
        # Technology adoption patterns
        tech_adoption = {}
        for tech in ['AI', 'Analytics', 'Security', 'Automation', 'Integration']:
            tech_requests = self.requests_df[
                self.requests_df['technologies'].apply(lambda x: tech in x)
            ]
            tech_adoption[tech] = {
                'request_count': len(tech_requests),
                'companies': tech_requests['company_standardized'].nunique(),
                'avg_complexity': tech_requests['complexity'].value_counts().to_dict()
            }
        
        # Industry trends
        industry_trends = self.requests_df.groupby('industry').agg({
            'capability': 'count',
            'complexity': lambda x: x.value_counts().to_dict(),
            'business_impact': lambda x: x.value_counts().to_dict()
        }).rename(columns={'capability': 'request_count'})
        
        insights = {
            'capability_volume': capability_volume.to_dict(),
            'company_engagement': company_engagement.to_dict(),
            'technology_adoption': tech_adoption,
            'industry_trends': industry_trends.to_dict(),
            'summary': {
                'total_requests': len(self.requests_df),
                'unique_companies': self.requests_df['company_standardized'].nunique(),
                'unique_capabilities': self.requests_df['capability'].nunique(),
                'avg_requests_per_company': len(self.requests_df) / self.requests_df['company_standardized'].nunique()
            }
        }
        
        return insights
    
    def run_complete_analysis(self) -> Dict:
        """Run complete analysis on the actual data"""
        print("🚀 Starting complete analysis of ServiceNow data...")
        
        # Load data
        if not self.load_data():
            return {"error": "Failed to load data"}
        
        # Analyze patterns
        patterns = self.analyze_request_patterns()
        
        # Identify emerging needs
        emerging_needs = self.identify_emerging_needs()
        
        # Generate recommendations
        recommendations = self.generate_recommendations(emerging_needs)
        
        # Generate insights
        insights = self.generate_insights()
        
        # Compile results
        results = {
            'patterns': patterns,
            'emerging_needs': emerging_needs,
            'recommendations': recommendations,
            'insights': insights,
            'analysis_timestamp': datetime.now().isoformat(),
            'data_summary': {
                'requests_analyzed': len(self.requests_df),
                'accelerators_in_catalog': len(self.accelerators_df),
                'emerging_needs_identified': len(emerging_needs),
                'recommendations_generated': len(recommendations)
            }
        }
        
        print("✅ Analysis complete!")
        return results
    
    def save_results(self, results: Dict, output_file: str = 'servicenow_analysis_results.json'):
        """Save analysis results to file"""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"📊 Results saved to {output_file}")
    
    def print_summary(self, results: Dict):
        """Print analysis summary"""
        print("\n" + "="*60)
        print("🎯 SERVICENOW TECHNICAL ACCELERATORS ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"📊 Data Analyzed:")
        print(f"   • {results['data_summary']['requests_analyzed']} Access to Experts requests")
        print(f"   • {results['data_summary']['accelerators_in_catalog']} current accelerators")
        
        print(f"\n🔍 Analysis Results:")
        print(f"   • {results['data_summary']['emerging_needs_identified']} emerging needs identified")
        print(f"   • {results['data_summary']['recommendations_generated']} accelerator recommendations")
        
        print(f"\n🏆 Top 3 Recommendations:")
        for i, rec in enumerate(results['recommendations'][:3], 1):
            print(f"   {i}. {rec['accelerator_name']}")
            print(f"      Priority Score: {rec['priority_score']:.2f}")
            print(f"      Market Size: ${rec['estimated_market_size']:,}")
            print(f"      Success Probability: {rec['success_probability']:.1%}")
            print()
        
        print(f"\n📈 Key Insights:")
        patterns = results['patterns']
        print(f"   • Most requested capability: {max(patterns['top_capabilities'], key=patterns['top_capabilities'].get)}")
        print(f"   • Most active company: {max(patterns['top_companies'], key=patterns['top_companies'].get)}")
        print(f"   • Top technology trend: {max(patterns['technology_trends'], key=patterns['technology_trends'].get)}")

def main():
    """Main function to run the analysis"""
    processor = DataProcessor()
    
    # Run complete analysis
    results = processor.run_complete_analysis()
    
    if "error" not in results:
        # Save results
        processor.save_results(results)
        
        # Print summary
        processor.print_summary(results)
    else:
        print(f"❌ Analysis failed: {results['error']}")

if __name__ == "__main__":
    main()
