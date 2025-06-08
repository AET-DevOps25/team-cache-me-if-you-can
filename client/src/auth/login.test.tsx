/* eslint-disable @typescript-eslint/no-require-imports */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Login from "./Login";
import { message } from "antd";

// Mock the dependencies
jest.mock("./AuthProvider", () => ({
  useAuth: jest.fn(),
}));
jest.mock("react-router-dom", () => ({
  useNavigate: jest.fn(),
}));
jest.mock("../nav/Navigator", () => () => <div>Navigator</div>);

jest.mock("antd", () => ({
  message: {
    success: jest.fn(),
    error: jest.fn(),
    warning: jest.fn(),
    info: jest.fn(),
  },
}));

describe("Login Component", () => {
  const mockLoginAction = jest.fn();
  const mockNavigate = jest.fn();

  beforeEach(() => {
    jest.spyOn(require("./AuthProvider"), "useAuth").mockReturnValue({
      loginAction: mockLoginAction,
    });
    jest
      .spyOn(require("react-router-dom"), "useNavigate")
      .mockReturnValue(mockNavigate);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("navigates to home page on successful login", async () => {
    mockLoginAction.mockResolvedValue(true);
    render(<Login />);

    const submitButton = screen.getByRole("button", { name: "Sign In" });
    fireEvent.change(screen.getByPlaceholderText("Enter your username"), {
      target: { value: "testuser" },
    });
    fireEvent.change(screen.getByPlaceholderText("Enter your password"), {
      target: { value: "testpass" },
    });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockLoginAction).toHaveBeenCalledWith({
        username: "testuser",
        password: "testpass",
      });
      expect(mockNavigate).toHaveBeenCalledWith("/");
    });
  });

  it("shows error and resets form on failed login", async () => {
    mockLoginAction.mockResolvedValue(false);

    render(<Login />);

    const usernameInput = screen.getByPlaceholderText("Enter your username");
    const passwordInput = screen.getByPlaceholderText("Enter your password");
    const submitButton = screen.getByRole("button", { name: "Sign In" });

    fireEvent.change(usernameInput, { target: { value: "testuser" } });
    fireEvent.change(passwordInput, { target: { value: "testpass" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(message.error).toHaveBeenCalledWith(
        "username or password is not right!"
      );
      expect(usernameInput).toHaveValue("");
      expect(passwordInput).toHaveValue("");
    });
  });
});
