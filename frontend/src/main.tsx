import { createInertiaApp } from "@inertiajs/react";
import { MantineProvider } from "@mantine/core";
import "@mantine/core/styles.css";
import type { ComponentType } from "react";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "vite/modulepreload-polyfill";
import { theme } from "./app/theme.ts";
import Layout from "./components/Layout/Layout.tsx";

const pages = import.meta.glob<ComponentType>("./pages/**/*.tsx");

document.addEventListener("DOMContentLoaded", () => {
    createInertiaApp({
        resolve: async (name: string) => {
            const importPage = pages[`./pages/${name}.tsx`];
            if (!importPage) {
                throw new Error(`Page ${name} not found`);
            }
            return await importPage()
        },
        layout: () => Layout,
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
