// src/nav/Navigator.tsx
import "./style_nav.css";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

export default function Navigator() {
    const navigate = useNavigate();
    const auth = useAuth();

    function logout() {
        auth.logOut();
        navigate("/login"); // ADD THIS LINE: Navigator now handles the navigation after logout
    }

    return (
        <div className="Nav">
            <div className="topLeft">
                <img
                    src="/study_groups_icon.svg"
                    alt="StudySync Logo"
                    className="logo-icon"
                />
                <h1 className="logo" onClick={() => navigate("/")}>
                    StudySync
                </h1>
            </div>
            <div className="topRight">
                {auth.user ? (
                    <>
                        <span
                            className="nav-link username-link"
                            onClick={() => navigate("/")}
                            style={{ cursor: "pointer" }}
                        >
                          {auth.user}
                        </span>
                        <span className="link-separator"> | </span>
                        <a onClick={logout} className="nav-link logOut"> {/* Changed onClick to call the new logout function */}
                            Log out
                        </a>
                    </>
                ) : (
                    <>
                        <Link to="/login" className="nav-link">
                            Login
                        </Link>
                        <span className="link-separator"> | </span>
                        <Link to="/register" className="nav-link">
                            Register
                        </Link>
                    </>
                )}
            </div>
        </div>
    );
}