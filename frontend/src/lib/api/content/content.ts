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

type ApiPayload<T> = {
  success: boolean;
  message: string;
  status: number;
  data: T;
};

export const getTermsAndConditions = async () => {
  const res = await requestJson<ApiPayload<ContentPageData>>("/api/admin/content/terms-and-conditions/");
  return res.data;
};

export const updateTermsAndConditions = async (data: Partial<ContentPageData>) => {
  const res = await requestJson<ApiPayload<ContentPageData>>("/api/admin/content/terms-and-conditions/", {
    method: "PATCH",
    body: JSON.stringify(data),
  });
  return res.data;
};

export const getPrivacyPolicy = async () => {
  const res = await requestJson<ApiPayload<ContentPageData>>("/api/admin/content/privacy-policy/");
  return res.data;
};

export const updatePrivacyPolicy = async (data: Partial<ContentPageData>) => {
  const res = await requestJson<ApiPayload<ContentPageData>>("/api/admin/content/privacy-policy/", {
    method: "PATCH",
    body: JSON.stringify(data),
  });
  return res.data;
};

export const getAccountDeletionPolicy = async () => {
  const res = await requestJson<ApiPayload<ContentPageData>>("/api/admin/content/account-deletion-policy/");
  return res.data;
};

export const updateAccountDeletionPolicy = async (data: Partial<ContentPageData>) => {
  const res = await requestJson<ApiPayload<ContentPageData>>("/api/admin/content/account-deletion-policy/", {
    method: "PATCH",
    body: JSON.stringify(data),
  });
  return res.data;
};
