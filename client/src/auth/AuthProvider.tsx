import { useContext, createContext, useState, ReactNode, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { message } from "antd";
import { LoginFormData } from "../models/LoginFormData";

interface AuthProviderProps {
  children: ReactNode;
}

interface AuthContextType {
  token: string | null;
  user: string | null;
  loginAction: (formData: LoginFormData) => Promise<boolean>;
  logOut: () => void;
  isTokenValidating: boolean; // Add loading state for token validation
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState(localStorage.getItem("username") || null);
  const [token, setToken] = useState(localStorage.getItem("authToken") || null);
  const [isTokenValidating, setIsTokenValidating] = useState(true); // Loading state
  const navigate = useNavigate();

  // Validate token on component mount
  useEffect(() => {
    const validateToken = async () => {
      const storedToken = localStorage.getItem("authToken");

      if (!storedToken) {
        setIsTokenValidating(false);
        return;
      }

      try {
        const response = await fetch("/api/auth/validate", {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${storedToken}`
          }
        });

        if (response.ok) {
          const user = localStorage.getItem("username");
          setUser(user);
          setToken(storedToken);
        } else {
          // Token is invalid - clear storage
          localStorage.removeItem("username");
          localStorage.removeItem("authToken");
        }
      } catch (error) {
        console.error("Token validation error:", error);
        message.error("Failed to validate session");
      } finally {
        setIsTokenValidating(false);
      }
    };

    validateToken();
  }, []);

  const loginAction = async (formData: LoginFormData): Promise<boolean> => {
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        message.error(errorData.message || "Login failed");
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
      message.error("Login failed. Please try again later.");
      return false;
    }
  };

  const logOut = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("username");
    localStorage.removeItem("authToken");
    navigate("/login");
  };

  return (
      <AuthContext.Provider value={{
        token,
        user,
        loginAction,
        logOut,
        isTokenValidating // Expose validation state
      }}>
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