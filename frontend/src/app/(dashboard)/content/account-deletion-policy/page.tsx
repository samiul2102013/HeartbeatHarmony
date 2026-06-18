"use client";

import { ContentPageEditor } from "@/components/dashboard/content/ContentPageEditor";
import {
  getAccountDeletionPolicy,
  updateAccountDeletionPolicy,
} from "@/lib/api/content/content";

export default function EditAccountDeletionPolicyPage() {
  return (
    <ContentPageEditor
      title="Edit Account Deletion Policy"
      description="Edit the Account Deletion Policy page content."
      fetchFn={getAccountDeletionPolicy}
      updateFn={updateAccountDeletionPolicy}
    />
  );
}
