'use client';

import {useEffect, useState} from 'react';
import {useRouter} from 'next/navigation';
import {motion, AnimatePresence} from 'framer-motion';
import {
    Plug,
    Plus,
    Search,
    Database,
    Cloud,
    HardDrive,
    Globe,
    Trash2,
    Edit,
    RefreshCw,
    X,
    ChevronRight
} from 'lucide-react';
import {AppLayout} from '@/components/layout/AppLayout';
import {
    getConnectors,
    deleteConnector,
    testConnector
} from '@/lib/api/connectors';
import {
    Connector,
    ConnectorType,
    getConnectorTypeLabel,
    getConnectorDisplayStatus
} from '@/types/connector';

const connectorTypes: { type: ConnectorType; label: string; icon: React.ElementType; description: string; color: string }[] = [
    {
        type: 'mysql',
        label: 'MySQL',
        icon: Database,
        description: 'Connect to MySQL database',
        color: '#4479A1'
    },
    {
        type: 'postgresql',
        label: 'PostgreSQL',
        icon: Database,
        description: 'Connect to PostgreSQL database',
        color: '#336791'
    },
    {
        type: 'mongodb',
        label: 'MongoDB',
        icon: Database,
        description: 'Connect to MongoDB document database',
        color: '#47A248'
    },
    {
        type: 'salesforce',
        label: 'Salesforce',
        icon: Cloud,
        description: 'Connect to Salesforce CRM data',
        color: '#00A1E0'
    },
    {
        type: 'csv',
        label: 'CSV File',
        icon: HardDrive,
        description: 'Import data from CSV files',
        color: '#28A745'
    },
    {
        type: 'api',
        label: 'REST API',
        icon: Globe,
        description: 'Fetch data via REST API',
        color: '#FF6C37'
    }
];

function getConnectorIcon(type: ConnectorType) {
    const config = connectorTypes.find(c => c.type === type);
    return config?.icon || Database;
}

function getConnectorColor(type: ConnectorType) {
    const config = connectorTypes.find(c => c.type === type);
    return config?.color || '#2563eb';
}

export default function ConnectorsPage() {
    const router = useRouter();
    const [connectors, setConnectors] = useState<Connector[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [testingId, setTestingId] = useState<string | null>(null);
    const [showAddModal, setShowAddModal] = useState(false);

    useEffect(() => {
        loadConnectors();
    }, []);

    const loadConnectors = async () => {
        try {
            setIsLoading(true);
            const response = await getConnectors(1, 50);
            setConnectors(response.data);
        } catch (error) {
            console.error('Failed to load connectors:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleTestConnection = async (id: string) => {
        setTestingId(id);
        try {
            await testConnector(id);
            await loadConnectors();
        } catch (error) {
            console.error('Failed to test connection:', error);
        } finally {
            setTestingId(null);
        }
    };

    const handleDeleteConnector = async (id: string) => {
        if (!confirm('Are you sure you want to delete this connector?')) { return; }

        try {
            await deleteConnector(id);
            setConnectors(prev => prev.filter(c => c.id !== id));
        } catch (error) {
            console.error('Failed to delete connector:', error);
        }
    };

    const filteredConnectors = connectors.filter(c =>
        c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.type.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <AppLayout>
            <div className="space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-[var(--color-text)]">Connectors</h1>
                        <p className="mt-1 text-[var(--color-text-muted)]">
                            Manage data source connections
                        </p>
                    </div>
                    <motion.button
                        whileHover={{scale: 1.02}}
                        whileTap={{scale: 0.98}}
                        onClick={() => setShowAddModal(true)}
                        className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-md"
                    >
                        <Plus className="w-5 h-5" />
                        New Connection
                    </motion.button>
                </div>

                {/* Supported Types */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {connectorTypes.map((type) => {
                        const Icon = type.icon;
                        const isConnected = connectors.some(c => c.type === type.type && c.lastTestStatus === 'success');

                        return (
                            <motion.div
                                key={type.type}
                                whileHover={{y: -2}}
                                className="bg-white rounded-xl p-5 border border-[var(--color-border)] shadow-[var(--shadow-card)] hover:shadow-[var(--shadow-card-hover)] transition-all"
                            >
                                <div className="flex items-start gap-4">
                                    <div
                                        className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
                                        style={{backgroundColor: `${type.color}15`}}
                                    >
                                        <Icon className="w-6 h-6" style={{color: type.color}} />
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2">
                                            <h3 className="font-medium text-[var(--color-text)]">{type.label}</h3>
                                            {isConnected && (
                                                <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                                                    Connected
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-sm text-[var(--color-text-muted)] mt-1">{type.description}</p>
                                    </div>
                                </div>
                            </motion.div>
                        );
                    })}
                </div>

                {/* Connected Accounts */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-semibold text-[var(--color-text)]">Connected Accounts</h2>
                        <div className="relative w-64">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-placeholder)]" />
                            <input
                                type="text"
                                placeholder="Search connectors..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 bg-white border border-[var(--color-border)] rounded-lg text-sm text-[var(--color-text)] placeholder-[var(--color-text-placeholder)] focus:outline-none focus:border-[var(--color-primary)] transition-all"
                            />
                        </div>
                    </div>

                    {isLoading ? (
                        <div className="flex items-center justify-center h-32">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
                        </div>
                    ) : filteredConnectors.length === 0 ? (
                        <div className="bg-white rounded-xl border border-[var(--color-border)] border-dashed p-12 text-center">
                            <Plug className="w-12 h-12 text-[var(--color-text-placeholder)] mx-auto mb-4" />
                            <p className="text-[var(--color-text-muted)]">No connected accounts</p>
                            <button
                                onClick={() => setShowAddModal(true)}
                                className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
                            >
                                Create your first connection
                            </button>
                        </div>
                    ) : (
                        <div className="bg-white rounded-xl border border-[var(--color-border)] shadow-[var(--shadow-card)] overflow-hidden">
                            <div className="divide-y divide-[var(--color-border)]">
                                {filteredConnectors.map((connector) => {
                                    const Icon = getConnectorIcon(connector.type);
                                    const color = getConnectorColor(connector.type);
                                    const status = getConnectorDisplayStatus(connector);

                                    return (
                                        <motion.div
                                            key={connector.id}
                                            initial={{opacity: 0}}
                                            animate={{opacity: 1}}
                                            className="p-4 flex items-center justify-between hover:bg-[var(--color-surface)] transition-colors"
                                        >
                                            <div className="flex items-center gap-4">
                                                <div
                                                    className="w-10 h-10 rounded-lg flex items-center justify-center"
                                                    style={{backgroundColor: `${color}15`}}
                                                >
                                                    <Icon className="w-5 h-5" style={{color}} />
                                                </div>
                                                <div>
                                                    <h3 className="font-medium text-[var(--color-text)]">{connector.name}</h3>
                                                    <div className="flex items-center gap-2 mt-0.5">
                                                        <span className="text-xs text-[var(--color-text-muted)]">
                                                            {getConnectorTypeLabel(connector.type)}
                                                        </span>
                                                        <span
                                                            className="w-1.5 h-1.5 rounded-full"
                                                            style={{backgroundColor: status.color}}
                                                        />
                                                        <span className="text-xs" style={{color: status.color}}>
                                                            {status.label}
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="flex items-center gap-2">
                                                <button
                                                    onClick={() => handleTestConnection(connector.id)}
                                                    disabled={testingId === connector.id}
                                                    className="p-2 hover:bg-white rounded-lg transition-colors disabled:opacity-50"
                                                >
                                                    <RefreshCw className={`w-4 h-4 text-[var(--color-text-muted)] ${testingId === connector.id ? 'animate-spin' : ''}`} />
                                                </button>
                                                <button
                                                    onClick={() => router.push(`/app/connectors/${connector.id}`)}
                                                    className="p-2 hover:bg-white rounded-lg transition-colors"
                                                >
                                                    <Edit className="w-4 h-4 text-[var(--color-text-muted)]" />
                                                </button>
                                                <button
                                                    onClick={() => handleDeleteConnector(connector.id)}
                                                    className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                                                >
                                                    <Trash2 className="w-4 h-4 text-red-500" />
                                                </button>
                                            </div>
                                        </motion.div>
                                    );
                                })}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Add Connector Modal */}
            <AnimatePresence>
                {showAddModal && (
                    <>
                        <div
                            className="fixed inset-0 bg-black/50 z-40"
                            onClick={() => setShowAddModal(false)}
                        />
                        <motion.div
                            initial={{opacity: 0, scale: 0.95}}
                            animate={{opacity: 1, scale: 1}}
                            exit={{opacity: 0, scale: 0.95}}
                            className="fixed inset-0 flex items-center justify-center z-50 p-4"
                        >
                            <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[80vh] overflow-hidden"
                                onClick={(e) => e.stopPropagation()}
                            >
                                <div className="p-6 border-b border-[var(--color-border)]">
                                    <div className="flex items-center justify-between">
                                        <h2 className="text-lg font-semibold text-[var(--color-text)]">Select Connector Type</h2>
                                        <button
                                            onClick={() => setShowAddModal(false)}
                                            className="p-1 hover:bg-[var(--color-surface)] rounded-lg transition-colors"
                                        >
                                            <X className="w-5 h-5 text-[var(--color-text-muted)]" />
                                        </button>
                                    </div>
                                </div>

                                <div className="p-6 overflow-y-auto">
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                        {connectorTypes.map((type) => {
                                            const Icon = type.icon;
                                            return (
                                                <motion.button
                                                    key={type.type}
                                                    whileHover={{scale: 1.02}}
                                                    whileTap={{scale: 0.98}}
                                                    onClick={() => {
                                                        setShowAddModal(false);
                                                        router.push(`/app/connectors/new?type=${type.type}`);
                                                    }}
                                                    className="flex items-center gap-4 p-4 rounded-xl border border-[var(--color-border)] hover:border-blue-500 hover:bg-blue-50 transition-all text-left"
                                                >
                                                    <div
                                                        className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
                                                        style={{backgroundColor: `${type.color}15`}}
                                                    >
                                                        <Icon className="w-6 h-6" style={{color: type.color}} />
                                                    </div>
                                                    <div>
                                                        <h3 className="font-medium text-[var(--color-text)]">{type.label}</h3>
                                                        <p className="text-sm text-[var(--color-text-muted)] mt-0.5">{type.description}</p>
                                                    </div>
                                                    <ChevronRight className="w-5 h-5 text-[var(--color-text-placeholder)] ml-auto" />
                                                </motion.button>
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </AppLayout>
    );
}
