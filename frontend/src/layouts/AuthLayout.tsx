import { Outlet } from "react-router-dom";

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-slate-100 px-4 py-8 text-slate-950 sm:px-6">
      <Outlet />
    </div>
  );
}
