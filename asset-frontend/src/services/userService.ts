import axiosInstance from './api';
import type { User } from '../types/auth';

export const userService = {
  async getMyProfile(): Promise<User> {
    const response = await axiosInstance.get<User>('/users/me');
    return response.data;
  },

  async updateMyProfile(data: Partial<User>): Promise<User> {
    const response = await axiosInstance.patch<User>('/users/me', data);
    return response.data;
  },
};
