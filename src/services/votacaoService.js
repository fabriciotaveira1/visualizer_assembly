import api from "./api";

export async function votarManual(payload) {
  const response = await api.post("/votos", payload);
  return response.data;
}

export async function importarCSV({ pautaId, file }) {
  const formData = new FormData();
  formData.append("pauta_id", pautaId);
  formData.append("file", file);

  const response = await api.post("/importacoes/votos", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
}

export async function enviarResultadoManual(payload) {
  const response = await api.post("/resultado-manual", payload);
  return response.data;
}

export async function obterResultado(pautaId) {
  const response = await api.get(`/pautas/${pautaId}/resultado`);
  return response.data;
}
