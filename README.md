# 08-pjt · DB 설계를 활용한 REST API 설계

도서, 카테고리, 게시글(Thread), 댓글 데이터를 조회하고 게시글·댓글을 작성·수정·삭제할 수 있는 **도서 커뮤니티 REST API 서버**입니다.
Django 5.2와 Django REST Framework(DRF)로 구현했습니다.

## 목차

1. [개발 환경과 실행 방법](#1-개발-환경과-실행-방법)
2. [프로젝트 구조](#2-프로젝트-구조)
3. [주요 기능 설명](#3-주요-기능-설명)
4. [요구사항별 실행 결과](#4-요구사항별-실행-결과)
5. [Git 협업 규칙과 점검 (NF801)](#5-git-협업-규칙과-점검-nf801)
6. [학습 내용](#6-학습-내용)
7. [느낀 점](#7-느낀-점)
8. [산출물 목록](#8-산출물-목록)

---

## 1. 개발 환경과 실행 방법

| 항목 | 버전 |
|---|---|
| Python | 3.11 |
| Django | 5.2.19 |
| Django REST Framework | 3.18.3 |
| DB | SQLite3 |

```bash
# 1) 가상환경 생성 및 활성화 (Windows Git Bash 기준)
python -m venv .venv
source .venv/Scripts/activate

# 2) 패키지 설치
pip install -r requirements.txt

# 3) DB 생성 및 초기 데이터(fixture) 적재 — 관계 순서대로 불러온다
python manage.py migrate
python manage.py loaddata categories.json books.json threads.json comments.json

# 4) 서버 실행
python manage.py runserver
```

서버 실행 후 `http://127.0.0.1:8000/api/v1/categories/` 로 접속하면 됩니다.

## 2. 프로젝트 구조

```
08-pjt/
├─ manage.py
├─ requirements.txt
├─ mypjt/                  # 프로젝트 설정 (F801)
│  ├─ settings.py          # INSTALLED_APPS 에 books, rest_framework 등록
│  └─ urls.py              # api/v1/ → books.urls
├─ books/                  # 도서 커뮤니티 앱
│  ├─ models.py            # Category, Book, Thread, Comment (F802~F805)
│  ├─ serializers.py       # 요구사항별 Serializer (F806)
│  ├─ views.py             # view 함수 9개 (F807~F815)
│  ├─ urls.py              # RESTful URL (NF802)
│  ├─ migrations/
│  └─ fixtures/            # categories / books / threads / comments .json
├─ 기본제공/               # 명세서, 제공 fixture 원본
└─ 산출물/
   ├─ README.md
   └─ screenshots/         # 실행 결과 캡쳐본
```

## 3. 주요 기능 설명

### 3-1. 모델 (F802 ~ F805)

```mermaid
erDiagram
    CATEGORY ||--o{ BOOK : "N:1 (category)"
    BOOK ||--o{ THREAD : "N:1 (book)"
    THREAD ||--o{ COMMENT : "N:1 (thread)"
```

| 모델 | 필드 | 관계 |
|---|---|---|
| `Category` | `name` | - |
| `Book` | `title`, `description`, `isbn`, `cover`, `publisher`, `pub_date`, `author`, `customer_review_rank` | `category` → Category (N:1) |
| `Thread` | `title`, `content`, `reading_date`, `created_at`, `updated_at` | `book` → Book (N:1, `related_name='threads'`) |
| `Comment` | `content`, `created_at`, `updated_at` | `thread` → Thread (N:1, `related_name='comments'`) |

- 모든 외래 키는 `on_delete=CASCADE` 입니다. 게시글을 삭제하면 그 게시글의 댓글도 함께 삭제됩니다.
- 제공된 fixture의 키가 소문자 `isbn` 이어서 필드명도 `isbn` 으로 맞췄습니다.
- 모델 하나를 만들 때마다 마이그레이션 파일을 하나씩 만들었습니다 (`0001_initial` ~ `0004_comment`).

### 3-2. API 명세 (F807 ~ F815, NF802, NF803)

모든 URL은 `/api/v1/` 아래에 있습니다. 자원은 복수형 명사로 쓰고, 행위는 HTTP method로 구분했습니다.

| 요구사항 | Method | URL | view 함수 | 성공 | 실패 |
|---|---|---|---|---|---|
| F807 | GET | `/categories/` | `category_list` | 200 | 405 |
| F808 | GET | `/books/` | `book_list` | 200 | 405 |
| F809 | GET | `/books/<book_pk>/` | `book_detail` | 200 | 404, 405 |
| F810 | GET | `/threads/` | `thread_list` | 200 | 405 |
| F811 | GET | `/threads/<thread_pk>/` | `thread_detail` | 200 | 404 |
| F811 | PUT | `/threads/<thread_pk>/` | `thread_detail` | 200 | 400, 404 |
| F811 | DELETE | `/threads/<thread_pk>/` | `thread_detail` | 204 | 404 |
| F812 | POST | `/books/<book_pk>/threads/` | `create_thread` | 201 | 400, 404, 405 |
| F813 | POST | `/threads/<thread_pk>/comments/` | `create_comment` | 201 | 400, 404, 405 |
| F814 | GET | `/comments/<comment_pk>/` | `comment_detail` | 200 | 404 |
| F814 | PUT | `/comments/<comment_pk>/` | `comment_detail` | 200 | 400, 404 |
| F814 | DELETE | `/comments/<comment_pk>/` | `comment_detail` | 204 | 404 |
| F815 | GET | `/books/search/?q=<검색어>` | `book_search` | 200 | 405 |

- **RESTful URL (NF802)**: 게시글은 "어떤 도서의 게시글"이므로 `/books/<book_pk>/threads/` 에, 댓글은 "어떤 게시글의 댓글"이므로 `/threads/<thread_pk>/comments/` 에 POST 합니다. 대상 도서·게시글은 요청 본문이 아니라 URL로 판별합니다.
- **허용 method 제한 (NF803)**: 모든 view에 `@api_view([...])` 로 허용 method를 명시했습니다. 허용하지 않은 method는 DRF가 `405 Method Not Allowed` 와 `Allow` 헤더를 응답합니다.
- **유효성 검증**: `serializer.is_valid(raise_exception=True)` 로 검증하고, 실패하면 `400 Bad Request` 와 필드별 오류 메시지를 응답합니다.
- **없는 자원**: `get_object_or_404` 로 조회해서 없으면 `404 Not Found` 를 응답합니다.
- **삭제 응답**: 명세서 예시와 같이 `204 No Content` 와 `{"message": "thread 1 is deleted."}` 형태의 메시지를 응답합니다.

### 3-3. Serializer (F806)

명세의 응답 예시와 필드 구성·순서가 같도록 view마다 필요한 Serializer를 나눠 만들었습니다.

| Serializer | 사용하는 곳 | 응답 필드 |
|---|---|---|
| `CategorySerializer` | `category_list`, 도서 상세의 `category` | `id`, `name` |
| `BookListSerializer` | `book_list`, `book_search` | `id`, `title`, `author`, `isbn`, `cover` |
| `BookThreadSerializer` | 도서 상세의 `threads` | `id`, `title`, `content`, `reading_date` |
| `BookSerializer` | `book_detail` | 도서 전체 필드 + `category`, `threads`, `num_of_threads` |
| `BookTitleSerializer` | 게시글 응답의 `book` | `title` |
| `ThreadListSerializer` | `thread_list` | `id`, `title`, `book` |
| `ThreadTitleSerializer` | 댓글 응답의 `thread` | `title` |
| `CommentSerializer` | `create_comment`, `comment_detail`, 게시글 상세의 `comments` | 댓글 전체 필드 + `thread` |
| `ThreadDetailSerializer` | `thread_detail` | 게시글 전체 필드 + `book`, `comments`, `num_of_comments` |
| `ThreadSerializer` | `create_thread` | 게시글 전체 필드 + `book` |

- 중첩 Serializer(`book`, `thread`, `category`, `threads`, `comments`)는 모두 `read_only=True` 입니다. 그래서 게시글 작성·수정 시에는 `title`, `content`, `reading_date` 만, 댓글은 `content` 만 보내면 됩니다.
- 개수 필드는 `serializers.IntegerField(source='threads.count', read_only=True)` 처럼 역참조 매니저의 `count` 를 사용했습니다.
- 외래 키 값은 view에서 `serializer.save(book=book)`, `serializer.save(thread=thread)` 로 넣습니다.

### 3-4. 도서 검색 (F815, 심화)

- `GET /api/v1/books/search/?q=검색어`
- 검색어는 자원의 위치가 아니라 조회 조건이므로 URL 경로가 아닌 **쿼리 스트링**으로 받습니다 (`request.query_params.get('q')`).
- 제목 또는 작가에 검색어가 포함된 도서를 찾습니다: `Q(title__icontains=query) | Q(author__icontains=query)`
- 검색어가 없거나 공백뿐이면 `{"message": "검색어를 입력해주세요."}` 를 응답합니다.
- 검색 결과가 없으면 빈 배열 `[]` 을 응답합니다.

## 4. 요구사항별 실행 결과

브라우저 화면은 DRF가 제공하는 Browsable API 페이지입니다. POST·PUT·DELETE 요청은 이 페이지의 입력 폼과 DELETE 버튼으로 보냈습니다.

### F801 · 프로젝트 구성

프로젝트 `mypjt`, 앱 `books` 를 만들고 `rest_framework` 를 등록했습니다.

![F801](산출물/screenshots/F801_project_setup.png)

### F802 ~ F805 · Model 클래스와 fixture 적재

마이그레이션 4개 적용 후 fixture 104건(카테고리 7, 도서 70, 게시글 9, 댓글 18)을 불러온 결과입니다.

![F802-F805](산출물/screenshots/F802-F805_models_migrate_loaddata.png)

### F806 · Serializer 유효성 검증

`content` 가 없고 `reading_date` 형식이 잘못된 데이터로 게시글을 작성하면 `400 Bad Request` 와 필드별 오류를 응답합니다.

![F806](산출물/screenshots/F806_serializer_validation_400.png)

### F807 · category_list

![F807](산출물/screenshots/F807_category_list.png)

### F808 · book_list

![F808](산출물/screenshots/F808_book_list.png)

### F809 · book_detail

도서 정보와 함께 카테고리, 게시글 목록(`id`, `title`, `content`, `reading_date`), 게시글 개수를 응답합니다.

![F809](산출물/screenshots/F809_book_detail.png)

### F810 · thread_list

![F810](산출물/screenshots/F810_thread_list.png)

### F811 · thread_detail

**GET** — 게시글과 함께 대상 도서, 댓글 목록, 댓글 개수를 응답합니다.

![F811 GET](산출물/screenshots/F811_thread_detail_GET.png)

**PUT** — 제목과 독서일을 수정했습니다. `updated_at` 만 바뀌고 `created_at` 은 그대로입니다.

![F811 PUT](산출물/screenshots/F811_thread_detail_PUT.png)

**DELETE**

![F811 DELETE](산출물/screenshots/F811_thread_detail_DELETE.png)

### F812 · create_thread

**GET 등 그 외 method** — `405` 를 응답하고, 브라우저에서는 데이터를 입력할 수 있는 폼이 함께 표시됩니다.

![F812 405](산출물/screenshots/F812_create_thread_GET_405.png)

**POST** — `201 Created`

![F812 POST](산출물/screenshots/F812_create_thread_POST_201.png)

### F813 · create_comment

**GET 등 그 외 method** — `405`

![F813 405](산출물/screenshots/F813_create_comment_GET_405.png)

**POST** — 방금 만든 게시글에 댓글을 작성했습니다. `201 Created`

![F813 POST](산출물/screenshots/F813_create_comment_POST_201.png)

### F814 · comment_detail

**GET** — 댓글과 함께 대상 게시글의 제목을 응답합니다.

![F814 GET](산출물/screenshots/F814_comment_detail_GET.png)

**PUT**

![F814 PUT](산출물/screenshots/F814_comment_detail_PUT.png)

**DELETE**

![F814 DELETE](산출물/screenshots/F814_comment_detail_DELETE.png)

### F815 · 도서 검색 (심화)

**제목으로 검색** — `?q=데미안`

![F815 제목](산출물/screenshots/F815_book_search_title.png)

**작가로 검색** — `?q=한강`

![F815 작가](산출물/screenshots/F815_book_search_author.png)

**검색어 없음** — `?q=`

![F815 빈 검색어](산출물/screenshots/F815_book_search_empty.png)

### F807 ~ F814 공통 · API 클라이언트 요청 시 JSON 응답

같은 URL이라도 브라우저가 아닌 API 클라이언트(curl)로 요청하면 `Content-Type: application/json` 으로 응답합니다. 없는 자원을 요청하면 `404 Not Found` 를 응답합니다.

![API 클라이언트 JSON 응답](산출물/screenshots/F807-F814_api_client_json_curl.png)

### NF803 · 허용하지 않은 method 차단

허용하지 않은 method로 요청하면 `405 Method Not Allowed` 와 허용 method 목록(`Allow` 헤더)을 응답합니다.

![NF803](산출물/screenshots/NF803_method_not_allowed_curl.png)

## 5. Git 협업 규칙과 점검 (NF801)

### 5-1. 브랜치 생성 원칙 (Git Flow 간소화)

```
master   ← 제출용. 직접 커밋 금지. develop에서만 병합
develop  ← 통합 브랜치. 모든 작업 브랜치의 출발점이자 병합 대상
feature/F8xx-<요약>  ← 요구사항 1개 = 브랜치 1개
fix/F8xx-<요약>      ← develop에 병합된 기능의 버그 수정
docs/<요약>          ← README 등 문서 작업
chore/<요약>         ← .gitignore, requirements.txt 등 설정
```

- 브랜치 이름은 소문자와 하이픈만 사용하고, 요구사항 번호는 대문자 그대로 씁니다. 예: `feature/F807-category-list`
- 선행 요구사항이 develop에 병합된 뒤에, **최신 develop에서** 새 브랜치를 만듭니다.
- 병합은 `git merge --no-ff` 로 해서 브랜치 단위의 이력이 그래프에 남게 합니다.
- F806(Serializer)은 별도 브랜치 없이, 그 Serializer를 사용하는 view 브랜치에서 함께 작성합니다. NF802·NF803도 각 view 브랜치에서 함께 지킵니다.

### 5-2. 커밋 기록 원칙

- 형식: `<type>(<요구사항번호>): <요구사항명> 구현` — 예: `feat(F807): category_list 구현`
- type: `feat`(기능), `fix`(버그 수정), `refactor`(동작 변화 없는 정리), `docs`(문서), `chore`(설정), `test`(테스트)
- 요구사항 번호가 없는 작업은 괄호를 생략합니다. 예: `chore: .gitignore, requirements.txt 추가`
- 커밋 시점: 모델 1개 + migrate 성공, 또는 view 1개 + URL + Serializer 동작 확인처럼 **동작하는 의미 단위**가 완성됐을 때만 커밋합니다.

### 5-3. 생성한 브랜치와 용도

| 브랜치 | 용도 | 커밋 |
|---|---|---|
| `master` | 제출용 | - |
| `develop` | 통합 | 병합 커밋만 존재 |
| `chore/gitignore-requirements` | `.gitignore`, `requirements.txt` | `chore: .gitignore, requirements.txt 추가` |
| `feature/F801-project-setup` | 프로젝트 `mypjt`, 앱 `books`, DRF 설정 | `feat(F801): 프로젝트 구성` |
| `feature/F802-category-model` | Category 모델, 카테고리 fixture | `feat(F802): Category 클래스 구현` |
| `feature/F803-book-model` | Book 모델, 도서 fixture | `feat(F803): Book 클래스 구현` |
| `feature/F804-thread-model` | Thread 모델, 게시글 fixture | `feat(F804): Thread 클래스 구현` |
| `feature/F805-comment-model` | Comment 모델, 댓글 fixture, 전체 적재 확인 | `feat(F805): Comment 클래스 구현` |
| `feature/F807-category-list` | 카테고리 목록 조회 | `feat(F807): category_list 구현` |
| `feature/F808-book-list` | 도서 목록 조회 | `feat(F808): book_list 구현` |
| `feature/F809-book-detail` | 도서 상세 조회 | `feat(F809): book_detail 구현` |
| `feature/F810-thread-list` | 게시글 목록 조회 | `feat(F810): thread_list 구현` |
| `feature/F811-thread-detail` | 게시글 조회·수정·삭제 | `feat(F811): thread_detail 구현` |
| `feature/F812-create-thread` | 게시글 작성 | `feat(F812): create_thread 구현` |
| `feature/F813-create-comment` | 댓글 작성 | `feat(F813): create_comment 구현` |
| `feature/F814-comment-detail` | 댓글 조회·수정·삭제 | `feat(F814): comment_detail 구현` |
| `feature/F815-book-search` | 도서 검색 (심화) | `feat(F815): 도서 검색 구현` |
| `docs/readme-deliverables` | README, 실행 결과 캡쳐본 | `docs: 실행 결과 캡쳐본 추가`, `docs: README 작성` |

### 5-4. 원칙 점검

| 원칙 | 결과 | 비고 |
|---|---|---|
| master 직접 커밋 금지 | 지킴 | 규칙을 정한 뒤로 master에는 직접 커밋하지 않았습니다 |
| 요구사항 1개 = 브랜치 1개 | 지킴 | F801~F805, F807~F815 가 각각 브랜치 1개 |
| 최신 develop에서 브랜치 생성 | 지킴 | 앞 브랜치를 병합한 뒤 다음 브랜치를 만들었습니다 |
| `--no-ff` 병합 | 지킴 | 브랜치마다 병합 커밋이 1개씩 남았습니다 |
| 커밋 메시지 형식 | 대체로 지킴 | 규칙을 정하기 전의 초기 커밋(`feat:기본제공 폴더추가` 등)은 형식이 다릅니다 |
| 동작하는 상태에서만 커밋 | 지킴 | 커밋 전에 `check`, `migrate`, 실제 요청으로 응답을 확인했습니다 |

**브랜치 운영 중 문제 상황과 원인 분석**

- 병합 충돌은 발생하지 않았습니다.
- 다만 view 브랜치(F807~F815)는 모두 `views.py`, `serializers.py`, `urls.py` 세 파일의 같은 위치(import 구문, `urlpatterns`)를 수정합니다. 같은 develop 커밋에서 여러 브랜치를 동시에 만들었다면 병합할 때 이 위치에서 충돌이 났을 구조입니다.
- "앞 브랜치를 develop에 병합한 뒤, 최신 develop에서 다음 브랜치를 만든다"는 원칙 덕분에 충돌 없이 진행됐습니다. 여러 명이 동시에 작업한다면 view별로 파일을 나누거나, 병합 전에 develop을 먼저 받아 충돌을 브랜치 안에서 해결하는 절차가 필요합니다.

### 5-5. 커밋 내역

`git log --graph` 로 확인한 develop 브랜치의 이력입니다.

![git log](산출물/screenshots/NF801_git_log_graph.png)

> GitLab 커밋 화면 캡쳐는 원격 저장소에 push 한 뒤 이 위치에 추가합니다.

## 6. 학습 내용

**DRF와 HTTP**

- `@api_view(['GET', 'PUT', 'DELETE'])` 처럼 허용 method를 적어 두면, 그 외 method는 view 코드가 실행되기 전에 DRF가 405로 막아 줍니다.
- 같은 view라도 요청의 `Accept` 헤더에 따라 응답 형식이 달라집니다. 브라우저에는 HTML(Browsable API)을, curl·Postman 같은 API 클라이언트에는 JSON을 응답합니다.
- 상태 코드를 목적에 맞게 구분했습니다: 조회·수정 200, 생성 201, 삭제 204, 검증 실패 400, 없는 자원 404, 허용하지 않은 method 405.
- `204 No Content` 는 원래 본문이 없는 응답입니다. 명세 예시대로 메시지를 담아 응답하면 Browsable API에서는 보이지만 curl에서는 본문이 출력되지 않았습니다. 응답 헤더의 `Content-Length` 는 34로 내려오는 것을 보고, 클라이언트가 204의 본문을 읽지 않는다는 것을 알았습니다.

**N:1 관계와 Serializer**

- `ForeignKey` 에 `related_name` 을 주면 역참조 이름이 정해집니다. `book.threads`, `thread.comments` 로 접근했고, 이 이름을 Serializer 필드명으로 그대로 써서 응답 키(`threads`, `comments`)를 맞췄습니다.
- `fields = '__all__'` 일 때 응답 순서는 `id` → Serializer에 직접 선언한 필드 → 나머지 모델 필드 순입니다. 선언 순서를 맞추는 것만으로 명세 예시와 같은 순서가 나왔습니다.
- 외래 키를 `read_only` 중첩 Serializer로 선언하면 입력 검증 대상에서 빠집니다. 그래서 값은 view에서 `serializer.save(book=book)` 으로 직접 넣어야 합니다.
- 같은 모델이라도 응답 모양이 다르면 Serializer를 나눠야 합니다. 게시글은 목록용, 상세용, 작성용 세 가지를 만들었습니다.
- 이번 명세에는 N:M 관계가 필요한 요구사항이 없어서 N:1 관계만 구현했습니다.

**Fixture**

- fixture는 참조되는 쪽부터 불러와야 합니다: `categories → books → threads → comments`.
- `auto_now_add`, `auto_now` 필드도 `loaddata` 로 넣을 때는 fixture에 적힌 값이 그대로 저장됩니다. 반면 API로 수정하면 `updated_at` 이 현재 시각으로 바뀝니다.
- 명세서에는 `ISBN` 으로 적혀 있지만 fixture의 키는 `isbn` 이었습니다. 모델 필드명은 fixture와 일치해야 적재됩니다.

**RESTful URL 설계**

- URL에는 자원(명사)만 쓰고 행위는 method로 표현합니다. `create_thread` 라는 view 이름이 URL에 드러나지 않습니다.
- 하위 자원을 만들 때는 상위 자원의 경로 아래에 POST 합니다 (`/books/1/threads/`).
- 검색어처럼 조회 조건을 바꾸는 값은 쿼리 스트링으로 받습니다.

**환경 설정**

- 가상환경 폴더는 내부 스크립트에 경로가 기록돼 있어서 폴더 이름만 바꾸면 동작하지 않습니다. 이름을 바꾸려면 새로 만들어야 합니다.

## 7. 느낀 점

- 명세서의 응답 예시와 필드 순서까지 똑같이 맞추려다 보니, Serializer가 단순히 "모델을 JSON으로 바꾸는 도구"가 아니라 응답의 모양을 설계하는 곳이라는 것을 알게 됐습니다. 같은 Thread 모델인데도 목록, 상세, 작성 응답이 모두 달라서 Serializer를 세 개로 나눈 것이 기억에 남습니다.
- 요구사항 하나에 브랜치 하나를 만드는 방식은 처음에는 번거롭게 느껴졌지만, `git log --graph` 로 보니 어떤 기능이 언제 들어왔는지 한눈에 보여서 규칙을 정해 두는 이유를 이해했습니다.
- 충돌이 한 번도 나지 않았지만, 그 이유가 순서대로 작업했기 때문이라는 점을 정리하면서 여러 명이 동시에 작업할 때는 같은 파일을 고치는 구조 자체가 위험하다는 것을 알았습니다.
- 204 응답에 메시지를 담아도 curl에서는 보이지 않는 것을 직접 확인하면서, 상태 코드마다 약속된 의미가 있고 클라이언트도 그 약속대로 동작한다는 것을 실감했습니다.

## 8. 산출물 목록

| 산출물 | 위치 |
|---|---|
| 구현 소스 코드 | 저장소 루트 (`manage.py`, `mypjt/`, `books/`, `requirements.txt`) |
| 실행 결과 캡쳐본 | [`산출물/screenshots/`](산출물/screenshots/) |
| README.md | `산출물/README.md` (저장소 루트의 `README.md` 와 같은 내용) |
