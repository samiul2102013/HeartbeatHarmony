"use client";

import { ContentPageEditor } from "@/components/dashboard/content/ContentPageEditor";
import {
  getTermsAndConditions,
  updateTermsAndConditions,
} from "@/lib/api/content/content";

export default function EditTermsAndConditionsPage() {
  return (
    <ContentPageEditor
      title="Edit Terms & Conditions"
      description="Edit the Terms and Conditions page content."
      fetchFn={getTermsAndConditions}
      updateFn={updateTermsAndConditions}
    />
  );
}
