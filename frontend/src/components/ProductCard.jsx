import { useNavigate } from "react-router-dom";

export default function ProductCard({ product }) {
  const navigate = useNavigate();

  const handleTryOn = () => {
    navigate("/fitting-room", { state: { product } });
  };

  return (
    <div style={{
      border: "1px solid #eee",
      borderRadius: 8,
      overflow: "hidden",
      display: "flex",
      flexDirection: "column",
    }}>
      <img
        src={product.image_url}
        alt={product.title}
        style={{ width: "100%", height: 240, objectFit: "cover" }}
      />
      <div style={{ padding: 12, flex: 1, display: "flex", flexDirection: "column", gap: 4 }}>
        <p style={{ fontWeight: 600, margin: 0 }}>{product.title}</p>
        <p style={{ color: "#666", margin: 0, fontSize: 14 }}>{product.brand}</p>
        <p style={{ margin: 0 }}>${product.price}</p>
        <button
          onClick={handleTryOn}
          style={{
            marginTop: "auto",
            padding: "8px 16px",
            background: "#000",
            color: "#fff",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
          }}
        >
          Try On
        </button>
      </div>
    </div>
  );
}
