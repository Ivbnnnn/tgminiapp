import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { authApi } from "../api/authApi";

const navItems = [
  { to: "/", label: "Обзор" },
  { to: "/calculations", label: "Расчеты" },
  { to: "/finance", label: "Финансы" },
  { to: "/profile", label: "Профиль" },
];

export default function MainLayout() {
  const navigate = useNavigate();

  const handleLogout = async () => {
    await authApi.logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="min-h-screen bg-slate-100 text-slate-950">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-3 py-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
          <div className="min-w-0">
            <p className="text-sm font-medium text-blue-700">ОСАГО кабинет</p>
            <h1 className="truncate text-lg font-semibold sm:text-xl">
              Агентская панель
            </h1>
          </div>

          <div className="flex w-full min-w-0  gap-2 lg:w-auto xl:flex-row xl:items-center">
            <nav className=" flex min-w-0 flex-1  overflow-x-auto px-1 pb-1 sm:flex-wrap xl:overflow-visible xl:pb-0">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === "/"}
                  className={({ isActive }) =>
                    [
                      "shrink-0 rounded-md px-3 py-2 text-sm font-medium transition",
                      isActive
                        ? "bg-blue-600 text-white"
                        : "text-slate-600 hover:bg-slate-100 hover:text-slate-950",
                    ].join(" ")
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>

            <button
              type="button"
              onClick={handleLogout}
               className="shrink-0 rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              Выйти
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-3 py-4 sm:px-6 sm:py-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}
