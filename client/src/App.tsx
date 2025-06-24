import GroupPage from "./pages/group_info/GroupPage";
import Home from "./pages/home/Home";
import Login from "./auth/Login";
import Register from "./auth/Register";
import AuthProvider from "./auth/AuthProvider";
import GroupProvider from "./pages/home/components/GroupProvider";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import ProtectedRoute from "./auth/ProtectedRoute";

const router = createBrowserRouter([
  // Public routes
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/register",
    element: <Register />,
  },

  // Protected routes
  {
    path: "/",
    element: <ProtectedRoute />,
    children: [
      {
        path: "/",
        element: (
            <GroupProvider>
              <Home />
            </GroupProvider>
        ),
      },
      {
        path: "/group/:groupId",
        element: (
            <GroupProvider>
              <GroupPage />
            </GroupProvider>
        ),
      },
    ],
  },

  // Redirect all unmatched paths to login
  {
    path: "*",
    element: <Navigate to="/login" replace />,
  }
]);

function App() {
  return (
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
  );
}

export default App;