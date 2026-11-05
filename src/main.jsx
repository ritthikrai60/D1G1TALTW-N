import React from "react"
import { createRoot } from "react-dom/client"
import "./theme/m3-tokens.css"
import "./style.css"
import App from "./App"
import { ToastProvider } from "@/components/ui/toaster"

const rootElement = document.getElementById("root")
if (rootElement) {
  createRoot(rootElement).render(
    <React.StrictMode>
      <ToastProvider>
        <App />
      </ToastProvider>
    </React.StrictMode>
  )
}

