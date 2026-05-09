# Mobile Habit Workflow

**Base URL:** `https://videos-explaining-spare-alleged.trycloudflare.com/`

---

## User Flow

```
Step 1: Get all categories
       ↓
Step 2: User picks a category
       ↓
Step 3: Get prebuilt habits under that category
       ↓
Step 4: User picks a prebuilt habit → auto-creates habit
         OR user creates a custom habit manually
         (Free user: max 3 total habits. Pro: unlimited)
       ↓
Step 5: Mark habit done
         (Pro only, max 3/day across all categories)
       ↓
Step 6: Check daily status
```

---

## 1. Get Categories

```
GET /api/categories/
Authorization: Bearer <token>
```

---

## 2. Get Prebuilt Habits for Selected Category

```
GET /api/habit-templates/?category=1
Authorization: Bearer <token>
```

**Returns:**
```json
[
  {
    "id": 1,
    "activity_name": "Morning Meditation",
    "description": "10 minutes mindfulness",
    "duration": 10
  }
]
```

---

## 3. Option A — Adopt Prebuilt Habit (Auto-Filled)

User taps a prebuilt habit. App sends only `template_id`:

```
POST /api/habits/
Authorization: Bearer <token>
Content-Type: application/json

{
  "template_id": 1
}
```

**Backend auto-copies:** `category`, `activity_name`, `description`, `duration`

**Expected:**
- Free user with 3+ habits → `400` error
- Pro user or under limit → `201` created

---

## 4. Option B — Create Custom Habit (Manual Entry)

User fills all fields manually:

```
POST /api/habits/
Authorization: Bearer <token>
Content-Type: application/json

{
  "category": 1,
  "activity_name": "Morning Run",
  "description": "Run 5km in the park",
  "duration": 30
}
```

**Expected:**
- Free user with 3+ habits → `400` error
- Pro user or under limit → `201` created

---

## 5. Mark Habit Done

```
POST /api/habits/1/done/
Authorization: Bearer <token>
```

**Expected:**
- Not Pro → `403`
- Already done 3 today → `400`
- Success → `201`

---

## 6. Check Daily Status

```
GET /api/habits/daily-status/
Authorization: Bearer <token>
```

**Returns:**
```json
{
  "daily_completions": 2,
  "daily_completion_limit": 3,
  "remaining": 1
}
```

---

## Limits Summary

| Action | Free User | Pro User |
|--------|-----------|----------|
| Total habits | 3 max | Unlimited |
| Mark done | Not allowed | 3/day across all categories |
