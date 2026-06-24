import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Spin } from "antd";
import { AuthProvider, useAuth } from "./store/auth";
import BasicLayout from "./layouts/BasicLayout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Vehicles from "./pages/Vehicles";
import Claims from "./pages/Claims";
import ClaimDetail from "./pages/ClaimDetail";
import Documents from "./pages/Documents";
import ServiceOrders from "./pages/ServiceOrders";
import Parts from "./pages/Parts";
import Assistant from "./pages/Assistant";
import ChatApp from "./chat/ChatApp";

function RequireAuth({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
        <Spin size="large" />
      </div>
    );
  }
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return children;
}

function Routed() {
  return (
    <Routes>
      <Route path="/chat" element={<ChatApp />} />
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <BasicLayout />
          </RequireAuth>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="vehicles" element={<Vehicles />} />
        <Route path="claims" element={<Claims />} />
        <Route path="claims/:id" element={<ClaimDetail />} />
        <Route path="documents" element={<Documents />} />
        <Route path="orders" element={<ServiceOrders />} />
        <Route path="parts" element={<Parts />} />
        <Route path="assistant" element={<Assistant />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Routed />
    </AuthProvider>
  );
}
