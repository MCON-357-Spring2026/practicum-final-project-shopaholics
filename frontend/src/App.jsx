import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Catalog from "./pages/Catalog";
import FittingRoom from "./pages/FittingRoom";
import ProtectedRoute from "./components/ProtectedRoute";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/catalog" element={<Catalog />} />
        <Route path="/fitting-room" element={<FittingRoom />} />
      </Route>

      <Route path="*" element={<Navigate to="/catalog" replace />} />
    </Routes>
  );
}
