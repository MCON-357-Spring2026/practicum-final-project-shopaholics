import client from "./client";

export const register = (email, password) =>
  client.post("/auth/register", { email, password });

export const login = async (email, password) => {
  const res = await client.post("/auth/login", { email, password });
  localStorage.setItem("access_token", res.data.access_token);
  return res.data.user;
};

export const logout = () => {
  localStorage.removeItem("access_token");
};

export const getMe = () => client.get("/auth/me");
