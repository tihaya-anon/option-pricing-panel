import { setupWorker } from "msw/browser";

import { pricingHandlers } from "./handlers";

export const worker = setupWorker(...pricingHandlers);
