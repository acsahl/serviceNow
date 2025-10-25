"""
FastAPI web service for ServiceNow Technical Accelerators Request Analysis Agent
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import asyncio
from datetime import datetime
import uvicorn

from request_analyzer import RequestAnalyzer

app = FastAPI(
    title="ServiceNow Technical Accelerators Analysis API",
    description="API for analyzing customer requests and recommending new accelerators",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global analyzer instance
analyzer = RequestAnalyzer()
analysis_results = {}

class AnalysisRequest(BaseModel):
    companies_file: str = "companies.csv"
    requests_file: str = "requests.csv"
    catalog_file: str = "catalog.csv"

class RecommendationRequest(BaseModel):
    category: str
    priority_score: float
    request_count: int
    technologies: List[str]
    industries: List[str]

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ServiceNow Technical Accelerators Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/analyze - Run complete analysis",
            "patterns": "/patterns - Get request patterns",
            "recommendations": "/recommendations - Get accelerator recommendations",
            "insights": "/insights - Get analysis insights",
            "health": "/health - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/analyze")
async def run_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Run complete analysis on the provided data files"""
    try:
        # Run analysis in background
        background_tasks.add_task(
            run_analysis_task,
            request.companies_file,
            request.requests_file,
            request.catalog_file
        )
        
        return {
            "message": "Analysis started",
            "status": "running",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_analysis_task(companies_file: str, requests_file: str, catalog_file: str):
    """Background task to run analysis"""
    global analysis_results
    try:
        results = analyzer.run_complete_analysis(companies_file, requests_file, catalog_file)
        analysis_results = results
        print("Analysis completed successfully")
    except Exception as e:
        print(f"Analysis failed: {str(e)}")
        analysis_results = {"error": str(e)}

@app.get("/patterns")
async def get_patterns():
    """Get request patterns and trends"""
    if not analysis_results or "patterns" not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not completed yet")
    
    patterns = analysis_results["patterns"]
    
    return {
        "industry_patterns": patterns["industry_patterns"].to_dict() if hasattr(patterns["industry_patterns"], 'to_dict') else patterns["industry_patterns"],
        "size_patterns": patterns["size_patterns"].to_dict() if hasattr(patterns["size_patterns"], 'to_dict') else patterns["size_patterns"],
        "urgency_analysis": patterns["urgency_analysis"].to_dict() if hasattr(patterns["urgency_analysis"], 'to_dict') else patterns["urgency_analysis"],
        "cluster_count": len(set(patterns["clusters"])),
        "topic_count": patterns["topics"].shape[1] if hasattr(patterns["topics"], 'shape') else 0
    }

@app.get("/recommendations")
async def get_recommendations():
    """Get accelerator recommendations"""
    if not analysis_results or "recommendations" not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not completed yet")
    
    recommendations = analysis_results["recommendations"]
    
    return {
        "total_recommendations": len(recommendations),
        "recommendations": recommendations,
        "top_3": recommendations[:3] if len(recommendations) >= 3 else recommendations
    }

@app.get("/insights")
async def get_insights():
    """Get analysis insights and statistics"""
    if not analysis_results or "insights" not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not completed yet")
    
    insights = analysis_results["insights"]
    
    return {
        "summary": {
            "total_requests": insights["total_requests"],
            "unique_companies": insights["unique_companies"],
            "analysis_timestamp": analysis_results.get("analysis_timestamp", "Unknown")
        },
        "distributions": {
            "industry": insights["industry_distribution"],
            "priority": insights["priority_distribution"],
            "urgency": insights["urgency_distribution"],
            "budget": insights["budget_distribution"]
        },
        "trends": {
            "technology": insights["technology_trends"],
            "monthly_requests": insights["monthly_requests"]
        }
    }

@app.get("/emerging-needs")
async def get_emerging_needs():
    """Get identified emerging needs and gaps"""
    if not analysis_results or "emerging_needs" not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not completed yet")
    
    emerging_needs = analysis_results["emerging_needs"]
    
    return {
        "total_emerging_needs": len(emerging_needs),
        "emerging_needs": emerging_needs,
        "priority_sorted": sorted(emerging_needs, key=lambda x: x.get('priority_score', 0), reverse=True)
    }

@app.post("/recommend-accelerator")
async def recommend_accelerator(request: RecommendationRequest):
    """Generate a specific accelerator recommendation"""
    try:
        # Create a mock emerging need
        emerging_need = {
            'category': request.category,
            'request_count': request.request_count,
            'priority_score': request.priority_score,
            'technologies': {tech: 1 for tech in request.technologies},
            'industries': {industry: 1 for industry in request.industries},
            'avg_budget': '50K-100K'  # Default budget
        }
        
        # Generate recommendation
        recommendations = analyzer.recommend_accelerators([emerging_need])
        
        if recommendations:
            return {
                "recommendation": recommendations[0],
                "status": "success"
            }
        else:
            return {
                "message": "No recommendation generated",
                "status": "no_recommendation"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_analysis_status():
    """Get current analysis status"""
    if not analysis_results:
        return {
            "status": "not_started",
            "message": "No analysis has been run yet"
        }
    elif "error" in analysis_results:
        return {
            "status": "error",
            "message": analysis_results["error"]
        }
    else:
        return {
            "status": "completed",
            "message": "Analysis completed successfully",
            "timestamp": analysis_results.get("analysis_timestamp", "Unknown"),
            "summary": {
                "emerging_needs": len(analysis_results.get("emerging_needs", [])),
                "recommendations": len(analysis_results.get("recommendations", [])),
                "total_requests": analysis_results.get("insights", {}).get("total_requests", 0)
            }
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
