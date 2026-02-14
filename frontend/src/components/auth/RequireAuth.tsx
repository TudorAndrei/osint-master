import type { ReactNode } from "react";
import { RedirectToSignIn, useAuth } from "@clerk/clerk-react";
import { authEnabled } from "@/components/auth/config";

type RequireAuthProps = {
  children: ReactNode;
};

function ClerkAuthGate({ children }: RequireAuthProps) {
  const { isLoaded, isSignedIn } = useAuth();

  if (!isLoaded) {
    return <div className="p-6 text-sm text-muted-foreground">Loading authentication...</div>;
  }

  if (!isSignedIn) {
    return <RedirectToSignIn />;
  }

  return <>{children}</>;
}

export default function RequireAuth({ children }: RequireAuthProps) {
  if (!authEnabled) {
    return <>{children}</>;
  }

  return <ClerkAuthGate>{children}</ClerkAuthGate>;
}
