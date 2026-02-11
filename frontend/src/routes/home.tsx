import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiClient, ApiError } from "@/api/client";

export default function HomePage() {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  const investigationsQuery = useQuery({
    queryKey: ["investigations", "home"],
    queryFn: () => apiClient.listInvestigations(),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      apiClient.createInvestigation({
        name: name.trim(),
        description: description.trim() || undefined,
      }),
    onSuccess: () => {
      setName("");
      setDescription("");
      setError(null);
      void queryClient.invalidateQueries({ queryKey: ["investigations"] });
    },
    onError: (err: unknown) => {
      setError(err instanceof ApiError ? err.message : "Could not create investigation");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiClient.deleteInvestigation(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["investigations"] });
    },
  });

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (!name.trim()) {
      setError("Name is required");
      return;
    }
    createMutation.mutate();
  };

  const investigations = investigationsQuery.data?.items ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Investigations</h1>
          <p className="text-muted-foreground">Create and manage your OSINT investigations</p>
        </div>
      </div>

      <form onSubmit={submit} className="rounded-lg border bg-background/70 p-4">
        <div className="grid gap-3 md:grid-cols-[1fr_1fr_auto]">
          <input
            className="rounded-md border bg-background px-3 py-2 text-sm"
            placeholder="Investigation name"
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
          <input
            className="rounded-md border bg-background px-3 py-2 text-sm"
            placeholder="Short description (optional)"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
          />
          <Button type="submit" disabled={createMutation.isPending}>
            <Plus className="mr-2 h-4 w-4" />
            {createMutation.isPending ? "Creating..." : "New Investigation"}
          </Button>
        </div>
        {error ? <p className="mt-2 text-sm text-destructive">{error}</p> : null}
      </form>

      <div className="space-y-2">
        {investigations.length === 0 ? (
          <div className="rounded-lg border border-dashed p-8 text-center">
            <p className="text-muted-foreground">
              No investigations yet. Create your first investigation to get started.
            </p>
          </div>
        ) : (
          investigations.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between rounded-md border bg-background/80 px-4 py-3"
            >
              <Link to={`/investigation/${item.id}`} className="min-w-0">
                <p className="truncate font-medium">{item.name}</p>
                <p className="truncate text-sm text-muted-foreground">{item.description || item.id}</p>
              </Link>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => deleteMutation.mutate(item.id)}
                aria-label="Delete investigation"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
