"use client";

import { ContentPageEditor } from "@/components/dashboard/content/ContentPageEditor";
import {
  getTermsAndConditions,
  updateTermsAndConditions,
} from "@/lib/api/content/content";

export default function TermsAndConditionsPage() {
  return (
    <ContentPageEditor
      title="Terms & Conditions"
      description="Manage the Terms and Conditions page content displayed to users."
      fetchFn={getTermsAndConditions}
      updateFn={updateTermsAndConditions}
    />
  );
}
