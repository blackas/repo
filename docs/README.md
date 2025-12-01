# Asset Portfolio Project Documentation

이 폴더는 Asset Portfolio 프로젝트(kstock_reporter + Asset Folio)의 전체 문서를 포함합니다.

## 📚 문서 목록

### 1. 프론트엔드 문서

#### [Frontend Design Plan](./frontend-design-plan.md)
프론트엔드 애플리케이션의 초기 설계 계획서입니다.

**내용**:
- 추천 기술 스택
- 핵심 설계 사상
- 유연한 컴포넌트 구조
- 확장 가능한 상태 관리
- 동적 API 서비스 모듈

#### [Frontend Implementation](./frontend-implementation.md)
프론트엔드 애플리케이션의 상세 구현 문서입니다.

**내용**:
- 프로젝트 개요 및 특징
- 기술 스택 및 선정 이유
- 프로젝트 구조 및 폴더 구성
- 핵심 설계 원칙 (제네릭 컴포넌트, 상태 관리, API 통합)
- 구현된 기능 상세 설명
- API 통합 가이드
- 설치 및 실행 방법
- 새로운 자산 타입 추가 방법
- 타입 시스템 및 코드 품질
- 성능 최적화 및 보안
- 트러블슈팅 가이드

### 2. 백엔드 문서

백엔드 관련 문서는 `kstock_reporter/docs/` 폴더를 참조하세요.

## 🏗️ 프로젝트 구조

```
repo/
├── kstock_reporter/          # Django 백엔드 프로젝트
│   ├── docs/                 # 백엔드 문서
│   └── ...
├── asset-frontend/           # React 프론트엔드 프로젝트
│   ├── src/
│   │   ├── components/       # 재사용 가능한 컴포넌트
│   │   ├── pages/            # 페이지 컴포넌트
│   │   ├── services/         # API 서비스
│   │   ├── store/            # 상태 관리
│   │   └── types/            # TypeScript 타입
│   └── README.md             # 프론트엔드 프로젝트 README
└── docs/                     # 전체 프로젝트 문서 (현재 위치)
    ├── README.md             # 이 파일
    ├── frontend-design-plan.md
    └── frontend-implementation.md
```

## 🚀 빠른 시작

### 백엔드 실행

```bash
cd kstock_reporter
python manage.py runserver
```

### 프론트엔드 실행

```bash
cd asset-frontend
npm install
npm run dev
```

## 📖 문서 읽는 순서

처음 프로젝트를 시작하는 경우 다음 순서로 문서를 읽는 것을 권장합니다:

1. **Frontend Design Plan** - 프론트엔드 설계 철학과 방향성 이해
2. **Frontend Implementation** - 구체적인 구현 내용 및 사용 방법 학습
3. **Backend Docs** - 백엔드 API 스펙 및 데이터 모델 확인

## 🔗 관련 링크

- [프론트엔드 프로젝트 README](../asset-frontend/README.md)
- [백엔드 프로젝트 문서](../kstock_reporter/docs/)

## 📝 문서 업데이트

문서를 업데이트할 때는 다음 사항을 준수해주세요:

- 날짜와 버전 정보 기록
- 명확하고 구체적인 설명
- 코드 예시 포함
- 마크다운 문법 준수

## ❓ 질문 및 이슈

프로젝트 관련 질문이나 이슈는 GitHub Issues를 통해 제출해주세요.

---

**최종 업데이트**: 2025-12-01
