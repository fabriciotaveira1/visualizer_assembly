import { useEffect, useState } from "react";

import { obterResultado } from "../../services/votacaoService";

export default function Resultado({ pautaId, refreshKey = 0 }) {
  const [resultado, setResultado] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadResultado() {
      if (!pautaId) {
        setResultado(null);
        return;
      }

      try {
        setLoading(true);
        setError("");
        const data = await obterResultado(pautaId);

        if (active) {
          setResultado(data);
        }
      } catch (requestError) {
        if (active) {
          setError(
            requestError.response?.data?.detail ||
              "Nao foi possivel carregar o resultado da pauta.",
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadResultado();

    return () => {
      active = false;
    };
  }, [pautaId, refreshKey]);

  return (
    <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
      <div className="mb-6">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-600">
          Resultado
        </p>
        <h3 className="mt-2 text-2xl font-semibold text-slate-950">
          Apuracao da pauta
        </h3>
      </div>

      {error ? (
        <p className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </p>
      ) : null}

      {!pautaId ? (
        <p className="text-sm text-slate-500">Selecione uma pauta para visualizar o resultado.</p>
      ) : loading ? (
        <p className="text-sm text-slate-500">Carregando resultado...</p>
      ) : !resultado ? (
        <p className="text-sm text-slate-500">Nenhum resultado disponivel.</p>
      ) : (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-3xl bg-slate-50 p-5">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Modo</p>
              <p className="mt-2 text-lg font-semibold text-slate-900">{resultado.modo_votacao}</p>
            </div>
            <div className="rounded-3xl bg-slate-50 p-5">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Total votos</p>
              <p className="mt-2 text-lg font-semibold text-slate-900">{resultado.total_votos}</p>
            </div>
            <div className="rounded-3xl bg-slate-50 p-5">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Total peso</p>
              <p className="mt-2 text-lg font-semibold text-slate-900">{resultado.total_peso}</p>
            </div>
          </div>

          <div className="overflow-x-auto rounded-3xl ring-1 ring-slate-200">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                    Opcao
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                    Votos
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                    Percentual
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {resultado.opcoes.map((opcao) => (
                  <tr key={`${opcao.codigo_opcao}-${opcao.descricao_opcao}`}>
                    <td className="px-6 py-5 text-sm font-medium text-slate-900">
                      {opcao.codigo_opcao} - {opcao.descricao_opcao}
                    </td>
                    <td className="px-6 py-5 text-sm text-slate-600">
                      {opcao.quantidade_votos}
                    </td>
                    <td className="px-6 py-5 text-sm text-slate-600">
                      {opcao.percentual}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}
