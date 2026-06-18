"use client";

import { ContentPageEditor } from "@/components/dashboard/content/ContentPageEditor";
import {
  getAccountDeletionPolicy,
  updateAccountDeletionPolicy,
} from "@/lib/api/content/content";

export default function AccountDeletionPolicyPage() {
  return (
    <ContentPageEditor
      title="Account Deletion Policy"
      description="Manage the Account Deletion Policy page content displayed to users."
      fetchFn={getAccountDeletionPolicy}
      updateFn={updateAccountDeletionPolicy}
    />
  );
}
