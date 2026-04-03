import api from "./api";

export async function listar() {
  const response = await api.get("/condominios");
  return response.data;
}

export async function criar(payload) {
  const response = await api.post("/condominios", payload);
  return response.data;
}
