import GroupPage from "./pages/group_info/GroupPage";
import Home from "./pages/home/Home";
import Login from "./auth/Login";
import Register from "./auth/Register";
import AuthProvider from "./auth/AuthProvider";
import GroupProvider from "./pages/home/components/GroupProvider";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import ProtectedRoute from "./auth/ProtectedRoute"; // 1. Import the ProtectedRoute

const router = createBrowserRouter([
  // 2. Define public routes that anyone can access
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/register",
    element: <Register />,
  },

  // 3. Define the protected routes under a parent guard route
  {
    path: "/",
    element: <ProtectedRoute />, // This component now guards all its children
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
      // You can add more protected routes here
      // For example: { path: "/profile", element: <ProfilePage /> }
    ],
  },
]);

function App() {
  // 4. Wrap the entire app in AuthProvider so the auth state is globally available
  return (
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
  );
}

export default App;