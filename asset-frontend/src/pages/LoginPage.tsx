import { Container, Paper, Box, Link as MuiLink } from '@mui/material';
import { Link } from 'react-router-dom';
import LoginForm from '../components/auth/LoginForm';

export default function LoginPage() {
  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <LoginForm />

          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <MuiLink component={Link} to="/register" variant="body2">
              Don't have an account? Sign Up
            </MuiLink>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}
