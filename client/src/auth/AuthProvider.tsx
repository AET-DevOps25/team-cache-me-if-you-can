/* eslint-disable react-refresh/only-export-components */
import { useContext, createContext, useState, ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { message } from "antd";
import { LoginFormData } from "../models/LoginFormData";

interface AuthProviderProps {
  children: ReactNode;
}

interface AuthContextType {
  token: string;
  user: string | null;
  loginAction: (formData: LoginFormData) => Promise<boolean>;
  logOut: () => void;
}
const AuthContext = createContext<AuthContextType | undefined>(undefined);

const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState(localStorage.getItem("name") || null);
  const [token, setToken] = useState(localStorage.getItem("site") || "");
  const navigate = useNavigate();
  const apiUrl = import.meta.env.VITE_API_URL;
  const loginAction = async (formData: LoginFormData): Promise<boolean> => {
    try {
      const response = await fetch(`${apiUrl}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        // Handle 401 unauthorized, etc.
        const errorData = await response.json();
        console.error("Login failed:", errorData);
        return false;
      }

      const data = await response.json();
      message.success("Login successful!");
      setUser(formData.username);
      setToken(data.token);
      localStorage.setItem("username", formData.username);
      localStorage.setItem("authToken", data.token);

      return true;
    } catch (err) {
      console.error("Network error:", err);
      message.error("Login failed. Please check your username or password.");
      return false;
    }
  };

  const logOut = () => {
    navigate("/login");
    setUser(null);
    setToken("");
    localStorage.removeItem("username");
    sessionStorage.removeItem("username");
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
