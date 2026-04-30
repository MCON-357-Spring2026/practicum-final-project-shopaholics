import client from "./client";

export const generateTryOn = (personImageUrl, garmentImageUrl, productId) =>
  client.post("/tryon/generate", {
    person_image_url: personImageUrl,
    garment_image_url: garmentImageUrl,
    product_id: productId,
  });

export const getJobStatus = (jobId) => client.get(`/tryon/jobs/${jobId}`);

export const getHistory = (page = 1) =>
  client.get("/tryon/history", { params: { page } });

export const deleteJob = (jobId) => client.delete(`/tryon/jobs/${jobId}`);
