import {
  useContext,
  createContext,
  useState,
  ReactNode,
  useEffect,
} from "react";
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
  isTokenValidating: boolean; // NEW: Add this to context
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState(localStorage.getItem("username") || null);
  const [token, setToken] = useState(localStorage.getItem("authToken") || null);
  const [isTokenValidating, setIsTokenValidating] = useState(true); // NEW: Initial state is true

  useEffect(() => {
    const validateToken = async () => {
      const storedToken = localStorage.getItem("authToken");
      const storedUsername = localStorage.getItem("username");

      if (!storedToken) {
        setIsTokenValidating(false); // No token, validation done.
        return;
      }

      try {
        const response = await fetch("/api/auth/validate", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${storedToken}`,
          },
        });

        if (response.ok) {
          // If token is valid, set user and token (they might already be set but ensures consistency)
          setUser(storedUsername);
          setToken(storedToken);
          message.success("Session re-validated successfully!"); // Optional: user feedback
        } else {
          // If token is invalid/expired, clear local storage
          localStorage.removeItem("username");
          localStorage.removeItem("authToken");
          setUser(null);
          setToken(null);
          message.info("Session expired or invalid. Please log in again.");
        }
      } catch (error) {
        console.error("Token validation error:", error);
        message.error("Failed to validate session. Please log in again.");
        localStorage.removeItem("username");
        localStorage.removeItem("authToken");
        setUser(null);
        setToken(null);
      } finally {
        setIsTokenValidating(false); // Validation complete, regardless of outcome
      }
    };

    validateToken();
  }, []); // Run only on mount

  const loginAction = async (formData: LoginFormData): Promise<boolean> => {
    setIsTokenValidating(true); // Set to true during login
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
    } finally {
      setIsTokenValidating(false); // Set to false after login attempt
    }
  };

  const logOut = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("username");
    localStorage.removeItem("authToken");
    message.info("You have been logged out."); // Optional: user feedback
    // No need to set isTokenValidating here, as we are explicitly logging out.
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        loginAction,
        logOut,
        isTokenValidating,
      }}
    >
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
