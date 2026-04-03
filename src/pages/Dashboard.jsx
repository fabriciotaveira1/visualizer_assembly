export default function Dashboard() {
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
          A autenticacao esta funcionando, o token foi salvo localmente e esta
          sendo enviado automaticamente para a API FastAPI.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <div className="rounded-3xl bg-brand-600 p-6 text-white shadow-sm">
          <p className="text-xs uppercase tracking-[0.22em] text-brand-100">
            Status
          </p>
          <p className="mt-4 text-2xl font-semibold">Conectado</p>
        </div>
        <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <p className="text-xs uppercase tracking-[0.22em] text-slate-500">
            API
          </p>
          <p className="mt-4 text-lg font-semibold text-slate-900">
            http://localhost:8000/api/v1
          </p>
        </div>
        <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <p className="text-xs uppercase tracking-[0.22em] text-slate-500">
            Proximo passo
          </p>
          <p className="mt-4 text-lg font-semibold text-slate-900">
            Integrar metricas reais
          </p>
        </div>
      </section>
    </div>
  );
}
