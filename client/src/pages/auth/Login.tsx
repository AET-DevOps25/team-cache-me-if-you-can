import React, { useState } from "react";
import { Eye, EyeOff, Mail, Lock } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Navigator from "../../nav/Navigator";
import "./login.css";

interface LoginFormData {
  email: string;
  password: string;
}

export default function Login() {
  const [formData, setFormData] = useState<LoginFormData>({
    email: "",
    password: "",
  });
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const navigate = useNavigate();

  const validateAuth = async (formData: LoginFormData): Promise<boolean> => {
    // TODO: fetch authentication data from server
    if (!formData) {
      return false;
    }
    return true;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (): Promise<void> => {
    setIsLoading(true);
    const isValid = await validateAuth(formData);
    if (isValid) {
      navigate("/");
    } else {
      alert("email or password is not right!");
      setFormData({
        email: "",
        password: "",
      });
      setIsLoading(false);
    }
  };

  return (
    <>
      <Navigator />
      <div className="login-container">
        <div className="login-card">
          <div className="login-header">
            <h1 className="login-title">Sign in to your account</h1>
          </div>

          <div className="login-form">
            <div className="form-group">
              <label htmlFor="email" className="form-label">
                Email Address
              </label>
              <div className="input-wrapper">
                <Mail className="input-icon" />
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="Enter your email"
                  autoComplete="email"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">
                Password
              </label>
              <div className="input-wrapper">
                <Lock className="input-icon" />
                <input
                  type={showPassword ? "text" : "password"}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="password-toggle"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <EyeOff className="toggle-icon" />
                  ) : (
                    <Eye className="toggle-icon" />
                  )}
                </button>
              </div>
            </div>

            <button
              type="button"
              onClick={handleSubmit}
              disabled={isLoading}
              className="submit-button"
            >
              {isLoading ? (
                <div className="loading-content">
                  <div className="spinner"></div>
                  Signing In...
                </div>
              ) : (
                "Sign In"
              )}
            </button>
          </div>

          <div className="login-footer">
            <div className="switch-mode">
              <p className="switch-text">
                Don't have an account?{" "}
                <button
                  onClick={() => navigate("/register")}
                  className="switch-button"
                >
                  Sign up
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
