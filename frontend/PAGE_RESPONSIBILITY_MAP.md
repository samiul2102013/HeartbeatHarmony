# Page Responsibility Map

This file maps each route to the main source files and code sections that control it.

## Auth Pages

| Route | Main file | Responsible code | Supporting files |
| --- | --- | --- | --- |
| `/signin` | `src/app/(auth)/signin/page.tsx` | Sign-in form, validation, login submit flow, redirect on success | `src/lib/api/accounts/auth.ts`, `src/lib/api/core/client.ts`, `src/lib/api/core/tokens.ts` |
| `/forgot-password` | `src/app/(auth)/forgot-password/page.tsx` | Email reset form and submit handler | `src/lib/api/accounts/auth.ts` |
| `/reset-password` | `src/app/(auth)/reset-password/page.tsx` | Token + new password form and submit handler | `src/lib/api/accounts/auth.ts` |
| `/verification` | `src/app/(auth)/verification/page.tsx` | OTP/token verification form and submit handler | `src/lib/api/accounts/auth.ts` |
| Auth shell | `src/app/(auth)/layout.tsx` | Auth route guard and access-token check | `src/lib/api/core/tokens.ts` |

## Dashboard Shell

| Route | Main file | Responsible code | Supporting files |
| --- | --- | --- | --- |
| Dashboard shell | `src/app/(dashboard)/layout.tsx` | Sidebar, top bar, session guard, route chrome | `src/lib/api/core/tokens.ts`, `src/components/dashboard/header.tsx` |
| Dashboard home | `src/app/(dashboard)/page.tsx` | KPI cards, traffic chart, summary data loading | `src/lib/api/dashboard/dashboard.ts`, `src/types/traffic.ts` |

## Dashboard Pages

| Route | Main file | Responsible code | Supporting files |
| --- | --- | --- | --- |
| `/dashboard/users` | `src/app/(dashboard)/users/page.tsx` | User list, paging, search, delete/view actions | `src/lib/api/accounts/users.ts`, `src/app/(dashboard)/users/edit-user-dialog.tsx`, `src/components/dashboard/modals/AddUserModal.tsx` |
| `/dashboard/check-ins` | `src/app/(dashboard)/check-ins/page.tsx` | Check-in table and row actions | `src/lib/api/checkins/checkins.ts`, `src/app/(dashboard)/check-ins/veiw-checksin-dialog.tsx` |

| `/dashboard/categories` | `src/app/(dashboard)/categories/page.tsx` | Category table, add/edit/toggle/delete logic | `src/components/dashboard/modals/AddCategoryModal.tsx`, `src/components/dashboard/modals/EditCategoryModal.tsx`, `src/lib/api/habits/categories.ts` |

| `/dashboard/mood-categories` | `src/app/(dashboard)/mood-categories/page.tsx` | Mood category table, create/edit/delete/status logic | `src/components/dashboard/modals/AddMoodCategoryModal.tsx`, `src/app/(dashboard)/mood-categories/edit-mood-dialog.tsx`, `src/lib/api/checkins/moods.ts` |

| `/dashboard/mood-scoring` | `src/app/(dashboard)/mood-scoring/page.tsx` | Mood scoring table and create/toggle/delete logic | `src/components/dashboard/modals/AddMoodModal.tsx`, `src/lib/api/checkins/moods.ts` |

| `/dashboard/pricing` | `src/app/(dashboard)/pricing/page.tsx` | Pricing plan list and pricing actions | `src/lib/api/pricing/plans.ts`, `src/lib/api/pricing/features.ts`, `src/components/dashboard/modals/EditPlanModal.tsx` |


| `/dashboard/quiz-test` | `src/app/(dashboard)/quiz-test/page.tsx` | Quiz list, create quiz, view quiz details, score modal | `src/components/dashboard/quiz-test-modals.tsx`, `src/lib/api/study/quizzes.ts`, `src/lib/api/study/questions.ts`, `src/lib/api/study/attempts.ts` |
| `/dashboard/settings` | `src/app/(dashboard)/settings/page.tsx` | Profile form, password change, settings save flows | `src/lib/api/accounts/settings.ts` |
| `/dashboard/study-materials` | `src/app/(dashboard)/study-materials/page.tsx` | Material list, topic lookup, create/delete material | `src/components/dashboard/modals/AddMaterialModal.tsx`, `src/lib/api/study/materials.ts`, `src/lib/api/study/topics.ts` |
| `/dashboard/study-scoring` | `src/app/(dashboard)/study-scoring/page.tsx` | Study topic list and scoring summary | `src/lib/api/study/topics.ts` |
| `/dashboard/subject-uploads` | `src/app/(dashboard)/subject-uploads/page.tsx` | Subject upload list, create topic/upload flow, delete action | `src/components/dashboard/modals/UploadBookModal.tsx`, `src/lib/api/study/topics.ts` |

## Shared UI Pieces

| File | Responsible code |
| --- | --- |
| `src/components/dashboard/modals/shared.tsx` | Shared modal footer, field wrapper, and inline error block |
| `src/components/dashboard/modals/index.ts` | Modal export barrel for the dashboard |
| `src/lib/index.ts` | App-wide API barrel used by pages and layout components |
| `src/lib/api/index.ts` | Lower-level API barrel for direct endpoint imports |
| `src/lib/api/core/client.ts` | Shared request wrapper, auth header handling, refresh retry, and normalized errors |
| `src/lib/api/core/tokens.ts` | Session token storage and cleanup |

## Notes

- The route file owns page-specific state, filtering, table rendering, and submit handlers.
- The modal file owns the form UI, local validation, and close/reset behavior.
- The API file owns the actual endpoint path, request method, and response normalization.
- If a page crashes during render, start with the page file first, then check the supporting modal or API file named in the table.
