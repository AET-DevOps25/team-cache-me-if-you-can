import "./style_nav.css";
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";

export default function Navigator() {
  const [username, setUsername] = useState(null);
  const navigate = useNavigate();

  //TODO: get authentication info from api
  //const getUserName = async () => {
  //  const response = await fetch(`/api/auth/${id}`);
  //  const result = await response.json();};

  function logout() {
    navigate("/");
    setUsername(null);
  }

  return (
    <div className="Nav">
      <div className="topLeft">
        <h1 className="logo" onClick={() => navigate("/")}>
          StudySync
        </h1>
      </div>
      <div className="topRight">
        {username ? (
          <>
            <Link to="/profile" className="nav-link">
              {username}
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
