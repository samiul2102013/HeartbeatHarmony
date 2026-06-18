"use client";

import { ContentPageViewer } from "@/components/dashboard/content/ContentPageViewer";
import {
  getTermsAndConditions,
} from "@/lib/api/content/content";

export default function TermsAndConditionsPage() {
  return (
    <ContentPageViewer
      title="Terms & Conditions"
      description="View the Terms and Conditions page content."
      fetchFn={getTermsAndConditions}
    />
  );
}
