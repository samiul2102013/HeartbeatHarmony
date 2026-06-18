"use client";

import { ContentPageViewer } from "@/components/dashboard/content/ContentPageViewer";
import {
  getPrivacyPolicy,
} from "@/lib/api/content/content";

export default function PrivacyPage() {
  return (
    <ContentPageViewer
      title="Privacy Policy"
      description="View the Privacy Policy page content."
      fetchFn={getPrivacyPolicy}
    />
  );
}
