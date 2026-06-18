"use client";

import { ContentPageViewer } from "@/components/dashboard/content/ContentPageViewer";
import {
  getAccountDeletionPolicy,
} from "@/lib/api/content/content";

export default function AccountDeletionPolicyPage() {
  return (
    <ContentPageViewer
      title="Account Deletion Policy"
      description="View the Account Deletion Policy page content."
      fetchFn={getAccountDeletionPolicy}
    />
  );
}
