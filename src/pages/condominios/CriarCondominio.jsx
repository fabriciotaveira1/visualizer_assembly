import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { criar as criarCondominio } from "../../services/condominioService";

export default function CriarCondominio() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ nome: "" });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    try {
      setSaving(true);
      setError("");
      await criarCondominio({
        nome: form.nome,
        ativo: true,
      });
      navigate("/condominios", { replace: true });
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Nao foi possivel criar o condominio.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-600">
          Novo condominio
        </p>
        <h2 className="mt-3 text-3xl font-semibold text-slate-950">
          Criar condominio
        </h2>
        <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-600">
          Cadastre um novo condominio para disponibilizar unidades, moradores e assembleias.
        </p>
      </section>

      <section className="rounded-[28px] bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div>
            <label
              htmlFor="nome"
              className="mb-2 block text-sm font-medium text-slate-700"
            >
              Nome
            </label>
            <input
              id="nome"
              name="nome"
              type="text"
              value={form.nome}
              onChange={handleChange}
              placeholder="Nome do condominio"
              className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100"
              required
            />
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
              to="/condominios"
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
