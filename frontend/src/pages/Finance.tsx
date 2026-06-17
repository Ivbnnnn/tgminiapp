import { useEffect, useMemo, useState } from "react";
import { financeApi, type Commission, type Payout } from "../api/financeApi";

const money = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  maximumFractionDigits: 0,
});

function toNumber(value: string | number | null | undefined) {
  const numeric = Number(value ?? 0);
  return Number.isFinite(numeric) ? numeric : 0;
}

function formatDate(value?: string | null) {
  if (!value) {
    return "-";
  }

  return new Intl.DateTimeFormat("ru-RU").format(new Date(value));
}

function getCommissionStatusText(status: string) {
  if (status === "waiting_for_payout") {
    return "Ожидает выплаты";
  }

  if (status === "paid") {
    return "Выплачена";
  }

  return status;
}

function StatusBadge({ status }: { status: string }) {
  const isPaid = status === "paid";

  return (
    <span
      className={[
        "inline-flex w-fit rounded-md px-2 py-1 text-xs font-medium",
        isPaid ? "bg-green-50 text-green-700" : "bg-amber-50 text-amber-700",
      ].join(" ")}
    >
      {getCommissionStatusText(status)}
    </span>
  );
}

export default function Finance() {
  const [commissions, setCommissions] = useState<Commission[]>([]);
  const [payouts, setPayouts] = useState<Payout[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const waitingAmount = useMemo(
    () =>
      commissions
        .filter((commission) => commission.status === "waiting_for_payout")
        .reduce((sum, commission) => sum + toNumber(commission.amount), 0),
    [commissions],
  );

  const paidAmount = useMemo(
    () =>
      payouts.reduce((sum, payout) => sum + toNumber(payout.total_amount), 0),
    [payouts],
  );

  const loadFinance = async (showLoading = true) => {
    if (showLoading) {
      setIsLoading(true);
    }

    setError("");

    try {
      const [commissionList, payoutList] = await Promise.all([
        financeApi.commissions(),
        financeApi.payouts(),
      ]);

      setCommissions(commissionList);
      setPayouts(payoutList);
    } catch {
      setError("Не удалось загрузить финансовые данные");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    async function loadInitialFinance() {
      try {
        const [commissionList, payoutList] = await Promise.all([
          financeApi.commissions(),
          financeApi.payouts(),
        ]);

        setCommissions(commissionList);
        setPayouts(payoutList);
      } catch {
        setError("Не удалось загрузить финансовые данные");
      } finally {
        setIsLoading(false);
      }
    }

    void loadInitialFinance();
  }, []);

  const handleCreatePayout = async () => {
    setIsCreating(true);
    setMessage("");
    setError("");

    try {
      await financeApi.createPayout();
      setMessage("Выплата создана");
      await loadFinance(false);
    } catch {
      setError("Не удалось создать выплату");
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="grid gap-6">
      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">К выплате</p>
          <p className="mt-2 break-words text-2xl font-semibold">
            {money.format(waitingAmount)}
          </p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Выплачено</p>
          <p className="mt-2 break-words text-2xl font-semibold">
            {money.format(paidAmount)}
          </p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Комиссий</p>
          <p className="mt-2 text-2xl font-semibold">{commissions.length}</p>
        </div>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white">
        <div className="flex flex-col gap-3 border-b border-slate-200 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold">Комиссии</h2>
            <p className="text-sm text-slate-500">
              Начисления по оплаченным полисам
            </p>
          </div>
          <button
            type="button"
            onClick={handleCreatePayout}
            disabled={isCreating || waitingAmount <= 0}
            className="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300 sm:w-auto"
          >
            {isCreating ? "Создание..." : "Создать выплату"}
          </button>
        </div>

        {message && (
          <div className="mx-5 mt-5 rounded-md bg-green-50 p-3 text-sm text-green-700">
            {message}
          </div>
        )}
        {error && (
          <div className="mx-5 mt-5 rounded-md bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="grid gap-3 p-4 md:hidden">
          {isLoading ? (
            <p className="text-sm text-slate-500">Загрузка...</p>
          ) : commissions.length === 0 ? (
            <p className="text-sm text-slate-500">Комиссий пока нет</p>
          ) : (
            commissions.map((commission) => (
              <article
                key={commission.id}
                className="rounded-lg border border-slate-200 p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-medium">Комиссия #{commission.id}</p>
                    <p className="mt-1 text-sm text-slate-500">
                      Расчет #{commission.calculation_id}
                    </p>
                  </div>
                  <StatusBadge status={commission.status} />
                </div>
                <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <dt className="text-slate-500">Полис</dt>
                    <dd className="mt-1 font-medium">
                      {money.format(toNumber(commission.policy_price))}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-slate-500">Процент</dt>
                    <dd className="mt-1 font-medium">
                      {toNumber(commission.percent)}%
                    </dd>
                  </div>
                  <div className="col-span-2">
                    <dt className="text-slate-500">Сумма</dt>
                    <dd className="mt-1 text-lg font-semibold">
                      {money.format(toNumber(commission.amount))}
                    </dd>
                  </div>
                </dl>
              </article>
            ))
          )}
        </div>

        <div className="hidden overflow-x-auto md:block">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="bg-slate-50 text-slate-500">
              <tr>
                <th className="px-5 py-3 font-medium">ID</th>
                <th className="px-5 py-3 font-medium">Расчет</th>
                <th className="px-5 py-3 font-medium">Полис</th>
                <th className="px-5 py-3 font-medium">Процент</th>
                <th className="px-5 py-3 font-medium">Сумма</th>
                <th className="px-5 py-3 font-medium">Статус</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr>
                  <td className="px-5 py-6 text-slate-500" colSpan={6}>
                    Загрузка...
                  </td>
                </tr>
              ) : commissions.length === 0 ? (
                <tr>
                  <td className="px-5 py-6 text-slate-500" colSpan={6}>
                    Комиссий пока нет
                  </td>
                </tr>
              ) : (
                commissions.map((commission) => (
                  <tr key={commission.id}>
                    <td className="px-5 py-4">#{commission.id}</td>
                    <td className="px-5 py-4">#{commission.calculation_id}</td>
                    <td className="px-5 py-4">
                      {money.format(toNumber(commission.policy_price))}
                    </td>
                    <td className="px-5 py-4">{toNumber(commission.percent)}%</td>
                    <td className="px-5 py-4 font-medium">
                      {money.format(toNumber(commission.amount))}
                    </td>
                    <td className="px-5 py-4">
                      <StatusBadge status={commission.status} />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white">
        <div className="border-b border-slate-200 p-5">
          <h2 className="text-lg font-semibold">Выплаты</h2>
        </div>
        <div className="divide-y divide-slate-100">
          {payouts.length === 0 ? (
            <p className="p-5 text-sm text-slate-500">Выплат пока нет</p>
          ) : (
            payouts.map((payout) => (
              <div
                key={payout.id}
                className="grid gap-3 p-5 sm:grid-cols-[1fr_auto_auto] sm:items-center"
              >
                <div>
                  <p className="font-medium">Выплата #{payout.id}</p>
                  <p className="text-sm text-slate-500">
                    {formatDate(payout.paid_at)}
                  </p>
                </div>
                <p className="break-words font-semibold">
                  {money.format(toNumber(payout.total_amount))}
                </p>
                <p className="w-fit rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700">
                  {payout.status ?? "Выплачена"}
                </p>
              </div>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
