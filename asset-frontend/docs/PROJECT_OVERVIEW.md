# Asset Frontend 프로젝트 문서

**프로젝트명**: Asset Folio Frontend
**마지막 업데이트**: 2025-12-09
**버전**: 0.0.0

---

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [기술 스택](#기술-스택)
3. [프로젝트 구조](#프로젝트-구조)
4. [핵심 기능](#핵심-기능)
5. [시작하기](#시작하기)
6. [아키텍처 설계](#아키텍처-설계)
7. [API 연동](#api-연동)
8. [상태 관리](#상태-관리)
9. [인증 시스템](#인증-시스템)
10. [개발 가이드](#개발-가이드)

---

## 프로젝트 개요

Asset Folio는 한국 주식, 미국 주식, 암호화폐 등 다양한 자산을 한 곳에서 추적하고 관리할 수 있는 종합 자산 관리 프론트엔드 애플리케이션입니다.

### 핵심 목표
- **멀티 마켓 지원**: 한국/미국 주식, 암호화폐를 하나의 인터페이스에서 관리
- **범용 컴포넌트**: 자산 타입에 관계없이 재사용 가능한 컴포넌트 설계
- **반응형 디자인**: 모바일 친화적 UI
- **실시간 데이터**: 백엔드 API와 연동하여 실시간 시장 데이터 제공
- **확장 가능한 구조**: 새로운 자산 타입 추가가 용이한 아키텍처

### 주요 특징
✅ OAuth 2.0 기반 인증 (JWT Token)
✅ Material-UI를 활용한 모던 UI/UX
✅ Zustand 경량 상태 관리
✅ TypeScript로 타입 안정성 확보
✅ Vite로 빠른 개발 경험
✅ Recharts를 통한 데이터 시각화

---

## 기술 스택

### Core Framework
- **React 19.2.0**: 최신 React 기능 활용
- **TypeScript 5.9.3**: 정적 타입 체크
- **Vite 7.2.4**: 빠른 번들링 및 HMR

### UI/UX
- **Material-UI (MUI) 7.3.5**: 컴포넌트 라이브러리
  - @mui/material: 핵심 컴포넌트
  - @mui/icons-material: 아이콘 세트
  - @emotion/react, @emotion/styled: 스타일링 엔진
- **Recharts 3.5.1**: 차트 및 그래프 시각화

### State Management & Routing
- **Zustand 5.0.9**: 경량 상태 관리 (Redux 대체)
- **React Router DOM 7.9.6**: 클라이언트 사이드 라우팅

### API & Data Fetching
- **Axios 1.13.2**: HTTP 클라이언트
  - Interceptor를 통한 JWT 토큰 자동 주입
  - Refresh Token 자동 갱신

### Development Tools
- **ESLint 9.39.1**: 코드 린팅
- **TypeScript ESLint 8.46.4**: TS 전용 린트 규칙
- **@vitejs/plugin-react 5.1.1**: Vite React 플러그인

---

## 프로젝트 구조

```
asset-frontend/
├── public/                 # 정적 파일
├── src/
│   ├── assets/            # 이미지, 폰트 등 에셋
│   ├── components/        # 재사용 가능한 컴포넌트
│   │   ├── layout/        # 레이아웃 컴포넌트
│   │   │   └── MainLayout.tsx    # 메인 레이아웃 (Drawer, AppBar)
│   │   └── common/        # 공통 UI 컴포넌트
│   │       └── ErrorBoundary.tsx  # 에러 경계
│   ├── pages/             # 페이지 컴포넌트
│   │   ├── Dashboard.tsx          # 대시보드 (홈)
│   │   ├── LoginPage.tsx          # 로그인
│   │   ├── RegisterPage.tsx       # 회원가입
│   │   ├── AssetListPage.tsx      # 자산 목록 (범용)
│   │   └── AssetDetailPage.tsx    # 자산 상세 (범용)
│   ├── services/          # API 서비스
│   │   ├── api.ts         # Axios 인스턴스 및 API 호출
│   │   └── authService.ts # 인증 API (OAuth 2.0)
│   ├── store/             # Zustand 스토어
│   │   ├── useStore.ts    # 자산 데이터 스토어
│   │   └── useAuthStore.ts # 인증 상태 스토어
│   ├── types/             # TypeScript 타입 정의
│   │   ├── index.ts       # 공통 타입
│   │   └── auth.ts        # 인증 관련 타입
│   ├── utils/             # 유틸리티 함수
│   │   └── tokenStorage.ts # 토큰 저장소
│   ├── App.tsx            # 메인 앱 컴포넌트 (라우팅)
│   ├── App.css            # 글로벌 스타일
│   ├── main.tsx           # 엔트리 포인트
│   └── index.css          # 기본 CSS
├── docs/                  # 문서
│   └── PROJECT_OVERVIEW.md
├── .env.example           # 환경 변수 템플릿
├── .gitignore             # Git 제외 파일
├── eslint.config.js       # ESLint 설정
├── index.html             # HTML 템플릿
├── package.json           # 의존성 및 스크립트
├── tsconfig.json          # TypeScript 설정 (메인)
├── tsconfig.app.json      # 앱용 TS 설정
├── tsconfig.node.json     # Node.js용 TS 설정
├── vite.config.ts         # Vite 설정
└── README.md              # 프로젝트 설명
```

---

## 핵심 기능

### 1. 멀티 마켓 자산 관리
- **한국 주식** (kr-stock): KOSPI, KOSDAQ 종목 추적
- **미국 주식** (us-stock): NYSE, NASDAQ 종목 추적 (예정)
- **암호화폐** (crypto): Upbit 코인 추적

### 2. 대시보드
- 포트폴리오 요약
- 최근 시장 동향
- 관심종목 현황

### 3. 자산 목록 페이지
- 검색 및 필터링
- 정렬 기능
- 페이지네이션

### 4. 자산 상세 페이지
- 가격 차트 (Recharts)
- 기본 정보
- 거래 내역

### 5. 인증 시스템
- **OAuth 2.0 기반 로그인**
  - Password Grant
  - Refresh Token Grant
- JWT Access Token (1시간 유효)
- Refresh Token (30일 유효)
- 자동 토큰 갱신 (Axios Interceptor)

### 6. 반응형 레이아웃
- Desktop: 좌측 Drawer 고정
- Mobile: Hamburger 메뉴
- Material-UI Breakpoints 활용

---

## 시작하기

### 사전 요구사항
- **Node.js**: v16 이상 권장
- **npm** 또는 **yarn**
- **Asset Backend API**: 실행 중이어야 함 (http://localhost:8001)

### 설치

```bash
# 의존성 설치
npm install

# 또는 yarn
yarn install
```

### 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일 내용:
```bash
# Backend API URL
VITE_API_BASE_URL=http://localhost:8001/api/v1
```

### 개발 서버 실행

```bash
npm run dev
```

앱이 `http://localhost:5173`에서 실행됩니다.

### 빌드

```bash
# 프로덕션 빌드
npm run build

# 빌드 미리보기
npm run preview
```

### 린팅

```bash
npm run lint
```

---

## 아키텍처 설계

### 1. 범용 컴포넌트 패턴

동일한 컴포넌트를 `assetType` prop으로 재사용:

```typescript
// AssetListPage.tsx
interface AssetListPageProps {
  assetType: 'kr-stock' | 'us-stock' | 'crypto';
  title: string;
}

export default function AssetListPage({ assetType, title }: AssetListPageProps) {
  const assets = useStore(state => state.assets[assetType]);
  // ...
}
```

**사용 예시**:
```tsx
<AssetListPage assetType="kr-stock" title="한국 주식" />
<AssetListPage assetType="us-stock" title="미국 주식" />
<AssetListPage assetType="crypto" title="암호화폐" />
```

### 2. 타입 안전성

TypeScript를 활용한 타입 정의:

```typescript
// types/index.ts
export type AssetType = 'kr-stock' | 'us-stock' | 'crypto';

export interface Asset {
  id: string;
  code: string;
  name: string;
  price: number;
  change: number;
  changeRate: number;
}

export interface AssetState {
  items: Asset[];
  isLoading: boolean;
  error: string | null;
}
```

### 3. 상태 격리

자산 타입별로 상태를 분리하여 데이터 충돌 방지:

```typescript
// store/useStore.ts
interface StoreState {
  assets: {
    'kr-stock': AssetState;
    'us-stock': AssetState;
    'crypto': AssetState;
  };
}
```

---

## API 연동

### API 서비스 구조

#### 1. Axios 인스턴스 생성 (`services/api.ts`)

```typescript
import axios from 'axios';
import { tokenStorage } from '../utils/tokenStorage';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api/v1';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: JWT 토큰 자동 주입
axiosInstance.interceptors.request.use(
  (config) => {
    const token = tokenStorage.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: 401 에러 시 토큰 갱신
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = tokenStorage.getRefreshToken();
      if (refreshToken) {
        try {
          // Refresh Token으로 새 Access Token 획득
          const { data } = await authService.refreshToken(refreshToken);
          tokenStorage.setTokens(data);

          // 원래 요청 재시도
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
          return axiosInstance(originalRequest);
        } catch (refreshError) {
          // Refresh 실패 시 로그아웃
          tokenStorage.clearTokens();
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  }
);
```

#### 2. 동적 엔드포인트 선택

```typescript
// services/api.ts
const getEndpointForAssetType = (assetType: AssetType): string => {
  const endpointMap: Record<AssetType, string> = {
    'kr-stock': '/stocks',
    'us-stock': '/stocks/us',
    'crypto': '/crypto',
  };
  return endpointMap[assetType] || '/stocks';
};

export const fetchAssets = async (assetType: AssetType): Promise<Asset[]> => {
  const endpoint = getEndpointForAssetType(assetType);
  const response = await axiosInstance.get(endpoint);
  return response.data.items || response.data;
};
```

### API 엔드포인트 목록

#### 인증 API
- `POST /auth/token`: 로그인 (OAuth 2.0 Password Grant)
- `POST /auth/token`: 토큰 갱신 (Refresh Token Grant)
- `POST /auth/register`: 회원가입
- `GET /auth/userinfo`: 현재 사용자 정보
- `POST /auth/logout`: 로그아웃

#### 자산 API
- `GET /stocks`: 한국 주식 목록
- `GET /stocks/{code}`: 주식 상세
- `GET /stocks/{code}/prices`: 주가 데이터
- `GET /crypto`: 암호화폐 목록 (예정)

#### 대시보드 API
- `GET /dashboard/summary`: 대시보드 요약 (예정)

---

## 상태 관리

### Zustand 스토어 구조

#### 1. 자산 스토어 (`store/useStore.ts`)

```typescript
import { create } from 'zustand';
import type { Asset, AssetType } from '../types';
import { fetchAssets } from '../services/api';

interface AssetState {
  items: Asset[];
  isLoading: boolean;
  error: string | null;
}

interface StoreState {
  assets: Record<AssetType, AssetState>;
  loadAssets: (assetType: AssetType) => Promise<void>;
}

export const useStore = create<StoreState>((set, get) => ({
  assets: {
    'kr-stock': { items: [], isLoading: false, error: null },
    'us-stock': { items: [], isLoading: false, error: null },
    'crypto': { items: [], isLoading: false, error: null },
  },

  loadAssets: async (assetType: AssetType) => {
    set((state) => ({
      assets: {
        ...state.assets,
        [assetType]: { ...state.assets[assetType], isLoading: true, error: null },
      },
    }));

    try {
      const items = await fetchAssets(assetType);
      set((state) => ({
        assets: {
          ...state.assets,
          [assetType]: { items, isLoading: false, error: null },
        },
      }));
    } catch (error: any) {
      set((state) => ({
        assets: {
          ...state.assets,
          [assetType]: {
            items: [],
            isLoading: false,
            error: error.message || 'Failed to load assets',
          },
        },
      }));
    }
  },
}));
```

#### 2. 인증 스토어 (`store/useAuthStore.ts`)

```typescript
import { create } from 'zustand';
import { authService } from '../services/authService';
import { tokenStorage } from '../utils/tokenStorage';
import type { User } from '../types/auth';

interface AuthStore {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loadUser: () => Promise<void>;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,

  login: async (username, password) => {
    set({ isLoading: true });

    try {
      // 1. 토큰 발급
      const tokenResponse = await authService.login(username, password);
      tokenStorage.setTokens(tokenResponse);

      // 2. 사용자 정보 조회
      const userInfo = await authService.getUserInfo(tokenResponse.access_token);

      // 3. 상태 업데이트
      set({
        user: {
          id: parseInt(userInfo.sub),
          username: userInfo.username,
          email: userInfo.email || '',
        },
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: async () => {
    try {
      const accessToken = tokenStorage.getAccessToken();
      if (accessToken) {
        await authService.logout(accessToken);
      }
    } finally {
      tokenStorage.clearTokens();
      set({ user: null, isAuthenticated: false });
    }
  },

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
        },
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      tokenStorage.clearTokens();
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
}));
```

---

## 인증 시스템

### OAuth 2.0 통합

#### 1. 로그인 플로우

```typescript
// pages/LoginPage.tsx
const handleLogin = async (e: React.FormEvent) => {
  e.preventDefault();

  try {
    await login(username, password);
    navigate('/dashboard');
  } catch (error: any) {
    setError(error.response?.data?.detail || 'Login failed');
  }
};
```

#### 2. 토큰 저장 (`utils/tokenStorage.ts`)

```typescript
export const tokenStorage = {
  setTokens: (tokens: TokenResponse) => {
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    localStorage.setItem('token_expires_at',
      new Date(Date.now() + tokens.expires_in * 1000).toISOString()
    );
  },

  getAccessToken: (): string | null => {
    return localStorage.getItem('access_token');
  },

  getRefreshToken: (): string | null => {
    return localStorage.getItem('refresh_token');
  },

  clearTokens: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_expires_at');
  },
};
```

#### 3. 자동 토큰 갱신

Axios Response Interceptor에서 401 에러 발생 시:
1. Refresh Token으로 `/auth/token` 호출 (grant_type=refresh_token)
2. 새 Access Token 획득
3. 원래 요청 재시도
4. Refresh Token도 만료 시 로그아웃

---

## 개발 가이드

### 새로운 자산 타입 추가

1. **타입 정의 추가** (`src/types/index.ts`)
```typescript
export type AssetType = 'kr-stock' | 'us-stock' | 'crypto' | 'new-asset';
```

2. **엔드포인트 매핑** (`src/services/api.ts`)
```typescript
const endpointMap: Record<AssetType, string> = {
  // ...
  'new-asset': '/new-assets',
};
```

3. **초기 상태 추가** (`src/store/useStore.ts`)
```typescript
assets: {
  // ...
  'new-asset': { items: [], isLoading: false, error: null },
}
```

4. **네비게이션 메뉴** (`src/components/layout/MainLayout.tsx`)
```tsx
<ListItem button component={Link} to="/new-asset">
  <ListItemIcon><NewIcon /></ListItemIcon>
  <ListItemText primary="New Asset" />
</ListItem>
```

5. **라우트 추가** (`src/App.tsx`)
```tsx
<Route
  path="/new-asset"
  element={<AssetListPage assetType="new-asset" title="New Asset" />}
/>
```

### 코딩 컨벤션

#### TypeScript
- 모든 컴포넌트에 명시적 타입 정의
- `interface` 우선, `type`은 Union/Intersection에만 사용
- Props는 `ComponentNameProps` 네이밍

#### 컴포넌트
- Functional Component + Hooks 사용
- 하나의 파일에 하나의 컴포넌트
- 기본 export 사용

#### 스타일링
- Material-UI의 `sx` prop 우선
- 복잡한 스타일은 `styled` 컴포넌트
- 테마 변수 활용

### 디버깅

#### React DevTools
브라우저 확장 프로그램 설치:
- [React DevTools](https://react.dev/learn/react-developer-tools)

#### Zustand DevTools
```typescript
import { devtools } from 'zustand/middleware';

export const useStore = create<StoreState>()(
  devtools(
    (set, get) => ({
      // ...
    }),
    { name: 'AssetStore' }
  )
);
```

---

## 배포

### Vercel 배포 (권장)

1. GitHub에 푸시
2. [Vercel](https://vercel.com)에 로그인
3. "New Project" → GitHub 저장소 선택
4. 환경 변수 설정:
   - `VITE_API_BASE_URL`: 프로덕션 API URL
5. "Deploy" 클릭

### 수동 배포

```bash
# 빌드
npm run build

# dist/ 폴더를 웹 서버에 배포
# (Nginx, Apache, AWS S3, Netlify 등)
```

### 환경 변수 (프로덕션)

```bash
VITE_API_BASE_URL=https://api.yourdomain.com/api/v1
```

---

## 트러블슈팅

### CORS 에러
**문제**: API 요청 시 CORS 에러 발생

**해결**:
1. 백엔드 `CORS_ALLOWED_ORIGINS`에 프론트엔드 URL 추가
2. 개발 환경: `http://localhost:5173`
3. 프로덕션: `https://yourdomain.com`

### 토큰 갱신 실패
**문제**: Refresh Token이 만료되어 자동 로그인 실패

**해결**:
- Refresh Token 유효기간 확인 (기본 30일)
- localStorage에 저장된 토큰 확인
- 필요 시 로그아웃 후 재로그인

### 빌드 에러
**문제**: TypeScript 타입 에러로 빌드 실패

**해결**:
```bash
# 타입 체크
npm run build

# 에러 확인 후 수정
# 또는 일시적으로 skipLibCheck 활성화 (권장하지 않음)
```

---

## 향후 계획

### 단기 (1-2개월)
- [ ] 미국 주식 API 연동
- [ ] 암호화폐 상세 페이지
- [ ] 포트폴리오 추적 기능
- [ ] 다크 모드 지원

### 중기 (3-6개월)
- [ ] 실시간 가격 업데이트 (WebSocket)
- [ ] 푸시 알림
- [ ] 차트 커스터마이징
- [ ] 다국어 지원 (i18n)

### 장기 (6개월+)
- [ ] 모바일 앱 (React Native)
- [ ] 고급 분석 도구
- [ ] 소셜 기능 (공유, 팔로우)
- [ ] AI 기반 추천

---

## 참고 자료

### 공식 문서
- [React](https://react.dev/)
- [TypeScript](https://www.typescriptlang.org/docs/)
- [Vite](https://vite.dev/)
- [Material-UI](https://mui.com/)
- [Zustand](https://zustand-demo.pmnd.rs/)
- [Axios](https://axios-http.com/)

### 관련 프로젝트
- [Asset Backend](../asset-backend/docs/PROJECT_OVERVIEW.md)
- [Asset Mobile App](../asset-app/docs/)

---

## 라이선스

MIT

---

**최종 업데이트**: 2025-12-09
**문서 버전**: 1.0.0
