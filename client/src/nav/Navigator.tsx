import "./style_nav.css";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

export default function Navigator() {
  const navigate = useNavigate();
  const auth = useAuth();

  function logout() {
    auth.logOut();
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
            <Link to="/profile" className="nav-link">
              {auth.user}
            </Link>
            <span className="link-separator"> | </span>
            <a onClick={logout} className="nav-link logOut">
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
