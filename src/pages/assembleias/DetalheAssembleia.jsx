import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  abrir,
  encerrar,
  finalizar,
  iniciar,
  obterPorId,
} from "../../services/assembleiaService";
import {
  encerrarVotacao,
  iniciarVotacao,
  listarPorAssembleia,
} from "../../services/pautaService";
import CriarPauta from "../pautas/CriarPauta";

function formatarData(value) {
  if (!value) {
    return "-";
  }

  return new Intl.DateTimeFormat("pt-BR", {
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00`));
}

export default function DetalheAssembleia() {
  const { id } = useParams();
  const [assembleia, setAssembleia] = useState(null);
  const [pautas, setPautas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingAction, setProcessingAction] = useState("");
  const [showCreatePauta, setShowCreatePauta] = useState(false);
  const [error, setError] = useState("");

  const pautaAtiva = useMemo(
    () => pautas.find((item) => item.status === "em_votacao") || null,
    [pautas],
  );
  const statusAssembleia = assembleia?.status || "";

  async function loadData() {
    if (!id) {
      return;
    }

    try {
      setLoading(true);
      setError("");
      const [assembleiaData, pautasData] = await Promise.all([
        obterPorId(id),
        listarPorAssembleia(id),
      ]);
      setAssembleia(assembleiaData);
      setPautas(pautasData);
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Nao foi possivel carregar a assembleia.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, [id]);

  async function handleAssembleiaAction(actionName, actionFn) {
    if (!id) {
      return;
    }

    try {
      setProcessingAction(actionName);
      setError("");
      const updated = await actionFn(id);
      setAssembleia(updated);
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Nao foi possivel atualizar a assembleia.",
      );
    } finally {
      setProcessingAction("");
    }
  }

  async function handlePautaAction(actionName, actionFn, pautaId) {
    try {
      setProcessingAction(`${actionName}-${pautaId}`);
      setError("");
      await actionFn(pautaId);
      await loadData();
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Nao foi possivel atualizar a pauta.",
      );
    } finally {
      setProcessingAction("");
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
        {loading ? (
          <p className="text-sm text-slate-500">Carregando assembleia...</p>
        ) : !assembleia ? (
          <p className="text-sm text-slate-500">Assembleia nao encontrada.</p>
        ) : (
          <div className="space-y-6">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-600">
                  Assembleia
                </p>
                <h2 className="mt-3 text-3xl font-semibold text-slate-950">
                  {assembleia.titulo}
                </h2>
                <p className="mt-3 text-sm text-slate-600">
                  Data da assembleia: {formatarData(assembleia.data)}
                </p>
              </div>
              <div className="flex flex-wrap gap-3">
                <span className="inline-flex rounded-full bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700">
                  {assembleia.status}
                </span>
                <Link
                  to={`/assembleias/${assembleia.id}/votacao`}
                  className="inline-flex items-center justify-center rounded-full bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
                >
                  Ir para votacao
                </Link>
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => handleAssembleiaAction("abrir", abrir)}
                disabled={processingAction === "abrir" || statusAssembleia !== "criada"}
                className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Abrir
              </button>
              <button
                type="button"
                onClick={() => handleAssembleiaAction("iniciar", iniciar)}
                disabled={processingAction === "iniciar" || statusAssembleia !== "aberta"}
                className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Iniciar
              </button>
              <button
                type="button"
                onClick={() => handleAssembleiaAction("encerrar", encerrar)}
                disabled={processingAction === "encerrar" || statusAssembleia !== "em_andamento"}
                className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Encerrar
              </button>
              <button
                type="button"
                onClick={() => handleAssembleiaAction("finalizar", finalizar)}
                disabled={processingAction === "finalizar" || statusAssembleia !== "encerrada"}
                className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Finalizar
              </button>
            </div>

            {pautaAtiva ? (
              <div className="rounded-3xl border border-brand-200 bg-brand-50 p-5">
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-700">
                  Pauta ativa
                </p>
                <p className="mt-2 text-lg font-semibold text-slate-950">
                  {pautaAtiva.titulo}
                </p>
                <p className="mt-2 text-sm text-slate-600">
                  Modo: {pautaAtiva.modo_votacao} | Tipo: {pautaAtiva.tipo_votacao}
                </p>
              </div>
            ) : null}
          </div>
        )}
      </section>

      {error ? (
        <p className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </p>
      ) : null}

      {showCreatePauta && id ? (
        <CriarPauta
          assembleiaId={id}
          onCreated={async () => {
            setShowCreatePauta(false);
            await loadData();
          }}
          onCancel={() => setShowCreatePauta(false)}
        />
      ) : null}

      <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-600">
              Pautas
            </p>
            <h3 className="mt-2 text-2xl font-semibold text-slate-950">
              Pautas da assembleia
            </h3>
          </div>
          <button
            type="button"
            onClick={() => setShowCreatePauta((current) => !current)}
            className="inline-flex items-center justify-center rounded-full bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700"
          >
            Nova pauta
          </button>
        </div>

        {loading ? (
          <p className="text-sm text-slate-500">Carregando pautas...</p>
        ) : pautas.length === 0 ? (
          <p className="text-sm text-slate-500">Nenhuma pauta cadastrada.</p>
        ) : (
          <div className="space-y-4">
            {pautas.map((pauta) => (
              <article
                key={pauta.id}
                className={`rounded-3xl border p-5 ${
                  pauta.status === "em_votacao"
                    ? "border-brand-200 bg-brand-50"
                    : "border-slate-200 bg-slate-50"
                }`}
              >
                <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                  <div className="space-y-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <h4 className="text-lg font-semibold text-slate-950">
                        {pauta.ordem}. {pauta.titulo}
                      </h4>
                      <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-700 ring-1 ring-slate-200">
                        {pauta.status}
                      </span>
                    </div>
                    <p className="text-sm text-slate-600">
                      {pauta.descricao || "Sem descricao cadastrada."}
                    </p>
                    <p className="text-sm text-slate-500">
                      Tipo: {pauta.tipo_votacao} | Regra: {pauta.regra_votacao} | Modo:{" "}
                      {pauta.modo_votacao}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-3">
                    <button
                      type="button"
                      onClick={() =>
                        handlePautaAction("iniciar", iniciarVotacao, pauta.id)
                      }
                      disabled={
                        processingAction === `iniciar-${pauta.id}` ||
                        pauta.status !== "aguardando" ||
                        statusAssembleia !== "em_andamento"
                      }
                      className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      Iniciar votacao
                    </button>
                    <button
                      type="button"
                      onClick={() =>
                        handlePautaAction("encerrar", encerrarVotacao, pauta.id)
                      }
                      disabled={
                        processingAction === `encerrar-${pauta.id}` ||
                        pauta.status !== "em_votacao"
                      }
                      className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      Encerrar votacao
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
