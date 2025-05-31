/* eslint-disable @typescript-eslint/no-require-imports */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import Register from "./Register";
import { message } from "antd";

// Mock the dependencies
global.fetch = jest.fn();
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

describe("Register Component", () => {
  const mockNavigate = jest.fn();

  beforeEach(() => {
    global.fetch = jest.fn();
    jest
      .spyOn(require("react-router-dom"), "useNavigate")
      .mockReturnValue(mockNavigate);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("validates form fields before submission", async () => {
    render(<Register />);

    fireEvent.click(screen.getByRole("button", { name: "Create Account" }));

    await waitFor(() => {
      expect(
        screen.getAllByText("User name is required").length
      ).toBeGreaterThan(0);
      expect(
        screen.getAllByText("Password is required").length
      ).toBeGreaterThan(0);
      expect(
        screen.getByText("Please confirm your password")
      ).toBeInTheDocument();
    });
  });

  it("validates username, name must be at least 2 characters", async () => {
    render(<Register />);

    fireEvent.change(screen.getByPlaceholderText("Enter your full name"), {
      target: { value: "1" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Create Account" }));

    await waitFor(() => {
      expect(
        screen.getByText("Name must be at least 2 characters")
      ).toBeInTheDocument();
    });
  });

  it("validates password, password must be at least 6 characters", async () => {
    render(<Register />);

    fireEvent.change(screen.getByPlaceholderText("Create a password"), {
      target: { value: "123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Create Account" }));

    await waitFor(() => {
      expect(
        screen.getByText("Password must be at least 6 characters")
      ).toBeInTheDocument();
    });
  });

  it("validates password, password must contain at least one lowercase letter", async () => {
    render(<Register />);

    fireEvent.change(screen.getByPlaceholderText("Create a password"), {
      target: { value: "123456" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Create Account" }));

    await waitFor(() => {
      expect(
        screen.getByText("Password must contain at least one lowercase letter")
      ).toBeInTheDocument();
    });
  });

  it("validates password, password must contain at least one number", async () => {
    render(<Register />);

    fireEvent.change(screen.getByPlaceholderText("Create a password"), {
      target: { value: "abcdefg" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Create Account" }));

    await waitFor(() => {
      expect(
        screen.getByText("Password must contain at least one number")
      ).toBeInTheDocument();
    });
  });

  it("shows error when passwords do not match", async () => {
    render(<Register />);

    fireEvent.change(screen.getByPlaceholderText("Create a password"), {
      target: { value: "Pass123" },
    });
    fireEvent.change(screen.getByPlaceholderText("Confirm your password"), {
      target: { value: "Different123" },
    });

    fireEvent.click(screen.getByRole("button", { name: "Create Account" }));

    await waitFor(() => {
      expect(screen.getByText("Passwords do not match")).toBeInTheDocument();
    });
  });

  it("submits the form successfully", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ message: "Registration successful" }),
    });

    render(<Register />);

    fireEvent.change(screen.getByPlaceholderText("Enter your full name"), {
      target: { value: "Test User" },
    });
    fireEvent.change(screen.getByPlaceholderText("Enter your university"), {
      target: { value: "Test University" },
    });
    fireEvent.change(screen.getByPlaceholderText("Create a password"), {
      target: { value: "Pass123" },
    });
    fireEvent.change(screen.getByPlaceholderText("Confirm your password"), {
      target: { value: "Pass123" },
    });

    fireEvent.click(screen.getByRole("button", { name: "Create Account" }));
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(message.success).toHaveBeenCalledWith("Registration successful");
      expect(mockNavigate).toHaveBeenCalledWith("/");
    });
  });

  it("handles username already exists error", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ message: "Username already exists" }),
    });

    render(<Register />);

    fireEvent.change(screen.getByPlaceholderText("Enter your full name"), {
      target: { value: "Existing User" },
    });
    fireEvent.change(screen.getByPlaceholderText("Enter your university"), {
      target: { value: "Test University" },
    });
    fireEvent.change(screen.getByPlaceholderText("Create a password"), {
      target: { value: "Pass123" },
    });
    fireEvent.change(screen.getByPlaceholderText("Confirm your password"), {
      target: { value: "Pass123" },
    });

    fireEvent.click(screen.getByRole("button", { name: "Create Account" }));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(screen.getByText("Username already exists")).toBeInTheDocument();
      expect(message.error).not.toHaveBeenCalled();
    });
  });
});
