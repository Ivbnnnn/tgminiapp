import { useState, type ChangeEvent, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { authApi, type LoginRequest, type SignUpRequest } from "../api/authApi";

const inputClass =
  "w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100";

function dateToDateTime(value: string) {
  return value ? `${value}T00:00:00.000Z` : value;
}

function getStatusDescription(status: string) {
  if (status === "individual") {
    return "Физическое лицо не сможет создавать расчеты, пока статус не изменится.";
  }

  if (status === "self_employed") {
    return "Для самозанятого нужен ИНН.";
  }

  return "Для ИП нужны ИНН и ОГРНИП.";
}

export default function Login() {
  const navigate = useNavigate();

  const [isLoginPage, setIsLoginPage] = useState(true);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const [loginData, setLoginData] = useState<LoginRequest>({
    email: "",
    password: "",
  });

  const [signupData, setSignupData] = useState<SignUpRequest>({
    lastname: "",
    firstname: "",
    middlename: "",
    phone: "",
    email: "",
    passport_serial: "",
    passport_number: "",
    passport_issue_date: "",
    passport_issuer: "",
    passport_code: "",
    birthdate: "",
    status: "self_employed",
    inn: "",
    ogrnip: "",
    password: "",
  });

  const showInn = signupData.status !== "individual";
  const showOgrnip = signupData.status === "ip";

  const handleLoginChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setLoginData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSignupChange = (
    event: ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = event.target;

    setSignupData((prev) => {
      if (name !== "status") {
        return { ...prev, [name]: value };
      }

      return {
        ...prev,
        status: value,
        inn: value === "individual" ? "" : prev.inn,
        ogrnip: value === "ip" ? prev.ogrnip : "",
      };
    });
  };

  const togglePage = () => {
    setError("");
    setIsLoginPage((prev) => !prev);
  };

  const handleLoginSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await authApi.login(loginData);
      navigate("/", { replace: true });
    } catch {
      setError("Неверный email или пароль");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignupSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await authApi.signup({
        ...signupData,
        inn: showInn ? signupData.inn : "",
        ogrnip: showOgrnip ? signupData.ogrnip : "",
        passport_issue_date: dateToDateTime(signupData.passport_issue_date),
      });
      navigate("/", { replace: true });
    } catch {
      setError("Не удалось зарегистрироваться");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto grid max-w-5xl gap-4 sm:gap-6 lg:grid-cols-[0.9fr_1.1fr]">
      <section className="rounded-lg border border-slate-200 bg-white p-6">
        <p className="text-sm font-medium text-blue-700">ОСАГО кабинет</p>
        <h1 className="mt-2 text-2xl font-semibold sm:text-3xl">
          {isLoginPage ? "Вход для агента" : "Регистрация агента"}
        </h1>
        <p className="mt-4 text-sm leading-6 text-slate-600">
          Управление расчетами, оплатами полисов, комиссиями и выплатами в одном
          рабочем кабинете.
        </p>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-6">
        {error && (
          <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {isLoginPage ? (
          <form onSubmit={handleLoginSubmit} className="grid gap-4">
            <label className="grid gap-1 text-sm font-medium">
              Email
              <input
                name="email"
                type="email"
                value={loginData.email}
                onChange={handleLoginChange}
                className={inputClass}
                required
              />
            </label>

            <label className="grid gap-1 text-sm font-medium">
              Пароль
              <input
                name="password"
                type="password"
                value={loginData.password}
                onChange={handleLoginChange}
                className={inputClass}
                required
              />
            </label>

            <button
              type="submit"
              disabled={isLoading}
              className="rounded-md bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700 disabled:bg-slate-300"
            >
              {isLoading ? "Вход..." : "Войти"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleSignupSubmit} className="grid gap-4">
            <div className="grid gap-4 md:grid-cols-3">
              <label className="grid gap-1 text-sm font-medium">
                Фамилия
                <input
                  name="lastname"
                  value={signupData.lastname}
                  onChange={handleSignupChange}
                  className={inputClass}
                  required
                />
              </label>
              <label className="grid gap-1 text-sm font-medium">
                Имя
                <input
                  name="firstname"
                  value={signupData.firstname}
                  onChange={handleSignupChange}
                  className={inputClass}
                  required
                />
              </label>
              <label className="grid gap-1 text-sm font-medium">
                Отчество
                <input
                  name="middlename"
                  value={signupData.middlename}
                  onChange={handleSignupChange}
                  className={inputClass}
                />
              </label>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <label className="grid gap-1 text-sm font-medium">
                Телефон
                <input
                  name="phone"
                  value={signupData.phone}
                  onChange={handleSignupChange}
                  className={inputClass}
                  required
                />
              </label>
              <label className="grid gap-1 text-sm font-medium">
                Email
                <input
                  name="email"
                  type="email"
                  value={signupData.email}
                  onChange={handleSignupChange}
                  className={inputClass}
                  required
                />
              </label>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <label className="grid gap-1 text-sm font-medium">
                Пароль
                <input
                  name="password"
                  type="password"
                  value={signupData.password}
                  onChange={handleSignupChange}
                  className={inputClass}
                  required
                />
              </label>
              <label className="grid gap-1 text-sm font-medium">
                Статус
                <select
                  name="status"
                  value={signupData.status}
                  onChange={handleSignupChange}
                  className={inputClass}
                  required
                >
                  <option value="self_employed">Самозанятый</option>
                  <option value="ip">ИП</option>
                  <option value="individual">Физическое лицо</option>
                </select>
                <span className="text-xs font-normal text-slate-500">
                  {getStatusDescription(signupData.status)}
                </span>
              </label>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <label className="grid gap-1 text-sm font-medium">
                Дата рождения
                <input
                  name="birthdate"
                  type="date"
                  value={signupData.birthdate}
                  onChange={handleSignupChange}
                  className={inputClass}
                  required
                />
              </label>
              <label className="grid gap-1 text-sm font-medium">
                Дата выдачи паспорта
                <input
                  name="passport_issue_date"
                  type="date"
                  value={signupData.passport_issue_date}
                  onChange={handleSignupChange}
                  className={inputClass}
                  required
                />
              </label>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <label className="grid gap-1 text-sm font-medium">
                Серия паспорта
                <input
                  name="passport_serial"
                  value={signupData.passport_serial}
                  onChange={handleSignupChange}
                  className={inputClass}
                  required
                />
              </label>
              <label className="grid gap-1 text-sm font-medium">
                Номер паспорта
                <input
                  name="passport_number"
                  value={signupData.passport_number}
                  onChange={handleSignupChange}
                  className={inputClass}
                  required
                />
              </label>
            </div>

            <label className="grid gap-1 text-sm font-medium">
              Кем выдан паспорт
              <input
                name="passport_issuer"
                value={signupData.passport_issuer}
                onChange={handleSignupChange}
                className={inputClass}
                required
              />
            </label>

            <div className="grid gap-4 md:grid-cols-3">
              <label className="grid gap-1 text-sm font-medium">
                Код подразделения
                <input
                  name="passport_code"
                  value={signupData.passport_code}
                  onChange={handleSignupChange}
                  className={inputClass}
                  required
                />
              </label>
              {showInn && (
                <label className="grid gap-1 text-sm font-medium">
                  ИНН
                  <input
                    name="inn"
                    value={signupData.inn}
                    onChange={handleSignupChange}
                    className={inputClass}
                    required
                  />
                </label>
              )}
              {showOgrnip && (
                <label className="grid gap-1 text-sm font-medium">
                  ОГРНИП
                  <input
                    name="ogrnip"
                    value={signupData.ogrnip}
                    onChange={handleSignupChange}
                    className={inputClass}
                    required
                  />
                </label>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="rounded-md bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700 disabled:bg-slate-300"
            >
              {isLoading ? "Регистрация..." : "Зарегистрироваться"}
            </button>
          </form>
        )}

        <button
          type="button"
          onClick={togglePage}
          className="mt-4 text-sm font-medium text-blue-700 hover:text-blue-800"
        >
          {isLoginPage
            ? "Нет аккаунта? Зарегистрироваться"
            : "Уже есть аккаунт? Войти"}
        </button>
      </section>
    </div>
  );
}
