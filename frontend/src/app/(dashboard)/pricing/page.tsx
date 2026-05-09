"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { listPlans, updatePlan, PricingPlan } from "@/lib/index";
import { EditPlanModal, EditPlanData } from "@/components/dashboard/modals/EditPlanModal";
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
                    <li key={feature.id} className="flex items-center gap-2 text-sm text-foreground">
                      <CheckCircle className={`h-4 w-4 shrink-0 ${feature.is_included ? "text-muted-foreground" : "text-destructive"}`} />
                      <span className={!feature.is_included ? "text-muted-foreground line-through" : ""}>
                        {feature.title}
                      </span>
                    </li>
                  ))}
                </ul>
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
    </div>
  );
}