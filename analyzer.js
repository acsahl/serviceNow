/**
 * ServiceNow Technical Accelerators Request Analysis Agent
 * JavaScript-based CSV analysis for identifying emerging needs and accelerator recommendations
 */

const fs = require('fs');
const csv = require('csv-parser');
const path = require('path');

class ServiceNowAnalyzer {
    constructor() {
        this.requests = [];
        this.accelerators = [];
        this.results = {};
    }

    /**
     * Load CSV data from files
     */
    async loadData() {
        console.log('📊 Loading ServiceNow data...');
        
        try {
            // Load requests data
            await this.loadCSV('csv/u_hack.csv', this.requests);
            console.log(`✅ Loaded ${this.requests.length} requests`);
            
            // Load accelerators data
            await this.loadCSV('csv/accelerators.csv', this.accelerators);
            console.log(`✅ Loaded ${this.accelerators.length} accelerators`);
            
            return true;
        } catch (error) {
            console.error('❌ Error loading data:', error.message);
            return false;
        }
    }

    /**
     * Load CSV file into array
     */
    loadCSV(filePath, targetArray) {
        return new Promise((resolve, reject) => {
            if (!fs.existsSync(filePath)) {
                reject(new Error(`File not found: ${filePath}`));
                return;
            }

            fs.createReadStream(filePath)
                .pipe(csv())
                .on('data', (row) => targetArray.push(row))
                .on('end', () => resolve())
                .on('error', (error) => reject(error));
        });
    }

    /**
     * Extract technologies from request description
     */
    extractTechnologies(description) {
        if (!description) return [];
        
        const techKeywords = [
            'ServiceNow', 'ITSM', 'ITOM', 'ITAM', 'CSM', 'HR', 'SPM', 'FSM',
            'AI', 'Machine Learning', 'Analytics', 'Reporting', 'Dashboard',
            'Workflow', 'Automation', 'Integration', 'API', 'Mobile',
            'Security', 'Compliance', 'RBAC', 'SSO', 'MFA',
            'Cloud', 'AWS', 'Azure', 'GCP', 'SaaS', 'PaaS',
            'Database', 'CMDB', 'Discovery', 'Event Management',
            'Virtual Agent', 'Chatbot', 'Knowledge Management',
            'Service Catalog', 'Incident Management', 'Change Management'
        ];
        
        const foundTechs = [];
        const descriptionLower = description.toLowerCase();
        
        techKeywords.forEach(tech => {
            if (descriptionLower.includes(tech.toLowerCase())) {
                foundTechs.push(tech);
            }
        });
        
        return foundTechs;
    }

    /**
     * Categorize request complexity
     */
    categorizeComplexity(description) {
        if (!description) return 'Medium';
        
        const descriptionLower = description.toLowerCase();
        
        const highComplexityKeywords = [
            'enterprise', 'comprehensive', 'integration', 'migration', 
            'automation', 'workflow', 'security', 'compliance'
        ];
        
        const lowComplexityKeywords = [
            'simple', 'basic', 'quick', 'easy', 'guidance', 'overview'
        ];
        
        const highCount = highComplexityKeywords.filter(keyword => 
            descriptionLower.includes(keyword)).length;
        const lowCount = lowComplexityKeywords.filter(keyword => 
            descriptionLower.includes(keyword)).length;
        
        if (highCount >= 2) return 'High';
        if (lowCount >= 2) return 'Low';
        return 'Medium';
    }

    /**
     * Extract business impact from description
     */
    extractBusinessImpact(description) {
        if (!description) return 'Medium';
        
        const descriptionLower = description.toLowerCase();
        
        const highImpactKeywords = [
            'critical', 'security', 'compliance', 'enterprise', 'strategic',
            'business continuity', 'risk', 'audit', 'governance'
        ];
        
        const lowImpactKeywords = [
            'convenience', 'nice to have', 'improvement', 'enhancement'
        ];
        
        const highCount = highImpactKeywords.filter(keyword => 
            descriptionLower.includes(keyword)).length;
        const lowCount = lowImpactKeywords.filter(keyword => 
            descriptionLower.includes(keyword)).length;
        
        if (highCount >= 2) return 'High';
        if (lowCount >= 1) return 'Low';
        return 'Medium';
    }

    /**
     * Standardize company names
     */
    standardizeCompanyName(companyName) {
        return companyName.replace(/(Group|Services|Solutions|Corp|Inc\.?|Ltd\.?)$/, '').trim();
    }

    /**
     * Infer industry from company name
     */
    inferIndustry(companyName) {
        const nameLower = companyName.toLowerCase();
        
        if (nameLower.includes('financial') || nameLower.includes('bank') || nameLower.includes('credit')) {
            return 'Financial Services';
        }
        if (nameLower.includes('tech') || nameLower.includes('software') || nameLower.includes('digital')) {
            return 'Technology';
        }
        if (nameLower.includes('health') || nameLower.includes('medical') || nameLower.includes('care')) {
            return 'Healthcare';
        }
        if (nameLower.includes('manufacturing') || nameLower.includes('industrial')) {
            return 'Manufacturing';
        }
        
        return 'Other';
    }

    /**
     * Analyze request patterns
     */
    analyzeRequestPatterns() {
        console.log('🔍 Analyzing request patterns...');
        
        // Add processed fields to requests
        this.requests.forEach(request => {
            request.technologies = this.extractTechnologies(request.description);
            request.complexity = this.categorizeComplexity(request.description);
            request.business_impact = this.extractBusinessImpact(request.description);
            request.company_standardized = this.standardizeCompanyName(request.company);
            request.industry = this.inferIndustry(request.company_standardized);
        });

        // Capability analysis
        const capabilityCounts = {};
        this.requests.forEach(req => {
            capabilityCounts[req.capability] = (capabilityCounts[req.capability] || 0) + 1;
        });

        // Company analysis
        const companyCounts = {};
        this.requests.forEach(req => {
            const company = req.company_standardized;
            companyCounts[company] = (companyCounts[company] || 0) + 1;
        });

        // Technology analysis
        const allTechnologies = [];
        this.requests.forEach(req => {
            allTechnologies.push(...req.technologies);
        });
        const techCounts = {};
        allTechnologies.forEach(tech => {
            techCounts[tech] = (techCounts[tech] || 0) + 1;
        });

        // Complexity analysis
        const complexityCounts = {};
        this.requests.forEach(req => {
            complexityCounts[req.complexity] = (complexityCounts[req.complexity] || 0) + 1;
        });

        // Business impact analysis
        const impactCounts = {};
        this.requests.forEach(req => {
            impactCounts[req.business_impact] = (impactCounts[req.business_impact] || 0) + 1;
        });

        // Industry analysis
        const industryCounts = {};
        this.requests.forEach(req => {
            industryCounts[req.industry] = (industryCounts[req.industry] || 0) + 1;
        });

        // Category analysis
        const categoryCounts = {};
        this.requests.forEach(req => {
            categoryCounts[req.primary_category] = (categoryCounts[req.primary_category] || 0) + 1;
        });

        const sortedCapabilities = this.sortByValue(capabilityCounts);
        const sortedCompanies = this.sortByValue(companyCounts);
        const sortedTechs = this.sortByValue(techCounts);
        
        return {
            top_capabilities: Object.fromEntries(Object.entries(sortedCapabilities).slice(0, 10)),
            top_companies: Object.fromEntries(Object.entries(sortedCompanies).slice(0, 10)),
            technology_trends: Object.fromEntries(Object.entries(sortedTechs).slice(0, 15)),
            complexity_distribution: complexityCounts,
            impact_distribution: impactCounts,
            industry_distribution: industryCounts,
            category_distribution: categoryCounts,
            total_requests: this.requests.length,
            unique_companies: Object.keys(companyCounts).length,
            unique_capabilities: Object.keys(capabilityCounts).length
        };
    }

    /**
     * Sort object by values (descending)
     */
    sortByValue(obj) {
        return Object.entries(obj)
            .sort(([,a], [,b]) => b - a)
            .reduce((acc, [key, value]) => {
                acc[key] = value;
                return acc;
            }, {});
    }

    /**
     * Identify emerging needs and gaps
     */
    identifyEmergingNeeds() {
        console.log('🌟 Identifying emerging needs...');
        
        // Get current accelerator categories
        const acceleratorCategories = new Set();
        this.accelerators.forEach(acc => {
            const desc = acc.description.toLowerCase();
            if (desc.includes('ai')) acceleratorCategories.add('AI/ML Implementation');
            if (desc.includes('security')) acceleratorCategories.add('Security Enhancement');
            if (desc.includes('analytics')) acceleratorCategories.add('Data Analytics');
            if (desc.includes('workflow')) acceleratorCategories.add('Process Automation');
            if (desc.includes('integration')) acceleratorCategories.add('Integration');
            if (desc.includes('mobile')) acceleratorCategories.add('Mobile Development');
        });

        // Analyze request capabilities not covered by current accelerators
        const capabilityCounts = {};
        this.requests.forEach(req => {
            capabilityCounts[req.capability] = (capabilityCounts[req.capability] || 0) + 1;
        });

        const gaps = [];
        Object.entries(capabilityCounts).forEach(([capability, count]) => {
            if (count >= 3) { // Only consider if significant demand
                // Check if this capability is covered by current accelerators
                const capabilityLower = capability.toLowerCase();
                let covered = false;
                
                for (const accCategory of acceleratorCategories) {
                    if (accCategory.toLowerCase().includes(capabilityLower) || 
                        capabilityLower.includes(accCategory.toLowerCase())) {
                        covered = true;
                        break;
                    }
                }
                
                if (!covered) {
                    const capabilityRequests = this.requests.filter(req => req.capability === capability);
                    
                    // Get technology distribution for this capability
                    const techCounts = {};
                    capabilityRequests.forEach(req => {
                        req.technologies.forEach(tech => {
                            techCounts[tech] = (techCounts[tech] || 0) + 1;
                        });
                    });

                    // Get industry distribution
                    const industryCounts = {};
                    capabilityRequests.forEach(req => {
                        industryCounts[req.industry] = (industryCounts[req.industry] || 0) + 1;
                    });

                    // Get complexity distribution
                    const complexityCounts = {};
                    capabilityRequests.forEach(req => {
                        complexityCounts[req.complexity] = (complexityCounts[req.complexity] || 0) + 1;
                    });

                    // Get impact distribution
                    const impactCounts = {};
                    capabilityRequests.forEach(req => {
                        impactCounts[req.business_impact] = (impactCounts[req.business_impact] || 0) + 1;
                    });

                    const gap = {
                        capability: capability,
                        request_count: count,
                        companies: new Set(capabilityRequests.map(req => req.company_standardized)).size,
                        industries: industryCounts,
                        technologies: this.sortByValue(techCounts),
                        complexity_distribution: complexityCounts,
                        impact_distribution: impactCounts,
                        priority_score: this.calculatePriorityScore(capabilityRequests)
                    };
                    
                    gaps.push(gap);
                }
            }
        });

        // Sort by priority score
        gaps.sort((a, b) => b.priority_score - a.priority_score);
        
        return gaps;
    }

    /**
     * Calculate priority score for a capability
     */
    calculatePriorityScore(capabilityRequests) {
        const requestCountScore = Math.min(capabilityRequests.length / 10, 1.0);
        const companyDiversityScore = Math.min(
            new Set(capabilityRequests.map(req => req.company_standardized)).size / 5, 1.0
        );
        
        const complexityScores = { 'Low': 0.3, 'Medium': 0.6, 'High': 1.0 };
        const avgComplexity = capabilityRequests.reduce((sum, req) => 
            sum + complexityScores[req.complexity], 0) / capabilityRequests.length;
        
        const impactScores = { 'Low': 0.3, 'Medium': 0.6, 'High': 1.0 };
        const avgImpact = capabilityRequests.reduce((sum, req) => 
            sum + impactScores[req.business_impact], 0) / capabilityRequests.length;
        
        return (requestCountScore * 0.3 + companyDiversityScore * 0.2 + 
                avgComplexity * 0.3 + avgImpact * 0.2);
    }

    /**
     * Generate accelerator recommendations
     */
    generateRecommendations(emergingNeeds) {
        console.log('💡 Generating accelerator recommendations...');
        
        const recommendations = [];
        
        emergingNeeds.forEach(need => {
            // Determine complexity based on request complexity distribution
            const complexityDist = need.complexity_distribution;
            let acceleratorComplexity, durationWeeks;
            
            if ((complexityDist.High || 0) > (complexityDist.Low || 0)) {
                acceleratorComplexity = 'Complex';
                durationWeeks = 8;
            } else if ((complexityDist.Low || 0) > (complexityDist.High || 0)) {
                acceleratorComplexity = 'Simple';
                durationWeeks = 4;
            } else {
                acceleratorComplexity = 'Medium';
                durationWeeks = 6;
            }
            
            const marketSize = need.request_count * 50000; // $50K per request estimate
            const successProbability = Math.min(0.95, 0.7 + need.priority_score * 0.25);
            
            const recommendation = {
                accelerator_name: `${need.capability} Accelerator`,
                capability: need.capability,
                description: `Comprehensive solution for ${need.capability.toLowerCase()} challenges, addressing the needs of ${need.companies} companies across multiple industries.`,
                complexity: acceleratorComplexity,
                duration_weeks: durationWeeks,
                estimated_market_size: marketSize,
                success_probability: successProbability,
                priority_score: need.priority_score,
                request_count: need.request_count,
                target_companies: need.companies,
                target_industries: Object.keys(need.industries).slice(0, 3),
                key_technologies: Object.keys(need.technologies).slice(0, 5),
                business_justification: this.generateBusinessJustification(need)
            };
            
            recommendations.push(recommendation);
        });
        
        return recommendations;
    }

    /**
     * Generate business justification
     */
    generateBusinessJustification(need) {
        const industries = Object.keys(need.industries).slice(0, 2).join(', ');
        const techs = Object.keys(need.technologies).slice(0, 3).join(', ');
        
        return `High demand for ${need.capability} solutions with ${need.request_count} requests from ${need.companies} companies. Strong presence in ${industries} industries with technologies including ${techs}. Priority score of ${need.priority_score.toFixed(2)} indicates significant business opportunity.`;
    }

    /**
     * Generate comprehensive insights
     */
    generateInsights(patterns) {
        console.log('📈 Generating insights...');
        
        return {
            summary: {
                total_requests: patterns.total_requests,
                unique_companies: patterns.unique_companies,
                unique_capabilities: patterns.unique_capabilities,
                analysis_timestamp: new Date().toISOString()
            },
            distributions: {
                industry: patterns.industry_distribution,
                complexity: patterns.complexity_distribution,
                impact: patterns.impact_distribution,
                category: patterns.category_distribution
            },
            trends: {
                technology: patterns.technology_trends,
                capabilities: patterns.top_capabilities,
                companies: patterns.top_companies
            }
        };
    }

    /**
     * Run complete analysis
     */
    async runCompleteAnalysis() {
        console.log('🚀 Starting ServiceNow Technical Accelerators Analysis');
        console.log('='.repeat(60));
        
        try {
            // Load data
            const dataLoaded = await this.loadData();
            if (!dataLoaded) {
                return { error: 'Failed to load data' };
            }
            
            // Analyze patterns
            const patterns = this.analyzeRequestPatterns();
            
            // Identify emerging needs
            const emergingNeeds = this.identifyEmergingNeeds();
            
            // Generate recommendations
            const recommendations = this.generateRecommendations(emergingNeeds);
            
            // Generate insights
            const insights = this.generateInsights(patterns);
            
            // Compile results
            this.results = {
                patterns: patterns,
                emerging_needs: emergingNeeds,
                recommendations: recommendations,
                insights: insights,
                analysis_timestamp: new Date().toISOString(),
                data_summary: {
                    requests_analyzed: this.requests.length,
                    accelerators_in_catalog: this.accelerators.length,
                    emerging_needs_identified: emergingNeeds.length,
                    recommendations_generated: recommendations.length
                }
            };
            
            console.log('✅ Analysis complete!');
            return this.results;
            
        } catch (error) {
            console.error('❌ Analysis failed:', error.message);
            return { error: error.message };
        }
    }

    /**
     * Save results to JSON file
     */
    saveResults(filename = 'servicenow_analysis_results.json') {
        if (this.results && !this.results.error) {
            fs.writeFileSync(filename, JSON.stringify(this.results, null, 2));
            console.log(`📊 Results saved to ${filename}`);
        }
    }

    /**
     * Print analysis summary
     */
    printSummary() {
        if (!this.results || this.results.error) {
            console.log('❌ No results to display');
            return;
        }
        
        console.log('\n' + '='.repeat(60));
        console.log('🎯 SERVICENOW TECHNICAL ACCELERATORS ANALYSIS SUMMARY');
        console.log('='.repeat(60));
        
        console.log(`📊 Data Analyzed:`);
        console.log(`   • ${this.results.data_summary.requests_analyzed} Access to Experts requests`);
        console.log(`   • ${this.results.data_summary.accelerators_in_catalog} current accelerators`);
        
        console.log(`\n🔍 Analysis Results:`);
        console.log(`   • ${this.results.data_summary.emerging_needs_identified} emerging needs identified`);
        console.log(`   • ${this.results.data_summary.recommendations_generated} accelerator recommendations`);
        
        console.log(`\n🏆 Top 3 Recommendations:`);
        this.results.recommendations.slice(0, 3).forEach((rec, i) => {
            console.log(`   ${i + 1}. ${rec.accelerator_name}`);
            console.log(`      Priority Score: ${rec.priority_score.toFixed(2)}`);
            console.log(`      Market Size: $${rec.estimated_market_size.toLocaleString()}`);
            console.log(`      Success Probability: ${(rec.success_probability * 100).toFixed(1)}%`);
            console.log();
        });
        
        console.log(`\n📈 Key Insights:`);
        const patterns = this.results.patterns;
        const topCapability = Object.keys(patterns.top_capabilities)[0];
        const topCompany = Object.keys(patterns.top_companies)[0];
        const topTech = Object.keys(patterns.technology_trends)[0];
        
        console.log(`   • Most requested capability: ${topCapability}`);
        console.log(`   • Most active company: ${topCompany}`);
        console.log(`   • Top technology trend: ${topTech}`);
    }
}

// Main execution
async function main() {
    const analyzer = new ServiceNowAnalyzer();
    
    try {
        const results = await analyzer.runCompleteAnalysis();
        
        if (!results.error) {
            analyzer.saveResults();
            analyzer.printSummary();
        } else {
            console.error(`❌ Analysis failed: ${results.error}`);
        }
    } catch (error) {
        console.error(`❌ Unexpected error: ${error.message}`);
    }
}

// Run if called directly
if (require.main === module) {
    main();
}

module.exports = ServiceNowAnalyzer;
