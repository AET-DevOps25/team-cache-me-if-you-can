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
        // Check if we have a redirect location from ProtectedRoute
        const from = location.state?.from?.pathname || "/";

        // If user is not authenticated, redirect to login
        if (!auth.token) {
            navigate("/login", { state: { from }, replace: true });
        }
    }, [auth.token, location.state, navigate]);

    return (
        <>
            <Navigator />
            <Group />
        </>
    );
}