# Asset Folio 프론트엔드 구현 문서

## 1. 프로젝트 개요

Asset Folio는 kstock_reporter 백엔드 프로젝트와 연동하여 국내 주식, 미국 주식, 암호화폐를 통합 관리하는 확장 가능한 웹 프론트엔드 애플리케이션입니다.

### 주요 특징

- **멀티 마켓 지원**: 한국 주식, 미국 주식, 암호화폐를 하나의 플랫폼에서 관리
- **제네릭 컴포넌트 아키텍처**: 재사용 가능한 컴포넌트로 코드 중복 최소화
- **확장 가능한 설계**: 새로운 자산 타입 추가가 용이한 구조
- **반응형 디자인**: 모바일, 태블릿, 데스크톱 모두 지원
- **실시간 데이터**: 백엔드 API와 연동하여 실시간 시장 데이터 제공

## 2. 기술 스택

### 핵심 기술

| 기술 | 버전 | 용도 |
|------|------|------|
| React | 18.x | UI 라이브러리 |
| TypeScript | 5.x | 타입 안정성 |
| Vite | 7.x | 빌드 도구 |
| Material-UI (MUI) | 7.x | UI 컴포넌트 라이브러리 |
| Zustand | - | 상태 관리 |
| Axios | 1.x | HTTP 클라이언트 |
| React Router DOM | - | 라우팅 |
| Recharts | - | 차트 라이브러리 |

### 선정 이유

- **React + TypeScript**: 안정성과 생산성의 균형
- **Vite**: 빠른 개발 환경 및 빌드 속도
- **MUI**: 검증된 Material Design 컴포넌트
- **Zustand**: Redux보다 가볍고 직관적인 상태 관리
- **Axios**: 인터셉터를 활용한 인증 토큰 관리 용이

## 3. 프로젝트 구조

```
asset-frontend/
├── public/                      # 정적 파일
├── src/
│   ├── components/              # 재사용 가능한 컴포넌트
│   │   ├── layout/              # 레이아웃 컴포넌트
│   │   │   └── MainLayout.tsx   # 사이드바 네비게이션 메인 레이아웃
│   │   └── common/              # 공통 UI 컴포넌트
│   ├── pages/                   # 페이지 컴포넌트
│   │   ├── Dashboard.tsx        # 통합 대시보드
│   │   ├── AssetListPage.tsx    # 제네릭 자산 목록 페이지
│   │   └── AssetDetailPage.tsx  # 제네릭 자산 상세 페이지
│   ├── services/                # API 서비스
│   │   └── api.ts              # Axios 설정 및 API 함수
│   ├── store/                   # 상태 관리
│   │   └── useStore.ts         # Zustand 스토어
│   ├── types/                   # TypeScript 타입 정의
│   │   └── index.ts            # 공통 타입 정의
│   ├── utils/                   # 유틸리티 함수
│   ├── App.tsx                  # 메인 앱 컴포넌트 (라우팅)
│   ├── main.tsx                 # 엔트리 포인트
│   └── App.css                  # 스타일
├── .env                         # 환경 변수
├── .env.example                 # 환경 변수 예제
├── package.json                 # 프로젝트 설정
├── tsconfig.json                # TypeScript 설정
├── vite.config.ts               # Vite 설정
└── README.md                    # 프로젝트 문서
```

## 4. 핵심 설계 원칙

### 4.1. 제네릭 컴포넌트 패턴

개별 자산마다 별도 페이지를 만들지 않고, `assetType` prop을 받아 동적으로 처리하는 재사용 가능한 컴포넌트를 설계했습니다.

#### AssetListPage 컴포넌트

```typescript
interface AssetListPageProps {
  assetType: AssetType;  // 'kr-stock' | 'us-stock' | 'crypto'
  title: string;
}

function AssetListPage({ assetType, title }: AssetListPageProps) {
  // assetType에 따라 동적으로 API 호출 및 렌더링
}
```

**사용 예시**:
```tsx
<AssetListPage assetType="kr-stock" title="Korean Stocks" />
<AssetListPage assetType="us-stock" title="US Stocks" />
<AssetListPage assetType="crypto" title="Cryptocurrencies" />
```

#### AssetDetailPage 컴포넌트

URL 파라미터를 통해 자산 타입과 ID를 받아 동적으로 상세 정보를 표시합니다.

```typescript
// URL: /assets/:assetType/:assetId
const { assetType, assetId } = useParams<{
  assetType: AssetType;
  assetId: string
}>();
```

### 4.2. 확장 가능한 상태 관리

Zustand를 사용하여 자산 타입별로 독립적인 상태를 관리합니다.

```typescript
{
  auth: { user: null, token: null },
  assets: {
    'kr-stock': { items: [], isLoading: false, error: null },
    'us-stock': { items: [], isLoading: false, error: null },
    'crypto':   { items: [], isLoading: false, error: null }
  }
}
```

**장점**:
- 데이터 충돌 방지
- 독립적인 로딩/에러 상태 관리
- 타입별 개별 업데이트 가능

### 4.3. 동적 API 서비스 모듈

자산 타입에 따라 엔드포인트를 동적으로 결정하는 API 서비스 레이어를 구현했습니다.

```typescript
const getEndpointForAssetType = (assetType: AssetType): string => {
  const endpointMap: Record<AssetType, string> = {
    'kr-stock': '/stocks/kr',
    'us-stock': '/stocks/us',
    'crypto': '/crypto',
  };
  return endpointMap[assetType];
};
```

#### API 인터셉터

**요청 인터셉터**: 인증 토큰 자동 추가
```typescript
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**응답 인터셉터**: 401 에러 시 자동 로그아웃
```typescript
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## 5. 구현된 기능

### 5.1. Dashboard (대시보드)

**경로**: `/`

**기능**:
- 전체 자산 요약 정보 표시
- 총 자산 수, 총 가치, 지원 마켓 수
- 마켓 개요 정보

**주요 컴포넌트**:
- Stack 레이아웃을 사용한 반응형 카드 배치
- Paper 컴포넌트로 정보 구분
- API를 통한 대시보드 요약 데이터 조회

### 5.2. AssetListPage (자산 목록)

**경로**:
- `/assets/kr-stock` - 한국 주식
- `/assets/us-stock` - 미국 주식
- `/assets/crypto` - 암호화폐

**기능**:
- 자산 타입별 목록 표시 (테이블)
- 가격, 변동률, 거래량 등 주요 정보 표시
- 행 클릭 시 상세 페이지로 이동
- 로딩 상태 및 에러 처리

**테이블 컬럼**:
- 이름 (Name)
- 심볼 (Symbol)
- 가격 (Price)
- 변동 (Change)
- 변동률 (Change %)
- 거래량 (Volume)

### 5.3. AssetDetailPage (자산 상세)

**경로**: `/assets/:assetType/:assetId`

**기능**:
- 자산의 상세 정보 표시
- 현재 가격 정보 (가격, 변동, 거래량, 시가총액)
- 추가 정보 (섹터, 산업, 설명)
- 가격 히스토리 차트 (Recharts LineChart)
- 뒤로 가기 버튼

**차트 기능**:
- Recharts를 활용한 시계열 데이터 시각화
- 반응형 차트 (ResponsiveContainer)
- 툴팁, 범례 포함

### 5.4. MainLayout (메인 레이아웃)

**기능**:
- 사이드바 네비게이션 (Drawer)
- 반응형 디자인 (모바일에서는 토글 메뉴)
- 라우팅 통합
- 통일된 헤더 및 레이아웃

**네비게이션 메뉴**:
1. Dashboard - 대시보드
2. Korean Stocks - 한국 주식
3. US Stocks - 미국 주식
4. Crypto - 암호화폐

## 6. API 통합

### 6.1. 환경 변수 설정

`.env` 파일:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 6.2. 필요한 백엔드 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/api/v1/stocks/kr` | GET | 한국 주식 목록 |
| `/api/v1/stocks/us` | GET | 미국 주식 목록 |
| `/api/v1/crypto` | GET | 암호화폐 목록 |
| `/api/v1/stocks/kr/{id}` | GET | 한국 주식 상세 |
| `/api/v1/stocks/us/{id}` | GET | 미국 주식 상세 |
| `/api/v1/crypto/{id}` | GET | 암호화폐 상세 |
| `/api/v1/dashboard/summary` | GET | 대시보드 요약 |
| `/api/v1/reports` | GET | 리포트 목록 |

### 6.3. API 응답 형식

**자산 목록**:
```json
{
  "results": [
    {
      "id": "1",
      "name": "삼성전자",
      "symbol": "005930",
      "currentPrice": 75000,
      "change": 1000,
      "changePercent": 1.35,
      "volume": 1000000,
      "marketCap": 450000000000000
    }
  ]
}
```

**자산 상세**:
```json
{
  "id": "1",
  "name": "삼성전자",
  "symbol": "005930",
  "currentPrice": 75000,
  "change": 1000,
  "changePercent": 1.35,
  "volume": 1000000,
  "marketCap": 450000000000000,
  "sector": "Technology",
  "industry": "Semiconductors",
  "description": "한국의 대표적인 전자 기업",
  "historicalData": [
    {
      "date": "2024-01-01",
      "open": 74000,
      "high": 75500,
      "low": 73500,
      "close": 75000,
      "volume": 1000000
    }
  ]
}
```

## 7. 설치 및 실행

### 7.1. 설치

```bash
cd asset-frontend
npm install
```

### 7.2. 개발 서버 실행

```bash
npm run dev
```

개발 서버는 `http://localhost:5173`에서 실행됩니다.

### 7.3. 빌드

```bash
npm run build
```

빌드된 파일은 `dist/` 폴더에 생성됩니다.

### 7.4. 프로덕션 미리보기

```bash
npm run preview
```

## 8. 새로운 자산 타입 추가하기

새로운 자산 타입을 추가하려면 다음 단계를 따르세요:

### Step 1: 타입 정의 추가

`src/types/index.ts`:
```typescript
export type AssetType = 'kr-stock' | 'us-stock' | 'crypto' | 'new-asset';
```

### Step 2: API 엔드포인트 매핑 추가

`src/services/api.ts`:
```typescript
const getEndpointForAssetType = (assetType: AssetType): string => {
  const endpointMap: Record<AssetType, string> = {
    'kr-stock': '/stocks/kr',
    'us-stock': '/stocks/us',
    'crypto': '/crypto',
    'new-asset': '/new-asset',  // 추가
  };
  return endpointMap[assetType];
};
```

### Step 3: 스토어 초기 상태 추가

`src/store/useStore.ts`:
```typescript
assets: {
  'kr-stock': { items: [], isLoading: false, error: null },
  'us-stock': { items: [], isLoading: false, error: null },
  'crypto': { items: [], isLoading: false, error: null },
  'new-asset': { items: [], isLoading: false, error: null },  // 추가
}
```

### Step 4: 네비게이션 메뉴 추가

`src/components/layout/MainLayout.tsx`:
```typescript
const navItems: NavItem[] = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Korean Stocks', icon: <TrendingUp />, path: '/assets/kr-stock' },
  { text: 'US Stocks', icon: <ShowChart />, path: '/assets/us-stock' },
  { text: 'Crypto', icon: <CurrencyBitcoin />, path: '/assets/crypto' },
  { text: 'New Asset', icon: <YourIcon />, path: '/assets/new-asset' },  // 추가
];
```

### Step 5: 라우트 추가

`src/App.tsx`:
```tsx
<Route
  path="assets/new-asset"
  element={<AssetListPage assetType="new-asset" title="New Asset Type" />}
/>
```

이렇게 5단계만으로 새로운 자산 타입을 추가할 수 있습니다!

## 9. 타입 시스템

### 9.1. 주요 타입 정의

```typescript
// 자산 타입
export type AssetType = 'kr-stock' | 'us-stock' | 'crypto';

// 자산 인터페이스
export interface Asset {
  id: string | number;
  name: string;
  symbol?: string;
  currentPrice?: number;
  change?: number;
  changePercent?: number;
  volume?: number;
  marketCap?: number;
  [key: string]: any;  // 확장 가능
}

// 자산 상세 인터페이스
export interface AssetDetail extends Asset {
  description?: string;
  sector?: string;
  industry?: string;
  historicalData?: PriceData[];
}

// 가격 데이터
export interface PriceData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// 자산 상태
export interface AssetState {
  items: Asset[];
  isLoading: boolean;
  error: string | null;
}

// 전체 스토어 상태
export interface StoreState {
  auth: {
    user: string | null;
    token: string | null;
  };
  assets: {
    [key in AssetType]: AssetState;
  };
  setAssets: (assetType: AssetType, assets: Asset[]) => void;
  setLoading: (assetType: AssetType, isLoading: boolean) => void;
  setError: (assetType: AssetType, error: string | null) => void;
  setAuth: (user: string | null, token: string | null) => void;
}
```

## 10. 코드 품질

### 10.1. TypeScript 설정

- Strict mode 활성화
- `verbatimModuleSyntax` 사용으로 타입 import 명확화
- 모든 타입은 `import type` 구문 사용

### 10.2. 컴포넌트 구조

- 함수형 컴포넌트 사용
- React Hooks 활용
- Props 타입 명시
- 재사용 가능한 구조

### 10.3. 에러 처리

- API 호출 시 try-catch 사용
- 로딩 상태 관리
- 사용자 친화적인 에러 메시지

## 11. 성능 최적화

### 11.1. 빌드 최적화

현재 번들 크기가 큰 편이므로, 다음 최적화를 고려할 수 있습니다:

1. **코드 스플리팅**: React.lazy와 Suspense 사용
```typescript
const Dashboard = lazy(() => import('./pages/Dashboard'));
const AssetListPage = lazy(() => import('./pages/AssetListPage'));
```

2. **Manual Chunks**: Vite 설정에서 라이브러리 분리
```typescript
// vite.config.ts
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'react-vendor': ['react', 'react-dom', 'react-router-dom'],
        'mui-vendor': ['@mui/material', '@mui/icons-material'],
        'chart-vendor': ['recharts'],
      }
    }
  }
}
```

### 11.2. 런타임 최적화

- React.memo로 불필요한 리렌더링 방지
- useCallback, useMemo 활용
- 가상 스크롤 (대용량 데이터 목록)

## 12. 보안 고려사항

### 12.1. 인증 토큰 관리

- localStorage에 토큰 저장
- Axios 인터셉터로 자동 헤더 추가
- 401 응답 시 자동 로그아웃

### 12.2. XSS 방지

- React의 기본 이스케이핑 활용
- dangerouslySetInnerHTML 사용 지양

### 12.3. CORS 설정

백엔드에서 적절한 CORS 헤더 설정 필요:
```python
# Django settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]
```

## 13. 향후 개선 사항

### 13.1. 기능 추가

- [ ] 검색 기능 구현
- [ ] 필터링 및 정렬
- [ ] 페이지네이션
- [ ] 즐겨찾기 기능
- [ ] 알림 기능
- [ ] 다크 모드
- [ ] 다국어 지원 (i18n)

### 13.2. 기술적 개선

- [ ] 단위 테스트 (Jest, React Testing Library)
- [ ] E2E 테스트 (Cypress, Playwright)
- [ ] Storybook 도입
- [ ] PWA 기능
- [ ] 오프라인 지원

### 13.3. UX 개선

- [ ] 스켈레톤 로더
- [ ] 애니메이션 효과
- [ ] 드래그 앤 드롭
- [ ] 키보드 단축키

## 14. 트러블슈팅

### 14.1. MUI Grid2 문제

MUI v7에서 Grid2 import 오류 발생 시, Stack 컴포넌트를 대안으로 사용:

```typescript
// Grid 대신
<Stack direction={{ xs: 'column', md: 'row' }} spacing={3}>
  <Paper sx={{ flex: 1 }}>...</Paper>
  <Paper sx={{ flex: 1 }}>...</Paper>
</Stack>
```

### 14.2. Type Import 오류

`verbatimModuleSyntax` 설정으로 인한 오류는 `import type` 사용:

```typescript
// 잘못된 예
import { AssetType } from '../types';

// 올바른 예
import type { AssetType } from '../types';
```

### 14.3. API 연결 오류

CORS 문제 발생 시 백엔드 설정 확인:
1. Django CORS 미들웨어 설치 및 설정
2. ALLOWED_ORIGINS 확인
3. 개발 환경에서는 프록시 설정 고려

## 15. 참고 자료

- [React 공식 문서](https://react.dev/)
- [TypeScript 공식 문서](https://www.typescriptlang.org/)
- [MUI 공식 문서](https://mui.com/)
- [Zustand 문서](https://github.com/pmndrs/zustand)
- [Vite 문서](https://vitejs.dev/)
- [Recharts 문서](https://recharts.org/)

## 16. 라이선스

MIT License

---

**작성일**: 2025-12-01
**작성자**: Claude
**버전**: 1.0.0
