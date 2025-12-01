import { useEffect, useState } from 'react';
import { Container, Paper, Typography, Box, Stack } from '@mui/material';
import { apiService } from '../services/api';

interface DashboardSummary {
  totalAssets?: number;
  totalValue?: number;
  marketStats?: Record<string, any>;
}

function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const data = await apiService.getDashboardSummary();
        setSummary(data);
      } catch (error) {
        console.error('Failed to fetch dashboard summary:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, []);

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography>Loading...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Asset Portfolio Dashboard
      </Typography>

      <Stack spacing={3} sx={{ mt: 2 }}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={3}>
          <Paper sx={{ p: 2, flex: 1 }}>
            <Typography variant="h6" color="text.secondary">
              Total Assets
            </Typography>
            <Typography variant="h4">
              {summary.totalAssets || 0}
            </Typography>
          </Paper>

          <Paper sx={{ p: 2, flex: 1 }}>
            <Typography variant="h6" color="text.secondary">
              Total Value
            </Typography>
            <Typography variant="h4">
              ${summary.totalValue?.toLocaleString() || 0}
            </Typography>
          </Paper>

          <Paper sx={{ p: 2, flex: 1 }}>
            <Typography variant="h6" color="text.secondary">
              Markets
            </Typography>
            <Typography variant="h4">
              3
            </Typography>
            <Typography variant="body2" color="text.secondary">
              KR, US, Crypto
            </Typography>
          </Paper>
        </Stack>

        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Market Overview
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body1">
              Welcome to Asset Folio - your comprehensive portfolio tracking platform
            </Typography>
          </Box>
        </Paper>
      </Stack>
    </Container>
  );
}

export default Dashboard;
