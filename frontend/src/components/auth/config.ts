export const clerkPublishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY?.trim() ?? "";

const disableAuthValue = import.meta.env.VITE_DISABLE_AUTH;
const disableAuth =
  disableAuthValue === undefined
    ? import.meta.env.DEV
    : disableAuthValue === "1" || disableAuthValue.toLowerCase() === "true";

export const authEnabled = !disableAuth;
export const clerkEnabled = authEnabled && clerkPublishableKey.length > 0;
