import { useNavigate } from "react-router-dom";

import useAuth from "../hooks/useAuth";

export default function Navbar() {
  const navigate = useNavigate();
  const { logout } = useAuth();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <header className="border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-brand-600">
            Visualizer Assembly
          </p>
          <h1 className="text-lg font-semibold text-slate-900">Painel</h1>
        </div>
        <button
          type="button"
          onClick={handleLogout}
          className="rounded-full border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-400 hover:bg-slate-100"
        >
          Logout
        </button>
      </div>
    </header>
  );
}
