/**
 * Express server for ServiceNow Technical Accelerators Analysis API
 */

const express = require('express');
const cors = require('cors');
const ServiceNowAnalyzer = require('./analyzer');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Global analyzer instance
let analyzer = new ServiceNowAnalyzer();
let analysisResults = {};

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        service: 'ServiceNow Technical Accelerators Analysis API'
    });
});

/**
 * Root endpoint with API information
 */
app.get('/', (req, res) => {
    res.json({
        message: 'ServiceNow Technical Accelerators Analysis API',
        version: '1.0.0',
        endpoints: {
            analyze: '/analyze - Run complete analysis',
            patterns: '/patterns - Get request patterns',
            recommendations: '/recommendations - Get accelerator recommendations',
            insights: '/insights - Get analysis insights',
            emerging_needs: '/emerging-needs - Get identified emerging needs',
            health: '/health - Health check'
        }
    });
});

/**
 * Run complete analysis
 */
app.post('/analyze', async (req, res) => {
    try {
        console.log('🔍 Starting analysis...');
        const results = await analyzer.runCompleteAnalysis();
        
        if (results.error) {
            return res.status(500).json({
                error: results.error,
                message: 'Analysis failed'
            });
        }
        
        analysisResults = results;
        
        res.json({
            message: 'Analysis completed successfully',
            status: 'completed',
            timestamp: new Date().toISOString(),
            summary: {
                requests_analyzed: results.data_summary.requests_analyzed,
                emerging_needs: results.data_summary.emerging_needs_identified,
                recommendations: results.data_summary.recommendations_generated
            }
        });
        
    } catch (error) {
        console.error('Analysis error:', error);
        res.status(500).json({
            error: error.message,
            message: 'Analysis failed'
        });
    }
});

/**
 * Get analysis status
 */
app.get('/status', (req, res) => {
    if (!analysisResults || Object.keys(analysisResults).length === 0) {
        return res.json({
            status: 'not_started',
            message: 'No analysis has been run yet'
        });
    }
    
    if (analysisResults.error) {
        return res.json({
            status: 'error',
            message: analysisResults.error
        });
    }
    
    res.json({
        status: 'completed',
        message: 'Analysis completed successfully',
        timestamp: analysisResults.analysis_timestamp,
        summary: {
            emerging_needs: analysisResults.data_summary.emerging_needs_identified,
            recommendations: analysisResults.data_summary.recommendations_generated,
            total_requests: analysisResults.data_summary.requests_analyzed
        }
    });
});

/**
 * Get request patterns
 */
app.get('/patterns', (req, res) => {
    if (!analysisResults.patterns) {
        return res.status(404).json({
            error: 'Analysis not completed yet',
            message: 'Please run analysis first'
        });
    }
    
    const patterns = analysisResults.patterns;
    
    res.json({
        industry_patterns: patterns.industry_distribution,
        company_patterns: patterns.top_companies,
        capability_patterns: patterns.top_capabilities,
        technology_trends: patterns.technology_trends,
        complexity_distribution: patterns.complexity_distribution,
        impact_distribution: patterns.impact_distribution,
        category_distribution: patterns.category_distribution,
        summary: {
            total_requests: patterns.total_requests,
            unique_companies: patterns.unique_companies,
            unique_capabilities: patterns.unique_capabilities
        }
    });
});

/**
 * Get accelerator recommendations
 */
app.get('/recommendations', (req, res) => {
    if (!analysisResults.recommendations) {
        return res.status(404).json({
            error: 'Analysis not completed yet',
            message: 'Please run analysis first'
        });
    }
    
    const recommendations = analysisResults.recommendations;
    
    res.json({
        total_recommendations: recommendations.length,
        recommendations: recommendations,
        top_3: recommendations.slice(0, 3)
    });
});

/**
 * Get emerging needs
 */
app.get('/emerging-needs', (req, res) => {
    if (!analysisResults.emerging_needs) {
        return res.status(404).json({
            error: 'Analysis not completed yet',
            message: 'Please run analysis first'
        });
    }
    
    const emergingNeeds = analysisResults.emerging_needs;
    
    res.json({
        total_emerging_needs: emergingNeeds.length,
        emerging_needs: emergingNeeds,
        priority_sorted: emergingNeeds.sort((a, b) => b.priority_score - a.priority_score)
    });
});

/**
 * Get analysis insights
 */
app.get('/insights', (req, res) => {
    if (!analysisResults.insights) {
        return res.status(404).json({
            error: 'Analysis not completed yet',
            message: 'Please run analysis first'
        });
    }
    
    res.json(analysisResults.insights);
});

/**
 * Generate specific accelerator recommendation
 */
app.post('/recommend-accelerator', (req, res) => {
    try {
        const { capability, priority_score, request_count, technologies, industries } = req.body;
        
        if (!capability || !priority_score || !request_count) {
            return res.status(400).json({
                error: 'Missing required fields',
                message: 'capability, priority_score, and request_count are required'
            });
        }
        
        // Create a mock emerging need
        const emergingNeed = {
            capability: capability,
            request_count: request_count,
            priority_score: priority_score,
            technologies: technologies || {},
            industries: industries || {},
            companies: 1
        };
        
        // Generate recommendation
        const recommendations = analyzer.generateRecommendations([emergingNeed]);
        
        if (recommendations.length > 0) {
            res.json({
                recommendation: recommendations[0],
                status: 'success'
            });
        } else {
            res.json({
                message: 'No recommendation generated',
                status: 'no_recommendation'
            });
        }
        
    } catch (error) {
        console.error('Recommendation error:', error);
        res.status(500).json({
            error: error.message,
            message: 'Failed to generate recommendation'
        });
    }
});

/**
 * Error handling middleware
 */
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).json({
        error: 'Internal server error',
        message: err.message
    });
});

/**
 * 404 handler
 */
app.use((req, res) => {
    res.status(404).json({
        error: 'Endpoint not found',
        message: 'The requested endpoint does not exist'
    });
});

/**
 * Start server
 */
app.listen(PORT, () => {
    console.log(`🚀 ServiceNow Technical Accelerators Analysis API`);
    console.log(`📡 Server running on port ${PORT}`);
    console.log(`🌐 Health check: http://localhost:${PORT}/health`);
    console.log(`📊 API docs: http://localhost:${PORT}/`);
});

module.exports = app;
