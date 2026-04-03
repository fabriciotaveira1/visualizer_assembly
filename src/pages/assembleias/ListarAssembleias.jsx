import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { listar as listarAssembleias } from "../../services/assembleiaService";

function formatarData(value) {
  if (!value) {
    return "-";
  }

  return new Intl.DateTimeFormat("pt-BR", {
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00`));
}

export default function ListarAssembleias() {
  const [assembleias, setAssembleias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadData() {
      try {
        setLoading(true);
        setError("");
        const data = await listarAssembleias();

        if (active) {
          setAssembleias(data);
        }
      } catch (requestError) {
        if (active) {
          setError(
            requestError.response?.data?.detail ||
              "Nao foi possivel carregar as assembleias.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadData();

    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      <section className="flex flex-col gap-4 rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-600">
            Assembleias
          </p>
          <h2 className="mt-3 text-3xl font-semibold text-slate-950">
            Gestao de assembleias
          </h2>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600">
            Crie assembleias, acompanhe o status e entre rapidamente no fluxo de votacao.
          </p>
        </div>
        <Link
          to="/assembleias/nova"
          className="inline-flex items-center justify-center rounded-full bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
        >
          Nova assembleia
        </Link>
      </section>

      {error ? (
        <p className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </p>
      ) : null}

      <section className="overflow-hidden rounded-[28px] bg-white shadow-sm ring-1 ring-slate-200">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Titulo
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Data
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Status
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Acao
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {loading ? (
                <tr>
                  <td className="px-6 py-5 text-sm text-slate-500" colSpan="4">
                    Carregando assembleias...
                  </td>
                </tr>
              ) : assembleias.length === 0 ? (
                <tr>
                  <td className="px-6 py-5 text-sm text-slate-500" colSpan="4">
                    Nenhuma assembleia cadastrada.
                  </td>
                </tr>
              ) : (
                assembleias.map((assembleia) => (
                  <tr key={assembleia.id}>
                    <td className="px-6 py-5 text-sm font-medium text-slate-900">
                      {assembleia.titulo || "-"}
                    </td>
                    <td className="px-6 py-5 text-sm text-slate-600">
                      {formatarData(assembleia.data)}
                    </td>
                    <td className="px-6 py-5 text-sm text-slate-600">
                      <span className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                        {assembleia.status || "-"}
                      </span>
                    </td>
                    <td className="px-6 py-5 text-sm">
                      <Link
                        to={`/assembleias/${assembleia.id}`}
                        className="font-semibold text-brand-600 hover:text-brand-700"
                      >
                        Gerenciar
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
