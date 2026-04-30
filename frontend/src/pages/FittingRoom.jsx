import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import ImageUpload from "../components/ImageUpload";
import TryOnStatus from "../components/TryOnStatus";
import { generateTryOn } from "../api/tryon";

export default function FittingRoom() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const product = state?.product;

  const [personImageKey, setPersonImageKey] = useState(null);
  const [personImageUrl, setPersonImageUrl] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!product) {
    return (
      <div style={{ textAlign: "center", padding: 64 }}>
        <p>No product selected.</p>
        <button onClick={() => navigate("/catalog")}>Back to Catalog</button>
      </div>
    );
  }

  const handleUpload = (key, url) => {
    setPersonImageKey(key);
    setPersonImageUrl(url);
  };

  const handleTryOn = async () => {
    if (!personImageKey) return;
    setError(null);
    setLoading(true);

    try {
      const res = await generateTryOn(personImageUrl, product.image_url, product.id);
      setJobId(res.data.job_id);
    } catch {
      setError("Failed to start try-on. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: "24px 16px" }}>
      <button
        onClick={() => navigate("/catalog")}
        style={{ background: "none", border: "none", cursor: "pointer", marginBottom: 16, fontSize: 14 }}
      >
        ← Back to Catalog
      </button>

      <h2>Fitting Room</h2>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 32 }}>
        {/* Garment */}
        <div>
          <h3>Selected Item</h3>
          <img
            src={product.image_url}
            alt={product.title}
            style={{ width: "100%", borderRadius: 8, objectFit: "cover" }}
          />
          <p style={{ fontWeight: 600 }}>{product.title}</p>
          <p style={{ color: "#666" }}>{product.brand} · ${product.price}</p>
        </div>

        {/* Upload + result */}
        <div>
          <h3>Your Photo</h3>
          <ImageUpload onUpload={handleUpload} />

          {personImageKey && !jobId && (
            <button
              onClick={handleTryOn}
              disabled={loading}
              style={{
                marginTop: 16,
                width: "100%",
                padding: 12,
                background: "#000",
                color: "#fff",
                border: "none",
                borderRadius: 6,
                cursor: loading ? "not-allowed" : "pointer",
                fontSize: 16,
              }}
            >
              {loading ? "Starting..." : "Try It On"}
            </button>
          )}

          {error && <p style={{ color: "red" }}>{error}</p>}
        </div>
      </div>

      {jobId && (
        <div style={{ marginTop: 40 }}>
          <TryOnStatus jobId={jobId} />
        </div>
      )}
    </div>
  );
}
