import { Navigate, Route, Routes } from "react-router-dom";
import { getToken } from "./api/client";
import Chat from "./pages/Chat";
import Conversations from "./pages/Conversations";
import Login from "./pages/Login";

function RequireAuth({ children }: { children: JSX.Element }) {
  if (!getToken()) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<RequireAuth><Conversations /></RequireAuth>} />
      <Route path="/chat/:id" element={<RequireAuth><Chat /></RequireAuth>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
