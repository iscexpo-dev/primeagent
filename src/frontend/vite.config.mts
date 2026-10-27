import react from "@vitejs/plugin-react-swc";
import * as dotenv from "dotenv";
import path from "path";
import { defineConfig, loadEnv } from "vite";
import istanbul from "vite-plugin-istanbul";
import svgr from "vite-plugin-svgr";
import tsconfigPaths from "vite-tsconfig-paths";
import {
  API_ROUTES,
  BASENAME,
  PORT,
  PROXY_TARGET,
} from "./src/customization/config-constants";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  const envPrimeagentResult = dotenv.config({
    path: path.resolve(__dirname, "../../.env"),
  });

  const envPrimeagent = envPrimeagentResult.parsed || {};

  const apiRoutes = API_ROUTES || ["^/api/v1/", "^/api/v2/", "/health"];

  const target =
    env.VITE_PROXY_TARGET || PROXY_TARGET || "http://localhost:7860";

  const port = Number(env.VITE_PORT) || PORT || 3000;

  const proxyTargets = apiRoutes.reduce((proxyObj, route) => {
    proxyObj[route] = {
      target: target,
      changeOrigin: true,
      secure: false,
      ws: true,
    };
    return proxyObj;
  }, {});

  return {
    base: BASENAME || "",
    build: {
      outDir: "build",
      chunkSizeWarningLimit: 2300,
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (!id.includes("node_modules")) return;
            if (id.includes("node_modules/elkjs/")) return "vendor-elk";
            if (
              id.includes("node_modules/vanilla-jsoneditor/") ||
              id.includes("node_modules/@codemirror/") ||
              id.includes("node_modules/@lezer/") ||
              id.includes("node_modules/codemirror/")
            )
              return "vendor-jsoneditor";
            if (id.includes("node_modules/ag-grid-")) return "vendor-ag-grid";
            if (
              id.includes("node_modules/moment-timezone/") ||
              id.includes("node_modules/moment/")
            )
              return "vendor-moment";
            if (id.includes("node_modules/ace-builds/")) return "vendor-ace";
            if (id.includes("node_modules/lucide-react/"))
              return "vendor-lucide";
            if (
              id.includes("node_modules/i18next/") ||
              id.includes("node_modules/react-i18next/")
            )
              return "vendor-i18n";
            if (
              id.includes("node_modules/@xyflow/") ||
              id.includes("node_modules/reactflow/")
            )
              return "vendor-flow";
            if (id.includes("node_modules/lodash/")) return "vendor-lodash";
            if (
              id.includes("node_modules/react-dom/") ||
              id.includes("node_modules/react/") ||
              id.includes("node_modules/scheduler/")
            )
              return "vendor-react";
            if (
              id.includes("node_modules/@chakra-ui/") ||
              id.includes("node_modules/@emotion/")
            )
              return "vendor-chakra";
            if (id.includes("node_modules/@radix-ui/")) return "vendor-radix";
            if (id.includes("node_modules/@tanstack/"))
              return "vendor-tanstack";
            if (id.includes("node_modules/framer-motion/"))
              return "vendor-motion";
            if (
              id.includes("node_modules/react-syntax-highlighter/") ||
              id.includes("node_modules/refractor/") ||
              id.includes("node_modules/highlight.js/")
            )
              return "vendor-syntax";
            if (id.includes("node_modules/mathjax")) return "vendor-mathjax";
            if (
              id.includes("node_modules/pdfjs-dist/") ||
              id.includes("node_modules/react-pdf/")
            )
              return "vendor-pdf";
            if (
              id.includes("node_modules/react-icons/") ||
              id.includes("node_modules/@fortawesome/")
            )
              return "vendor-icons";
          },
        },
      }, origin/realease/v2
    },
    define: {
      "import.meta.env.BACKEND_URL": JSON.stringify(
        envPrimeagent.BACKEND_URL ?? "http://localhost:7860",
      ),
      "import.meta.env.ACCESS_TOKEN_EXPIRE_SECONDS": JSON.stringify(
        envPrimeagent.ACCESS_TOKEN_EXPIRE_SECONDS ?? 60,
      ),
      "import.meta.env.CI": JSON.stringify(envPrimeagent.CI ?? false),
      "import.meta.env.PRIMEAGENT_AUTO_LOGIN": JSON.stringify(
        envPrimeagent.PRIMEAGENT_AUTO_LOGIN ?? true,
      ),
      "import.meta.env.PRIMEAGENT_MCP_COMPOSER_ENABLED": JSON.stringify(
        envPrimeagent.PRIMEAGENT_MCP_COMPOSER_ENABLED ?? "true",
      ),
      // Compile-time hard kill switch for the palette Bundle-header
      // Reload action.  The actual user-facing gate is the runtime
      // ``enable_extension_reload`` flag served from ``/config`` (mirrors
      // ``PRIMEAGENT_ENABLE_EXTENSION_RELOAD``), so a packaged frontend
      // built once can still light up the button when an operator opts
      // the backend in via ``--env-file`` or ``wfx extension dev``.
      // Default ``true`` here means the bundle SHIPS the UI; corporate
      // Mode B/C builds that want to drop the code entirely can set
      // ``PRIMEAGENT_EXTENSION_RELOAD_ENABLED=false`` in ``.env`` to dead-code-
      // eliminate the Reload UI at build time.
      "import.meta.env.PRIMEAGENT_EXTENSION_RELOAD_ENABLED": JSON.stringify(
        envPrimeagent.PRIMEAGENT_EXTENSION_RELOAD_ENABLED ?? "true",
      ),
      "import.meta.env.PRIMEAGENT_WXO_UTM_SOURCE": JSON.stringify(
        envPrimeagent.PRIMEAGENT_WXO_UTM_SOURCE ?? "primeagent",
      ),
    },
    plugins: [
      react(),
      svgr(),
      tsconfigPaths(),
      istanbul({
        include: "src/**/*",
        extension: [".ts", ".tsx", ".js", ".jsx"],
        requireEnv: false,
      }),
    ],
    server: {
      port: port,
      proxy: {
        ...proxyTargets,
      },
    },
  };
});
