import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getHistory, deleteJob } from "../api/tryon";

export default function History() {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = async (p) => {
    setLoading(true);
    setError(null);
    try {
      const res = await getHistory(p);
      setJobs(res.data.jobs);
      setPages(res.data.pages || 1);
      setPage(res.data.page || p);
    } catch {
      setError("Failed to load your try-on history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(1);
  }, []);

  const handleDelete = async (jobId) => {
    try {
      await deleteJob(jobId);
      setJobs((prev) => prev.filter((j) => j.id !== jobId));
    } catch {
      setError("Failed to delete that try-on.");
    }
  };

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: "24px 16px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 style={{ margin: 0 }}>My Try-Ons</h1>
        <button
          onClick={() => navigate("/catalog")}
          style={{ background: "none", border: "1px solid #ccc", padding: "6px 14px", borderRadius: 6, cursor: "pointer" }}
        >
          ← Back to Catalog
        </button>
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {loading && <p style={{ color: "#666" }}>Loading...</p>}

      {!loading && jobs.length === 0 && (
        <p style={{ color: "#666" }}>No try-ons yet. Pick an item from the catalog to get started.</p>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 20 }}>
        {jobs.map((job) => (
          <div
            key={job.id}
            style={{ border: "1px solid #eee", borderRadius: 8, overflow: "hidden", display: "flex", flexDirection: "column" }}
          >
            {job.status === "DONE" && job.result_url ? (
              <img
                src={job.result_url}
                alt="try-on result"
                style={{ width: "100%", height: 280, objectFit: "cover" }}
              />
            ) : (
              <div
                style={{
                  height: 280,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  background: "#fafafa",
                  color: job.status === "FAILED" ? "red" : "#666",
                  textAlign: "center",
                  padding: 12,
                }}
              >
                {job.status === "FAILED"
                  ? `Failed: ${job.error_message || "unknown error"}`
                  : `${job.status}...`}
              </div>
            )}

            <div style={{ padding: 12, display: "flex", flexDirection: "column", gap: 6 }}>
              <p style={{ margin: 0, fontSize: 13, color: "#666" }}>
                {new Date(job.created_at).toLocaleString()}
              </p>
              <button
                onClick={() => handleDelete(job.id)}
                style={{
                  marginTop: "auto",
                  padding: "8px 16px",
                  background: "#fff",
                  color: "#c00",
                  border: "1px solid #e0b0b0",
                  borderRadius: 6,
                  cursor: "pointer",
                }}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {pages > 1 && (
        <div style={{ display: "flex", gap: 12, justifyContent: "center", marginTop: 32, alignItems: "center" }}>
          <button onClick={() => load(page - 1)} disabled={page <= 1} style={{ padding: "6px 14px", borderRadius: 6, cursor: page <= 1 ? "not-allowed" : "pointer" }}>
            Previous
          </button>
          <span style={{ color: "#666" }}>Page {page} of {pages}</span>
          <button onClick={() => load(page + 1)} disabled={page >= pages} style={{ padding: "6px 14px", borderRadius: 6, cursor: page >= pages ? "not-allowed" : "pointer" }}>
            Next
          </button>
        </div>
      )}
    </div>
  );
}
