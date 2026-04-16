import LoadingSpinner from "@/components/LoadingSpinner";

export default function Loading() {
  return (
    <div className="card p-6">
      <LoadingSpinner label="Loading dashboard..." />
    </div>
  );
}
