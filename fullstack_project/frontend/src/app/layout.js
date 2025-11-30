"use client"
import { Provider } from "@/components/ui/provider"
import { AuthProvider} from "./context/AuthContext"
import Sidebar from "@/components/Sidebar"
import  'bootstrap/dist/css/bootstrap.min.css'
import './globals.css'
import { ColorModeProvider } from "@/components/ui/color-mode"

export default function RootLayout({ children }) {
  return (
    <html suppressHydrationWarning>
      <body>
        <AuthProvider>
          <Provider>
            <ColorModeProvider>
              <Sidebar>
                {children}
              </Sidebar>
            </ColorModeProvider>
          </Provider>
          <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossOrigin="anonymous"></script>
        </AuthProvider>
      </body>
    </html>
  )
}
