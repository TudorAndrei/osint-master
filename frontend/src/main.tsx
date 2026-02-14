import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { ClerkProvider } from "@clerk/clerk-react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import AuthTokenBridge from "@/components/auth/AuthTokenBridge";
import { authEnabled, clerkEnabled, clerkPublishableKey } from "@/components/auth/config";
import { setAuthTokenGetter } from "@/api/client";
import App from "./App";
import "./index.css";
import "katex/dist/katex.min.css";
import "streamdown/styles.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1 minute
      retry: 1,
    },
  },
});

if (!authEnabled || !clerkEnabled) {
  setAuthTokenGetter(async () => null);
}

if (authEnabled && !clerkEnabled) {
  throw new Error("Missing VITE_CLERK_PUBLISHABLE_KEY while auth is enabled");
}

const appTree = (
  <QueryClientProvider client={queryClient}>
    {clerkEnabled ? <AuthTokenBridge /> : null}
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </QueryClientProvider>
);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    {authEnabled ? (
      <ClerkProvider publishableKey={clerkPublishableKey} afterSignOutUrl="/">
        {appTree}
      </ClerkProvider>
    ) : (
      appTree
    )}
  </StrictMode>
);
