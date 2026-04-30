import { useState, useEffect, useRef } from "react";
import { getJobStatus } from "../api/tryon";

const POLL_INTERVAL = 3000;
const TERMINAL = ["DONE", "FAILED"];

export default function TryOnStatus({ jobId }) {
  const [job, setJob] = useState(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (!jobId) return;

    const poll = async () => {
      try {
        const res = await getJobStatus(jobId);
        setJob(res.data);
        if (TERMINAL.includes(res.data.status)) {
          clearInterval(intervalRef.current);
        }
      } catch {
        clearInterval(intervalRef.current);
      }
    };

    poll();
    intervalRef.current = setInterval(poll, POLL_INTERVAL);
    return () => clearInterval(intervalRef.current);
  }, [jobId]);

  if (!job) return null;

  if (job.status === "PENDING" || job.status === "PROCESSING") {
    return (
      <div style={{ textAlign: "center", padding: 32 }}>
        <p>Generating your try-on... this takes ~30 seconds</p>
        <progress style={{ width: "100%" }} />
      </div>
    );
  }

  if (job.status === "FAILED") {
    return <p style={{ color: "red" }}>Try-on failed: {job.error_message}</p>;
  }

  return (
    <div style={{ textAlign: "center" }}>
      <p style={{ fontWeight: 600 }}>Here's your look!</p>
      <img
        src={job.result_url}
        alt="try-on result"
        style={{ maxWidth: "100%", borderRadius: 8 }}
      />
    </div>
  );
}
