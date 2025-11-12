import { Provider } from "@/components/ui/provider"
import { AuthProvider} from "./context/AuthContext"
import  'bootstrap/dist/css/bootstrap.min.css'
import "./globals.css";
import Script from "next/script";




export default function RootLayout({ children }) {
  return (
    <html suppressHydrationWarning>
      <body>
        <AuthProvider>
          <Provider>{children}</Provider>
          <Script
            src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"
            strategy="afterInteractive"
          />
        </AuthProvider>
      </body>
    </html>
  )
}
