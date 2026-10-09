import { createInertiaApp } from "@inertiajs/react";
import { MantineProvider } from "@mantine/core";
import "@mantine/core/styles.css";
import type { ComponentType } from "react";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "vite/modulepreload-polyfill";
import App from "./app/App.tsx";
import { theme } from "./app/theme.ts";
const pages = import.meta.glob("./pages/**/*.tsx");

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <App />
    </StrictMode>,
);

document.addEventListener("DOMContentLoaded", () => {
    createInertiaApp({
        resolve: (name: string) => {
            const importPage = pages[`./pages/${name}.tsx`];
            if (!importPage) {
                throw new Error(`Page ${name} not found`);
            }
            return importPage().then(
                (module) => (module as { default: ComponentType }).default,
            );
        },
        setup({ el, App, props }) {
            createRoot(el).render(
                <StrictMode>
                    <MantineProvider theme={theme}>
                        <App {...props} />
                    </MantineProvider>
                </StrictMode>,
            );
        },
    });
});
