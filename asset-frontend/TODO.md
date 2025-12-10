# Frontend Development Plan

This document outlines the development plan for the asset-frontend application, breaking down the work into logical phases.

## Phase 0: Implemented Features

This section summarizes the features that are already implemented and functional.

- **[x] Comprehensive Authentication System:**
  - Login, registration, logout, and session management are fully implemented.
  - Secure token handling (access and refresh tokens) is in place.
  - Protected routes are functional, guarding access to authenticated sections.
- **[x] Basic Asset Viewing:**
  - A generic `AssetListPage` displays lists of stocks and cryptocurrencies.
  - A generic `AssetDetailPage` shows asset details and a basic price chart.

---

## Phase 1: UI/UX and Core Structure

This phase focuses on establishing a solid and user-friendly foundation for the application.

- **[ ] Design and Implement Main Application Layout:**
  - Create a consistent `MainLayout` component including a header, navigation sidebar, and content area.
  - Implement a responsive design that works well on both desktop and mobile devices.
- **[ ] Refine UI Components and Styling:**
  - Review and enhance the styling of existing components (`LoginForm`, `RegisterForm`, tables, etc.) for a more polished look and feel.
  - Ensure consistent use of the chosen UI library (MUI) and a defined theme.
- **[ ] Global State Management Review:**
  - Refactor the global store (`useStore.ts`) to be more modular and scalable as new features are added.
  - Establish clear patterns for managing state for different features (assets, user, watchlists, etc.).
- **[ ] Centralized Error Handling:**
  - Implement a global error handling mechanism (e.g., using a notification/toast system) to provide consistent feedback to the user.
  - Improve specific error messages to be more user-friendly.

---

## Phase 2: Complete Core Features

This phase aims to complete the core asset management functionality.

- **[ ] Enhance Asset List Page:**
  - Implement pagination to handle large datasets of assets.
  - Add a search bar for finding assets by name or symbol.
  - Implement filtering capabilities (e.g., by market for stocks).
- **[ ] Enhance Asset Detail Page:**
  - Implement chart controls to allow users to switch between different time intervals (daily, weekly, monthly).
  - Add more detailed data visualizations as needed.

---

## Phase 3: User-Specific Features

This phase focuses on features that are personalized for the logged-in user.

- **[x] Implement User Profile Page:**
  - Create a page for users to view and update their profile information.
  - Connect the page to the `/api/v1/users/me` endpoints.
- **[x] Implement Watchlists:**
  - Build a watchlist management page to create, rename, and delete watchlists.
  - Integrate "add/remove from watchlist" functionality into the `AssetDetailPage`.

---

## Phase 4: Advanced Features

This phase introduces more complex, value-add features.

- **[ ] Implement Reports:**
  - Create a page to list and view daily user reports.
  - Implement date filtering for report navigation.
  - Build a detailed view for a single report.

---

## Phase 5: Testing and Quality Assurance

This final phase ensures the application is robust and reliable.

- **[ ] Set up a Testing Framework:**
  - Configure a testing framework like Jest and React Testing Library.
- **[ ] Write Unit Tests:**
  - Write unit tests for critical components and utility functions.
- **[ ] Write Integration Tests:**
  - Write integration tests for key user flows, such as login, registration, and adding an asset to a watchlist.
