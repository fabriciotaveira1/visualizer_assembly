import { useEffect, useState } from "react";

import api from "../services/api";

const initialMetrics = {
  total_assembleias: 0,
  total_votos: 0,
  assembleias_ativas: 0,
  media_votos_por_assembleia: 0,
  total_presencas: 0,
};

export default function Dashboard() {
  const [metrics, setMetrics] = useState(initialMetrics);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadMetrics() {
      try {
        setLoading(true);
        setError("");
        const response = await api.get("/dashboard");

        if (active) {
          setMetrics(response.data);
        }
      } catch (requestError) {
        if (active) {
          setError(
            requestError.response?.data?.detail ||
              "Nao foi possivel carregar as metricas do dashboard.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadMetrics();

    return () => {
      active = false;
    };
  }, []);

  const cards = [
    {
      label: "Assembleias",
      value: metrics.total_assembleias,
      tone: "bg-brand-600 text-white",
    },
    {
      label: "Votos",
      value: metrics.total_votos,
      tone: "bg-white text-slate-900 ring-1 ring-slate-200",
    },
    {
      label: "Assembleias ativas",
      value: metrics.assembleias_ativas,
      tone: "bg-white text-slate-900 ring-1 ring-slate-200",
    },
    {
      label: "Media de votos por assembleia",
      value: metrics.media_votos_por_assembleia,
      tone: "bg-white text-slate-900 ring-1 ring-slate-200",
    },
  ];

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-600">
          Dashboard
        </p>
        <h2 className="mt-3 text-3xl font-semibold text-slate-950">
          Bem-vindo
        </h2>
        <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600">
          Painel administrativo conectado a API FastAPI com metricas reais,
          autenticacao por token e base pronta para evoluir.
        </p>
        {error ? (
          <p className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {error}
          </p>
        ) : null}
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => (
          <div key={card.label} className={`rounded-3xl p-6 shadow-sm ${card.tone}`}>
            <p
              className={`text-xs uppercase tracking-[0.22em] ${
                card.tone.includes("bg-brand-600") ? "text-brand-100" : "text-slate-500"
              }`}
            >
              {card.label}
            </p>
            <p className="mt-4 text-3xl font-semibold">
              {loading ? "..." : card.value}
            </p>
          </div>
        ))}
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <p className="text-xs uppercase tracking-[0.22em] text-slate-500">
            Presencas registradas
          </p>
          <p className="mt-4 text-2xl font-semibold text-slate-900">
            {loading ? "..." : metrics.total_presencas}
          </p>
          <p className="mt-2 text-sm text-slate-600">
            Esse numero ajuda a acompanhar adesao e quoruns das assembleias.
          </p>
        </div>
        <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <p className="text-xs uppercase tracking-[0.22em] text-slate-500">
            API
          </p>
          <p className="mt-4 text-lg font-semibold text-slate-900">
            http://localhost:8000/api/v1
          </p>
          <p className="mt-2 text-sm text-slate-600">
            Todas as requisicoes usam o token salvo no login automaticamente.
          </p>
        </div>
      </section>
    </div>
  );
}
