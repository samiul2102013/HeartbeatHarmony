"use client";

import { ContentPageEditor } from "@/components/dashboard/content/ContentPageEditor";
import {
  getPrivacyPolicy,
  updatePrivacyPolicy,
} from "@/lib/api/content/content";

export default function PrivacyPolicyPage() {
  return (
    <ContentPageEditor
      title="Privacy Policy"
      description="Manage the Privacy Policy page content displayed to users."
      fetchFn={getPrivacyPolicy}
      updateFn={updatePrivacyPolicy}
    />
  );
}
