import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  Button,
  List,
  ListItem,
  ListItemText,
  IconButton,
  TextField,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  CircularProgress,
  Grid,
} from '@mui/material';
import { Edit, Delete, Add } from '@mui/icons-material';
import { useWatchlistStore } from '../store/watchlistStore';
import type { Watchlist, WatchlistAsset } from '../services/watchlistService';

const WatchlistPage: React.FC = () => {
  const {
    watchlists,
    selectedWatchlist,
    watchlistAssets,
    isLoading,
    fetchWatchlists,
    createWatchlist,
    updateWatchlist,
    deleteWatchlist,
    selectWatchlist,
  } = useWatchlistStore();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [newWatchlistName, setNewWatchlistName] = useState('');
  const [editingWatchlist, setEditingWatchlist] = useState<Watchlist | null>(null);

  useEffect(() => {
    fetchWatchlists();
  }, [fetchWatchlists]);

  const handleOpenDialog = (watchlist: Watchlist | null = null) => {
    setEditingWatchlist(watchlist);
    setNewWatchlistName(watchlist ? watchlist.name : '');
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingWatchlist(null);
    setNewWatchlistName('');
  };

  const handleSaveWatchlist = async () => {
    if (newWatchlistName.trim()) {
      if (editingWatchlist) {
        await updateWatchlist(editingWatchlist.id, newWatchlistName);
      } else {
        await createWatchlist(newWatchlistName);
      }
      handleCloseDialog();
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this watchlist?')) {
      await deleteWatchlist(id);
    }
  };

  return (
    <Container maxWidth="xl">
      <Paper sx={{ p: 3, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          My Watchlists
        </Typography>
        <Grid container spacing={3}>
          {/* Watchlist List */}
          <Grid item xs={12} md={4}>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => handleOpenDialog()}
              sx={{ mb: 2 }}
            >
              New Watchlist
            </Button>
            {isLoading && !watchlists.length ? (
              <CircularProgress />
            ) : (
              <List component="nav">
                {watchlists.map((w) => (
                  <ListItem
                    key={w.id}
                    button
                    selected={selectedWatchlist?.id === w.id}
                    onClick={() => selectWatchlist(w)}
                    secondaryAction={
                      <>
                        <IconButton edge="end" aria-label="edit" onClick={() => handleOpenDialog(w)}>
                          <Edit />
                        </IconButton>
                        <IconButton edge="end" aria-label="delete" onClick={() => handleDelete(w.id)}>
                          <Delete />
                        </IconButton>
                      </>
                    }
                  >
                    <ListItemText primary={w.name} />
                  </ListItem>
                ))}
              </List>
            )}
          </Grid>

          {/* Watchlist Assets */}
          <Grid item xs={12} md={8}>
            {selectedWatchlist ? (
              <>
                <Typography variant="h5">{selectedWatchlist.name}</Typography>
                {isLoading && !watchlistAssets.length ? (
                  <CircularProgress />
                ) : (
                  <List>
                    {watchlistAssets.map((asset) => (
                      <ListItem key={asset.id}>
                        <ListItemText primary={asset.symbol} secondary={asset.asset_type} />
                      </ListItem>
                    ))}
                  </List>
                )}
              </>
            ) : (
              <Typography>Select a watchlist to see its assets.</Typography>
            )}
          </Grid>
        </Grid>
      </Paper>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog}>
        <DialogTitle>{editingWatchlist ? 'Edit Watchlist' : 'Create New Watchlist'}</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="name"
            label="Watchlist Name"
            type="text"
            fullWidth
            variant="standard"
            value={newWatchlistName}
            onChange={(e) => setNewWatchlistName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSaveWatchlist}>Save</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default WatchlistPage;