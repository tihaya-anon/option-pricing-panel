import { StrictMode } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { createRoot } from "react-dom/client";

import { isMockEnabled } from "@/config/env";
import { queryClient } from "@/lib/query-client";

import "./index.css";
import App from "./App.tsx";

async function enableMocking() {
  if (!isMockEnabled) {
    return;
  }

  const { worker } = await import("@/mocks/browser");

  await worker.start({
    onUnhandledRequest: "bypass",
  });
}

function renderApplication() {
  createRoot(document.getElementById("root")!).render(
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </StrictMode>
  );
}

void enableMocking().then(renderApplication);
