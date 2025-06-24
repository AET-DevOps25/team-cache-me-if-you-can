import GroupPage from "./pages/group_info/GroupPage";
import Home from "./pages/home/Home";
import Login from "./auth/Login";
import Register from "./auth/Register";
import AuthProvider from "./auth/AuthProvider";
import GroupProvider from "./pages/home/components/GroupProvider";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <AuthProvider>
        <GroupProvider>
          <Home />
        </GroupProvider>
      </AuthProvider>
    ),
  },
  {
    path: "/group/:groupId",
    element: (
      <AuthProvider>
        <GroupProvider>
          <GroupPage />
        </GroupProvider>
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
