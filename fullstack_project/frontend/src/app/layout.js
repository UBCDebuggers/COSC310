import { Provider } from "@/components/ui/provider"
import { AuthProvider} from "./context/AuthContext"
import  'bootstrap/dist/css/bootstrap.min.css'
import './globals.css'

export default function RootLayout({ children }) {
  return (
    <html suppressHydrationWarning>
      <body>
        <AuthProvider>
          <Provider>{children}</Provider>
          <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossOrigin="anonymous"></script>
        </AuthProvider>
      </body>
    </html>
  )
}
