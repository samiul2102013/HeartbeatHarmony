# Study Materials & Quizzes — User Testing Workflow

## Overview

**Data model:**
- `StudyTopic` (Subject) → has many `StudyMaterial`s
- `StudyTopic` → has many `Quiz`es
- `Quiz` → has many `Question`s (MCQ, 4 options A-D)

**User capabilities:**
- Browse subjects → view materials inside each → read/download them
- Mark materials as completed (progress tracking)
- Take quizzes → get instant score + per-answer feedback
- View quiz history grouped by subject

---

## 1. List Subjects (Study Topics)

**GET** `https://<host>/api/study/topics/`

**Headers:**
```
Authorization: Bearer <user_access_token>
Content-Type: application/json
```

**Expected response (flat array, no pagination):**
```json
[
  {
    "id": 1,
    "title": "Nutrition Basics",
    "description": "Learn about healthy eating.",
    "thumbnail": "https://<host>/media/study/thumbnails/nutrition.jpg",
    "material_count": 5,
    "completed_count": 2,
    "created_at": "2026-05-01T10:00:00Z"
  }
]
```

**Note:** `completed_count` is the number of materials this user has already marked done.

---

## 2. Get Subject Detail (Materials + Quizzes)

**GET** `https://<host>/api/study/topics/1/`

**Expected response:**
```json
{
  "id": 1,
  "title": "Nutrition Basics",
  "description": "Learn about healthy eating.",
  "thumbnail": "...",
  "material_count": 5,
  "completed_count": 2,
  "materials": [
    {
      "id": 101,
      "title": "Macronutrients Guide",
      "description": "Overview of proteins, carbs, fats.",
      "material_type": "pdf",
      "file": "https://<host>/media/study/materials/guide.pdf",
      "pdf": null,
      "video_url": "",
      "is_completed": false,
      "created_at": "2026-05-01T10:00:00Z"
    },
    {
      "id": 102,
      "title": "Meal Prep Video",
      "description": "Quick healthy recipes.",
      "material_type": "video",
      "file": null,
      "pdf": null,
      "video_url": "https://youtube.com/watch?v=abc123",
      "is_completed": true,
      "created_at": "2026-05-02T10:00:00Z"
    }
  ],
  "created_at": "2026-05-01T10:00:00Z"
}
```

**How to use:**
- **PDF material:** open the `file` or `pdf` URL in a viewer / download it
- **Video material:** open `video_url` in a video player or WebView
- **Text material:** `file` will contain the text content (or read from backend directly)
- `is_completed` = true means user already marked this as read

---

## 3. Mark Material as Completed

**POST** `https://<host>/api/study/materials/complete/`

**Headers:**
```
Authorization: Bearer <user_access_token>
Content-Type: application/json
```

**Body:**
```json
{
  "material_id": 101
}
```

**Expected response:**
```json
{
  "success": true,
  "data": {
    "detail": "Material marked as complete.",
    "created": true
  }
}
```

Call this after the user finishes reading a PDF or watches a video.

---

## 4. List Available Quizzes

**GET** `https://<host>/api/study/quizzes/`

**Headers:**
```
Authorization: Bearer <user_access_token>
```

**Expected response (flat array):**
```json
[
  {
    "id": 10,
    "title": "Nutrition Quiz 1",
    "description": "Test your knowledge on macros.",
    "question_count": 5,
    "last_score": {
      "score": 4,
      "total": 5,
      "percentage": 80.0
    },
    "created_at": "2026-05-01T10:00:00Z"
  }
]
```

`last_score` = user's most recent attempt (null if never taken).

---

## 5. Get Quiz Questions (Take Quiz)

**GET** `https://<host>/api/study/quizzes/10/`

**Expected response (correct answers HIDDEN):**
```json
{
  "id": 10,
  "topic": 1,
  "title": "Nutrition Quiz 1",
  "description": "Test your knowledge on macros.",
  "question_count": 5,
  "questions": [
    {
      "id": 51,
      "text": "Which nutrient is the body's primary energy source?",
      "option_a": "Protein",
      "option_b": "Carbohydrate",
      "option_c": "Fat",
      "option_d": "Vitamin",
      "order": 1
    },
    {
      "id": 52,
      "text": "How many essential amino acids are there?",
      "option_a": "8",
      "option_b": "9",
      "option_c": "10",
      "option_d": "11",
      "order": 2
    }
  ],
  "created_at": "2026-05-01T10:00:00Z"
}
```

**Note:** `correct_option` is intentionally omitted so users can't cheat.

---

## 6. Submit Quiz Answers

**POST** `https://<host>/api/study/quizzes/submit/`

**Headers:**
```
Authorization: Bearer <user_access_token>
Content-Type: application/json
```

**Body:**
```json
{
  "quiz_id": 10,
  "answers": [
    { "question_id": 51, "selected_option": "B" },
    { "question_id": 52, "selected_option": "B" }
  ]
}
```

**Expected response:**
```json
{
  "success": true,
  "data": {
    "attempt_id": 45,
    "quiz_title": "Nutrition Quiz 1",
    "score": 2,
    "total_questions": 2,
    "score_percentage": 100.0,
    "answers": [
      {
        "question_id": 51,
        "question_text": "Which nutrient is the body's primary energy source?",
        "selected_option": "B",
        "correct_option": "B",
        "is_correct": true
      },
      {
        "question_id": 52,
        "question_text": "How many essential amino acids are there?",
        "selected_option": "B",
        "correct_option": "B",
        "is_correct": true
      }
    ]
  }
}
```

**How to display:**
- Show score: `2 / 2` or `100%`
- Show each question with user's answer + correct answer
- Green if `is_correct: true`, red if false

---

## 7. View Quiz Attempt History

**GET** `https://<host>/api/study/attempts/`

**Optional filter by subject:** `?topic=1`

**Expected response (flat array):**
```json
[
  {
    "id": 45,
    "quiz": 10,
    "quiz_title": "Nutrition Quiz 1",
    "topic_id": 1,
    "topic_title": "Nutrition Basics",
    "score": 2,
    "total_questions": 2,
    "score_percentage": 100.0,
    "completed_at": "2026-05-08T08:30:00Z"
  }
]
```

---

## 8. View Attempt Detail (Review Answers)

**GET** `https://<host>/api/study/attempts/45/`

**Expected response:**
```json
{
  "id": 45,
  "quiz": 10,
  "quiz_title": "Nutrition Quiz 1",
  "score": 2,
  "total_questions": 2,
  "score_percentage": 100.0,
  "completed_at": "2026-05-08T08:30:00Z",
  "answers": [
    {
      "question_id": 51,
      "question_text": "Which nutrient is the body's primary energy source?",
      "selected_option": "B",
      "correct_option": "B",
      "is_correct": true
    }
  ]
}
```

---

## Summary Table

| Step | Action | Endpoint | Method |
|------|--------|----------|--------|
| 1 | List subjects | `/api/study/topics/` | GET |
| 2 | Subject detail (materials) | `/api/study/topics/<id>/` | GET |
| 3 | Mark material read | `/api/study/materials/complete/` | POST |
| 4 | List quizzes | `/api/study/quizzes/` | GET |
| 5 | Get quiz questions | `/api/study/quizzes/<id>/` | GET |
| 6 | Submit answers | `/api/study/quizzes/submit/` | POST |
| 7 | Quiz history | `/api/study/attempts/` | GET |
| 8 | Review attempt | `/api/study/attempts/<id>/` | GET |

---

## Admin Endpoints (for reference)

| Action | Endpoint | Method |
|--------|----------|--------|
| Create subject | `/api/admin/study/topics/` | POST |
| Upload material | `/api/admin/study/materials/` | POST (multipart/form-data) |
| Create quiz | `/api/admin/study/quizzes/` | POST |
| Add question | `/api/admin/study/questions/` | POST |
| View all attempts | `/api/admin/study/attempts/` | GET |

---

*Last updated: 2026-05-08*
