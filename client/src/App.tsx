import GroupInfo from "./pages/group_info/GroupInfo";
import Home from "./pages/home/Home";
import Login from "./auth/Login";
import Register from "./auth/Register";
import AuthProvider from "./auth/AuthProvider";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <AuthProvider>
        <Home />
      </AuthProvider>
    ),
  },
  {
    path: "/group/:groupName",
    element: (
      <AuthProvider>
        <GroupInfo />
      </AuthProvider>
    ),
  },
  {
    path: "/login",
    element: (
      <AuthProvider>
        <Login />
      </AuthProvider>
    ),
  },
  {
    path: "/register",
    element: (
      <AuthProvider>
        <Register />
      </AuthProvider>
    ),
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
