import { useEffect } from "react";
import { useAuth } from "@clerk/clerk-react";

import { setAuthTokenGetter } from "@/api/client";

export default function AuthTokenBridge() {
  const { getToken } = useAuth();

  useEffect(() => {
    setAuthTokenGetter(() => getToken());
    return () => {
      setAuthTokenGetter(async () => null);
    };
  }, [getToken]);

  return null;
}
