import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "next-themes";
import { AuthProvider } from "@/lib/AuthContext";           // ← new
import ProtectedRoute from "@/components/ProtectedRoute";   // ← new
import Index from "./pages/Index";
import SignIn from "./pages/SignIn";                         // ← new
import CloudRemovalUpload from "./pages/CloudRemovalUpload";
import ColorProcessingUpload from "./pages/ColorProcessingUpload";
import NotFound from "./pages/NotFound";
import Contact from "./pages/Contact";


const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <AuthProvider>                                         {/* ← new */}
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              <Route path="/signin" element={<SignIn />} />
              <Route path="/" element={<ProtectedRoute><Index /></ProtectedRoute>} />
              <Route path="/cloud-removal-upload" element={<ProtectedRoute><CloudRemovalUpload /></ProtectedRoute>} />
              <Route path="/color-processing-upload" element={<ProtectedRoute><ColorProcessingUpload /></ProtectedRoute>} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </TooltipProvider>
      </AuthProvider>                                        {/* ← new */}
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;