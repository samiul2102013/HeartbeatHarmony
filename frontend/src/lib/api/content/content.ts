import { requestJson } from "../core/client";

export type ContentPageData = {
  id?: number;
  slug: string;
  title: string;
  content: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
};

const CONTENT_SLUGS = {
  terms: "terms-and-conditions",
  privacy: "privacy-policy",
  deletionPolicy: "account-deletion-policy",
} as const;

export const getTermsAndConditions = () =>
  requestJson<ContentPageData>("/api/admin/content/terms-and-conditions/");

export const updateTermsAndConditions = (data: Partial<ContentPageData>) =>
  requestJson<ContentPageData>("/api/admin/content/terms-and-conditions/", {
    method: "PATCH",
    body: JSON.stringify(data),
  });

export const getPrivacyPolicy = () =>
  requestJson<ContentPageData>("/api/admin/content/privacy-policy/");

export const updatePrivacyPolicy = (data: Partial<ContentPageData>) =>
  requestJson<ContentPageData>("/api/admin/content/privacy-policy/", {
    method: "PATCH",
    body: JSON.stringify(data),
  });

export const getAccountDeletionPolicy = () =>
  requestJson<ContentPageData>("/api/admin/content/account-deletion-policy/");

export const updateAccountDeletionPolicy = (data: Partial<ContentPageData>) =>
  requestJson<ContentPageData>("/api/admin/content/account-deletion-policy/", {
    method: "PATCH",
    body: JSON.stringify(data),
  });
