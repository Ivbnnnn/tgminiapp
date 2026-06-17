import {
  useEffect,
  useMemo,
  useState,
  type ChangeEvent,
  type FormEvent,
} from "react";
import {
  financeApi,
  type Calculation,
  type InsuranceCompanyInfo,
  type Person,
  type Vehicle,
} from "../api/financeApi";
import {
  osagoApi,
  type CalculationRequest,
  type InsuranceCompany,
  type Offer,
} from "../api/osagoApi";

const inputClass =
  "w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100";

const money = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  maximumFractionDigits: 0,
});

type VehicleIdentifierType =
  | "license_plate"
  | "vin"
  | "body_number"
  | "chassis_number";

type DetailRecord = Record<string, unknown>;

type CalculationDetails = {
  calculation: Calculation;
  owner: Person | null;
  driver: Person | null;
  vehicle: Vehicle | null;
  company: InsuranceCompanyInfo | null;
};

const vehicleIdentifierLabels: Record<VehicleIdentifierType, string> = {
  license_plate: "Госномер",
  vin: "VIN",
  body_number: "Номер кузова",
  chassis_number: "Номер шасси",
};

const statusLabels: Record<string, string> = {
  calculated: "Предложения получены",
  waiting_for_payment: "Ожидает оплаты",
  paid: "Оплачен",
  canceled: "Отменен",
  waiting_for_payout: "Ожидает выплаты",
};

const purposeLabels: Record<string, string> = {
  personal: "Личное использование",
  taxi: "Такси",
  commercial: "Коммерческое использование",
};

const stsDocTypeLabels: Record<number, string> = {
  0: "ПТС",
  1: "СТС",
  2: "ЭПТС",
};

function today() {
  return new Date().toISOString().slice(0, 10);
}

function toNumber(value: string | number | null | undefined) {
  const numeric = Number(value ?? 0);
  return Number.isFinite(numeric) ? numeric : 0;
}

function firstItem<T>(value: T | T[] | null | undefined): T | null {
  if (Array.isArray(value)) {
    return value[0] ?? null;
  }

  return value ?? null;
}

function text(value: unknown) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  return String(value);
}

function yesNo(value: boolean | null | undefined) {
  if (value === null || value === undefined) {
    return "-";
  }

  return value ? "Да" : "Нет";
}

function formatDate(value?: string | null) {
  if (!value) {
    return "-";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("ru-RU").format(date);
}

function formatStatus(status: string) {
  return statusLabels[status] ?? status;
}

function StatusBadge({ status }: { status: string }) {
  const colorClass =
    status === "paid"
      ? "bg-green-50 text-green-700"
      : status === "waiting_for_payment"
        ? "bg-amber-50 text-amber-700"
        : status === "canceled"
          ? "bg-red-50 text-red-700"
          : "bg-slate-100 text-slate-700";

  return (
    <span className={`inline-flex w-fit rounded-md px-2 py-1 text-xs font-medium ${colorClass}`}>
      {formatStatus(status)}
    </span>
  );
}

function personName(value: Person[] | Person | null | undefined) {
  const person = firstItem(value);

  if (!person) {
    return "-";
  }

  return [person.lastname, person.firstname, person.middlename]
    .filter(Boolean)
    .join(" ");
}

function vehicleName(value: Vehicle[] | Vehicle | null | undefined) {
  const vehicle = firstItem(value);

  if (!vehicle) {
    return "-";
  }

  return [vehicle.brand, vehicle.model, vehicle.license_plate]
    .filter(Boolean)
    .join(" ");
}

function offerCompanyId(offer: Offer) {
  return offer.id ?? offer.company_id ?? offer.insurance_company_id ?? 0;
}

function offerName(offer: Offer) {
  return offer.name ?? offer.company_name ?? `Компания #${offerCompanyId(offer)}`;
}

function offerPrice(offer: Offer) {
  return toNumber(offer.policy_price ?? offer.price);
}

function getEntityId(
  value:
    | Person[]
    | Person
    | Vehicle[]
    | Vehicle
    | InsuranceCompanyInfo[]
    | InsuranceCompanyInfo
    | null
    | undefined,
) {
  return firstItem(value)?.id;
}

function asRecordList(value: unknown): DetailRecord[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.filter(
    (item): item is DetailRecord =>
      typeof item === "object" && item !== null && !Array.isArray(item),
  );
}

function DetailField({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <p className="text-xs font-medium uppercase text-slate-500">{label}</p>
      <p className="mt-1 text-sm text-slate-900">{value}</p>
    </div>
  );
}

function DetailSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-lg border border-slate-200">
      <div className="border-b border-slate-200 px-4 py-3">
        <h3 className="font-semibold">{title}</h3>
      </div>
      <div className="grid gap-4 p-4 sm:grid-cols-2">{children}</div>
    </section>
  );
}

const initialForm: CalculationRequest = {
  lastname: "",
  firstname: "",
  middlename: "",
  insurance_companies: null,
  license_plate: null,
  vin: null,
  body_number: null,
  chassis_number: null,
  license_serial: "",
  license_number: "",
  use_period: 12,
  policy_start_date: today(),
};

export default function Calculations() {
  const [form, setForm] = useState<CalculationRequest>(initialForm);
  const [identifierType, setIdentifierType] =
    useState<VehicleIdentifierType>("license_plate");
  const [identifierValue, setIdentifierValue] = useState("");
  const [companies, setCompanies] = useState<InsuranceCompany[]>([]);
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>([]);
  const [offers, setOffers] = useState<Offer[]>([]);
  const [calculationId, setCalculationId] = useState<number | null>(null);
  const [selectedCompanyId, setSelectedCompanyId] = useState<number | null>(null);
  const [paidCalculationIds, setPaidCalculationIds] = useState<Set<number>>(
    () => new Set(),
  );
  const [calculations, setCalculations] = useState<Calculation[]>([]);
  const [details, setDetails] = useState<CalculationDetails | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCalculating, setIsCalculating] = useState(false);
  const [isTestDataLoading, setIsTestDataLoading] = useState(false);
  const [isChoosingId, setIsChoosingId] = useState<number | null>(null);
  const [isPaying, setIsPaying] = useState(false);
  const [isDetailsLoading, setIsDetailsLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const sortedOffers = useMemo(
    () => [...offers].sort((left, right) => offerPrice(left) - offerPrice(right)),
    [offers],
  );

  const currentCalculationPaid =
    calculationId !== null && paidCalculationIds.has(calculationId);

  const loadPageData = async (showLoading = true) => {
    if (showLoading) {
      setIsLoading(true);
    }

    setError("");

    try {
      const [companyList, calculationList] = await Promise.all([
        osagoApi.companies(),
        financeApi.calculations(),
      ]);

      setCompanies(companyList);
      setCalculations(calculationList);
      setPaidCalculationIds(
        new Set(
          calculationList
            .filter((calculation) => calculation.status === "paid")
            .map((calculation) => calculation.id),
        ),
      );
    } catch {
      setError("Не удалось загрузить данные для расчетов");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    async function loadInitialPageData() {
      try {
        const [companyList, calculationList] = await Promise.all([
          osagoApi.companies(),
          financeApi.calculations(),
        ]);

        setCompanies(companyList);
        setCalculations(calculationList);
        setPaidCalculationIds(
          new Set(
            calculationList
              .filter((calculation) => calculation.status === "paid")
              .map((calculation) => calculation.id),
          ),
        );
      } catch {
        setError("Не удалось загрузить данные для расчетов");
      } finally {
        setIsLoading(false);
      }
    }

    void loadInitialPageData();
  }, []);

  const handleChange = (
    event: ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = event.target;

    setForm((prev) => ({
      ...prev,
      [name]: name === "use_period" ? Number(value) : value,
    }));
  };

  const handleCompanyToggle = (companyName: string) => {
    setSelectedCompanies((prev) =>
      prev.includes(companyName)
        ? prev.filter((name) => name !== companyName)
        : [...prev, companyName],
    );
  };

  const handleFillTestData = async () => {
    setIsTestDataLoading(true);
    setMessage("");
    setError("");

    try {
      const testData = await osagoApi.testData();
      const identifier =
        (["license_plate", "vin", "body_number", "chassis_number"] as const)
          .map((type) => ({ type, value: testData[type] }))
          .find((item) => Boolean(item.value));

      if (!identifier) {
        setError("В тестовых данных не найден идентификатор автомобиля");
        return;
      }

      setIdentifierType(identifier.type);
      setIdentifierValue(identifier.value ?? "");
      setForm(testData);
      setSelectedCompanies(testData.insurance_companies ?? []);
      setOffers([]);
      setCalculationId(null);
      setSelectedCompanyId(null);
      setMessage("Тестовые данные подставлены");
    } catch {
      setError("Не удалось получить тестовые данные");
    } finally {
      setIsTestDataLoading(false);
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setMessage("");
    setError("");

    if (!identifierValue.trim()) {
      setError("Укажите идентификатор автомобиля");
      return;
    }

    setIsCalculating(true);
    setOffers([]);
    setCalculationId(null);
    setSelectedCompanyId(null);

    try {
      const vehicleFields = {
        license_plate: null,
        vin: null,
        body_number: null,
        chassis_number: null,
        [identifierType]: identifierValue.trim(),
      };

      const result = await osagoApi.getOffers({
        ...form,
        ...vehicleFields,
        middlename: form.middlename || null,
        insurance_companies:
          selectedCompanies.length > 0 ? selectedCompanies : null,
        license_serial: form.license_serial || null,
        license_number: form.license_number || null,
      });

      setOffers(result.offers ?? []);
      setCalculationId(result.calculation_id ?? null);
      setMessage("Предложения получены");
      await loadPageData(false);
    } catch {
      setError("Не удалось выполнить расчет");
    } finally {
      setIsCalculating(false);
    }
  };

  const handleChoose = async (companyId: number) => {
    if (!calculationId || currentCalculationPaid) {
      return;
    }

    setIsChoosingId(companyId);
    setMessage("");
    setError("");

    try {
      await osagoApi.chooseOffer(companyId, calculationId);
      setSelectedCompanyId(companyId);
      setMessage("Предложение выбрано");
      await loadPageData(false);
    } catch {
      setError("Не удалось выбрать предложение");
    } finally {
      setIsChoosingId(null);
    }
  };

  const handlePay = async () => {
    if (!calculationId || !selectedCompanyId || currentCalculationPaid || isPaying) {
      return;
    }

    setIsPaying(true);
    setMessage("");
    setError("");

    try {
      await osagoApi.payOffer(calculationId);
      setPaidCalculationIds((prev) => new Set(prev).add(calculationId));
      setMessage("Полис оплачен");
      await loadPageData(false);
    } catch {
      setError("Не удалось оплатить предложение");
    } finally {
      setIsPaying(false);
    }
  };

  const loadSearchRecord = async (
    modelName: string,
    id: number | undefined,
    relations: string[] = [],
  ) => {
    if (!id) {
      return null;
    }

    const result = await osagoApi.search({
      model_name: modelName,
      relations,
      filters: [{ field: "id", value: String(id) }],
    });

    return asRecordList(result)[0] ?? null;
  };

  const handleOpenDetails = async (calculation: Calculation) => {
    setIsDetailsLoading(true);
    setError("");

    try {
      const ownerId = getEntityId(calculation.owner);
      const driverId = getEntityId(calculation.driver);
      const vehicleId = getEntityId(calculation.vehicle);
      const companyId = getEntityId(calculation.company);

      const [owner, driver, vehicle, company] = await Promise.all([
        loadSearchRecord("Person", ownerId, ["addresses"]),
        loadSearchRecord("Driver", driverId),
        loadSearchRecord("Vehicle", vehicleId, ["sts_documents"]),
        loadSearchRecord("InsuranceCompany", companyId),
      ]);

      setDetails({
        calculation,
        owner: owner as Person | null,
        driver: driver as Person | null,
        vehicle: vehicle as Vehicle | null,
        company:
          (company as InsuranceCompanyInfo | null) ??
          firstItem(calculation.company),
      });
    } catch {
      setError("Не удалось открыть расчет");
    } finally {
      setIsDetailsLoading(false);
    }
  };

  return (
    <div className="grid gap-6">
      <section className="rounded-lg border border-slate-200 bg-white">
        <div className="border-b border-slate-200 p-5">
          <h2 className="text-lg font-semibold">Новый расчет ОСАГО</h2>
          <p className="text-sm text-slate-500">
            Если страховые компании не выбраны, расчет выполняется по всем
            компаниям.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="grid gap-5 p-5">
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
              Фамилия владельца
              <input
                name="lastname"
                value={form.lastname}
                onChange={handleChange}
                className={inputClass}
                required
              />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              Имя владельца
              <input
                name="firstname"
                value={form.firstname}
                onChange={handleChange}
                className={inputClass}
                required
              />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              Отчество владельца
              <input
                name="middlename"
                value={form.middlename ?? ""}
                onChange={handleChange}
                className={inputClass}
              />
            </label>
          </div>

          <div className="grid gap-4 md:grid-cols-[240px_1fr]">
            <label className="grid gap-1 text-sm font-medium">
              Идентификатор авто
              <select
                value={identifierType}
                onChange={(event) =>
                  setIdentifierType(event.target.value as VehicleIdentifierType)
                }
                className={inputClass}
              >
                {Object.entries(vehicleIdentifierLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </label>
            <label className="grid gap-1 text-sm font-medium">
              {vehicleIdentifierLabels[identifierType]}
              <input
                value={identifierValue}
                onChange={(event) => setIdentifierValue(event.target.value)}
                className={inputClass}
                required
              />
            </label>
          </div>

          <div className="grid gap-4 md:grid-cols-4">
            <label className="grid gap-1 text-sm font-medium">
              Серия ВУ
              <input
                name="license_serial"
                value={form.license_serial ?? ""}
                onChange={handleChange}
                className={inputClass}
                required
              />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              Номер ВУ
              <input
                name="license_number"
                value={form.license_number ?? ""}
                onChange={handleChange}
                className={inputClass}
                required
              />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              Начало полиса
              <input
                name="policy_start_date"
                type="date"
                value={form.policy_start_date}
                onChange={handleChange}
                className={inputClass}
                required
              />
            </label>
            <label className="grid gap-1 text-sm font-medium">
              Период
              <select
                name="use_period"
                value={form.use_period}
                onChange={handleChange}
                className={inputClass}
              >
                <option value={3}>3 месяца</option>
                <option value={6}>6 месяцев</option>
                <option value={9}>9 месяцев</option>
                <option value={12}>12 месяцев</option>
              </select>
            </label>
          </div>

          <div>
            <p className="mb-2 text-sm font-medium">Страховые компании</p>
            <div className="flex flex-wrap gap-2">
              {companies.map((company) => (
                <label
                  key={company.id}
                  className={[
                    "flex cursor-pointer items-center gap-2 rounded-md border px-3 py-2 text-sm",
                    selectedCompanies.includes(company.name)
                      ? "border-blue-600 bg-blue-50 text-blue-800"
                      : "border-slate-300 bg-white text-slate-700",
                  ].join(" ")}
                >
                  <input
                    type="checkbox"
                    checked={selectedCompanies.includes(company.name)}
                    onChange={() => handleCompanyToggle(company.name)}
                    className="h-4 w-4"
                  />
                  {company.name}
                </label>
              ))}
              {!isLoading && companies.length === 0 && (
                <p className="text-sm text-slate-500">Компании не найдены</p>
              )}
            </div>
          </div>

          <div className="grid gap-2 sm:flex sm:flex-wrap">
            <button
              type="submit"
              disabled={isCalculating}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:bg-slate-300"
            >
              {isCalculating ? "Расчет..." : "Получить предложения"}
            </button>
            <button
              type="button"
              onClick={handleFillTestData}
              disabled={isTestDataLoading}
              className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:bg-slate-100 disabled:text-slate-500"
            >
              {isTestDataLoading ? "Загрузка..." : "Тест"}
            </button>
          </div>
        </form>
      </section>

      {sortedOffers.length > 0 && (
        <section className="rounded-lg border border-slate-200 bg-white">
          <div className="border-b border-slate-200 p-5">
            <h2 className="text-lg font-semibold">Предложения</h2>
          </div>
          <div className="grid gap-3 p-5 md:grid-cols-2 xl:grid-cols-3">
            {sortedOffers.map((offer) => {
              const companyId = offerCompanyId(offer);
              const isSelected = selectedCompanyId === companyId;

              return (
                <article
                  key={companyId}
                  className="rounded-lg border border-slate-200 p-4"
                >
                  <p className="font-semibold">{offerName(offer)}</p>
                  <p className="mt-2 text-2xl font-semibold">
                    {money.format(offerPrice(offer))}
                  </p>
                  <p className="mt-1 text-sm text-slate-500">
                    Комиссия {toNumber(offer.commission_percent)}%
                  </p>
                  <div className="mt-4 flex gap-2">
                    <button
                      type="button"
                      onClick={() => handleChoose(companyId)}
                      disabled={
                        isSelected ||
                        currentCalculationPaid ||
                        isChoosingId !== null
                      }
                      className="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-500"
                    >
                      {isChoosingId === companyId
                        ? "Выбор..."
                        : isSelected
                          ? "Выбрано"
                          : "Выбрать"}
                    </button>
                    {isSelected && (
                      <button
                        type="button"
                        onClick={handlePay}
                        disabled={isPaying || currentCalculationPaid}
                        className="rounded-md bg-green-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-slate-300"
                      >
                        {currentCalculationPaid
                          ? "Оплачено"
                          : isPaying
                            ? "Оплата..."
                            : "Оплатить"}
                      </button>
                    )}
                  </div>
                </article>
              );
            })}
          </div>
        </section>
      )}

      <section className="rounded-lg border border-slate-200 bg-white">
        <div className="border-b border-slate-200 p-5">
          <h2 className="text-lg font-semibold">История расчетов</h2>
        </div>

        <div className="grid gap-3 p-4 md:hidden">
          {isLoading ? (
            <p className="text-sm text-slate-500">Загрузка...</p>
          ) : calculations.length === 0 ? (
            <p className="text-sm text-slate-500">Расчетов пока нет</p>
          ) : (
            calculations.map((calculation) => (
              <article
                key={calculation.id}
                className="rounded-lg border border-slate-200 p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-medium">Расчет #{calculation.id}</p>
                    <p className="mt-1 text-sm text-slate-500">
                      {vehicleName(calculation.vehicle)}
                    </p>
                  </div>
                  <StatusBadge status={calculation.status} />
                </div>

                <dl className="mt-4 grid gap-3 text-sm">
                  <div>
                    <dt className="text-slate-500">Владелец</dt>
                    <dd className="mt-1 font-medium">
                      {personName(calculation.owner)}
                    </dd>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <dt className="text-slate-500">Период</dt>
                      <dd className="mt-1 font-medium">
                        {calculation.use_period ?? "-"} мес.
                      </dd>
                    </div>
                    <div>
                      <dt className="text-slate-500">Стоимость</dt>
                      <dd className="mt-1 font-medium">
                        {calculation.policy_price
                          ? money.format(toNumber(calculation.policy_price))
                          : "-"}
                      </dd>
                    </div>
                  </div>
                </dl>

                <button
                  type="button"
                  onClick={() => handleOpenDetails(calculation)}
                  disabled={isDetailsLoading}
                  className="mt-4 w-full rounded-md border border-slate-300 px-3 py-2 text-sm font-medium transition hover:bg-slate-50 disabled:bg-slate-100"
                >
                  Открыть
                </button>
              </article>
            ))
          )}
        </div>

        <div className="hidden overflow-x-auto md:block">
          <table className="w-full min-w-[1000px] text-left text-sm">
            <thead className="bg-slate-50 text-slate-500">
              <tr>
                <th className="px-5 py-3 font-medium">ID</th>
                <th className="px-5 py-3 font-medium">Владелец</th>
                <th className="px-5 py-3 font-medium">Автомобиль</th>
                <th className="px-5 py-3 font-medium">Период</th>
                <th className="px-5 py-3 font-medium">Стоимость</th>
                <th className="px-5 py-3 font-medium">Статус</th>
                <th className="px-5 py-3 font-medium">Действие</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr>
                  <td className="px-5 py-6 text-slate-500" colSpan={7}>
                    Загрузка...
                  </td>
                </tr>
              ) : calculations.length === 0 ? (
                <tr>
                  <td className="px-5 py-6 text-slate-500" colSpan={7}>
                    Расчетов пока нет
                  </td>
                </tr>
              ) : (
                calculations.map((calculation) => (
                  <tr key={calculation.id}>
                    <td className="px-5 py-4">#{calculation.id}</td>
                    <td className="px-5 py-4">{personName(calculation.owner)}</td>
                    <td className="px-5 py-4">{vehicleName(calculation.vehicle)}</td>
                    <td className="px-5 py-4">
                      {calculation.use_period ?? "-"} мес.
                    </td>
                    <td className="px-5 py-4">
                      {calculation.policy_price
                        ? money.format(toNumber(calculation.policy_price))
                        : "-"}
                    </td>
                    <td className="px-5 py-4">
                      <StatusBadge status={calculation.status} />
                    </td>
                    <td className="px-5 py-4">
                      <button
                        type="button"
                        onClick={() => handleOpenDetails(calculation)}
                        disabled={isDetailsLoading}
                        className="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium transition hover:bg-slate-50 disabled:bg-slate-100"
                      >
                        Открыть
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      {details && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/40 p-2 sm:p-4">
          <div className="mx-auto my-3 max-w-5xl rounded-lg bg-white shadow-xl sm:my-8">
            <div className="flex flex-col gap-3 border-b border-slate-200 p-4 sm:flex-row sm:items-center sm:justify-between sm:p-5">
              <div className="min-w-0">
                <h2 className="text-lg font-semibold">
                  Расчет #{details.calculation.id}
                </h2>
                <p className="text-sm text-slate-500">
                  {formatStatus(details.calculation.status)}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setDetails(null)}
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm font-medium transition hover:bg-slate-50 sm:w-auto"
              >
                Закрыть
              </button>
            </div>

            <div className="grid gap-4 p-4 sm:p-5">
              <DetailSection title="Полис">
                <DetailField
                  label="Стоимость"
                  value={
                    details.calculation.policy_price
                      ? money.format(toNumber(details.calculation.policy_price))
                      : "-"
                  }
                />
                <DetailField
                  label="Начало действия"
                  value={formatDate(details.calculation.policy_start_date)}
                />
                <DetailField
                  label="Период использования"
                  value={`${details.calculation.use_period ?? "-"} мес.`}
                />
                <DetailField
                  label="Дата расчета"
                  value={formatDate(details.calculation.created_at)}
                />
              </DetailSection>

              <div className="grid gap-4 lg:grid-cols-2">
                <DetailSection title="Владелец">
                  <DetailField label="ФИО" value={personName(details.owner)} />
                  <DetailField
                    label="Дата рождения"
                    value={formatDate(details.owner?.birthdate)}
                  />
                  <DetailField label="Телефон" value={text(details.owner?.phone)} />
                  <DetailField label="Email" value={text(details.owner?.email)} />
                  <DetailField
                    label="Паспорт"
                    value={`${text(details.owner?.passport_serial)} ${text(
                      details.owner?.passport_number,
                    )}`}
                  />
                  <DetailField
                    label="Код подразделения"
                    value={text(details.owner?.passport_code)}
                  />
                  <DetailField
                    label="Кем выдан"
                    value={text(details.owner?.passport_issuer)}
                  />
                  <DetailField
                    label="Дата выдачи"
                    value={formatDate(details.owner?.passport_issue_date)}
                  />
                  <DetailField
                    label="Адрес"
                    value={text(details.owner?.addresses?.[0]?.full_address)}
                  />
                </DetailSection>

                <DetailSection title="Водитель">
                  <DetailField label="ФИО" value={personName(details.driver)} />
                  <DetailField
                    label="Дата рождения"
                    value={formatDate(details.driver?.birthdate)}
                  />
                  <DetailField
                    label="Водительское удостоверение"
                    value={`${text(details.driver?.license_serial)} ${text(
                      details.driver?.license_number,
                    )}`}
                  />
                  <DetailField
                    label="Дата выдачи ВУ"
                    value={formatDate(details.driver?.license_issue_date)}
                  />
                  <DetailField
                    label="Действует до"
                    value={formatDate(details.driver?.license_exp_date)}
                  />
                  <DetailField label="КБМ" value={text(details.driver?.kbm)} />
                  <DetailField
                    label="Иностранные права"
                    value={yesNo(details.driver?.licence_foreign)}
                  />
                </DetailSection>

                <DetailSection title="Автомобиль">
                  <DetailField
                    label="Марка и модель"
                    value={[details.vehicle?.brand, details.vehicle?.model]
                      .filter(Boolean)
                      .join(" ")}
                  />
                  <DetailField label="Год" value={text(details.vehicle?.year)} />
                  <DetailField
                    label="Госномер"
                    value={text(details.vehicle?.license_plate)}
                  />
                  <DetailField label="VIN" value={text(details.vehicle?.vin)} />
                  <DetailField
                    label="Номер кузова"
                    value={text(details.vehicle?.body_number)}
                  />
                  <DetailField
                    label="Номер шасси"
                    value={text(details.vehicle?.chassis_number)}
                  />
                  <DetailField
                    label="Мощность"
                    value={
                      details.vehicle?.power_hp
                        ? `${details.vehicle.power_hp} л.с.`
                        : "-"
                    }
                  />
                  <DetailField
                    label="Назначение"
                    value={
                      details.vehicle?.purpose
                        ? purposeLabels[details.vehicle.purpose] ??
                          details.vehicle.purpose
                        : "-"
                    }
                  />
                  <DetailField
                    label="Прицеп"
                    value={yesNo(details.vehicle?.use_trailer)}
                  />
                  <DetailField
                    label="Документ ТС"
                    value={
                      details.vehicle?.sts_documents?.[0]
                        ? `${
                            stsDocTypeLabels[
                              details.vehicle.sts_documents[0].doc_type ?? -1
                            ] ?? "Документ"
                          } ${text(details.vehicle.sts_documents[0].serial)} ${text(
                            details.vehicle.sts_documents[0].number,
                          )}`
                        : "-"
                    }
                  />
                </DetailSection>

                <DetailSection title="Страховая компания">
                  <DetailField label="Название" value={text(details.company?.name)} />
                  <DetailField
                    label="Комиссия агента"
                    value={
                      details.company?.commission_percent
                        ? `${details.company.commission_percent}%`
                        : "-"
                    }
                  />
                  <DetailField
                    label="Коэффициент"
                    value={text(details.company?.koef)}
                  />
                </DetailSection>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
