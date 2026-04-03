import { useState } from "react";

import { criar as criarPauta, criarOpcao } from "../../services/pautaService";

const initialOption = { codigo: "", descricao: "" };

export default function CriarPauta({ assembleiaId, onCreated, onCancel }) {
  const [form, setForm] = useState({
    titulo: "",
    descricao: "",
    tipo_votacao: "unidade",
    regra_votacao: "simples",
    modo_votacao: "manual",
  });
  const [opcoes, setOpcoes] = useState([
    { codigo: "1", descricao: "Sim" },
    { codigo: "2", descricao: "Nao" },
    { codigo: "3", descricao: "Abstencao" },
  ]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  function handleOptionChange(index, field, value) {
    setOpcoes((current) =>
      current.map((item, itemIndex) =>
        itemIndex === index ? { ...item, [field]: value } : item,
      ),
    );
  }

  function handleAddOption() {
    setOpcoes((current) => [...current, initialOption]);
  }

  function handleRemoveOption(index) {
    setOpcoes((current) => current.filter((_, itemIndex) => itemIndex !== index));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    try {
      setSaving(true);
      setError("");
      const pauta = await criarPauta({
        ...form,
        assembleia_id: assembleiaId,
      });

      const validOptions = opcoes.filter(
        (item) => item.codigo.trim() && item.descricao.trim(),
      );

      for (const option of validOptions) {
        await criarOpcao(pauta.id, {
          codigo: Number(option.codigo),
          descricao: option.descricao,
        });
      }

      onCreated?.(pauta);
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail || "Nao foi possivel criar a pauta.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
      <div className="mb-6 flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-600">
            Nova pauta
          </p>
          <h3 className="mt-2 text-2xl font-semibold text-slate-950">
            Configurar pauta
          </h3>
        </div>
        {onCancel ? (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
          >
            Fechar
          </button>
        ) : null}
      </div>

      <form className="space-y-6" onSubmit={handleSubmit}>
        <div className="grid gap-6 md:grid-cols-2">
          <div className="md:col-span-2">
            <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="titulo">
              Titulo
            </label>
            <input
              id="titulo"
              name="titulo"
              value={form.titulo}
              onChange={handleChange}
              className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
              required
            />
          </div>

          <div className="md:col-span-2">
            <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="descricao">
              Descricao
            </label>
            <textarea
              id="descricao"
              name="descricao"
              value={form.descricao}
              onChange={handleChange}
              rows="4"
              className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="tipo_votacao">
              Tipo de votacao
            </label>
            <select
              id="tipo_votacao"
              name="tipo_votacao"
              value={form.tipo_votacao}
              onChange={handleChange}
              className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
            >
              <option value="unidade">Unidade</option>
              <option value="fracao">Fracao</option>
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="regra_votacao">
              Regra de votacao
            </label>
            <select
              id="regra_votacao"
              name="regra_votacao"
              value={form.regra_votacao}
              onChange={handleChange}
              className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
            >
              <option value="simples">Simples</option>
              <option value="2_3">2/3</option>
              <option value="unanimidade">Unanimidade</option>
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="modo_votacao">
              Modo de votacao
            </label>
            <select
              id="modo_votacao"
              name="modo_votacao"
              value={form.modo_votacao}
              onChange={handleChange}
              className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
            >
              <option value="manual">Manual</option>
              <option value="importado">Importado</option>
              <option value="resultado_manual">Resultado manual</option>
            </select>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-semibold text-slate-900">Opcoes de votacao</p>
              <p className="text-sm text-slate-500">
                Essas opcoes alimentam o voto manual, a importacao e os resultados.
              </p>
            </div>
            <button
              type="button"
              onClick={handleAddOption}
              className="rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              Adicionar opcao
            </button>
          </div>

          <div className="space-y-3">
            {opcoes.map((option, index) => (
              <div key={`${index}-${option.codigo}`} className="grid gap-3 md:grid-cols-[120px_1fr_auto]">
                <input
                  type="number"
                  min="1"
                  value={option.codigo}
                  onChange={(event) => handleOptionChange(index, "codigo", event.target.value)}
                  placeholder="Codigo"
                  className="rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
                />
                <input
                  type="text"
                  value={option.descricao}
                  onChange={(event) => handleOptionChange(index, "descricao", event.target.value)}
                  placeholder="Descricao"
                  className="rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
                />
                <button
                  type="button"
                  onClick={() => handleRemoveOption(index)}
                  className="rounded-2xl border border-rose-200 px-4 py-3 text-sm font-semibold text-rose-700 transition hover:bg-rose-50"
                >
                  Remover
                </button>
              </div>
            ))}
          </div>
        </div>

        {error ? (
          <p className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {error}
          </p>
        ) : null}

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={saving}
            className="rounded-full bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {saving ? "Salvando..." : "Salvar pauta"}
          </button>
        </div>
      </form>
    </section>
  );
}
