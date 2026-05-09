# Testing Workflow

**Base URL:** `https://videos-explaining-spare-alleged.trycloudflare.com/`

---

## 1. Authentication (Admin)

### Login
```
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}
```
**Expected:** Returns `access` and `refresh` tokens.

### Use in all subsequent requests:
```
Authorization: Bearer <access_token>
```

---

## 2. Categories & Habits (Mobile User Flow)

### User Flow (Mobile / App):
```
Step 1: Get all categories
       ↓
Step 2: User picks a category
       ↓
Step 3: GET prebuilt habits under that category
       ↓
Step 4: User selects a prebuilt habit OR creates a custom habit
         - Free user: max 3 total habits (combined custom + adopted)
         - Pro user: unlimited
       ↓
Step 5: Habit is added to user's personal list
       ↓
Step 6: User marks habit done (Pro only, 3/day limit)
       ↓
Step 7: Check daily status
```

### List Categories (User)
```
GET /api/categories/
Authorization: Bearer <token>
```

### List Prebuilt Habits by Category (User)
```
GET /api/habit-templates/?category=1
Authorization: Bearer <token>
```
**Returns:** Array of `HabitTemplate` objects with `id`, `activity_name`, `description`, `duration`.

### Create Habit from Template (User)
```
POST /api/habits/
Authorization: Bearer <token>
Content-Type: application/json

{
  "template_id": 1
}
```
**Expected:** Copies template data (category, name, desc, duration) into user's own habit. Free users limited to 3 total habits. Pro users unlimited.

### Create Custom Habit (User)
```
POST /api/habits/
Authorization: Bearer <token>
Content-Type: application/json

{
  "category": 1,
  "activity_name": "Morning Run",
  "description": "Run 5km",
  "duration": 30
}
```
**Expected:** Free users can create up to 3 habits. Pro users unlimited.

### Mark Habit Done (Pro only, max 3/day across ALL categories)
```
POST /api/habits/1/done/
Authorization: Bearer <token>
```
**Expected:**
- 403 if user is not Pro
- 201 if successful
- 400 if daily limit (3) already reached

### Undo Habit Done
```
DELETE /api/habits/1/undo/
Authorization: Bearer <token>
```

### Check Daily Status
```
GET /api/habits/daily-status/
Authorization: Bearer <token>
```
**Expected:** Returns `daily_completions`, `daily_completion_limit: 3`, `remaining`.

---

## 3. Subjects (Admin Upload)

### List Topics (Subjects)
```
GET /api/study/topics/
Authorization: Bearer <token>
```

### Create Topic (Admin)
```
POST /api/admin/study/topics/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "title": "Mathematics",
  "description": "Basic math concepts",
  "is_active": true
}
```
**Or via frontend:** `/subject-uploads` page → Upload Book modal.

---

## 4. Study Materials (PDF Upload)

### Create Material with PDF (Admin)
```
POST /api/admin/study/materials/
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data

- topic: 1
- title: "Algebra Notes"
- description: "Chapter 1 notes"
- material_type: pdf
- pdf: <file.pdf>
- is_active: true
```
**Note:** Use `multipart/form-data` when uploading `pdf` file.

### List Materials (Admin)
```
GET /api/admin/study/materials/
Authorization: Bearer <admin_token>
```

### View Material Detail (User)
```
GET /api/study/materials/1/
Authorization: Bearer <token>
```

---

## 5. Quiz (Subjects → Quizzes)

### Create Quiz (Admin)
```
POST /api/admin/study/quizzes/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "topic": 1,
  "title": "Math Quiz 1",
  "description": "Basic algebra",
  "is_active": true
}
```

### Add Questions (Admin)
```
POST /api/admin/study/questions/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "quiz": 1,
  "text": "What is 2+2?",
  "option_a": "3",
  "option_b": "4",
  "option_c": "5",
  "option_d": "6",
  "correct_option": "B",
  "order": 1
}
```

### Take Quiz (User)
```
GET /api/study/quizzes/1/
Authorization: Bearer <token>
```
**Returns:** Quiz with questions (correct answers hidden).

### Submit Quiz (User)
```
POST /api/study/quizzes/submit/
Authorization: Bearer <token>
Content-Type: application/json

{
  "quiz_id": 1,
  "answers": [
    {"question_id": 1, "selected_option": "B"}
  ]
}
```
**Expected:** Returns score, percentage, and per-answer results. All attempts are saved.

### View Quiz History by Topic (User)
```
GET /api/study/attempts/by-topic/
Authorization: Bearer <token>
```
**Expected:** Returns all topics where user has attempts, with nested quiz history.

### View All Attempts (User)
```
GET /api/study/attempts/?topic=1
Authorization: Bearer <token>
```

### View All Attempts (Admin)
```
GET /api/admin/study/attempts/?quiz=1
Authorization: Bearer <admin_token>
```

---

## 6. Admin Habit Template Management

### Create Prebuilt Habit (Admin)
```
POST /api/admin/habit-templates/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "category": 1,
  "activity_name": "Morning Meditation",
  "description": "10 minutes mindfulness",
  "duration": 10,
  "is_active": true
}
```

### List Prebuilt Habits (Admin)
```
GET /api/admin/habit-templates/?category=1&search=meditation
Authorization: Bearer <admin_token>
```

### Update Prebuilt Habit (Admin)
```
PATCH /api/admin/habit-templates/1/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "activity_name": "Evening Meditation",
  "duration": 15
}
```

### Delete Prebuilt Habit (Admin)
```
DELETE /api/admin/habit-templates/1/
Authorization: Bearer <admin_token>
```

---

## 7. API Documentation (Swagger)

**Open in browser:**
```
https://videos-explaining-spare-alleged.trycloudflare.com/api/docs/
```

---

## Verified Logic Summary

| Feature | Status | Details |
|---------|--------|---------|
| Category system | ✅ Exists | Admin-managed categories |
| Habit creation limit | ✅ Exists | Free: 3 max, Pro: unlimited |
| Habit done limit | ✅ Exists | Pro only, 3/day across all categories |
| Prebuilt habit templates | ✅ Implemented | Admin creates via `/habits` page + `/api/admin/habit-templates/` |
| User adopts template | ✅ Implemented | `POST /api/habits/` with `template_id` copies template data |
| Subject upload (admin) | ✅ Exists | `Subject Uploads` page + `/api/admin/study/topics/` |
| Quiz under topic | ✅ Exists | `Quiz` linked to `StudyTopic` |
| Quiz attempts persist | ✅ Exists | `QuizAttempt` + `QuizAnswer` models keep all history |
| Quiz results by topic | ✅ Exists | `GET /api/study/attempts/by-topic/` |
| Study scoring | ✅ Removed | Nav item removed per request |
| Study material PDF upload | ✅ Implemented | Separate `pdf` field in model + file upload in modal |
| Admin Habits page | ✅ Implemented | New `/habits` page in admin panel with category filter |
