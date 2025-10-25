"""
ServiceNow Technical Accelerators Request Analysis Agent

This module provides intelligent analysis of customer requests to identify
emerging needs and recommend new accelerators for the portfolio.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

class RequestAnalyzer:
    """
    Main class for analyzing customer requests and generating accelerator recommendations
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.scaler = StandardScaler()
        
        # Analysis results storage
        self.patterns = {}
        self.recommendations = {}
        self.insights = {}
        
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text data"""
        if pd.isna(text):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize and lemmatize
        tokens = word_tokenize(text)
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                 if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def load_data(self, companies_file: str, requests_file: str, catalog_file: str):
        """Load and prepare data for analysis"""
        print("Loading data...")
        
        self.companies_df = pd.read_csv(companies_file)
        self.requests_df = pd.read_csv(requests_file)
        self.catalog_df = pd.read_csv(catalog_file)
        
        # Convert date columns
        self.requests_df['request_date'] = pd.to_datetime(self.requests_df['request_date'])
        
        print(f"Loaded {len(self.companies_df)} companies, {len(self.requests_df)} requests, {len(self.catalog_df)} catalog items")
        
    def analyze_request_patterns(self) -> Dict:
        """Analyze patterns in customer requests"""
        print("Analyzing request patterns...")
        
        # Preprocess request descriptions
        self.requests_df['processed_description'] = self.requests_df['description'].apply(self.preprocess_text)
        
        # Vectorize text data
        tfidf_matrix = self.vectorizer.fit_transform(self.requests_df['processed_description'])
        
        # Topic modeling using LDA
        lda = LatentDirichletAllocation(n_components=10, random_state=42)
        lda.fit(tfidf_matrix)
        
        # Get topic distributions
        topic_distributions = lda.transform(tfidf_matrix)
        self.requests_df['dominant_topic'] = np.argmax(topic_distributions, axis=1)
        
        # Cluster requests using K-means
        kmeans = KMeans(n_clusters=8, random_state=42)
        clusters = kmeans.fit_predict(tfidf_matrix)
        self.requests_df['cluster'] = clusters
        
        # Analyze patterns by industry
        industry_patterns = self.requests_df.groupby(['industry', 'request_type']).size().unstack(fill_value=0)
        
        # Analyze patterns by company size
        size_patterns = self.requests_df.groupby(['size', 'request_type']).size().unstack(fill_value=0)
        
        # Analyze urgency and priority patterns
        urgency_analysis = self.requests_df.groupby(['urgency', 'priority']).size().unstack(fill_value=0)
        
        self.patterns = {
            'topic_model': lda,
            'vectorizer': self.vectorizer,
            'industry_patterns': industry_patterns,
            'size_patterns': size_patterns,
            'urgency_analysis': urgency_analysis,
            'clusters': clusters,
            'topics': topic_distributions
        }
        
        return self.patterns
    
    def identify_emerging_needs(self) -> List[Dict]:
        """Identify emerging needs and gaps in the catalog"""
        print("Identifying emerging needs...")
        
        # Analyze request types not covered by current catalog
        catalog_categories = set(self.catalog_df['category'].unique())
        request_types = set(self.requests_df['request_type'].unique())
        
        # Find gaps
        gaps = request_types - catalog_categories
        
        # Analyze trending technologies
        tech_counter = Counter()
        for tech_list in self.requests_df['technologies_involved']:
            if isinstance(tech_list, str):
                techs = eval(tech_list) if tech_list.startswith('[') else tech_list.split(',')
                tech_counter.update(techs)
        
        trending_techs = tech_counter.most_common(10)
        
        # Analyze high-priority, high-urgency requests
        critical_requests = self.requests_df[
            (self.requests_df['priority'] == 'High') & 
            (self.requests_df['urgency'] == 'High')
        ]
        
        # Find common themes in critical requests
        critical_themes = critical_requests['request_type'].value_counts()
        
        emerging_needs = []
        
        for gap in gaps:
            gap_requests = self.requests_df[self.requests_df['request_type'] == gap]
            if len(gap_requests) > 0:
                emerging_needs.append({
                    'category': gap,
                    'request_count': len(gap_requests),
                    'avg_budget': gap_requests['budget_range'].mode().iloc[0] if len(gap_requests) > 0 else 'Unknown',
                    'industries': gap_requests['industry'].value_counts().head(3).to_dict(),
                    'technologies': gap_requests['technologies_involved'].apply(
                        lambda x: eval(x) if isinstance(x, str) and x.startswith('[') else x.split(',')
                    ).explode().value_counts().head(5).to_dict(),
                    'priority_score': self._calculate_priority_score(gap_requests)
                })
        
        return emerging_needs
    
    def _calculate_priority_score(self, requests_df: pd.DataFrame) -> float:
        """Calculate priority score for a request type"""
        priority_weights = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
        urgency_weights = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
        
        priority_score = requests_df['priority'].map(priority_weights).mean()
        urgency_score = requests_df['urgency'].map(urgency_weights).mean()
        
        return (priority_score + urgency_score) / 2
    
    def recommend_accelerators(self, emerging_needs: List[Dict]) -> List[Dict]:
        """Generate accelerator recommendations based on emerging needs"""
        print("Generating accelerator recommendations...")
        
        recommendations = []
        
        for need in emerging_needs:
            # Calculate potential market size
            market_size = need['request_count'] * 1000  # Estimate revenue per request
            
            # Determine complexity based on technologies involved
            tech_count = len(need['technologies'])
            complexity = 'Simple' if tech_count <= 2 else 'Medium' if tech_count <= 4 else 'Complex'
            
            # Estimate duration based on complexity
            duration_weeks = 2 if complexity == 'Simple' else 4 if complexity == 'Medium' else 8
            
            # Calculate success probability
            success_prob = min(0.95, 0.7 + (need['priority_score'] - 2) * 0.1)
            
            recommendation = {
                'accelerator_name': f"{need['category']} Accelerator",
                'category': need['category'],
                'description': f"Comprehensive solution for {need['category'].lower()} challenges",
                'target_industries': list(need['industries'].keys())[:3],
                'technologies': list(need['technologies'].keys())[:5],
                'complexity': complexity,
                'duration_weeks': duration_weeks,
                'estimated_market_size': market_size,
                'success_probability': success_prob,
                'priority_score': need['priority_score'],
                'request_count': need['request_count'],
                'recommended_budget_range': need['avg_budget'],
                'business_justification': self._generate_business_justification(need)
            }
            
            recommendations.append(recommendation)
        
        # Sort by priority score and market size
        recommendations.sort(key=lambda x: x['priority_score'] * x['estimated_market_size'], reverse=True)
        
        return recommendations
    
    def _generate_business_justification(self, need: Dict) -> str:
        """Generate business justification for accelerator recommendation"""
        industries = ', '.join(list(need['industries'].keys())[:2])
        techs = ', '.join(list(need['technologies'].keys())[:3])
        
        return f"""
        High demand for {need['category']} solutions across {industries} industries. 
        {need['request_count']} requests identified with technologies including {techs}. 
        Priority score of {need['priority_score']:.1f} indicates strong business need.
        """
    
    def generate_insights(self) -> Dict:
        """Generate comprehensive insights and analytics"""
        print("Generating insights...")
        
        # Request volume trends
        monthly_requests = self.requests_df.groupby(
            self.requests_df['request_date'].dt.to_period('M')
        ).size()
        
        # Industry distribution
        industry_dist = self.requests_df['industry'].value_counts()
        
        # Technology trends
        tech_trends = self.requests_df['technologies_involved'].apply(
            lambda x: eval(x) if isinstance(x, str) and x.startswith('[') else x.split(',')
        ).explode().value_counts()
        
        # Priority and urgency analysis
        priority_dist = self.requests_df['priority'].value_counts()
        urgency_dist = self.requests_df['urgency'].value_counts()
        
        # Budget analysis
        budget_dist = self.requests_df['budget_range'].value_counts()
        
        self.insights = {
            'monthly_requests': monthly_requests.to_dict(),
            'industry_distribution': industry_dist.to_dict(),
            'technology_trends': tech_trends.head(10).to_dict(),
            'priority_distribution': priority_dist.to_dict(),
            'urgency_distribution': urgency_dist.to_dict(),
            'budget_distribution': budget_dist.to_dict(),
            'total_requests': len(self.requests_df),
            'unique_companies': self.requests_df['company_id'].nunique(),
            'avg_request_complexity': self.requests_df['complexity'].value_counts().to_dict()
        }
        
        return self.insights
    
    def create_visualizations(self) -> Dict:
        """Create interactive visualizations for insights"""
        print("Creating visualizations...")
        
        visualizations = {}
        
        # Industry distribution pie chart
        fig_industry = px.pie(
            values=self.insights['industry_distribution'].values(),
            names=self.insights['industry_distribution'].keys(),
            title="Request Distribution by Industry"
        )
        visualizations['industry_distribution'] = fig_industry
        
        # Technology trends bar chart
        tech_data = list(self.insights['technology_trends'].items())[:10]
        fig_tech = px.bar(
            x=[item[0] for item in tech_data],
            y=[item[1] for item in tech_data],
            title="Top 10 Technology Trends"
        )
        visualizations['technology_trends'] = fig_tech
        
        # Priority vs Urgency heatmap
        priority_urgency = self.requests_df.groupby(['priority', 'urgency']).size().unstack(fill_value=0)
        fig_heatmap = px.imshow(
            priority_urgency.values,
            x=priority_urgency.columns,
            y=priority_urgency.index,
            title="Priority vs Urgency Heatmap"
        )
        visualizations['priority_urgency_heatmap'] = fig_heatmap
        
        return visualizations
    
    def run_complete_analysis(self, companies_file: str, requests_file: str, catalog_file: str) -> Dict:
        """Run complete analysis pipeline"""
        print("Starting complete analysis...")
        
        # Load data
        self.load_data(companies_file, requests_file, catalog_file)
        
        # Analyze patterns
        patterns = self.analyze_request_patterns()
        
        # Identify emerging needs
        emerging_needs = self.identify_emerging_needs()
        
        # Generate recommendations
        recommendations = self.recommend_accelerators(emerging_needs)
        
        # Generate insights
        insights = self.generate_insights()
        
        # Create visualizations
        visualizations = self.create_visualizations()
        
        # Compile results
        results = {
            'patterns': patterns,
            'emerging_needs': emerging_needs,
            'recommendations': recommendations,
            'insights': insights,
            'visualizations': visualizations,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        print("Analysis complete!")
        return results
    
    def save_results(self, results: Dict, output_file: str = 'analysis_results.json'):
        """Save analysis results to file"""
        # Convert numpy arrays and other non-serializable objects
        serializable_results = self._make_serializable(results)
        
        with open(output_file, 'w') as f:
            json.dump(serializable_results, f, indent=2, default=str)
        
        print(f"Results saved to {output_file}")
    
    def _make_serializable(self, obj):
        """Convert non-serializable objects to serializable format"""
        if isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        else:
            return obj

def main():
    """Main function to run the analysis"""
    analyzer = RequestAnalyzer()
    
    # Run analysis (assuming data files exist)
    try:
        results = analyzer.run_complete_analysis(
            'companies.csv',
            'requests.csv', 
            'catalog.csv'
        )
        
        # Save results
        analyzer.save_results(results)
        
        # Print summary
        print("\n" + "="*50)
        print("ANALYSIS SUMMARY")
        print("="*50)
        print(f"Total requests analyzed: {results['insights']['total_requests']}")
        print(f"Unique companies: {results['insights']['unique_companies']}")
        print(f"Emerging needs identified: {len(results['emerging_needs'])}")
        print(f"Accelerator recommendations: {len(results['recommendations'])}")
        
        print("\nTop 3 Recommendations:")
        for i, rec in enumerate(results['recommendations'][:3], 1):
            print(f"{i}. {rec['accelerator_name']} - Priority: {rec['priority_score']:.1f}")
        
    except FileNotFoundError as e:
        print(f"Data file not found: {e}")
        print("Please ensure data files exist or run data_generator.py first")

if __name__ == "__main__":
    main()
