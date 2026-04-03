import api from "./api";

export async function listarPorAssembleia(assembleiaId) {
  const response = await api.get("/pautas", {
    params: { assembleia_id: assembleiaId },
  });
  return response.data;
}

export async function criar(payload) {
  const response = await api.post("/pautas", payload);
  return response.data;
}

export async function criarOpcao(pautaId, payload) {
  const response = await api.post(`/pautas/${pautaId}/opcoes`, payload);
  return response.data;
}

export async function listarOpcoes(pautaId) {
  const response = await api.get(`/pautas/${pautaId}/opcoes`);
  return response.data;
}

export async function iniciarVotacao(pautaId) {
  const response = await api.post(`/pautas/${pautaId}/iniciar-votacao`);
  return response.data;
}

export async function encerrarVotacao(pautaId) {
  const response = await api.post(`/pautas/${pautaId}/encerrar-votacao`);
  return response.data;
}
