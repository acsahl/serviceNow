"""
Data Generator for ServiceNow Technical Accelerators
Creates realistic sample data for testing the request analysis agent
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json

class DataGenerator:
    def __init__(self):
        self.industries = [
            'Healthcare', 'Financial Services', 'Manufacturing', 'Government',
            'Education', 'Retail', 'Technology', 'Energy', 'Transportation', 'Telecommunications'
        ]
        
        self.company_sizes = ['Small (1-50)', 'Medium (51-500)', 'Large (501-5000)', 'Enterprise (5000+)']
        
        self.accelerator_categories = [
            'IT Service Management', 'Security & Compliance', 'Cloud Migration',
            'Process Automation', 'Data Analytics', 'Integration', 'Mobile Development',
            'AI/ML Implementation', 'DevOps', 'Customer Experience'
        ]
        
        self.request_types = [
            'Custom Development', 'Integration', 'Process Optimization',
            'Security Enhancement', 'Cloud Migration', 'Data Migration',
            'Mobile App Development', 'AI/ML Implementation', 'Performance Optimization',
            'Compliance Implementation'
        ]
        
        self.technologies = [
            'ServiceNow', 'AWS', 'Azure', 'GCP', 'Salesforce', 'SAP', 'Oracle',
            'Microsoft 365', 'Slack', 'Teams', 'Jira', 'Confluence', 'Power BI',
            'Tableau', 'Python', 'Java', 'JavaScript', 'React', 'Angular', 'Vue'
        ]

    def generate_companies(self, num_companies=1000):
        """Generate company data"""
        companies = []
        
        for i in range(num_companies):
            company = {
                'company_id': f'COMP_{i+1:04d}',
                'company_name': f'Company {i+1}',
                'industry': random.choice(self.industries),
                'size': random.choice(self.company_sizes),
                'revenue': random.randint(1, 1000) * 1000000,  # Revenue in millions
                'employees': random.randint(10, 50000),
                'location': random.choice(['North America', 'Europe', 'Asia Pacific', 'Latin America']),
                'maturity_level': random.choice(['Startup', 'Growing', 'Mature', 'Enterprise']),
                'tech_stack': random.sample(self.technologies, random.randint(3, 8))
            }
            companies.append(company)
        
        return pd.DataFrame(companies)

    def generate_requests(self, num_requests=2000, companies_df=None):
        """Generate Access to Experts (A2E) request data"""
        requests = []
        
        if companies_df is None:
            companies_df = self.generate_companies(100)
        
        for i in range(num_requests):
            company = companies_df.iloc[random.randint(0, len(companies_df)-1)]
            
            # Generate request based on company characteristics
            request = {
                'request_id': f'REQ_{i+1:06d}',
                'company_id': company['company_id'],
                'industry': company['industry'],
                'size': company['size'],
                'request_type': random.choice(self.request_types),
                'description': self._generate_request_description(company),
                'priority': random.choice(['Low', 'Medium', 'High', 'Critical']),
                'complexity': random.choice(['Simple', 'Medium', 'Complex', 'Very Complex']),
                'estimated_hours': random.randint(8, 200),
                'budget_range': random.choice(['<10K', '10K-50K', '50K-100K', '100K-500K', '>500K']),
                'technologies_involved': random.sample(self.technologies, random.randint(1, 5)),
                'business_impact': random.choice(['Low', 'Medium', 'High', 'Critical']),
                'urgency': random.choice(['Low', 'Medium', 'High', 'Critical']),
                'request_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'status': random.choice(['Open', 'In Progress', 'Completed', 'Cancelled']),
                'tags': self._generate_tags(company)
            }
            requests.append(request)
        
        return pd.DataFrame(requests)

    def generate_catalog(self, num_accelerators=50):
        """Generate current catalog of accelerators"""
        catalog = []
        
        for i in range(num_accelerators):
            accelerator = {
                'accelerator_id': f'ACC_{i+1:03d}',
                'name': f'Accelerator {i+1}',
                'category': random.choice(self.accelerator_categories),
                'description': f'Comprehensive solution for {random.choice(self.request_types).lower()}',
                'technologies': random.sample(self.technologies, random.randint(2, 6)),
                'duration_weeks': random.randint(2, 12),
                'complexity': random.choice(['Simple', 'Medium', 'Complex']),
                'target_industries': random.sample(self.industries, random.randint(2, 5)),
                'success_rate': random.uniform(0.7, 0.95),
                'avg_rating': random.uniform(3.5, 5.0),
                'delivery_count': random.randint(10, 200),
                'revenue_generated': random.randint(100000, 5000000),
                'last_updated': datetime.now() - timedelta(days=random.randint(1, 180))
            }
            catalog.append(accelerator)
        
        return pd.DataFrame(catalog)

    def _generate_request_description(self, company):
        """Generate realistic request descriptions"""
        templates = [
            f"We need help with {random.choice(self.request_types).lower()} for our {company['industry'].lower()} operations",
            f"Looking for expertise in {random.choice(self.technologies)} to improve our business processes",
            f"Require assistance with {random.choice(['digital transformation', 'process automation', 'data integration'])}",
            f"Need support for {random.choice(['security compliance', 'cloud migration', 'performance optimization'])}",
            f"Seeking guidance on {random.choice(['AI implementation', 'mobile development', 'integration'])}"
        ]
        return random.choice(templates)

    def _generate_tags(self, company):
        """Generate relevant tags for requests"""
        tags = [company['industry'], company['size'], company['maturity_level']]
        tags.extend(random.sample(self.technologies, random.randint(1, 3)))
        return tags

    def save_data(self):
        """Generate and save all data files"""
        print("Generating companies data...")
        companies_df = self.generate_companies(1000)
        companies_df.to_csv('companies.csv', index=False)
        
        print("Generating requests data...")
        requests_df = self.generate_requests(2000, companies_df)
        requests_df.to_csv('requests.csv', index=False)
        
        print("Generating catalog data...")
        catalog_df = self.generate_catalog(50)
        catalog_df.to_csv('catalog.csv', index=False)
        
        print("Data generation complete!")
        return companies_df, requests_df, catalog_df

if __name__ == "__main__":
    generator = DataGenerator()
    companies, requests, catalog = generator.save_data()
    
    print(f"\nGenerated data summary:")
    print(f"Companies: {len(companies)}")
    print(f"Requests: {len(requests)}")
    print(f"Catalog items: {len(catalog)}")
