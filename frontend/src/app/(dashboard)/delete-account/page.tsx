"use client";

import { ContentPageViewer } from "@/components/dashboard/content/ContentPageViewer";
import {
  getAccountDeletionPolicy,
} from "@/lib/api/content/content";

export default function DeleteAccountPage() {
  return (
    <ContentPageViewer
      title="Account Deletion Policy"
      description="Account Deletion Policy"
      fetchFn={getAccountDeletionPolicy}
    />
  );
}
