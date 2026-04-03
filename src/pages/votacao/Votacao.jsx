import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import { obterPorId } from "../../services/assembleiaService";
import { listarOpcoes, listarPorAssembleia } from "../../services/pautaService";
import { listarPorCondominio } from "../../services/unidadeService";
import {
  enviarResultadoManual,
  importarCSV,
  votarManual,
} from "../../services/votacaoService";
import Resultado from "./Resultado";

export default function Votacao() {
  const { id } = useParams();
  const [assembleia, setAssembleia] = useState(null);
  const [pautas, setPautas] = useState([]);
  const [unidades, setUnidades] = useState([]);
  const [opcoes, setOpcoes] = useState([]);
  const [selectedPautaId, setSelectedPautaId] = useState("");
  const [manualVoteForm, setManualVoteForm] = useState({
    unidade_id: "",
    codigo_opcao: "",
  });
  const [resultadoManualForm, setResultadoManualForm] = useState([
    { codigo_opcao: "1", descricao_opcao: "Sim", quantidade_votos: "", percentual: "", peso_total: "" },
  ]);
  const [csvFile, setCsvFile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  const pautaSelecionada = useMemo(
    () => pautas.find((item) => item.id === selectedPautaId) || null,
    [pautas, selectedPautaId],
  );
  const pautaEmVotacao = pautaSelecionada?.status === "em_votacao";

  useEffect(() => {
    async function loadData() {
      if (!id) {
        return;
      }

      try {
        setLoading(true);
        setError("");
        const assembleiaData = await obterPorId(id);
        setAssembleia(assembleiaData);

        const pautasData = await listarPorAssembleia(id);
        setPautas(pautasData);

        const currentPauta =
          pautasData.find((item) => item.status === "em_votacao") || pautasData[0] || null;
        setSelectedPautaId(currentPauta?.id || "");

        if (assembleiaData.condominio_id) {
          const unidadesData = await listarPorCondominio(assembleiaData.condominio_id);
          setUnidades(unidadesData);
        } else {
          setUnidades([]);
        }
      } catch (requestError) {
        setError(
          requestError.response?.data?.detail ||
            "Nao foi possivel carregar a votacao da assembleia.",
        );
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [id]);

  useEffect(() => {
    if (!selectedPautaId) {
      setOpcoes([]);
      return;
    }

    async function loadOpcoes() {
      try {
        const data = await listarOpcoes(selectedPautaId);
        setOpcoes(data);
        setManualVoteForm((current) => ({
          ...current,
          codigo_opcao: current.codigo_opcao || String(data[0]?.codigo || "1"),
        }));
      } catch {
        setOpcoes([]);
      }
    }

    loadOpcoes();
  }, [selectedPautaId]);

  function handleManualVoteChange(event) {
    const { name, value } = event.target;
    setManualVoteForm((current) => ({ ...current, [name]: value }));
  }

  function handleResultadoManualChange(index, field, value) {
    setResultadoManualForm((current) =>
      current.map((item, itemIndex) =>
        itemIndex === index ? { ...item, [field]: value } : item,
      ),
    );
  }

  function addResultadoLinha() {
    setResultadoManualForm((current) => [
      ...current,
      { codigo_opcao: "", descricao_opcao: "", quantidade_votos: "", percentual: "", peso_total: "" },
    ]);
  }

  async function handleManualVoteSubmit(event) {
    event.preventDefault();
    if (!pautaSelecionada) {
      return;
    }

    try {
      setSubmitting(true);
      setError("");
      setSuccessMessage("");
      await votarManual({
        pauta_id: pautaSelecionada.id,
        unidade_id: manualVoteForm.unidade_id,
        codigo_opcao: Number(manualVoteForm.codigo_opcao),
      });
      setSuccessMessage("Voto registrado com sucesso.");
      setRefreshKey((current) => current + 1);
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Nao foi possivel registrar o voto.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function handleImportSubmit(event) {
    event.preventDefault();
    if (!pautaSelecionada || !csvFile) {
      return;
    }

    try {
      setSubmitting(true);
      setError("");
      setSuccessMessage("");
      const response = await importarCSV({
        pautaId: pautaSelecionada.id,
        file: csvFile,
      });
      setSuccessMessage(
        `Importacao concluida com status ${response.status}. Sucessos: ${response.quantidade_sucesso}.`,
      );
      setRefreshKey((current) => current + 1);
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Nao foi possivel importar os votos.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function handleResultadoManualSubmit(event) {
    event.preventDefault();
    if (!pautaSelecionada) {
      return;
    }

    try {
      setSubmitting(true);
      setError("");
      setSuccessMessage("");
      await enviarResultadoManual({
        pauta_id: pautaSelecionada.id,
        resultados: resultadoManualForm
          .filter((item) => item.codigo_opcao && item.descricao_opcao)
          .map((item) => ({
            codigo_opcao: Number(item.codigo_opcao),
            descricao_opcao: item.descricao_opcao,
            quantidade_votos: Number(item.quantidade_votos || 0),
            peso_total: Number(item.peso_total || 0),
            percentual: Number(item.percentual || 0),
          })),
      });
      setSuccessMessage("Resultado manual enviado com sucesso.");
      setRefreshKey((current) => current + 1);
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Nao foi possivel enviar o resultado manual.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
        {loading ? (
          <p className="text-sm text-slate-500">Carregando votacao...</p>
        ) : (
          <div className="space-y-4">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-600">
              Votacao
            </p>
            <h2 className="text-3xl font-semibold text-slate-950">
              {assembleia?.titulo || "Assembleia"}
            </h2>
            <p className="text-sm text-slate-600">
              Selecione a pauta e execute o modo de votacao configurado.
            </p>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="pauta_id">
                Pauta
              </label>
              <select
                id="pauta_id"
                value={selectedPautaId}
                onChange={(event) => setSelectedPautaId(event.target.value)}
                className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
              >
                <option value="">Selecione uma pauta</option>
                {pautas.map((pauta) => (
                  <option key={pauta.id} value={pauta.id}>
                    {pauta.ordem}. {pauta.titulo} - {pauta.status}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}
      </section>

      {error ? (
        <p className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </p>
      ) : null}

      {successMessage ? (
        <p className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          {successMessage}
        </p>
      ) : null}

      {pautaSelecionada && !pautaEmVotacao ? (
        <p className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
          A pauta selecionada ainda nao esta em votacao. Inicie a votacao na tela da assembleia para registrar votos.
        </p>
      ) : null}

      {pautaSelecionada?.modo_votacao === "manual" ? (
        <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-600">
            Voto manual
          </p>
          <h3 className="mt-2 text-2xl font-semibold text-slate-950">
            Registrar voto por unidade
          </h3>

          <form className="mt-6 space-y-6" onSubmit={handleManualVoteSubmit}>
            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="unidade_id">
                  Unidade
                </label>
                <select
                  id="unidade_id"
                  name="unidade_id"
                  value={manualVoteForm.unidade_id}
                  onChange={handleManualVoteChange}
                  className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
                  required
                >
                  <option value="">Selecione uma unidade</option>
                  {unidades.map((unidade) => (
                    <option key={unidade.id} value={unidade.id}>
                      {unidade.identificador_externo} {unidade.bloco ? `- ${unidade.bloco}` : ""}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="codigo_opcao">
                  Opcao
                </label>
                {opcoes.length > 0 ? (
                  <select
                    id="codigo_opcao"
                    name="codigo_opcao"
                    value={manualVoteForm.codigo_opcao}
                    onChange={handleManualVoteChange}
                    className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
                    required
                  >
                    <option value="">Selecione uma opcao</option>
                    {opcoes.map((opcao) => (
                      <option key={opcao.id} value={opcao.codigo}>
                        {opcao.codigo} - {opcao.descricao}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    id="codigo_opcao"
                    name="codigo_opcao"
                    type="number"
                    min="1"
                    value={manualVoteForm.codigo_opcao}
                    onChange={handleManualVoteChange}
                    className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
                    required
                  />
                )}
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting || !pautaEmVotacao}
              className="rounded-full bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {submitting ? "Registrando..." : "Votar"}
            </button>
          </form>
        </section>
      ) : null}

      {pautaSelecionada?.modo_votacao === "importado" ? (
        <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-600">
            Importacao de votos
          </p>
          <h3 className="mt-2 text-2xl font-semibold text-slate-950">
            Enviar CSV da pauta
          </h3>

          <form className="mt-6 space-y-6" onSubmit={handleImportSubmit}>
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={(event) => setCsvFile(event.target.files?.[0] || null)}
              className="block w-full text-sm text-slate-600"
            />

            <button
              type="submit"
              disabled={submitting || !csvFile || !pautaEmVotacao}
              className="rounded-full bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {submitting ? "Importando..." : "Importar CSV"}
            </button>
          </form>
        </section>
      ) : null}

      {pautaSelecionada?.modo_votacao === "resultado_manual" ? (
        <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
          <div className="mb-6 flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-600">
                Resultado manual
              </p>
              <h3 className="mt-2 text-2xl font-semibold text-slate-950">
                Inserir resultado agregado
              </h3>
            </div>
            <button
              type="button"
              onClick={addResultadoLinha}
              className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              Adicionar linha
            </button>
          </div>

          <form className="space-y-4" onSubmit={handleResultadoManualSubmit}>
            {resultadoManualForm.map((item, index) => (
              <div key={index} className="grid gap-3 md:grid-cols-5">
                <input
                  type="number"
                  min="1"
                  value={item.codigo_opcao}
                  onChange={(event) =>
                    handleResultadoManualChange(index, "codigo_opcao", event.target.value)
                  }
                  placeholder="Codigo"
                  className="rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
                />
                <input
                  type="text"
                  value={item.descricao_opcao}
                  onChange={(event) =>
                    handleResultadoManualChange(index, "descricao_opcao", event.target.value)
                  }
                  placeholder="Descricao"
                  className="rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
                />
                <input
                  type="number"
                  min="0"
                  value={item.quantidade_votos}
                  onChange={(event) =>
                    handleResultadoManualChange(index, "quantidade_votos", event.target.value)
                  }
                  placeholder="Quantidade"
                  className="rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
                />
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={item.percentual}
                  onChange={(event) =>
                    handleResultadoManualChange(index, "percentual", event.target.value)
                  }
                  placeholder="Percentual"
                  className="rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
                />
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={item.peso_total}
                  onChange={(event) =>
                    handleResultadoManualChange(index, "peso_total", event.target.value)
                  }
                  placeholder="Peso total"
                  className="rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
                />
              </div>
            ))}

            <button
              type="submit"
              disabled={submitting || !pautaEmVotacao}
              className="rounded-full bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {submitting ? "Enviando..." : "Enviar resultado"}
            </button>
          </form>
        </section>
      ) : null}

      <Resultado pautaId={selectedPautaId} refreshKey={refreshKey} />
    </div>
  );
}
