import { useMemo } from "react";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ThemeToggle } from "@/components/layout/ThemeToggle";
import { apiClient } from "@/api/client";

export default function RootLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { data } = useQuery({
    queryKey: ["investigations", "sidebar"],
    queryFn: () => apiClient.listInvestigations(),
  });

  const investigations = data?.items ?? [];
  const activeId = useMemo(() => {
    const match = location.pathname.match(/^\/investigation\/([^/]+)/);
    return match?.[1] ?? null;
  }, [location.pathname]);

  const isInvestigationRoute = location.pathname.startsWith("/investigation/");

  return (
    <div className="min-h-screen bg-background bg-[radial-gradient(circle_at_top_left,hsl(202_80%_95%),transparent_45%),radial-gradient(circle_at_bottom_right,hsl(20_80%_94%),transparent_38%)] dark:bg-[radial-gradient(circle_at_top_left,hsl(202_35%_16%),transparent_45%),radial-gradient(circle_at_bottom_right,hsl(20_35%_14%),transparent_40%)]">
      <header className="sticky top-0 z-50 w-full border-b bg-background/85 backdrop-blur">
        <div className="flex h-14 w-full items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <Link to="/" className="text-lg font-semibold tracking-tight">
              OSINT Master
            </Link>
            <span className="rounded-full border px-2 py-0.5 text-xs text-muted-foreground">
              Investigation Graph Workspace
            </span>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={activeId ?? ""}
              onChange={(event) => {
                const nextId = event.target.value;
                if (nextId) {
                  navigate(`/investigation/${nextId}`);
                  return;
                }
                navigate("/");
              }}
              className="max-w-[220px] rounded-md border bg-background px-3 py-2 text-sm sm:max-w-[280px]"
              disabled={investigations.length === 0}
              aria-label="Select investigation"
            >
              <option value="">Select investigation</option>
              {investigations.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name} ({item.entity_count})
                </option>
              ))}
            </select>
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main className={isInvestigationRoute ? "w-full" : "mx-auto w-full max-w-[1400px] px-4 py-4"}>
        <section className={isInvestigationRoute ? "min-w-0" : "min-w-0 rounded-lg border bg-card/70 p-4 md:p-5"}>
          <Outlet />
        </section>
      </main>
    </div>
  );
}
