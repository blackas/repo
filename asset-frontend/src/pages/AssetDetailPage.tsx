import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  Box,
  CircularProgress,
  Alert,
  Button,
  Stack,
} from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { AssetType, AssetDetail } from '../types';
import { apiService } from '../services/api';

function AssetDetailPage() {
  const { assetType, assetId } = useParams<{ assetType: AssetType; assetId: string }>();
  const navigate = useNavigate();
  const [asset, setAsset] = useState<AssetDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAssetDetail = async () => {
      if (!assetType || !assetId) return;

      setLoading(true);
      setError(null);
      try {
        const data = await apiService.getAssetDetail(assetType as AssetType, assetId);
        setAsset(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch asset details');
      } finally {
        setLoading(false);
      }
    };

    fetchAssetDetail();
  }, [assetType, assetId]);

  const handleBack = () => {
    navigate(-1);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error || !asset) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error || 'Asset not found'}</Alert>
        <Button onClick={handleBack} sx={{ mt: 2 }}>
          Go Back
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Button startIcon={<ArrowBack />} onClick={handleBack} sx={{ mb: 2 }}>
        Back
      </Button>

      <Typography variant="h4" gutterBottom>
        {asset.name}
      </Typography>
      {asset.symbol && (
        <Typography variant="h6" color="text.secondary" gutterBottom>
          {asset.symbol}
        </Typography>
      )}

      <Stack spacing={3} sx={{ mt: 2 }}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={3}>
          <Paper sx={{ p: 3, flex: 1 }}>
            <Typography variant="h6" gutterBottom>
              Current Information
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body1">
                <strong>Price:</strong> {asset.currentPrice ? `$${asset.currentPrice.toFixed(2)}` : 'N/A'}
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  color: asset.change && asset.change > 0 ? 'success.main' : 'error.main',
                }}
              >
                <strong>Change:</strong> {asset.change ? asset.change.toFixed(2) : 'N/A'} (
                {asset.changePercent ? `${asset.changePercent.toFixed(2)}%` : 'N/A'})
              </Typography>
              <Typography variant="body1">
                <strong>Volume:</strong> {asset.volume ? asset.volume.toLocaleString() : 'N/A'}
              </Typography>
              <Typography variant="body1">
                <strong>Market Cap:</strong> {asset.marketCap ? `$${asset.marketCap.toLocaleString()}` : 'N/A'}
              </Typography>
            </Box>
          </Paper>

          <Paper sx={{ p: 3, flex: 1 }}>
            <Typography variant="h6" gutterBottom>
              Additional Information
            </Typography>
            <Box sx={{ mt: 2 }}>
              {asset.sector && (
                <Typography variant="body1">
                  <strong>Sector:</strong> {asset.sector}
                </Typography>
              )}
              {asset.industry && (
                <Typography variant="body1">
                  <strong>Industry:</strong> {asset.industry}
                </Typography>
              )}
              {asset.description && (
                <Typography variant="body1" sx={{ mt: 2 }}>
                  {asset.description}
                </Typography>
              )}
            </Box>
          </Paper>
        </Stack>

        {asset.historicalData && asset.historicalData.length > 0 && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Price History
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={asset.historicalData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="close" stroke="#8884d8" name="Close Price" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        )}
      </Stack>
    </Container>
  );
}

export default AssetDetailPage;
