import { useMemo, useState } from "react";
import { SignedIn, SignedOut, SignInButton, SignUpButton, UserButton } from "@clerk/clerk-react";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ThemeToggle } from "@/components/layout/ThemeToggle";
import { Button } from "@/components/ui/button";
import { authEnabled } from "@/components/auth/config";
import { apiClient, ApiError } from "@/api/client";

export default function RootLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [createError, setCreateError] = useState<string | null>(null);

  const { data } = useQuery({
    queryKey: ["investigations", "sidebar"],
    queryFn: () => apiClient.listInvestigations(),
  });

  const createInvestigationMutation = useMutation({
    mutationFn: (name: string) => apiClient.createInvestigation({ name }),
    onSuccess: async (created) => {
      setCreateError(null);
      await queryClient.invalidateQueries({ queryKey: ["investigations"] });
      navigate(`/investigation/${created.id}`);
    },
    onError: (error: unknown) => {
      setCreateError(error instanceof ApiError ? error.message : "Could not create investigation");
    },
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
            {!authEnabled ? (
              <span className="rounded-full border border-amber-300 bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
                Auth disabled (dev)
              </span>
            ) : null}
          </div>
          <div className="flex items-center gap-2">
            <select
              value={activeId ?? ""}
              onChange={(event) => {
                const nextId = event.target.value;
                if (nextId === "__create__") {
                  const rawName = window.prompt("Investigation name");
                  const trimmedName = rawName?.trim() ?? "";
                  if (!trimmedName) {
                    return;
                  }
                  createInvestigationMutation.mutate(trimmedName);
                  return;
                }
                if (nextId) {
                  navigate(`/investigation/${nextId}`);
                  return;
                }
                navigate("/");
              }}
              className="max-w-[220px] rounded-md border bg-background px-3 py-2 text-sm sm:max-w-[280px]"
              disabled={createInvestigationMutation.isPending}
              aria-label="Select investigation"
            >
              <option value="">Select investigation</option>
              <option value="__create__">+ Create investigation</option>
              {investigations.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name} ({item.entity_count})
                </option>
              ))}
            </select>
            {createError ? <p className="max-w-[240px] text-xs text-destructive">{createError}</p> : null}
            <ThemeToggle />
            {authEnabled ? (
              <>
                <SignedOut>
                  <SignInButton mode="modal">
                    <Button variant="outline" size="sm">
                      Sign in
                    </Button>
                  </SignInButton>
                  <SignUpButton mode="modal">
                    <Button size="sm">Sign up</Button>
                  </SignUpButton>
                </SignedOut>
                <SignedIn>
                  <UserButton />
                </SignedIn>
              </>
            ) : null}
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
