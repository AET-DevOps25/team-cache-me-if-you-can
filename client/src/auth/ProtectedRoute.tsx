import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "./AuthProvider";

const ProtectedRoute = () => {
    const { token, isTokenValidating } = useAuth();
    const location = useLocation();

    // Show loading state while validating token
    if (isTokenValidating) {
        return <div>Validating session...</div>; // Or a spinner
    }

    if (!token) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return <Outlet />;
};

export default ProtectedRoute;