import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { register } from "../api/auth";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode] = useState("login"); // "login" | "register"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (mode === "register") {
        await register(email, password);
      }
      await login(email, password);
      navigate("/catalog");
    } catch (err) {
      setError(err.response?.data?.error || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      maxWidth: 400,
      margin: "100px auto",
      padding: 32,
      border: "1px solid #eee",
      borderRadius: 8,
    }}>
      <h2 style={{ marginTop: 0 }}>
        {mode === "login" ? "Sign In" : "Create Account"}
      </h2>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={{ padding: 10, borderRadius: 6, border: "1px solid #ccc" }}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{ padding: 10, borderRadius: 6, border: "1px solid #ccc" }}
        />

        {error && <p style={{ color: "red", margin: 0 }}>{error}</p>}

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: 12,
            background: "#000",
            color: "#fff",
            border: "none",
            borderRadius: 6,
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Please wait..." : mode === "login" ? "Sign In" : "Register"}
        </button>
      </form>

      <p style={{ marginTop: 16, textAlign: "center" }}>
        {mode === "login" ? "No account? " : "Already have one? "}
        <button
          onClick={() => setMode(mode === "login" ? "register" : "login")}
          style={{ background: "none", border: "none", cursor: "pointer", textDecoration: "underline" }}
        >
          {mode === "login" ? "Register" : "Sign In"}
        </button>
      </p>
    </div>
  );
}
