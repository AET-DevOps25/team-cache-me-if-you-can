// src/auth/ProtectedRoute.tsx
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./AuthProvider";
import React from "react";

const ProtectedRoute = () => {
    const { token } = useAuth();

    // If the user is not authenticated (no token), redirect them to the login page
    if (!token) {
        return <Navigate to="/login" />;
    }

    // If they are authenticated, render the child route (e.g., Home, GroupPage)
    return <Outlet />;
};

export default ProtectedRoute;