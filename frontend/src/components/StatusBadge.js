export default function StatusBadge({ status }) {
    const statusMap = {
        'new': { label: 'New', color: 'amber' },
        'priority': { label: 'Priority', color: 'green' }, // Added 'priority' mapping just in case
        'accepted': { label: 'Priority', color: 'green' },
        'qualified': { label: 'Qualified', color: 'blue' },
        'rejected': { label: 'Rejected', color: 'red' },
        'contacted': { label: 'Contacted', color: 'green' },
        'converted': { label: 'Converted', color: 'purple' },
        'review_required': { label: 'Review', color: 'amber' } // Added backend default
    };

    const normalizeStatus = (s) => (s || 'new').toLowerCase();
    const statusInfo = statusMap[normalizeStatus(status)] || statusMap['new'];

    const colorClasses = {
        green: 'text-green-600 bg-green-50 border-green-100',
        blue: 'text-blue-600 bg-blue-50 border-blue-100',
        amber: 'text-amber-600 bg-amber-50 border-amber-100',
        red: 'text-red-600 bg-red-50 border-red-100',
        purple: 'text-purple-600 bg-purple-50 border-purple-100'
    };

    return (
        <span className={`font-black text-[9px] px-2 py-1 lg:px-4 lg:py-2 border rounded-full uppercase tracking-widest shadow-sm whitespace-nowrap ${colorClasses[statusInfo.color] || colorClasses.amber}`}>
            {statusInfo.label}
        </span>
    );
}
