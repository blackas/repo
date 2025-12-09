import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  Box,
  Pagination,
} from '@mui/material';
import type { AssetType } from '../types';
import useAssetStore from '../store/assetStore';
import { apiService } from '../services/api';

interface AssetListPageProps {
  assetType: AssetType;
  title: string;
  market?: 'KRX' | 'NASDAQ';
}

function AssetListPage({ assetType, title, market }: AssetListPageProps) {
  const navigate = useNavigate();
  const {
    [assetType]: assetState,
    setAssets,
    setLoading,
    setError,
  } = useAssetStore();

  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    const fetchAssets = async () => {
      setLoading(assetType, true);
      try {
        const params = market ? { market, page } : { page };
        const response = await apiService.getAssets(assetType, params);
        setAssets(assetType, response.items);
        setTotalPages(response.total_pages);
      } catch (error) {
        setError(assetType, error instanceof Error ? error.message : 'Failed to fetch assets');
      }
    };

    fetchAssets();
  }, [assetType, market, page, setAssets, setLoading, setError]);

  const handleRowClick = (assetId: string | number) => {
    navigate(`/assets/${assetType}/${assetId}`);
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value);
  };

  if (assetState.isLoading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (assetState.error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{assetState.error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        {title}
      </Typography>

      {assetState.items.length === 0 ? (
        <Box sx={{ mt: 4 }}>
          <Alert severity="info">No assets found</Alert>
        </Box>
      ) : (
        <>
          <TableContainer component={Paper} sx={{ mt: 3 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Symbol</TableCell>
                  <TableCell align="right">Price</TableCell>
                  <TableCell align="right">Change</TableCell>
                  <TableCell align="right">Change %</TableCell>
                  <TableCell align="right">Volume</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {assetState.items.map((asset) => (
                  <TableRow
                    key={asset.id}
                    hover
                    onClick={() => handleRowClick(asset.id)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell>{asset.name}</TableCell>
                    <TableCell>{asset.symbol || '-'}</TableCell>
                    <TableCell align="right">
                      {asset.currentPrice ? `$${asset.currentPrice.toFixed(2)}` : '-'}
                    </TableCell>
                    <TableCell
                      align="right"
                      sx={{
                        color: asset.change && asset.change > 0 ? 'success.main' : 'error.main',
                      }}
                    >
                      {asset.change ? asset.change.toFixed(2) : '-'}
                    </TableCell>
                    <TableCell
                      align="right"
                      sx={{
                        color: asset.changePercent && asset.changePercent > 0 ? 'success.main' : 'error.main',
                      }}
                    >
                      {asset.changePercent ? `${asset.changePercent.toFixed(2)}%` : '-'}
                    </TableCell>
                    <TableCell align="right">
                      {asset.volume ? asset.volume.toLocaleString() : '-'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
            <Pagination count={totalPages} page={page} onChange={handlePageChange} />
          </Box>
        </>
      )}
    </Container>
  );
}

export default AssetListPage;
