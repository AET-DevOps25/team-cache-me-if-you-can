import React, { useState } from "react";
import { Eye, EyeOff, User, Lock, School } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { message } from "antd";
import Navigator from "../nav/Navigator";
import "./Register.css";
import { getEnv } from "../utils/env";

interface RegisterFormData {
  username: string;
  university: string;
  password: string;
  confirmPassword: string;
}

interface RegisterFormErrors {
  username?: string;
  university?: string;
  password?: string;
  confirmPassword?: string;
}

interface RegisterProps {
  onSwitchToLogin?: () => void;
  onRegisterSuccess?: (username: string, email: string) => void;
}

const Register: React.FC<RegisterProps> = () => {
  const [formData, setFormData] = useState<RegisterFormData>({
    username: "",
    university: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState<RegisterFormErrors>({});
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [showConfirmPassword, setShowConfirmPassword] =
    useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const navigate = useNavigate();
  const { apiUrl } = getEnv();

  const validatePassword = (
    password: string
  ): { isValid: boolean; message?: string } => {
    if (password.length < 6) {
      return {
        isValid: false,
        message: "Password must be at least 6 characters",
      };
    }
    if (!/(?=.*[a-z])/.test(password)) {
      return {
        isValid: false,
        message: "Password must contain at least one lowercase letter",
      };
    }
    if (!/(?=.*\d)/.test(password)) {
      return {
        isValid: false,
        message: "Password must contain at least one number",
      };
    }
    return { isValid: true };
  };

  const validateForm = (): boolean => {
    const newErrors: RegisterFormErrors = {};

    // Name validation
    if (!formData.username.trim()) {
      newErrors.username = "User name is required";
    } else if (formData.username.trim().length < 2) {
      newErrors.username = "Name must be at least 2 characters";
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = "Password is required";
    } else {
      const passwordCheck = validatePassword(formData.password);
      if (!passwordCheck.isValid) {
        newErrors.password = passwordCheck.message;
      }
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = "Please confirm your password";
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear error when user starts typing
    if (errors[name as keyof RegisterFormErrors]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  const handleSubmit = async (): Promise<void> => {
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${apiUrl}/api/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password,
          university: formData.university,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        if (data.message === "Username already exists") {
          setErrors({ ...errors, username: data.message });
        } else {
          message.error(data.message || "Registration failed");
        }
        setIsLoading(false);
        return;
      }

      message.success(data.message || "Registration successful");
      navigate("/");
    } catch (error) {
      console.error("Registration error:", error);
      message.error("An error occurred during registration");
    } finally {
      setIsLoading(false);
    }

    navigate("/");
    setIsLoading(false);
  };

  return (
    <>
      <Navigator />
      <div className="register-container">
        <div className="register-card">
          <div className="register-header">
            <h1 className="register-title">Create Account</h1>
          </div>

          <div className="register-form">
            <div className="form-group">
              <label htmlFor="name" className="form-label">
                User Name
              </label>
              <div className="input-wrapper">
                <User className="input-icon" />
                <input
                  type="text"
                  id="name"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className={`form-input ${
                    errors.username ? "input-error" : ""
                  }`}
                  placeholder="Enter your full name"
                  autoComplete="name"
                />
              </div>
              {errors.username && (
                <p className="error-message">{errors.username}</p>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="university" className="form-label">
                University
              </label>
              <div className="input-wrapper">
                <School className="input-icon" />
                <input
                  type="text"
                  id="university"
                  name="university"
                  value={formData.university}
                  onChange={handleInputChange}
                  className={`form-input ${
                    errors.university ? "input-error" : ""
                  }`}
                  placeholder="Enter your university"
                  autoComplete="university"
                />
              </div>
              {errors.university && (
                <p className="error-message">{errors.university}</p>
              )}
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
                  className={`form-input ${
                    errors.password ? "input-error" : ""
                  }`}
                  placeholder="Create a password"
                  autoComplete="new-password"
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
              {errors.password && (
                <p className="error-message">{errors.password}</p>
              )}
              <div className="password-requirements">
                <ul className="requirements-list">
                  <li
                    className={
                      formData.password.length >= 6 ? "requirement-met" : ""
                    }
                  >
                    At least 6 characters
                  </li>
                  <li
                    className={
                      /(?=.*[a-z])/.test(formData.password)
                        ? "requirement-met"
                        : ""
                    }
                  >
                    One lowercase letter
                  </li>
                  <li
                    className={
                      /(?=.*\d)/.test(formData.password)
                        ? "requirement-met"
                        : ""
                    }
                  >
                    One number
                  </li>
                </ul>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword" className="form-label">
                Confirm Password
              </label>
              <div className="input-wrapper">
                <Lock className="input-icon" />
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className={`form-input ${
                    errors.confirmPassword ? "input-error" : ""
                  }`}
                  placeholder="Confirm your password"
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="password-toggle"
                  aria-label={
                    showConfirmPassword ? "Hide password" : "Show password"
                  }
                >
                  {showConfirmPassword ? (
                    <EyeOff className="toggle-icon" />
                  ) : (
                    <Eye className="toggle-icon" />
                  )}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="error-message">{errors.confirmPassword}</p>
              )}
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
                  Creating Account...
                </div>
              ) : (
                "Create Account"
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default Register;
