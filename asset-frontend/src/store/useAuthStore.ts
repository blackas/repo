import { create } from 'zustand';
import type { User, AuthState, RegisterRequest } from '../types/auth';
import { authService } from '../services/authService';
import { tokenStorage } from '../utils/tokenStorage';
import { toastUtils } from '../utils/toast';

interface AuthStore extends AuthState {
  // Actions
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (data: RegisterRequest) => Promise<User>;
  loadUser: () => Promise<void>;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  // Initial state
  user: null,
  isAuthenticated: false,
  isLoading: false,

  // Login
  login: async (username, password) => {
    set({ isLoading: true });

    try {
      // 1. 토큰 발급
      const tokenResponse = await authService.login(username, password);

      // 2. 토큰 저장
      tokenStorage.setTokens(tokenResponse);

      // 3. 사용자 정보 조회
      const userInfo = await authService.getUserInfo(tokenResponse.access_token);

      // 4. 상태 업데이트
      set({
        user: {
          id: parseInt(userInfo.sub),
          username: userInfo.username,
          email: userInfo.email || '',
          phone_number: userInfo.phone_number,
          receive_daily_report: true,
        },
        isAuthenticated: true,
        isLoading: false,
      });
      toastUtils.success('Logged in successfully');
    } catch (error) {
      set({ isLoading: false });
      toastUtils.error('Login failed. Please check your credentials.');
      throw error;
    }
  },

  // Logout
  logout: async () => {
    try {
      const accessToken = tokenStorage.getAccessToken();
      if (accessToken) {
        // 서버에 로그아웃 요청 (모든 토큰 무효화)
        await authService.logout(accessToken);
      }
    } catch (error) {
      console.error('Logout error:', error);
      toastUtils.error('Logout failed.');
    } finally {
      // 로컬 토큰 삭제
      tokenStorage.clearTokens();

      // 상태 초기화
      set({
        user: null,
        isAuthenticated: false,
      });
      toastUtils.success('Logged out successfully');
    }
  },

  // Register
  register: async (data) => {
    set({ isLoading: true });

    try {
      const user = await authService.register(data);
      set({ isLoading: false });
      toastUtils.success('Registration successful. Please log in.');
      return user;
    } catch (error) {
      set({ isLoading: false });
      toastUtils.error('Registration failed. Please try again.');
      throw error;
    }
  },

  // Load user info (앱 시작 시 호출)
  loadUser: async () => {
    const accessToken = tokenStorage.getAccessToken();

    if (!accessToken) {
      set({ isAuthenticated: false, isLoading: false });
      return;
    }

    set({ isLoading: true });

    try {
      const userInfo = await authService.getUserInfo(accessToken);

      set({
        user: {
          id: parseInt(userInfo.sub),
          username: userInfo.username,
          email: userInfo.email || '',
          phone_number: userInfo.phone_number,
          receive_daily_report: true,
        },
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      // 토큰이 유효하지 않으면 삭제
      tokenStorage.clearTokens();
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },

  // Set user
  setUser: (user) => {
    set({ user, isAuthenticated: !!user });
  },
}));
