# Asset Folio

A comprehensive frontend application for tracking and managing assets across multiple markets including Korean stocks, US stocks, and cryptocurrencies.

## Tech Stack

- **Framework:** React with TypeScript
- **Build Tool:** Vite
- **UI Library:** Material-UI (MUI)
- **State Management:** Zustand
- **API Communication:** Axios
- **Routing:** React Router DOM
- **Charts:** Recharts

## Features

- **Multi-Market Support:** Track Korean stocks, US stocks, and cryptocurrencies in one place
- **Generic Components:** Reusable components that work across different asset types
- **Responsive Design:** Mobile-friendly UI with drawer navigation
- **Real-time Data:** Integration with backend API for live market data
- **Interactive Charts:** Visualize price history and trends
- **Scalable Architecture:** Easy to add new asset types or features

## Project Structure

```
asset-frontend/
├── src/
│   ├── components/          # Reusable components
│   │   ├── layout/          # Layout components (MainLayout)
│   │   └── common/          # Common UI components
│   ├── pages/               # Page components
│   │   ├── Dashboard.tsx    # Main dashboard
│   │   ├── AssetListPage.tsx    # Generic asset list page
│   │   └── AssetDetailPage.tsx  # Generic asset detail page
│   ├── services/            # API services
│   │   └── api.ts          # Axios configuration and API calls
│   ├── store/              # State management
│   │   └── useStore.ts     # Zustand store
│   ├── types/              # TypeScript type definitions
│   │   └── index.ts
│   ├── utils/              # Utility functions
│   ├── App.tsx             # Main app component with routing
│   └── main.tsx            # Entry point
└── package.json
```

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Backend API running (kstock_reporter)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` to set your API base URL:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Development

Run the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Key Design Principles

### 1. Generic Components

Instead of creating separate pages for each asset type, we use generic components that accept an `assetType` prop:

```typescript
<AssetListPage assetType="kr-stock" title="Korean Stocks" />
<AssetListPage assetType="us-stock" title="US Stocks" />
<AssetListPage assetType="crypto" title="Cryptocurrencies" />
```

### 2. Scalable State Management

State is organized by asset type to prevent data collisions:

```typescript
{
  assets: {
    'kr-stock': { items: [], isLoading: false, error: null },
    'us-stock': { items: [], isLoading: false, error: null },
    'crypto': { items: [], isLoading: false, error: null }
  }
}
```

### 3. Dynamic API Services

API functions dynamically select endpoints based on asset type:

```typescript
const endpoint = getEndpointForAssetType(assetType);
const response = await axiosInstance.get(endpoint);
```

## API Integration

The frontend expects the following API endpoints:

- `GET /api/v1/stocks/kr` - Korean stocks list
- `GET /api/v1/stocks/us` - US stocks list
- `GET /api/v1/crypto` - Cryptocurrencies list
- `GET /api/v1/stocks/{type}/{id}` - Asset details
- `GET /api/v1/dashboard/summary` - Dashboard summary
- `GET /api/v1/reports` - Reports for an asset

## Adding New Asset Types

To add a new asset type:

1. Update the `AssetType` in `src/types/index.ts`
2. Add the endpoint mapping in `src/services/api.ts`
3. Initialize state in `src/store/useStore.ts`
4. Add navigation item in `src/components/layout/MainLayout.tsx`
5. Add route in `src/App.tsx`

## License

MIT
