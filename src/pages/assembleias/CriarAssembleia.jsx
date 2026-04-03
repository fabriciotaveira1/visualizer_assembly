import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { listar as listarCondominios } from "../../services/condominioService";
import { criar as criarAssembleia } from "../../services/assembleiaService";

export default function CriarAssembleia() {
  const navigate = useNavigate();
  const [condominios, setCondominios] = useState([]);
  const [loadingCondominios, setLoadingCondominios] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    condominio_id: "",
    titulo: "",
    data: "",
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

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    try {
      setSaving(true);
      setError("");
      const created = await criarAssembleia(form);
      navigate(`/assembleias/${created.id}`, { replace: true });
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Nao foi possivel criar a assembleia.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-600">
          Nova assembleia
        </p>
        <h2 className="mt-3 text-3xl font-semibold text-slate-950">
          Criar assembleia
        </h2>
      </section>

      <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="md:col-span-2">
              <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="condominio_id">
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

            <div className="md:col-span-2">
              <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="titulo">
                Titulo
              </label>
              <input
                id="titulo"
                name="titulo"
                type="text"
                value={form.titulo}
                onChange={handleChange}
                placeholder="Assembleia geral ordinaria"
                className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
                required
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="data">
                Data
              </label>
              <input
                id="data"
                name="data"
                type="date"
                value={form.data}
                onChange={handleChange}
                className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
                required
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
              disabled={saving}
              className="inline-flex items-center justify-center rounded-full bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {saving ? "Salvando..." : "Criar"}
            </button>
            <Link
              to="/assembleias"
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
