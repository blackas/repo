import { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  FormControlLabel,
  Checkbox,
  CircularProgress,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/useAuthStore';

export default function RegisterForm() {
  const navigate = useNavigate();
  const { register, isLoading } = useAuthStore();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    phone_number: '',
    receive_daily_report: true,
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    // 비밀번호 확인
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    // 비밀번호 길이 검증
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    try {
      await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        phone_number: formData.phone_number || undefined,
        receive_daily_report: formData.receive_daily_report,
      });

      setSuccess(true);
      // 회원가입 성공 -> 로그인 페이지로 이동
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Registration failed. Please try again.'
      );
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
      <Typography variant="h5" gutterBottom>
        Create Account
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Registration successful! Redirecting to login...
        </Alert>
      )}

      <TextField
        margin="normal"
        required
        fullWidth
        name="username"
        label="Username"
        autoComplete="username"
        value={formData.username}
        onChange={handleChange}
        disabled={isLoading || success}
        autoFocus
      />

      <TextField
        margin="normal"
        required
        fullWidth
        name="email"
        label="Email Address"
        type="email"
        autoComplete="email"
        value={formData.email}
        onChange={handleChange}
        disabled={isLoading || success}
      />

      <TextField
        margin="normal"
        required
        fullWidth
        name="password"
        label="Password"
        type="password"
        autoComplete="new-password"
        value={formData.password}
        onChange={handleChange}
        disabled={isLoading || success}
        helperText="At least 8 characters"
      />

      <TextField
        margin="normal"
        required
        fullWidth
        name="confirmPassword"
        label="Confirm Password"
        type="password"
        autoComplete="new-password"
        value={formData.confirmPassword}
        onChange={handleChange}
        disabled={isLoading || success}
      />

      <TextField
        margin="normal"
        fullWidth
        name="phone_number"
        label="Phone Number (Optional)"
        autoComplete="tel"
        value={formData.phone_number}
        onChange={handleChange}
        disabled={isLoading || success}
        placeholder="+82-10-1234-5678"
      />

      <FormControlLabel
        control={
          <Checkbox
            name="receive_daily_report"
            checked={formData.receive_daily_report}
            onChange={handleChange}
            disabled={isLoading || success}
            color="primary"
          />
        }
        label="Receive daily reports via email"
      />

      <Button
        type="submit"
        fullWidth
        variant="contained"
        sx={{ mt: 3, mb: 2 }}
        disabled={isLoading || success}
      >
        {isLoading ? <CircularProgress size={24} /> : 'Sign Up'}
      </Button>
    </Box>
  );
}
