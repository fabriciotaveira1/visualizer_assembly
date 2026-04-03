import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { listar as listarCondominios } from "../../services/condominioService";
import { listarPorCondominio } from "../../services/unidadeService";

export default function ListarUnidades() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [condominios, setCondominios] = useState([]);
  const [unidades, setUnidades] = useState([]);
  const [loadingCondominios, setLoadingCondominios] = useState(true);
  const [loadingUnidades, setLoadingUnidades] = useState(false);
  const [error, setError] = useState("");

  const condominioId = searchParams.get("condominio_id") || "";

  useEffect(() => {
    let active = true;

    async function loadCondominios() {
      try {
        setLoadingCondominios(true);
        setError("");
        const data = await listarCondominios();

        if (!active) {
          return;
        }

        setCondominios(data);

        if (!condominioId && data.length > 0) {
          setSearchParams({ condominio_id: data[0].id });
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
          setLoadingCondominios(false);
        }
      }
    }

    loadCondominios();

    return () => {
      active = false;
    };
  }, [condominioId, setSearchParams]);

  useEffect(() => {
    let active = true;

    async function loadUnidades() {
      if (!condominioId) {
        setUnidades([]);
        return;
      }

      try {
        setLoadingUnidades(true);
        setError("");
        const data = await listarPorCondominio(condominioId);

        if (active) {
          setUnidades(data);
        }
      } catch (requestError) {
        if (active) {
          setError(
            requestError.response?.data?.detail ||
              "Nao foi possivel carregar as unidades.",
          );
        }
      } finally {
        if (active) {
          setLoadingUnidades(false);
        }
      }
    }

    loadUnidades();

    return () => {
      active = false;
    };
  }, [condominioId]);

  function handleCondominioChange(event) {
    const value = event.target.value;
    if (value) {
      setSearchParams({ condominio_id: value });
      return;
    }

    setSearchParams({});
  }

  return (
    <div className="space-y-6">
      <section className="flex flex-col gap-4 rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-600">
            Unidades
          </p>
          <h2 className="mt-3 text-3xl font-semibold text-slate-950">
            Gestao de unidades
          </h2>
          <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600">
            Filtre por condominio para consultar unidades e acompanhar o cadastro da base.
          </p>
        </div>
        <Link
          to="/unidades/novo"
          className="inline-flex items-center justify-center rounded-full bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
        >
          Nova unidade
        </Link>
      </section>

      <section className="rounded-[28px] bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <label
          htmlFor="condominio_id"
          className="mb-2 block text-sm font-medium text-slate-700"
        >
          Filtrar por condominio
        </label>
        <select
          id="condominio_id"
          value={condominioId}
          onChange={handleCondominioChange}
          disabled={loadingCondominios}
          className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
        >
          <option value="">Selecione um condominio</option>
          {condominios.map((condominio) => (
            <option key={condominio.id} value={condominio.id}>
              {condominio.nome}
            </option>
          ))}
        </select>
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
                  Bloco
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Numero
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Identificador
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Fracao ideal
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {loadingUnidades ? (
                <tr>
                  <td className="px-6 py-5 text-sm text-slate-500" colSpan="4">
                    Carregando unidades...
                  </td>
                </tr>
              ) : !condominioId ? (
                <tr>
                  <td className="px-6 py-5 text-sm text-slate-500" colSpan="4">
                    Selecione um condominio para listar as unidades.
                  </td>
                </tr>
              ) : unidades.length === 0 ? (
                <tr>
                  <td className="px-6 py-5 text-sm text-slate-500" colSpan="4">
                    Nenhuma unidade cadastrada para este condominio.
                  </td>
                </tr>
              ) : (
                unidades.map((unidade) => (
                  <tr key={unidade.id}>
                    <td className="px-6 py-5 text-sm text-slate-900">
                      {unidade.bloco || "-"}
                    </td>
                    <td className="px-6 py-5 text-sm text-slate-900">
                      {unidade.numero || "-"}
                    </td>
                    <td className="px-6 py-5 text-sm font-medium text-slate-900">
                      {unidade.identificador_externo}
                    </td>
                    <td className="px-6 py-5 text-sm text-slate-600">
                      {unidade.fracao_ideal ?? "-"}
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
