import { useState, useRef } from "react";
import { uploadPersonPhoto } from "../api/uploads";

export default function ImageUpload({ onUpload }) {
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const handleFile = async (file) => {
    if (!file) return;
    setPreview(URL.createObjectURL(file));
    setError(null);
    setUploading(true);

    try {
      const res = await uploadPersonPhoto(file);
      onUpload(res.data.key, res.data.url);
    } catch (err) {
      setError("Upload failed. Please try again.");
      setPreview(null);
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  return (
    <div
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      onClick={() => inputRef.current.click()}
      style={{
        border: "2px dashed #ccc",
        borderRadius: 8,
        padding: 24,
        textAlign: "center",
        cursor: "pointer",
        minHeight: 180,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        style={{ display: "none" }}
        onChange={(e) => handleFile(e.target.files[0])}
      />

      {preview ? (
        <img
          src={preview}
          alt="preview"
          style={{ maxHeight: 200, borderRadius: 8 }}
        />
      ) : (
        <p>{uploading ? "Uploading..." : "Click or drag your photo here"}</p>
      )}

      {error && <p style={{ color: "red", marginTop: 8 }}>{error}</p>}
    </div>
  );
}
