import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { listar as listarCondominios } from "../../services/condominioService";

export default function ListarCondominios() {
  const [condominios, setCondominios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadCondominios() {
      try {
        setLoading(true);
        setError("");
        const data = await listarCondominios();

        if (active) {
          setCondominios(data);
        }
      } catch (requestError) {
        if (active) {
          setError(
            requestError.response?.data?.detail ||
              "Nao foi possivel carregar os condominios.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadCondominios();

    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      <section className="flex flex-col gap-4 rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-600">
            Condominios
          </p>
          <h2 className="mt-3 text-3xl font-semibold text-slate-950">
            Gestao de condominios
          </h2>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600">
            Consulte os registros existentes e crie novos condominios pela interface administrativa.
          </p>
        </div>
        <Link
          to="/condominios/novo"
          className="inline-flex items-center justify-center rounded-full bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
        >
          Novo condominio
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
                  Nome
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {loading ? (
                <tr>
                  <td className="px-6 py-5 text-sm text-slate-500" colSpan="2">
                    Carregando condominios...
                  </td>
                </tr>
              ) : condominios.length === 0 ? (
                <tr>
                  <td className="px-6 py-5 text-sm text-slate-500" colSpan="2">
                    Nenhum condominio cadastrado.
                  </td>
                </tr>
              ) : (
                condominios.map((condominio) => (
                  <tr key={condominio.id}>
                    <td className="px-6 py-5 text-sm font-medium text-slate-900">
                      {condominio.nome}
                    </td>
                    <td className="px-6 py-5 text-sm text-slate-600">
                      <span
                        className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                          condominio.ativo
                            ? "bg-emerald-50 text-emerald-700"
                            : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        {condominio.ativo ? "Ativo" : "Inativo"}
                      </span>
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
