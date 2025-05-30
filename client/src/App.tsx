import GroupInfo from "./pages/group_info/GroupInfo";
import Home from "./pages/home/Home";
import Login from "./auth/Login";
import Register from "./auth/Register";
import AuthProvider from "./auth/AuthProvider";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Home />,
  },
  {
    path: "/group/:groupName",
    element: <GroupInfo />,
  },
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/register",
    element: <Register />,
  },
]);

function App() {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  );
}

export default App;
