export function StatCardSkeleton() {
  return (
    <div className="bg-white rounded-2xl p-5 sm:p-6 shadow-lg shadow-gray-200/50 border border-gray-100 animate-pulse">
      <div className="w-12 h-12 rounded-xl bg-gray-200 mb-4" />
      <div className="h-4 w-20 bg-gray-200 rounded mb-2" />
      <div className="h-8 w-16 bg-gray-200 rounded" />
    </div>
  );
}
