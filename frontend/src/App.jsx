import React, { useState, useEffect } from "react";
import { ChatProvider } from "./context/ChatContext";
import { Home } from "./pages/Home";
import { Admin } from "./pages/Admin";
import { ChatbotLauncher } from "./components/chatbot/ChatbotLauncher";
import { ChatbotWindow } from "./components/chatbot/ChatbotWindow";

export default function App() {
  const [currentView, setCurrentView] = useState(() => {
    if (typeof window !== "undefined") {
      if (
        window.location.pathname.startsWith("/admin") ||
        window.location.hash.toLowerCase() === "#admin"
      ) {
        return "admin";
      }
    }
    return "home";
  });

  // Listen for hashchange
  useEffect(() => {
    const handleHashChange = () => {
      if (window.location.hash.toLowerCase() === "#admin") {
        setCurrentView("admin");
      } else {
        setCurrentView("home");
      }
    };
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  const navigateToAdmin = () => {
    if (typeof window !== "undefined") {
      window.location.hash = "admin";
    }
    setCurrentView("admin");
  };

  const navigateToHome = () => {
    if (typeof window !== "undefined") {
      window.location.hash = "";
    }
    setCurrentView("home");
  };

  return (
    <ChatProvider>
      {currentView === "admin" ? (
        <Admin onBackToHome={navigateToHome} />
      ) : (
        <>
          <Home onNavigateAdmin={navigateToAdmin} />
          <ChatbotLauncher />
          <ChatbotWindow />
        </>
      )}
    </ChatProvider>
  );
}
