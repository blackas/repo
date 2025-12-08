import { Container, Paper, Box, Link as MuiLink } from '@mui/material';
import { Link } from 'react-router-dom';
import RegisterForm from '../components/auth/RegisterForm';

export default function RegisterPage() {
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
          <RegisterForm />

          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <MuiLink component={Link} to="/login" variant="body2">
              Already have an account? Sign In
            </MuiLink>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}
