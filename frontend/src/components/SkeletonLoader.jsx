/**
 * Skeleton Loader Components
 * 
 * Loading placeholders that show the structure of content while it loads
 */

export function ContractCardSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow animate-pulse">
      <div className="p-6">
        {/* Title */}
        <div className="h-6 bg-gray-200 rounded w-3/4 mb-3"></div>
        
        {/* Description */}
        <div className="space-y-2 mb-4">
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        </div>
        
        {/* Badges */}
        <div className="flex gap-2 mb-4">
          <div className="h-6 bg-gray-200 rounded w-16"></div>
          <div className="h-6 bg-gray-200 rounded w-20"></div>
        </div>
        
        {/* File size */}
        <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
        
        {/* Date */}
        <div className="h-3 bg-gray-200 rounded w-32 mb-4"></div>
        
        {/* Buttons */}
        <div className="flex gap-2">
          <div className="h-9 bg-gray-200 rounded flex-1"></div>
          <div className="h-9 bg-gray-200 rounded w-20"></div>
        </div>
      </div>
    </div>
  );
}

export function ContractListSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <ContractCardSkeleton key={i} />
      ))}
    </div>
  );
}

export function ContractDetailSkeleton() {
  return (
    <div className="bg-white rounded-lg shadow p-8 animate-pulse">
      {/* Header */}
      <div className="mb-6">
        <div className="h-8 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div className="h-6 bg-gray-200 rounded w-1/3"></div>
      </div>
      
      {/* Status */}
      <div className="mb-6">
        <div className="h-6 bg-gray-200 rounded w-24"></div>
      </div>
      
      {/* Content sections */}
      <div className="space-y-6">
        {[1, 2, 3].map((i) => (
          <div key={i}>
            <div className="h-6 bg-gray-200 rounded w-1/4 mb-3"></div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 rounded w-full"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
              <div className="h-4 bg-gray-200 rounded w-4/6"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
