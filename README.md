# AZA Fullstack Project

이 프로젝트는 FastAPI 및 Flask를 백엔드로, React 및 CSS를 프론트엔드로 사용하는 풀스택 애플리케이션입니다.
백엔드는 고성능 비동기 API를 위한 FastAPI와 간단한 웹 페이지와 RESTful API를 위한 Flask로 나뉩니다. MongoDB를 데이터베이스로 사용합니다.

## 프로젝트 구조

### 백엔드 구조

#### `fastapi_app/`
- **`__init__.py`**: FastAPI 앱 초기화 파일.
- **`crud.py`**: 데이터베이스와 상호작용하는 함수 (Create, Read, Update, Delete) 저장 파일.
- **`database.py`**: MongoDB 데이터베이스 연결 및 관련 함수.
- **`main.py`**: FastAPI 앱의 진입점.
- **`models.py`**: 요청 및 응답 본문을 위한 Pydantic 모델.
- **`routers/`**
  - **`__init__.py`**: 라우터 초기화 파일.
  - **`item_router.py`**: 아이템 관련 엔드포인트를 위한 라우터.
- **`schemas.py`**: 데이터 검증 및 직렬화를 위한 스키마.
- **`utils.py`**: 유틸리티 함수들.

#### `flask_app/`
- **`__init__.py`**: Flask 앱 초기화 파일.
- **`routes.py`**: 웹 요청을 처리하는 라우트.
- **`server.py`**: Flask 앱의 진입점.
- **`models.py`**: 데이터베이스 모델 및 스키마 정의.
- **`templates/`**: 웹 페이지 렌더링을 위한 HTML 템플릿.
  - **`base.html`**: 기본 템플릿.
  - **`dashboard.html`**: 대시보드 페이지 템플릿.
  - **`login.html`**: 로그인 페이지 템플릿.
- **`static/`**: 정적 파일들 (CSS, JS, 이미지).
  - **`style.css`**: 스타일링을 위한 CSS 파일.
- **`utils.py`**: 유틸리티 함수들.

### 프론트엔드 구조

#### `public/`
- **`index.html`**: React 앱을 위한 메인 HTML 파일.

#### `src/`
- **`components/`**
  - **`Header.js`**: 헤더 컴포넌트.
  - **`Footer.js`**: 푸터 컴포넌트.
  - **`Home.js`**: 홈 컴포넌트.
  - **`App.js`**: 메인 애플리케이션 컴포넌트.
- **`styles/`**
  - **`App.css`**: React 앱을 위한 스타일링 CSS 파일.
- **`App.js`**: 메인 애플리케이션 컴포넌트.
- **`index.js`**: React 앱의 진입점.
- **`setupProxy.js`**: API 호출을 위한 프록시 설정.

