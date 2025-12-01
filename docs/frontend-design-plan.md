# 프론트엔드 설계 계획서: Asset Folio

kstock_reporter 백엔드 프로젝트와 연동하여, 국내 주식, 미국 주식, 암호화폐를 모두 지원하는 확장 가능한 프론트엔드 애플리케이션을 구축한다.

## 1. 추천 기술 스택

- **프레임워크:** **React (with TypeScript)**
  - 안정성과 생산성을 위해 TypeScript를 적극 활용.
- **빌드 도구:** **Vite**
  - 빠른 개발 및 빌드 속도.
- **UI 라이브러리:** **Material-UI (MUI)** 또는 **Ant Design (AntD)**
  - 검증된 디자인의 컴포넌트를 활용하여 신속하게 UI 개발.
- **상태 관리:** **Zustand**
  - 가볍고 직관적인 API를 가진 상태 관리 라이브러리. Redux Toolkit도 좋은 대안.
- **API 통신:** **Axios**
  - HTTP 요청/응답 처리를 위한 라이브러리. 인터셉터를 활용해 인증 토큰 관리.
- **라우팅:** **React Router DOM**
  - SPA(Single Page Application)의 페이지 전환 관리.
- **차트:** **Recharts** 또는 **ECharts for React**
  - 자산의 시계열 데이터를 시각화.

## 2. 핵심 설계 사상

### 2.1. 유연한 컴포넌트 구조 (Generic Components)

개별 자산(국내주식, 미국주식 등)마다 별도의 페이지를 만들지 않고, 어떤 자산이든 처리할 수 있는 **재사용 가능한 제네릭 컴포넌트**를 설계한다.

- **`AssetListPage.tsx`**:
  - `assetType` prop (예: `kr-stock`, `us-stock`, `crypto`)을 받아, 해당 타입에 맞는 API 호출과 테이블 컬럼을 동적으로 렌더링한다.
- **`AssetDetailPage.tsx`**:
  - URL 파라미터(`/:assetType/:assetId`)를 통해 자산의 종류와 식별자를 받아, 동적으로 상세 정보를 렌더링한다.

**기대 효과**: 신규 자산 타입이 추가되어도 컴포넌트 재사용으로 코드 중복을 최소화하고 유지보수 비용을 절감한다.

### 2.2. 확장 가능한 상태 관리 (Scalable State)

전역 상태(Zustand Store)를 자산 유형별로 명확히 분리하여 관리한다.

- **Store 구조 예시**:
  ```typescript
  {
    "auth": { "user": "...", "token": "..." },
    "assets": {
      "kr-stock": { "items": [], "isLoading": false, "error": null },
      "us-stock": { "items": [], "isLoading": false, "error": null },
      "crypto":   { "items": [], "isLoading": false, "error": null }
    },
    // ...
  }
  ```
- **기대 효과**: 데이터 충돌을 방지하고, 각 자산 목록의 로딩/에러 상태를 독립적으로 관리할 수 있다.

### 2.3. 동적 API 서비스 모듈

API 호출 함수들이 `assetType`을 인자로 받아, 각 타입에 맞는 API 엔드포인트로 요청을 보낼 수 있도록 설계한다.

- **API 함수 예시**:
  ```typescript
  const getAssets = (assetType: 'kr-stock' | 'us-stock' | 'crypto') => {
    const endpoint = getEndpointForAssetType(assetType); // 타입에 맞는 URL 반환
    return axiosInstance.get(endpoint);
  };
  ```

### 2.4. 통합된 UI/UX

- **네비게이션**: 사이드바 또는 탭을 통해 자산 시장(국내, 미국, 암호화폐) 간 전환이 용이하도록 설계한다.
- **대시보드**: 모든 자산을 아우르는 통합 포트폴리오 요약 정보를 제공한다.
- **검색**: 전체 자산을 대상으로 하는 통합 검색 기능을 고려한다.

## 3. 추천 프로젝트 이름

- `asset-frontend`
