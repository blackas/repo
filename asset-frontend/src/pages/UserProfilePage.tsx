import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  Paper,
  CircularProgress,
  Switch,
  FormControlLabel,
} from '@mui/material';
import { useAuthStore } from '../store/useAuthStore';
import { userService } from '../services/userService';
import { toastUtils } from '../utils/toast';
import type { User } from '../types/auth';

const profileSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  email: z.string().email('Invalid email address'),
  phone_number: z.string().optional(),
  receive_daily_report: z.boolean(),
});

type ProfileFormData = z.infer<typeof profileSchema>;

const UserProfilePage: React.FC = () => {
  const { user, setUser } = useAuthStore();
  const [isLoading, setIsLoading] = useState(true);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
    setValue,
    watch,
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
  });

  const receiveDailyReport = watch('receive_daily_report', user?.receive_daily_report ?? false);

  useEffect(() => {
    const fetchUserProfile = async () => {
      setIsLoading(true);
      try {
        // Zustand store에 user 정보가 없으면 API 호출
        if (!user) {
          const userProfile = await userService.getMyProfile();
          setUser(userProfile);
          reset(userProfile);
        } else {
          reset(user);
        }
      } catch (error) {
        toastUtils.error('Failed to fetch user profile.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserProfile();
  }, [user, setUser, reset]);

  useEffect(() => {
    if (user) {
      setValue('username', user.username);
      setValue('email', user.email);
      setValue('phone_number', user.phone_number);
      setValue('receive_daily_report', user.receive_daily_report);
    }
  }, [user, setValue]);

  const onSubmit = async (data: ProfileFormData) => {
    try {
      const updatedUser = await userService.updateMyProfile(data);
      setUser(updatedUser);
      toastUtils.success('Profile updated successfully!');
    } catch (error) {
      toastUtils.error('Failed to update profile.');
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="md">
      <Paper sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          User Profile
        </Typography>
        <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate sx={{ mt: 2 }}>
          <TextField
            margin="normal"
            fullWidth
            id="username"
            label="Username"
            {...register('username')}
            error={!!errors.username}
            helperText={errors.username?.message}
            InputProps={{
              readOnly: true, // username은 변경 불가
            }}
          />
          <TextField
            margin="normal"
            fullWidth
            id="email"
            label="Email Address"
            {...register('email')}
            error={!!errors.email}
            helperText={errors.email?.message}
          />
          <TextField
            margin="normal"
            fullWidth
            id="phone_number"
            label="Phone Number"
            {...register('phone_number')}
            error={!!errors.phone_number}
            helperText={errors.phone_number?.message}
          />
          <FormControlLabel
            control={
              <Switch
                {...register('receive_daily_report')}
                checked={receiveDailyReport}
                onChange={(e) => setValue('receive_daily_report', e.target.checked)}
              />
            }
            label="Receive Daily Reports"
            sx={{ mt: 1, display: 'block' }}
          />

          <Button type="submit" fullWidth variant="contained" sx={{ mt: 3, mb: 2 }} disabled={isSubmitting}>
            {isSubmitting ? <CircularProgress size={24} /> : 'Update Profile'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default UserProfilePage;