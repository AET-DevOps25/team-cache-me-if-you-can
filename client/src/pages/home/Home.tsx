import Navigator from "../../nav/Navigator";
import Group from "./components/Group";
import { useEffect } from "react";
import { useAuth } from "../../auth/AuthProvider";
import { useLocation, useNavigate } from "react-router-dom";

export default function Home() {
    const auth = useAuth();
    const location = useLocation();
    const navigate = useNavigate();

    useEffect(() => {
        // If the user is validating their token, wait for it to complete.
        // If token validation fails, AuthProvider will clear the token and user.
        if (auth.isTokenValidating) {
            return;
        }

        // Check if we have a redirect location from ProtectedRoute
        const from = location.state?.from?.pathname || "/";

        // If user is not authenticated, redirect to login
        if (!auth.token) {
            navigate("/login", { state: { from }, replace: true });
        }
    }, [auth.token, location.state, navigate, auth.isTokenValidating]); // Add auth.isTokenValidating to dependencies

    // Render loading state while token is validating
    if (auth.isTokenValidating) {
        return (
            <>
                <Navigator />
                <div style={{ padding: '20px', textAlign: 'center', fontSize: '1.2em' }}>
                    Validating session...
                </div>
            </>
        );
    }

    // Only render Group if token is valid (or if we're on public paths)
    // The ProtectedRoute ensures this Home component is only rendered if authenticated
    return (
        <>
            <Navigator />
            <Group />
        </>
    );
}