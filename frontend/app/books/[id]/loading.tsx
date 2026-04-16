import LoadingSpinner from "@/components/LoadingSpinner";

export default function LoadingBookDetail() {
  return (
    <div className="card p-6">
      <LoadingSpinner label="Loading book details..." />
    </div>
  );
}
