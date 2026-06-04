import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { searchProducts, getFeaturedProducts } from "../api/products";
import ProductCard from "../components/ProductCard";

export default function Catalog() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searched, setSearched] = useState(false);

  // Show clothing by default so the catalog isn't empty until you search.
  const loadFeatured = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getFeaturedProducts();
      setProducts(res.data);
      setSearched(false);
    } catch {
      setError("Failed to load the catalog. Try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFeatured();
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      loadFeatured();
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await searchProducts(query);
      setProducts(res.data);
      setSearched(true);
    } catch {
      setError("Failed to fetch products. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: "24px 16px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 style={{ margin: 0 }}>FitVision</h1>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={() => navigate("/history")} style={{ background: "none", border: "1px solid #ccc", padding: "6px 14px", borderRadius: 6, cursor: "pointer" }}>
            My Try-Ons
          </button>
          <button onClick={logout} style={{ background: "none", border: "1px solid #ccc", padding: "6px 14px", borderRadius: 6, cursor: "pointer" }}>
            Log out
          </button>
        </div>
      </div>

      <form onSubmit={handleSearch} style={{ display: "flex", gap: 8, marginBottom: 32 }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for clothing..."
          style={{ flex: 1, padding: 10, borderRadius: 6, border: "1px solid #ccc" }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{ padding: "10px 20px", background: "#000", color: "#fff", border: "none", borderRadius: 6, cursor: "pointer" }}
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {searched && products.length === 0 && !loading && (
        <p style={{ color: "#666" }}>
          No products found for "{query}".{" "}
          <button
            onClick={() => { setQuery(""); loadFeatured(); }}
            style={{ background: "none", border: "none", color: "#06c", cursor: "pointer", textDecoration: "underline", padding: 0 }}
          >
            Show all items
          </button>
        </p>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 20 }}>
        {products.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    </div>
  );
}
