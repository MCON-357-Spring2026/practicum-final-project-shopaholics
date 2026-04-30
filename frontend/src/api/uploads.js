import client from "./client";

export const uploadPersonPhoto = (file) => {
  const form = new FormData();
  form.append("file", file);
  return client.post("/uploads/person", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};
