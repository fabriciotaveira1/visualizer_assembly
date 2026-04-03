import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import { listar as listarCondominios } from "../../services/condominioService";
import { criar as criarUnidade } from "../../services/unidadeService";

export default function CriarUnidade() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [condominios, setCondominios] = useState([]);
  const [loadingCondominios, setLoadingCondominios] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    condominio_id: searchParams.get("condominio_id") || "",
    bloco: "",
    numero: "",
    identificador_externo: "",
    fracao_ideal: "",
  });

  useEffect(() => {
    let active = true;

    async function loadCondominios() {
      try {
        setLoadingCondominios(true);
        const data = await listarCondominios();

        if (!active) {
          return;
        }

        setCondominios(data);
        setForm((current) => ({
          ...current,
          condominio_id: current.condominio_id || data[0]?.id || "",
        }));
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
  }, []);

  const canSubmit = Boolean(
    form.condominio_id && form.identificador_externo.trim(),
  );

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    try {
      setSaving(true);
      setError("");
      await criarUnidade({
        condominio_id: form.condominio_id,
        bloco: form.bloco || null,
        numero: form.numero || null,
        identificador_externo: form.identificador_externo,
        fracao_ideal: form.fracao_ideal === "" ? null : form.fracao_ideal,
        ativo: true,
      });
      navigate(`/unidades?condominio_id=${form.condominio_id}`, { replace: true });
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Nao foi possivel criar a unidade.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-600">
          Nova unidade
        </p>
        <h2 className="mt-3 text-3xl font-semibold text-slate-950">
          Criar unidade
        </h2>
        <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600">
          Cadastre unidades vinculadas a um condominio para preparar moradores, presencas e votacoes.
        </p>
      </section>

      <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="md:col-span-2">
              <label
                htmlFor="condominio_id"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Condominio
              </label>
              <select
                id="condominio_id"
                name="condominio_id"
                value={form.condominio_id}
                onChange={handleChange}
                disabled={loadingCondominios}
                className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
                required
              >
                <option value="">Selecione um condominio</option>
                {condominios.map((condominio) => (
                  <option key={condominio.id} value={condominio.id}>
                    {condominio.nome}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label
                htmlFor="bloco"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Bloco
              </label>
              <input
                id="bloco"
                name="bloco"
                type="text"
                value={form.bloco}
                onChange={handleChange}
                placeholder="Bloco A"
                className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
              />
            </div>

            <div>
              <label
                htmlFor="numero"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Numero
              </label>
              <input
                id="numero"
                name="numero"
                type="text"
                value={form.numero}
                onChange={handleChange}
                placeholder="101"
                className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
              />
            </div>

            <div>
              <label
                htmlFor="identificador_externo"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Identificador externo
              </label>
              <input
                id="identificador_externo"
                name="identificador_externo"
                type="text"
                value={form.identificador_externo}
                onChange={handleChange}
                placeholder="A-101"
                className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
                required
              />
            </div>

            <div>
              <label
                htmlFor="fracao_ideal"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Fracao ideal
              </label>
              <input
                id="fracao_ideal"
                name="fracao_ideal"
                type="number"
                step="0.0001"
                min="0"
                value={form.fracao_ideal}
                onChange={handleChange}
                placeholder="0.2500"
                className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
              />
            </div>
          </div>

          {error ? (
            <p className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
              {error}
            </p>
          ) : null}

          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              type="submit"
              disabled={saving || !canSubmit}
              className="inline-flex items-center justify-center rounded-full bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {saving ? "Salvando..." : "Criar"}
            </button>
            <Link
              to={form.condominio_id ? `/unidades?condominio_id=${form.condominio_id}` : "/unidades"}
              className="inline-flex items-center justify-center rounded-full border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
            >
              Voltar
            </Link>
          </div>
        </form>
      </section>
    </div>
  );
}
