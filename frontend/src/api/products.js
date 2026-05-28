import client from "./client";

export const getFeaturedProducts = () => client.get("/products/featured");

export const searchProducts = (query, { category, limit = 20 } = {}) =>
  client.get("/products/search", { params: { q: query, category, limit } });

export const getProduct = (id) => client.get(`/products/${id}`);
