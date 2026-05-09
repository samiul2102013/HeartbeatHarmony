"use client";

import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { getDashboardStats } from "@/lib/index";
import { TrafficPoint } from "@/types/traffic";
import { HeartHandshake, LayoutGrid, Users, UsersRound } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  Area,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from "recharts";

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <Card className="rounded-xl border border-border shadow-[5px_12px_40px_-16px_rgba(0,0,0,0.2)]">
      <CardContent className="flex flex-col items-center justify-center gap-3 p-4 text-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-lg" style={{ backgroundColor: "rgba(209,61,61,0.12)" }}>
          <div className="[&_svg]:size-8" style={{ color: "var(--primary)" }}>
            {icon}
          </div>
        </div>
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground">{label}</p>
          <p className="text-2xl font-semibold text-foreground">{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function HeartBalanceBarChart({ data }: { data: { day: string; value: number }[] }) {
  return (
    <Card className="rounded-[20px] border border-border bg-card shadow-[0px_12px_40px_-16px_rgba(0,0,0,0.2)]">
      <CardHeader className="flex flex-row items-center justify-between px-6 pt-6">
        <h3 className="text-xl font-semibold text-foreground">Heart Balance Trend</h3>
      </CardHeader>
      <CardContent className="px-6 pb-6 pt-4">
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 8, right: 8, left: -14, bottom: 12 }}>
              <CartesianGrid stroke="var(--border)" strokeDasharray="0" vertical={false} />
              <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: "var(--muted-foreground)", fontSize: 13 }} />
              <YAxis axisLine={false} tickLine={false} tick={{ fill: "var(--muted-foreground)", fontSize: 13 }} />
              <Bar dataKey="value" fill="var(--primary)" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

function MoodDistribution({ data }: { data: { name: string; value: number; color: string }[] }) {
  return (
    <Card className="rounded-[20px] border border-border bg-card shadow-[0px_12px_40px_-16px_rgba(0,0,0,0.2)]">
      <CardHeader className="px-6 pt-6">
        <h3 className="text-xl font-semibold text-foreground">Mood Distribution</h3>
      </CardHeader>
      <CardContent className="px-6 pb-6">
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data} cx="50%" cy="50%" innerRadius={80} outerRadius={120} dataKey="value" label={false}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

function UserInsights({ stats }: { stats: any }) {
  const rows = [
    { id: "total", label: "Total Users", value: stats.total.toLocaleString() },
    { id: "active", label: "Active Users", value: stats.active.toLocaleString() },
    { id: "pro", label: "Pro Users", value: stats.pro.toLocaleString() },
  ];

  return (
    <Card className="rounded-[20px] border border-border bg-card shadow-[0px_12px_40px_-16px_rgba(0,0,0,0.2)]">
      <CardHeader className="flex flex-row items-center justify-between px-6 pt-6">
        <h3 className="text-xl font-semibold text-foreground">User Insights</h3>
      </CardHeader>
      <CardContent className="space-y-3 px-6 pb-6">
        {rows.map((row) => (
          <div key={row.id} className="flex items-center justify-between py-1">
            <p className="text-sm font-medium text-foreground">{row.label}</p>
            <span className="text-xs text-muted-foreground">{row.value}</span>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

function HartBalanceChart({ data }: { data: TrafficPoint[] }) {
  const [hasSize, setHasSize] = useState(false);
  const chartContainerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const element = chartContainerRef.current;
    if (!element) return;

    const update = () => {
      const { width, height } = element.getBoundingClientRect();
      setHasSize(width > 0 && height > 0);
    };

    update();
    const observer = new ResizeObserver(update);
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  return (
    <Card className="rounded-[20px] border border-border bg-card shadow-[0px_12px_40px_-16px_rgba(0,0,0,0.2)]">
      <CardHeader className="flex flex-row items-start justify-between gap-4 px-6 pb-0 pt-6">
        <h3 className="text-xl font-semibold text-foreground">Hard Balance Trend</h3>
      </CardHeader>
      <CardContent className="px-6 pb-6 pt-4">
        <div ref={chartContainerRef} className="h-80 w-full min-w-0">
          {hasSize && (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ top: 8, right: 8, left: -14, bottom: 12 }}>
                <CartesianGrid stroke="var(--border)" strokeDasharray="0" vertical={false} />
                <XAxis dataKey="month" axisLine={false} tickLine={false} height={40} tickMargin={10} tick={{ fill: "var(--muted-foreground)", fontSize: 13 }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: "var(--muted-foreground)", fontSize: 13 }} />
                <Area type="natural" dataKey="value" stroke="none" fill="var(--primary)" fillOpacity={0.06} />
                <Line type="natural" dataKey="value" stroke="var(--foreground)" strokeWidth={1.5} dot={false} activeDot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function normalizeDashboardStats(response: any) {
  const source = response?.data ?? response?.result ?? response?.results ?? response ?? {};

  return {
    user_insights: {
      total: Number(source?.user_insights?.total ?? source?.total ?? 0),
      active: Number(source?.user_insights?.active ?? source?.active ?? 0),
      pro: Number(source?.user_insights?.pro ?? source?.pro ?? 0),
    },
    heart_balance_trend: Array.isArray(source?.heart_balance_trend) ? source.heart_balance_trend : [],
    mood_distribution: Array.isArray(source?.mood_distribution) ? source.mood_distribution : [],
  };
}

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const load = async () => {
      try {
        setLoading(true);
        const response = await getDashboardStats();
        if (!mounted) return;
        setStats(normalizeDashboardStats(response));
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : "Unable to load dashboard data");
      } finally {
        if (mounted) setLoading(false);
      }
    };

    void load();

    return () => {
      mounted = false;
    };
  }, []);

  const heartBalanceData = useMemo(
    () =>
      (Array.isArray(stats?.heart_balance_trend) ? stats.heart_balance_trend : []).map((point: any) => ({
        month: new Date(point.date).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
        value: point.avg_score,
      })),
    [stats]
  );

  const heartBalanceBarData = useMemo(
    () =>
      (Array.isArray(stats?.heart_balance_trend) ? stats.heart_balance_trend : []).map((point: any) => ({
        day: new Date(point.date).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
        value: point.avg_score,
      })),
    [stats]
  );

  const moodData = useMemo(
    () =>
      (Array.isArray(stats?.mood_distribution) ? stats.mood_distribution : []).map((item: any, index: number) => ({
        name: item.mood__name,
        value: item.count,
        color: ["#10B981", "#3B82F6", "#F59E0B", "#9CA3AF", "#EF4444", "#6366F1", "#8B5CF6"][index % 7],
      })),
    [stats]
  );

  const avgHeartBalance = useMemo(() => {
    if (!heartBalanceData.length) return 0;
    const total = heartBalanceData.reduce((sum: number, point: any) => sum + point.value, 0);
    return total / heartBalanceData.length;
  }, [heartBalanceData]);

  const totalCheckIns = useMemo(() => moodData.reduce((sum: number, item: any) => sum + item.value, 0), [moodData]);

  return (
    <div className="space-y-6 bg-background p-6">
      {error && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard icon={<UsersRound />} label="Total Users" value={loading ? "..." : (stats?.user_insights?.total ?? 0).toLocaleString()} />
        <StatCard icon={<Users />} label="Active Users (Today)" value={loading ? "..." : (stats?.user_insights?.active ?? 0).toLocaleString()} />
        <StatCard icon={<HeartHandshake />} label="Avg. Heart Balance" value={loading ? "..." : avgHeartBalance.toFixed(1)} />
        <StatCard icon={<LayoutGrid />} label="Total Check-ins" value={loading ? "..." : totalCheckIns.toLocaleString()} />
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <HartBalanceChart data={heartBalanceData.length ? heartBalanceData : [{ month: "No data", value: 0 }]} />
        <HeartBalanceBarChart data={heartBalanceBarData.length ? heartBalanceBarData : [{ day: "No data", value: 0 }]} />
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <MoodDistribution data={moodData.length ? moodData : [{ name: "No data", value: 0, color: "#9CA3AF" }]} />
        <UserInsights stats={stats?.user_insights ?? { total: 0, active: 0, pro: 0 }} />
      </div>
    </div>
  );
}