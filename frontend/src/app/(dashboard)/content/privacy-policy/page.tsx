"use client";

import { ContentPageEditor } from "@/components/dashboard/content/ContentPageEditor";
import {
  getPrivacyPolicy,
  updatePrivacyPolicy,
} from "@/lib/api/content/content";

export default function EditPrivacyPolicyPage() {
  return (
    <ContentPageEditor
      title="Edit Privacy Policy"
      description="Edit the Privacy Policy page content."
      fetchFn={getPrivacyPolicy}
      updateFn={updatePrivacyPolicy}
    />
  );
}
