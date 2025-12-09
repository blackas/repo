import { useEffect, useState } from 'react';
import { Container, Grid, Paper, Typography, Box, Icon } from '@mui/material';
import { ShowChart, AccountBalanceWallet, BarChart, PieChart } from '@mui/icons-material';
import { apiService } from '../services/api';

interface InfoCardProps {
  title: string;
  value: string | number;
  icon: React.ReactElement;
  color: string;
}

function InfoCard({ title, value, icon, color }: InfoCardProps) {
  return (
    <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', height: '100%' }}>
      <Icon sx={{ fontSize: 40, color, mr: 2 }}>{icon}</Icon>
      <Box>
        <Typography color="text.secondary">{title}</Typography>
        <Typography variant="h5" component="p">
          {value}
        </Typography>
      </Box>
    </Paper>
  );
}

interface DashboardSummary {
  totalValue: number;
  totalAssets: number;
  stockValue: number;
  cryptoValue: number;
}

function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      setLoading(true);
      try {
        // Mock data for now, since the API endpoint doesn't exist
        const data: DashboardSummary = {
          totalValue: 125300.50,
          totalAssets: 15,
          stockValue: 85200.00,
          cryptoValue: 40100.50,
        };
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
        Dashboard
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Info Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <InfoCard
            title="Total Value"
            value={`$${summary?.totalValue?.toLocaleString() || 0}`}
            icon={<AccountBalanceWallet />}
            color="primary.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <InfoCard
            title="Total Assets"
            value={summary?.totalAssets || 0}
            icon={<ShowChart />}
            color="secondary.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <InfoCard
            title="Stock Value"
            value={`$${summary?.stockValue?.toLocaleString() || 0}`}
            icon={<BarChart />}
            color="success.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <InfoCard
            title="Crypto Value"
            value={`$${summary?.cryptoValue?.toLocaleString() || 0}`}
            icon={<PieChart />}
            color="warning.main"
          />
        </Grid>

        {/* Asset Allocation Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 300, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              Asset Allocation
            </Typography>
            <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Typography color="text.secondary">[Chart Placeholder]</Typography>
            </Box>
          </Paper>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 300, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Typography color="text.secondary">[Activity Feed Placeholder]</Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard;
