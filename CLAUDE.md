# 08-pjt 작업 규칙 (AI 에이전트용)

Django 5.2 + DRF 기반 도서 커뮤니티 REST API 서버 (프로젝트 `mypjt`, 앱 `books`).
요구사항 명세: `기본제공/(26_1113) 관통템플릿_Python_16기_8회차.pdf`, 초기 데이터: `기본제공/skeleton/fixtures/`.

## 브랜치 전략 (Git Flow 간소화)

```
master   ← 제출용. 직접 커밋 금지. develop에서만 병합.
develop  ← 통합 브랜치. 모든 feature 브랜치의 출발점이자 병합 대상.
feature/F8xx-<요약>  ← 요구사항 1개 = 브랜치 1개
fix/F8xx-<요약>      ← 이미 develop에 병합된 기능의 버그 수정
docs/<요약>          ← README 등 문서 작업
chore/<요약>         ← .gitignore, requirements.txt 등 설정
```

### 이름 규칙
- 소문자 + 하이픈(kebab-case), 영어만 사용. 한글·공백·언더스코어 금지.
- 요구사항 번호는 대문자 그대로 (`F807`), 그 뒤에 view/모델 이름을 하이픈으로.
- 예: `feature/F807-category-list`, `fix/F811-thread-put-validation`

### 요구사항 ↔ 브랜치 매핑
작업 요청을 받으면 아래 표에서 해당 브랜치 이름을 그대로 사용한다.

| 번호 | 내용 | 브랜치 | 선행 브랜치 |
|---|---|---|---|
| F801 | 프로젝트 `mypjt`, 앱 `books` 생성, DRF 설정 | `feature/F801-project-setup` | - |
| F802 | Category 모델 | `feature/F802-category-model` | F801 |
| F803 | Book 모델 (Category N:1) | `feature/F803-book-model` | F802 |
| F804 | Thread 모델 (Book N:1) | `feature/F804-thread-model` | F803 |
| F805 | Comment 모델 (Thread N:1) + fixture 로드 확인 | `feature/F805-comment-model` | F804 |
| F807 | category_list (GET) | `feature/F807-category-list` | F805 |
| F808 | book_list (GET) | `feature/F808-book-list` | F805 |
| F809 | book_detail (GET, 카테고리·게시글 목록·게시글 수) | `feature/F809-book-detail` | F805 |
| F810 | thread_list (GET, 도서 제목 포함) | `feature/F810-thread-list` | F805 |
| F811 | thread_detail (GET/PUT/DELETE) | `feature/F811-thread-detail` | F805 |
| F812 | create_thread (POST, 그 외 405) | `feature/F812-create-thread` | F805 |
| F813 | create_comment (POST, 그 외 405) | `feature/F813-create-comment` | F805 |
| F814 | comment_detail (GET/PUT/DELETE) | `feature/F814-comment-detail` | F805 |
| F815 | 도서 검색 (제목·작가, 심화) | `feature/F815-book-search` | F808 |

- **F806(Serializer)는 별도 브랜치를 만들지 않는다.** 각 view 브랜치에서 그 view에 필요한 Serializer를 함께 작성한다.
- **NF802(RESTful URL), NF803(허용 Method 제한)** 은 각 view 브랜치에서 함께 지킨다.
- 선행 브랜치가 develop에 병합되지 않았으면 작업을 시작하지 말고 사용자에게 알린다.
- 표에 없는 추가 기능은 `feature/<요약>` 형식으로 만들고, 만들기 전에 이름을 사용자에게 확인받는다.

### 작업 절차
1. `develop`이 없으면 `master`에서 생성한다: `git switch -c develop master`
2. 최신 develop에서 브랜치 생성: `git switch develop` → `git switch -c feature/F8xx-...`
3. 해당 요구사항 범위만 구현한다. 다른 요구사항 코드는 건드리지 않는다.
4. 커밋 (아래 커밋 규칙).
5. 사용자가 확인/승인하면 develop에 병합: `git switch develop` → `git merge --no-ff feature/F8xx-...`
   - `--no-ff`로 병합 기록을 남긴다 (README에 브랜치 이력 정리 필요 - NF801).
6. 충돌·문제 발생 시 임의로 해결하지 말고, **원인 분석**을 사용자에게 먼저 보고한다 (NF801 요구사항).
7. `git push`, master 병합, 브랜치 삭제는 사용자가 명시적으로 요청할 때만 한다.

## 커밋 규칙

형식: `<type>(<요구사항번호>): <한글 요약>`

| type | 용도 |
|---|---|
| feat | 기능 추가 |
| fix | 버그 수정 |
| refactor | 동작 변화 없는 코드 정리 |
| docs | README 등 문서 |
| chore | 설정, 패키지, .gitignore |
| test | 테스트 |

- 예: `feat(F807): category_list 조회 API 구현`, `fix(F811): PUT 요청 시 유효성 검증 누락 수정`
- 요구사항 번호가 없는 작업은 괄호 생략: `chore: .gitignore 추가`
- 커밋 시점: 모델 1개 완성 + migrate 성공 / view 1개 + URL + Serializer 동작 확인 시 등 **의미 있는 단위로 동작하는 상태**에서 커밋한다. 동작하지 않는 코드는 커밋하지 않는다.

## 기타
- `.gitignore`에 `__pycache__/`, `*.pyc`, `db.sqlite3`, `venv/`, `.venv/`, `.env` 포함.
- 각 view는 DRF `@api_view`로 허용 method를 명시한다 (NF803).
