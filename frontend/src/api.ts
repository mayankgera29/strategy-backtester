import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000/api/v1",
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

export async function saveStrategy(name: string, graph: any, metadata = {}) {
  const payload = { name, graph, metadata };
  const r = await API.post("/strategies", payload);
  return r.data;
}

export async function listStrategies() {
  const r = await API.get("/strategies");
  return r.data;
}

export async function getStrategy(id: number) {
  const r = await API.get(`/strategies/${id}`);
  return r.data;
}

export default API;
