"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { createFeature, deleteFeature, listPlans, updateFeature, updatePlan, PricingPlan, PlanFeature } from "@/lib/index";
import { EditPlanModal, EditPlanData } from "@/components/dashboard/modals/EditPlanModal";
import { FeatureModal, FeatureFormData } from "@/components/dashboard/modals/FeatureModal";
import { CheckCircle } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

function formatDuration(duration: PricingPlan["duration"]) {
  if (duration === "monthly") return "/month";
  if (duration === "yearly") return "/year";
  return "/lifetime";
}

export default function Pricing() {
  const [plans, setPlans] = useState<PricingPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editPlan, setEditPlan] = useState<PricingPlan | null>(null);
  const [editOpen, setEditOpen] = useState(false);
  const [featureOpen, setFeatureOpen] = useState(false);
  const [featurePlan, setFeaturePlan] = useState<PricingPlan | null>(null);
  const [featureItem, setFeatureItem] = useState<FeatureFormData | null>(null);

  useEffect(() => {
    let mounted = true;

    const loadPlans = async () => {
      try {
        setLoading(true);
        const data = await listPlans();
        if (!mounted) return;
        setPlans(data);
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : "Unable to load pricing plans");
      } finally {
        if (mounted) setLoading(false);
      }
    };

    void loadPlans();

    return () => {
      mounted = false;
    };
  }, []);

  const visiblePlans = useMemo(() => plans.filter((plan) => plan.is_active), [plans]);

  const sortFeatures = (features: PlanFeature[] = []) => [...features].sort((a, b) => (a.order ?? 0) - (b.order ?? 0));

  const openCreateFeature = (plan: PricingPlan) => {
    const maxOrder = Math.max(0, ...(plan.features ?? []).map((feature) => feature.order ?? 0));
    setFeaturePlan(plan);
    setFeatureItem({
      plan: plan.id,
      title: "",
      is_included: true,
      order: maxOrder + 1,
    });
    setFeatureOpen(true);
  };

  const openEditFeature = (plan: PricingPlan, feature: PlanFeature) => {
    setFeaturePlan(plan);
    setFeatureItem({
      id: feature.id,
      plan: plan.id,
      title: feature.title,
      is_included: feature.is_included,
      order: feature.order ?? 0,
    });
    setFeatureOpen(true);
  };

  const applyFeatureToPlans = (planId: number, nextFeature: PlanFeature, replaceId?: number) => {
    setPlans((prev) =>
      prev.map((plan) => {
        if (plan.id !== planId) return plan;
        const features = sortFeatures(plan.features ?? []);
        const nextFeatures = replaceId
          ? features.map((feature) => (feature.id === replaceId ? nextFeature : feature))
          : [...features.filter((feature) => feature.id !== nextFeature.id), nextFeature];
        return { ...plan, features: sortFeatures(nextFeatures) };
      })
    );
  };

  const handleDeleteFeature = async (plan: PricingPlan, feature: PlanFeature) => {
    if (!confirm(`Delete feature \"${feature.title}\"?`)) return;
    try {
      await deleteFeature(feature.id);
      setPlans((prev) =>
        prev.map((item) =>
          item.id === plan.id
            ? { ...item, features: (item.features ?? []).filter((current) => current.id !== feature.id) }
            : item
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to delete feature");
    }
  };

  return (
    <div className="space-y-5 p-6">
      <div>
        <h1 className="text-xl font-semibold text-foreground">Subscription Pricing</h1>
        <p className="mt-0.5 text-sm text-muted-foreground">
          Configure plan features, pricing tiers, and revenue settings.
        </p>
      </div>

      {error && <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">{error}</div>}

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3">
        {loading ? (
          <div className="col-span-full rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground">
            Loading pricing plans...
          </div>
        ) : visiblePlans.length === 0 ? (
          <div className="col-span-full rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground">
            No active plans found.
          </div>
        ) : (
          visiblePlans.map((plan) => (
            <Card key={plan.id} className="flex flex-col rounded-xl border border-border bg-card shadow-sm">
              <CardHeader className="space-y-1 px-6 pb-2 pt-6">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-medium text-muted-foreground">{plan.name}</p>
                  {plan.is_popular && (
                    <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-medium text-amber-700">
                      Popular
                    </span>
                  )}
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-4xl font-bold text-foreground">${plan.price}</span>
                  <span className="text-sm text-muted-foreground">{formatDuration(plan.duration)}</span>
                </div>
              </CardHeader>
              <CardContent className="flex flex-1 flex-col gap-4 px-6 pb-6">
                <ul className="flex-1 space-y-2">
                  {(plan.features ?? []).map((feature) => (
                    <li key={feature.id} className="flex items-start justify-between gap-3 rounded-lg border border-border px-3 py-2 text-sm text-foreground">
                      <div className="flex items-start gap-2">
                        <CheckCircle className={`mt-0.5 h-4 w-4 shrink-0 ${feature.is_included ? "text-muted-foreground" : "text-destructive"}`} />
                        <div className="space-y-0.5">
                          <p className={!feature.is_included ? "text-muted-foreground line-through" : ""}>{feature.title}</p>
                          <p className="text-xs text-muted-foreground">Order {feature.order ?? 0}</p>
                        </div>
                      </div>
                      <div className="flex shrink-0 gap-2">
                        <Button type="button" variant="ghost" className="h-7 px-2 text-xs" onClick={() => openEditFeature(plan, feature)}>
                          Edit
                        </Button>
                        <Button type="button" variant="ghost" className="h-7 px-2 text-xs text-destructive" onClick={() => void handleDeleteFeature(plan, feature)}>
                          Delete
                        </Button>
                      </div>
                    </li>
                  ))}
                </ul>
                <Button
                  type="button"
                  variant="outline"
                  className="h-10 w-full text-sm font-medium"
                  onClick={() => openCreateFeature(plan)}
                >
                  Add Feature
                </Button>
                <Button
                  className="mt-2 h-10 w-full text-sm font-medium"
                  style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
                  onClick={() => {
                    setEditPlan(plan);
                    setEditOpen(true);
                  }}
                >
                  Edit Plan
                </Button>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      <EditPlanModal
        open={editOpen}
        onOpenChange={setEditOpen}
        plan={editPlan ? { id: editPlan.id, name: editPlan.name, price: editPlan.price, duration: editPlan.duration, is_active: editPlan.is_active, is_popular: editPlan.is_popular } : null}
        onSubmit={async (data: EditPlanData) => {
          const updated = await updatePlan(data.id, {
            name: data.name,
            price: data.price,
            duration: data.duration,
            is_active: data.is_active,
            is_popular: data.is_popular,
          });
          setPlans((prev) => prev.map((p) => (p.id === updated.id ? { ...p, ...updated } : p)));
          setEditPlan(null);
        }}
      />

      <FeatureModal
        open={featureOpen}
        onOpenChange={(value) => {
          setFeatureOpen(value);
          if (!value) {
            setFeaturePlan(null);
            setFeatureItem(null);
          }
        }}
        planName={featurePlan?.name ?? "Plan"}
        feature={featureItem}
        onSubmit={async (data) => {
          if (!featurePlan) return;

          if (data.id) {
            const updated = await updateFeature(data.id, {
              title: data.title,
              is_included: data.is_included,
              order: data.order,
            });
            const nextFeature = {
              id: updated?.id ?? data.id,
              plan: updated?.plan ?? data.plan,
              title: updated?.title ?? data.title,
              is_included: updated?.is_included ?? data.is_included,
              order: updated?.order ?? data.order,
            };
            applyFeatureToPlans(featurePlan.id, nextFeature as PlanFeature, data.id);
          } else {
            const created = await createFeature({
              plan: featurePlan.id,
              title: data.title,
              is_included: data.is_included,
              order: data.order,
            });
            const nextFeature = created?.data ?? created;
            applyFeatureToPlans(featurePlan.id, {
              id: nextFeature?.id ?? Date.now(),
              plan: nextFeature?.plan ?? featurePlan.id,
              title: nextFeature?.title ?? data.title,
              is_included: nextFeature?.is_included ?? data.is_included,
              order: nextFeature?.order ?? data.order,
            } as PlanFeature);
          }

          setFeatureOpen(false);
          setFeaturePlan(null);
          setFeatureItem(null);
        }}
      />
    </div>
  );
}