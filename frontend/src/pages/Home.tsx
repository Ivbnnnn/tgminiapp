import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { agentApi, type AgentRead } from "../api/agentApi";
import {
  financeApi,
  type Calculation,
  type Commission,
  type Payout,
} from "../api/financeApi";

const money = new Intl.NumberFormat("ru-RU", {
  style: "currency",
  currency: "RUB",
  maximumFractionDigits: 0,
});

function toNumber(value: string | number | null | undefined) {
  const numeric = Number(value ?? 0);
  return Number.isFinite(numeric) ? numeric : 0;
}

function getStatusLabel(status: string) {
  const labels: Record<string, string> = {
    calculated: "Рассчитан",
    waiting_for_payment: "Ожидает оплаты",
    paid: "Оплачен",
    waiting_for_payout: "К выплате",
    canceled: "Отменен",
  };

  return labels[status] ?? status;
}

export default function Home() {
  const [agent, setAgent] = useState<AgentRead | null>(null);
  const [calculations, setCalculations] = useState<Calculation[]>([]);
  const [commissions, setCommissions] = useState<Commission[]>([]);
  const [payouts, setPayouts] = useState<Payout[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      setIsLoading(true);

      const [agentResult, calculationsResult, commissionsResult, payoutsResult] =
        await Promise.allSettled([
          agentApi.me(),
          financeApi.calculations(),
          financeApi.commissions(),
          financeApi.payouts(),
        ]);

      if (agentResult.status === "fulfilled") {
        setAgent(agentResult.value);
      }

      if (calculationsResult.status === "fulfilled") {
        setCalculations(calculationsResult.value);
      }

      if (commissionsResult.status === "fulfilled") {
        setCommissions(commissionsResult.value);
      }

      if (payoutsResult.status === "fulfilled") {
        setPayouts(payoutsResult.value);
      }

      if (
        calculationsResult.status === "rejected" ||
        commissionsResult.status === "rejected" ||
        payoutsResult.status === "rejected"
      ) {
        setError("Часть данных недоступна для текущего статуса агента");
      }

      setIsLoading(false);
    }

    void loadDashboard();
  }, []);

  const commissionTotal = useMemo(
    () =>
      commissions
        .filter((commission) => commission.status === "waiting_for_payout")
        .reduce((sum, commission) => sum + toNumber(commission.amount), 0),
    [commissions],
  );

  const payoutTotal = useMemo(
    () =>
      payouts.reduce((sum, payout) => sum + toNumber(payout.total_amount), 0),
    [payouts],
  );

  const paidCalculations = calculations.filter(
    (calculation) => calculation.status === "paid",
  ).length;

  const recentCalculations = calculations.slice(0, 5);

  return (
    <div className="grid gap-6">
      <section className="rounded-lg border border-slate-200 bg-white p-5">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm text-slate-500">
              {isLoading ? "Загрузка..." : "Добро пожаловать"}
            </p>
            <h2 className="mt-1 text-2xl font-semibold">
              {agent
                ? `${agent.lastname} ${agent.firstname}`
                : "Агентский кабинет"}
            </h2>
          </div>
          <Link
            to="/calculations"
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
          >
            Новый расчет
          </Link>
        </div>

        {error && (
          <div className="mt-4 rounded-md bg-amber-50 p-3 text-sm text-amber-800">
            {error}
          </div>
        )}
      </section>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Расчетов</p>
          <p className="mt-2 text-2xl font-semibold">{calculations.length}</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Оплачено</p>
          <p className="mt-2 text-2xl font-semibold">{paidCalculations}</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">К выплате</p>
          <p className="mt-2 break-words text-2xl font-semibold">
            {money.format(commissionTotal)}
          </p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Выплачено</p>
          <p className="mt-2 break-words text-2xl font-semibold">
            {money.format(payoutTotal)}
          </p>
        </div>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white">
        <div className="flex flex-col gap-2 border-b border-slate-200 p-5 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="text-lg font-semibold">Последние расчеты</h2>
          <Link
            to="/calculations"
            className="text-sm font-medium text-blue-700 hover:text-blue-800"
          >
            Все расчеты
          </Link>
        </div>

        <div className="divide-y divide-slate-100">
          {recentCalculations.length === 0 ? (
            <p className="p-5 text-sm text-slate-500">Расчетов пока нет</p>
          ) : (
            recentCalculations.map((calculation) => (
              <div
                key={calculation.id}
                className="grid gap-3 p-5 md:grid-cols-[1fr_auto_auto] md:items-center"
              >
                <div>
                  <p className="font-medium">Расчет #{calculation.id}</p>
                  <p className="text-sm text-slate-500">
                    Период: {calculation.use_period ?? "-"} мес.
                  </p>
                </div>
                <p className="break-words font-semibold">
                  {money.format(toNumber(calculation.policy_price))}
                </p>
                <span className="w-fit rounded-md bg-slate-100 px-2 py-1 text-sm text-slate-700">
                  {getStatusLabel(calculation.status)}
                </span>
              </div>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
