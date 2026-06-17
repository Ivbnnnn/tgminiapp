import { useEffect, useState, type ChangeEvent, type FormEvent } from "react";
import { agentApi, type AgentRead } from "../api/agentApi";

const inputClass =
  "w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100";

type ProfileForm = Omit<AgentRead, "id" | "is_verified">;

function toDateInput(value: string | null) {
  return value ? value.slice(0, 10) : "";
}

const emptyForm: ProfileForm = {
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
};

export default function Profile() {
  const [agent, setAgent] = useState<AgentRead | null>(null);
  const [form, setForm] = useState<ProfileForm>(emptyForm);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadProfile() {
      try {
        const data = await agentApi.me();
        setAgent(data);
        setForm({
          lastname: data.lastname,
          firstname: data.firstname,
          middlename: data.middlename ?? "",
          phone: data.phone,
          email: data.email,
          passport_serial: data.passport_serial,
          passport_number: data.passport_number,
          passport_issue_date: toDateInput(data.passport_issue_date),
          passport_issuer: data.passport_issuer,
          passport_code: data.passport_code,
          birthdate: toDateInput(data.birthdate),
          status: data.status,
          inn: data.inn,
          ogrnip: data.ogrnip,
        });
      } catch {
        setError("Не удалось загрузить профиль");
      } finally {
        setIsLoading(false);
      }
    }

    void loadProfile();
  }, []);

  const handleChange = (
    event: ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSaving(true);
    setMessage("");
    setError("");

    try {
      const updated = await agentApi.update({
        ...form,
        passport_issue_date: form.passport_issue_date
          ? `${form.passport_issue_date}T00:00:00.000Z`
          : null,
        birthdate: form.birthdate || null,
      });

      setAgent(updated);
      setMessage("Профиль сохранен");
    } catch {
      setError("Не удалось сохранить профиль");
    } finally {
      setIsSaving(false);
    }
  };

  const handleVerify = async () => {
    setIsVerifying(true);
    setMessage("");
    setError("");

    try {
      const updated = await agentApi.update({ is_verified: true });
      setAgent(updated);
      setMessage("Профиль подтвержден");
    } catch {
      setError("Не удалось подтвердить профиль");
    } finally {
      setIsVerifying(false);
    }
  };

  if (isLoading) {
    return <div className="text-slate-500">Загрузка...</div>;
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
      <section className="rounded-lg border border-slate-200 bg-white">
        <div className="border-b border-slate-200 p-5">
          <h2 className="text-lg font-semibold">Профиль агента</h2>
          <p className="text-sm text-slate-500">
            Данные используются при работе с расчетами
          </p>
        </div>

        <form onSubmit={handleSubmit} className="grid gap-4 p-5">
          {message && (
            <div className="rounded-md bg-green-50 p-3 text-sm text-green-700">
              {message}
            </div>
          )}
          {error && (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="grid gap-4 md:grid-cols-3">
            <label className="grid gap-1 text-sm font-medium">
              Фамилия
              <input
                name="lastname"
                value={form.lastname}
                onChange={handleChange}
                className={inputClass}
              />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              Имя
              <input
                name="firstname"
                value={form.firstname}
                onChange={handleChange}
                className={inputClass}
              />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              Отчество
              <input
                name="middlename"
                value={form.middlename ?? ""}
                onChange={handleChange}
                className={inputClass}
              />
            </label>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <label className="grid gap-1 text-sm font-medium">
              Телефон
              <input
                name="phone"
                value={form.phone}
                onChange={handleChange}
                className={inputClass}
              />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              Email
              <input
                name="email"
                type="email"
                value={form.email}
                onChange={handleChange}
                className={inputClass}
              />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              Статус
              <select
                name="status"
                value={form.status}
                onChange={handleChange}
                className={inputClass}
              >
                <option value="self_employed">Самозанятый</option>
                <option value="ip">ИП</option>
                <option value="individual">Физическое лицо</option>
              </select>
            </label>
          </div>

          <div className="grid gap-4 md:grid-cols-4">
            <label className="grid gap-1 text-sm font-medium">
              Серия
              <input
                name="passport_serial"
                value={form.passport_serial}
                onChange={handleChange}
                className={inputClass}
              />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              Номер
              <input
                name="passport_number"
                value={form.passport_number}
                onChange={handleChange}
                className={inputClass}
              />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              Дата выдачи
              <input
                name="passport_issue_date"
                type="date"
                value={form.passport_issue_date ?? ""}
                onChange={handleChange}
                className={inputClass}
              />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              Дата рождения
              <input
                name="birthdate"
                type="date"
                value={form.birthdate ?? ""}
                onChange={handleChange}
                className={inputClass}
              />
            </label>
          </div>

          <label className="grid gap-1 text-sm font-medium">
            Кем выдан паспорт
            <input
              name="passport_issuer"
              value={form.passport_issuer}
              onChange={handleChange}
              className={inputClass}
            />
          </label>

          <div className="grid gap-4 md:grid-cols-3">
            <label className="grid gap-1 text-sm font-medium">
              Код подразделения
              <input
                name="passport_code"
                value={form.passport_code}
                onChange={handleChange}
                className={inputClass}
              />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              ИНН
              <input
                name="inn"
                value={form.inn}
                onChange={handleChange}
                className={inputClass}
              />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              ОГРНИП
              <input
                name="ogrnip"
                value={form.ogrnip}
                onChange={handleChange}
                className={inputClass}
              />
            </label>
          </div>

          <button
            type="submit"
            disabled={isSaving}
            className="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:bg-slate-300 sm:w-fit"
          >
            {isSaving ? "Сохранение..." : "Сохранить"}
          </button>
        </form>
      </section>

      <aside className="rounded-lg border border-slate-200 bg-white p-5">
        <p className="text-sm text-slate-500">ID агента</p>
        <p className="mt-1 text-xl font-semibold">#{agent?.id}</p>
        <div className="mt-5 rounded-md bg-slate-50 p-4">
          <p className="text-sm text-slate-500">Верификация</p>
          <p className="mt-1 font-medium">
            {agent?.is_verified ? "Подтверждена" : "Не подтверждена"}
          </p>
          <button
            type="button"
            onClick={handleVerify}
            disabled={agent?.is_verified || isVerifying}
            className="mt-4 w-full rounded-md border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400"
          >
            {isVerifying ? "Подтверждение..." : "Подтвердить профиль"}
          </button>
        </div>
      </aside>
    </div>
  );
}
