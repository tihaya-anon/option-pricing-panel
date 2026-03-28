import { defineConfig } from "orval";

export default defineConfig({
  option_price: {
    output: {
      mode: "split",
      client: "react-query",
      target: "./src/api/option_price.ts",
      schemas: "./src/api/model",
      mock: {
        type: "msw",
        delay: 1000,
        useExamples: false,
        generateEachHttpStatus: false,
        baseUrl: "",
        locale: "en",
      },
    },
    input: {
      target: "./openapi.yaml",
    },
  },
});
