import React, { useState, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Box,
  Chip,
  LinearProgress,
  Alert,
  Snackbar,
  Tabs,
  Tab,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  IconButton,
  Tooltip,
  Badge,
  CircularProgress,
  Fade,
  Zoom
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  Business as BusinessIcon,
  Assessment as AssessmentIcon,
  Refresh as RefreshIcon,
  PlayArrow as PlayArrowIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Star as StarIcon,
  AttachMoney as AttachMoneyIcon,
  Schedule as ScheduleIcon,
  Group as GroupIcon,
  Build as BuildIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          borderRadius: '12px',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
  },
});

interface AnalysisData {
  patterns: {
    total_requests: number;
    unique_companies: number;
    unique_capabilities: number;
    top_capabilities: Record<string, number>;
    top_companies: Record<string, number>;
    technology_trends: Record<string, number>;
    complexity_distribution: Record<string, number>;
    impact_distribution: Record<string, number>;
  };
  recommendations: {
    total_recommendations: number;
    recommendations: Array<{
      accelerator_name: string;
      capability: string;
      description: string;
      priority_score: number;
      estimated_market_size: number;
      success_probability: number;
      duration_weeks: number;
      complexity: string;
    }>;
  };
  insights: {
    summary: {
      total_requests: number;
      unique_companies: number;
      unique_capabilities: number;
    };
  };
}

const API_BASE = 'http://localhost:3000';

function App() {
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' | 'info' });
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    checkAPIHealth();
  }, []);

  const checkAPIHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE}/health`);
      if (response.data.status === 'healthy') {
        setApiStatus('connected');
      } else {
        setApiStatus('disconnected');
      }
    } catch (error) {
      setApiStatus('disconnected');
    }
  };

  const runAnalysis = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/analyze`);
      if (response.status === 200) {
        setSnackbar({
          open: true,
          message: `Analysis completed! Analyzed ${response.data.summary.requests_analyzed} requests.`,
          severity: 'success'
        });
        loadResults();
      }
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Analysis failed. Please try again.',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const loadResults = async () => {
    try {
      const [patternsResponse, recommendationsResponse, insightsResponse] = await Promise.all([
        axios.get(`${API_BASE}/patterns`),
        axios.get(`${API_BASE}/recommendations`),
        axios.get(`${API_BASE}/insights`)
      ]);

      setAnalysisData({
        patterns: patternsResponse.data,
        recommendations: recommendationsResponse.data,
        insights: insightsResponse.data
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to load results.',
        severity: 'error'
      });
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'success';
      case 'disconnected': return 'error';
      default: return 'info';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected': return <CheckCircleIcon />;
      case 'disconnected': return <ErrorIcon />;
      default: return <InfoIcon />;
    }
  };

  const StatCard = ({ title, value, icon, color = 'primary' }: { title: string; value: string | number; icon: React.ReactElement; color?: 'primary' | 'secondary' }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" color={color}>
              {value}
            </Typography>
          </Box>
          <Box color={`${color}.main`}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  const RecommendationCard = ({ recommendation, index }: { recommendation: any; index: number }) => (
    <Zoom in={true} style={{ transitionDelay: `${index * 100}ms` }}>
      <Card sx={{ mb: 2, borderLeft: 4, borderLeftColor: 'primary.main' }}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={2}>
            <StarIcon color="primary" sx={{ mr: 1 }} />
            <Typography variant="h6" component="div">
              {recommendation.accelerator_name}
            </Typography>
            <Chip 
              label={`#${index + 1}`} 
              color="primary" 
              size="small" 
              sx={{ ml: 'auto' }}
            />
          </Box>
          
          <Typography variant="body2" color="textSecondary" paragraph>
            {recommendation.description}
          </Typography>

          <Grid container spacing={2}>
            <Grid item xs={6} sm={3}>
              <Box textAlign="center">
                <Typography variant="body2" color="textSecondary">
                  Priority Score
                </Typography>
                <Typography variant="h6" color="primary">
                  {recommendation.priority_score.toFixed(2)}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box textAlign="center">
                <Typography variant="body2" color="textSecondary">
                  Market Size
                </Typography>
                <Typography variant="h6" color="success.main">
                  {formatCurrency(recommendation.estimated_market_size)}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box textAlign="center">
                <Typography variant="body2" color="textSecondary">
                  Success Rate
                </Typography>
                <Typography variant="h6" color="info.main">
                  {(recommendation.success_probability * 100).toFixed(1)}%
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Box textAlign="center">
                <Typography variant="body2" color="textSecondary">
                  Duration
                </Typography>
                <Typography variant="h6" color="warning.main">
                  {recommendation.duration_weeks} weeks
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Zoom>
  );

  const TabPanel = ({ children, value, index }: { children: React.ReactNode; value: number; index: number }) => (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static" elevation={0}>
          <Toolbar>
            <DashboardIcon sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              ServiceNow Technical Accelerators Analysis
            </Typography>
            <Chip
              icon={getStatusIcon(apiStatus)}
              label={`API ${apiStatus}`}
              color={getStatusColor(apiStatus) as any}
              variant="outlined"
              sx={{ color: 'white', borderColor: 'white' }}
            />
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h4" component="h1" gutterBottom>
              Analysis Dashboard
            </Typography>
            <Box>
              <Button
                variant="contained"
                startIcon={<PlayArrowIcon />}
                onClick={runAnalysis}
                disabled={loading || apiStatus !== 'connected'}
                sx={{ mr: 1 }}
              >
                {loading ? 'Analyzing...' : 'Run Analysis'}
              </Button>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={loadResults}
                disabled={apiStatus !== 'connected'}
              >
                Load Results
              </Button>
            </Box>
          </Box>

          {loading && <LinearProgress sx={{ mb: 2 }} />}

          {analysisData ? (
            <Box>
              <Paper sx={{ mb: 3 }}>
                <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
                  <Tab icon={<DashboardIcon />} label="Overview" />
                  <Tab icon={<AnalyticsIcon />} label="Patterns" />
                  <Tab icon={<TrendingUpIcon />} label="Recommendations" />
                  <Tab icon={<BusinessIcon />} label="Insights" />
                </Tabs>
              </Paper>

              <TabPanel value={activeTab} index={0}>
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                      title="Total Requests"
                      value={analysisData.patterns.total_requests}
                      icon={<AssessmentIcon />}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                      title="Unique Companies"
                      value={analysisData.patterns.unique_companies}
                      icon={<BusinessIcon />}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                      title="Capabilities"
                      value={analysisData.patterns.unique_capabilities}
                      icon={<BuildIcon />}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                      title="Recommendations"
                      value={analysisData.recommendations.total_recommendations}
                      icon={<StarIcon />}
                      color="secondary"
                    />
                  </Grid>
                </Grid>
              </TabPanel>

              <TabPanel value={activeTab} index={1}>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Top Capabilities
                        </Typography>
                        <List>
                          {Object.entries(analysisData.patterns.top_capabilities).slice(0, 5).map(([capability, count], index) => (
                            <ListItem key={capability}>
                              <ListItemIcon>
                                <Chip label={index + 1} color="primary" size="small" />
                              </ListItemIcon>
                              <ListItemText 
                                primary={capability} 
                                secondary={`${count} requests`}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Technology Trends
                        </Typography>
                        <List>
                          {Object.entries(analysisData.patterns.technology_trends).slice(0, 5).map(([tech, count], index) => (
                            <ListItem key={tech}>
                              <ListItemIcon>
                                <Chip label={index + 1} color="secondary" size="small" />
                              </ListItemIcon>
                              <ListItemText 
                                primary={tech} 
                                secondary={`${count} mentions`}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </TabPanel>

              <TabPanel value={activeTab} index={2}>
                <Typography variant="h5" gutterBottom>
                  Accelerator Recommendations
                </Typography>
                {analysisData.recommendations.recommendations.slice(0, 5).map((recommendation, index) => (
                  <RecommendationCard 
                    key={recommendation.accelerator_name}
                    recommendation={recommendation}
                    index={index}
                  />
                ))}
              </TabPanel>

              <TabPanel value={activeTab} index={3}>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Complexity Distribution
                        </Typography>
                        <Box height={300}>
                          <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                              <Pie
                                data={Object.entries(analysisData.patterns.complexity_distribution).map(([key, value]) => ({ name: key, value }))}
                                cx="50%"
                                cy="50%"
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="value"
                                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                              >
                                {Object.entries(analysisData.patterns.complexity_distribution).map((_, index) => (
                                  <Cell key={`cell-${index}`} fill={['#8884d8', '#82ca9d', '#ffc658'][index % 3]} />
                                ))}
                              </Pie>
                              <RechartsTooltip />
                            </PieChart>
                          </ResponsiveContainer>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Business Impact Distribution
                        </Typography>
                        <Box height={300}>
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={Object.entries(analysisData.patterns.impact_distribution).map(([name, value]) => ({ name, value }))}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="name" />
                              <YAxis />
                              <RechartsTooltip />
                              <Bar dataKey="value" fill="#8884d8" />
                            </BarChart>
                          </ResponsiveContainer>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </TabPanel>
            </Box>
          ) : (
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 8 }}>
                <DashboardIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="textSecondary" gutterBottom>
                  No Analysis Data Available
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Run an analysis to see insights and recommendations
                </Typography>
              </CardContent>
            </Card>
          )}
        </Container>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </ThemeProvider>
  );
}

export default App;