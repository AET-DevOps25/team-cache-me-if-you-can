/* eslint-disable react-refresh/only-export-components */
import { useContext, createContext, useState, ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { message } from "antd";
import { LoginFormData } from "../models/LoginFormData";

interface AuthProviderProps {
  children: ReactNode;
}

interface AuthContextType {
  token: string | null; // Can be null when logged out
  user: string | null;
  loginAction: (formData: LoginFormData) => Promise<boolean>;
  logOut: () => void;
}
const AuthContext = createContext<AuthContextType | undefined>(undefined);

const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  // --- FIX 1: Use consistent localStorage keys ---
  // Initialize state directly from the same keys we save to.
  const [user, setUser] = useState(localStorage.getItem("username") || null);
  const [token, setToken] = useState(localStorage.getItem("authToken") || null);
  const navigate = useNavigate();

  const loginAction = async (formData: LoginFormData): Promise<boolean> => {
    try {
      // The API endpoint is proxied, so the full URL isn't needed here.
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Login failed:", errorData);
        return false;
      }

      const data = await response.json();
      message.success("Login successful!");

      // --- FIX 2: Set state and localStorage with consistent keys ---
      setUser(formData.username);
      setToken(data.token);
      localStorage.setItem("username", formData.username);
      localStorage.setItem("authToken", data.token); // Use "authToken" consistently

      return true;
    } catch (err) {
      console.error("Network error:", err);
      message.error("Login failed. Please check your username or password.");
      return false;
    }
  };

  const logOut = () => {
    setUser(null);
    setToken(null);
    // --- FIX 3: Remove all auth-related items from localStorage on logout ---
    localStorage.removeItem("username");
    localStorage.removeItem("authToken"); // Ensure token is removed
    navigate("/login"); // Navigate to login page after logout
  };

  return (
      <AuthContext.Provider value={{ token, user, loginAction, logOut }}>
        {children}
      </AuthContext.Provider>
  );
};

export default AuthProvider;

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};