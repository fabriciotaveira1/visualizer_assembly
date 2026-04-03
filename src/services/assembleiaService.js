import api from "./api";

export async function listar() {
  const response = await api.get("/assembleias");
  return response.data;
}

export async function obterPorId(id) {
  const response = await api.get(`/assembleias/${id}`);
  return response.data;
}

export async function criar(payload) {
  const response = await api.post("/assembleias", payload);
  return response.data;
}

export async function abrir(id) {
  const response = await api.post(`/assembleias/${id}/abrir`);
  return response.data;
}

export async function iniciar(id) {
  const response = await api.post(`/assembleias/${id}/iniciar`);
  return response.data;
}

export async function encerrar(id) {
  const response = await api.post(`/assembleias/${id}/encerrar`);
  return response.data;
}

export async function finalizar(id) {
  const response = await api.post(`/assembleias/${id}/finalizar`);
  return response.data;
}
