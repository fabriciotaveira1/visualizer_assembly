import api from "./api";

export async function listarPorCondominio(condominioId) {
  const response = await api.get("/unidades", {
    params: { condominio_id: condominioId },
  });
  return response.data;
}

export async function criar(payload) {
  const response = await api.post("/unidades", payload);
  return response.data;
}
