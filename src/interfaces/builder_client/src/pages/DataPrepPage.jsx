import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import {
    Upload, FileText, CheckCircle2, Trash2, Loader2,
    FolderSearch, Search, Activity, BarChart3, AlertCircle,
    HardDrive, FileCode, Hash, Clock, ChevronDown, ChevronRight,
    BookOpen, Lightbulb, Database, Layers, Save, FolderOpen, X,
    Folder, ArrowUp, Lock, Download,
} from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Badge, ProgressBar, StatCard } from '../components/ui';
import {
    uploadData, scanDataDir, startDataAnalysis, getAnalysisStatus,
    getActiveDataPrep, saveActiveDataPrep,
    listDataPrepProfiles, saveDataPrepProfile, loadDataPrepProfile, deleteDataPrepProfile,
    browseDataDir,
} from '../lib/api';
import { formatBytes } from '../lib/utils';
import toast from 'react-hot-toast';

export default function DataPrepPage() {
    const [files, setFiles] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [uploadResults, setUploadResults] = useState(null);

    // Directory analysis state
    const [dirPath, setDirPath] = useState('');
    const [scanResult, setScanResult] = useState(null);
    const [scanning, setScanning] = useState(false);
    const [analyzing, setAnalyzing] = useState(false);
    const [analysisStatus, setAnalysisStatus] = useState(null);
    const [showLogs, setShowLogs] = useState(true);
    const pollRef = useRef(null);
    const logEndRef = useRef(null);

    // Refs for latest state (avoid stale closures in polling)
    const dirPathRef = useRef(dirPath);
    const scanResultRef = useRef(scanResult);
    useEffect(() => { dirPathRef.current = dirPath; }, [dirPath]);
    useEffect(() => { scanResultRef.current = scanResult; }, [scanResult]);

    // Profile state
    const [profiles, setProfiles] = useState([]);
    const [profileName, setProfileName] = useState('');
    const [showSaveDialog, setShowSaveDialog] = useState(false);
    const [savingProfile, setSavingProfile] = useState(false);
    const [loadingProfiles, setLoadingProfiles] = useState(false);

    // Directory browser state
    const [showBrowser, setShowBrowser] = useState(false);
    const [browserPath, setBrowserPath] = useState('');
    const [browserItems, setBrowserItems] = useState([]);
    const [browserParent, setBrowserParent] = useState(null);
    const [browserLoading, setBrowserLoading] = useState(false);

    // ── Restore active state + load profiles on mount ──
    useEffect(() => {
        (async () => {
            try {
                const { data } = await getActiveDataPrep();
                if (data?.active) {
                    const a = data.active;
                    if (a.dirPath) setDirPath(a.dirPath);
                    if (a.scanResult) setScanResult(a.scanResult);
                    if (a.analysisSummary) {
                        setAnalysisStatus({
                            phase: 'complete', progress: 100, running: false,
                            total_files: a.analysisSummary.total_files || 0,
                            scanned: a.analysisSummary.total_files || 0,
                            logs: a.analysisLogs || [], summary: a.analysisSummary, error: null,
                        });
                    }
                }
            } catch { /* first load, no saved state yet */ }
            fetchProfiles();
        })();
    }, []);

    const fetchProfiles = async () => {
        setLoadingProfiles(true);
        try {
            const { data } = await listDataPrepProfiles();
            setProfiles(data?.profiles || []);
        } catch { /* ignore */ }
        finally { setLoadingProfiles(false); }
    };

    // ── Auto-save helper ──
    const autoSave = useCallback(async (dp, sr, as_, logs) => {
        try {
            await saveActiveDataPrep({
                dirPath: dp,
                scanResult: sr,
                analysisSummary: as_,
                analysisLogs: logs || null,
            });
        } catch { /* background save, ignore errors */ }
    }, []);

    // ── Save report as JSON download ──
    const handleSaveReport = useCallback(() => {
        const report = {
            dirPath,
            scanResult: scanResult || null,
            analysisSummary: analysisStatus?.summary || null,
            analysisLogs: analysisStatus?.logs || null,
            generatedAt: new Date().toISOString(),
        };
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const ts = new Date().toISOString().replace(/[:.]/g, '').replace('T', '_').slice(0, 15);
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dataprep_report_${ts}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        toast.success('Report saved');
    }, [dirPath, scanResult, analysisStatus]);

    // ── Directory browser ──
    const openBrowser = async (path) => {
        setBrowserLoading(true);
        try {
            const { data } = await browseDataDir(path || '');
            setBrowserItems(data?.items || []);
            setBrowserPath(data?.path || '');
            setBrowserParent(data?.parent ?? null);
            setShowBrowser(true);
        } catch (err) {
            toast.error(err.response?.data?.error || 'Failed to browse directory');
        } finally {
            setBrowserLoading(false);
        }
    };

    const selectBrowserFolder = (path) => {
        setDirPath(path);
        setShowBrowser(false);
    };

    const onDrop = useCallback((accepted) => {
        setFiles((prev) => [...prev, ...accepted]);
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'text/plain': ['.txt'], 'text/csv': ['.csv'], 'application/json': ['.json', '.jsonl'] },
        maxSize: 500 * 1024 * 1024,
    });

    const removeFile = (idx) => setFiles((prev) => prev.filter((_, i) => i !== idx));

    const handleUpload = async () => {
        if (files.length === 0) return toast.error('No files selected');
        setUploading(true);
        try {
            const formData = new FormData();
            files.forEach((f) => formData.append('files', f));
            const { data } = await uploadData(formData);
            setUploadResults(data);
            toast.success(`Uploaded ${files.length} file(s) successfully`);
            setFiles([]);
        } catch (err) {
            toast.error(err.response?.data?.error || 'Upload failed');
        } finally {
            setUploading(false);
        }
    };

    // Directory scan
    const handleScan = async () => {
        if (!dirPath.trim()) return toast.error('Enter a directory path');
        setScanning(true);
        setScanResult(null);
        try {
            const { data } = await scanDataDir(dirPath.trim());
            setScanResult(data);
            autoSave(dirPath.trim(), data, null, null);
            if (data.total_files === 0) {
                toast('No supported data files found in directory', { icon: '\u26a0\ufe0f' });
            } else {
                toast.success(`Found ${data.total_files} files (${formatBytes(data.total_bytes)})`);
            }
        } catch (err) {
            toast.error(err.response?.data?.error || 'Scan failed');
        } finally {
            setScanning(false);
        }
    };

    // Start analysis
    const handleAnalyze = async () => {
        if (!dirPath.trim()) return toast.error('Enter a directory path first');
        setAnalyzing(true);
        setAnalysisStatus(null);
        try {
            await startDataAnalysis(dirPath.trim());
            toast.success('Analysis started');
            startPolling();
        } catch (err) {
            toast.error(err.response?.data?.error || 'Failed to start analysis');
            setAnalyzing(false);
        }
    };

    const startPolling = () => {
        stopPolling();
        pollRef.current = setInterval(async () => {
            try {
                const { data } = await getAnalysisStatus();
                setAnalysisStatus(data);
                if (!data.running && data.phase === 'complete') {
                    stopPolling();
                    setAnalyzing(false);
                    toast.success('Analysis complete');
                    // Use refs for latest values (avoid stale closure)
                    autoSave(dirPathRef.current, scanResultRef.current, data.summary, data.logs || []);
                }
                if (data.error) {
                    stopPolling();
                    setAnalyzing(false);
                    toast.error(`Analysis error: ${data.error}`);
                }
            } catch { /* ignore poll errors */ }
        }, 1000);
    };

    const stopPolling = () => {
        if (pollRef.current) {
            clearInterval(pollRef.current);
            pollRef.current = null;
        }
    };

    useEffect(() => () => stopPolling(), []);

    useEffect(() => {
        if (logEndRef.current) logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }, [analysisStatus?.logs?.length]);

    // ── Profile handlers ──
    const handleSaveProfile = async () => {
        if (!profileName.trim()) return toast.error('Enter a profile name');
        setSavingProfile(true);
        try {
            await saveDataPrepProfile({
                name: profileName.trim(),
                dirPath,
                scanResult,
                analysisSummary: analysisStatus?.summary || null,
            });
            toast.success(`Profile "${profileName.trim()}" saved`);
            setProfileName('');
            setShowSaveDialog(false);
            fetchProfiles();
        } catch (err) {
            toast.error(err.response?.data?.error || 'Failed to save profile');
        } finally {
            setSavingProfile(false);
        }
    };

    const handleLoadProfile = async (id) => {
        try {
            const { data } = await loadDataPrepProfile(id);
            const p = data?.profile;
            if (!p) return toast.error('Profile data not found');
            setDirPath(p.dirPath || '');
            setScanResult(p.scanResult || null);
            if (p.analysisSummary) {
                setAnalysisStatus({
                    phase: 'complete', progress: 100, running: false,
                    total_files: p.analysisSummary.total_files || 0,
                    scanned: p.analysisSummary.total_files || 0,
                    logs: [], summary: p.analysisSummary, error: null,
                });
            } else {
                setAnalysisStatus(null);
            }
            autoSave(p.dirPath || '', p.scanResult || null, p.analysisSummary || null);
            toast.success(`Loaded profile "${p.name}"`);
        } catch (err) {
            toast.error(err.response?.data?.error || 'Failed to load profile');
        }
    };

    const handleDeleteProfile = async (id, name) => {
        try {
            await deleteDataPrepProfile(id);
            toast.success(`Deleted profile "${name}"`);
            fetchProfiles();
        } catch (err) {
            toast.error(err.response?.data?.error || 'Failed to delete profile');
        }
    };

    const summary = analysisStatus?.summary;
    const isComplete = analysisStatus?.phase === 'complete' && summary;

    return (
        <ContentArea title="Data Preparation" subtitle="Upload, browse, and analyze training datasets.">
            <div className="space-y-6">
                {/* Data Prep Info Banner */}
                <Card>
                    <CardTitle icon={BookOpen}>About Data Preparation</CardTitle>
                    <p className="text-sm text-txt-secondary leading-relaxed mt-3">
                        Data preparation is the foundation of model training. This step lets you upload files directly
                        or point to an existing data directory on your system. The <strong>Analyze</strong> tool scans your data
                        for quality metrics — file types, line counts, token estimates, duplicates, and encoding issues —
                        giving you actionable recommendations before you proceed to tokenization and training.
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-4">
                        <div className="flex items-start gap-2 text-xs text-txt-muted">
                            <Database size={14} className="text-accent-cyan shrink-0 mt-0.5" />
                            <span><strong className="text-txt-secondary">Supported formats:</strong> .txt, .csv, .json, .jsonl, .parquet, .tsv, .md, .yaml</span>
                        </div>
                        <div className="flex items-start gap-2 text-xs text-txt-muted">
                            <Layers size={14} className="text-accent-indigo shrink-0 mt-0.5" />
                            <span><strong className="text-txt-secondary">Quality checks:</strong> Duplicates, encoding, empty files, line length distribution</span>
                        </div>
                        <div className="flex items-start gap-2 text-xs text-txt-muted">
                            <Lightbulb size={14} className="text-accent-warning shrink-0 mt-0.5" />
                            <span><strong className="text-txt-secondary">Recommendations:</strong> Token estimates, next steps, and optimization tips</span>
                        </div>
                    </div>
                </Card>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left column */}
                    <div className="lg:col-span-2 space-y-4">
                        {/* Directory Browser */}
                        <Card>
                            <CardTitle icon={FolderSearch}>Browse Data Directory</CardTitle>
                            <p className="text-xs text-txt-muted mt-1 mb-3">
                                Enter the full path to a folder, or click <strong>Browse</strong> to navigate your drives. Click <strong>Scan</strong> to preview files, then <strong>Analyze</strong> for deep inspection.
                            </p>
                            <div className="flex gap-2">
                                <div className="flex-1 relative">
                                    <HardDrive
                                        size={16}
                                        className="absolute left-3 top-1/2 -translate-y-1/2 text-txt-muted hover:text-accent-cyan cursor-pointer transition-colors z-10"
                                        onClick={() => openBrowser(dirPath || '')}
                                        title="Browse folders"
                                    />
                                    <input
                                        type="text"
                                        value={dirPath}
                                        onChange={(e) => setDirPath(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && handleScan()}
                                        placeholder="D:\data\training or /home/user/data"
                                        className="input-dark pl-10 w-full"
                                    />
                                </div>
                                <button
                                    onClick={() => openBrowser(dirPath || '')}
                                    disabled={browserLoading}
                                    className="btn-secondary whitespace-nowrap"
                                    title="Browse folders"
                                >
                                    {browserLoading ? <Loader2 size={16} className="animate-spin" /> : <FolderOpen size={16} />}
                                    Browse
                                </button>
                                <button onClick={handleScan} disabled={scanning} className="btn-secondary whitespace-nowrap">
                                    {scanning ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
                                    Scan
                                </button>
                                <button
                                    onClick={handleAnalyze}
                                    disabled={analyzing || (!scanResult && !dirPath.trim())}
                                    className="btn-primary whitespace-nowrap"
                                >
                                    {analyzing ? <Loader2 size={16} className="animate-spin" /> : <Activity size={16} />}
                                    Analyze
                                </button>
                                <button
                                    onClick={handleSaveReport}
                                    disabled={!scanResult && !analysisStatus?.summary}
                                    className="btn-secondary whitespace-nowrap"
                                    title="Save scan & analysis report as JSON"
                                >
                                    <Download size={16} />
                                    Save
                                </button>
                            </div>

                            {/* Folder browser panel */}
                            {showBrowser && (
                                <div className="mt-3 border border-ic-border rounded-xl bg-ic-bg overflow-hidden animate-fade-in-up">
                                    <div className="flex items-center justify-between px-3 py-2 bg-ic-surface border-b border-ic-border">
                                        <div className="flex items-center gap-2 text-xs text-txt-primary font-medium min-w-0">
                                            <Folder size={14} className="text-accent-cyan shrink-0" />
                                            <span className="truncate">{browserPath || 'Drives'}</span>
                                        </div>
                                        <div className="flex items-center gap-1 shrink-0">
                                            {browserParent !== null && (
                                                <button
                                                    onClick={() => openBrowser(browserParent)}
                                                    className="p-1 rounded hover:bg-ic-bg text-txt-muted hover:text-txt-secondary transition-colors"
                                                    title="Go up"
                                                >
                                                    <ArrowUp size={14} />
                                                </button>
                                            )}
                                            {browserPath && (
                                                <button
                                                    onClick={() => openBrowser('')}
                                                    className="p-1 rounded hover:bg-ic-bg text-txt-muted hover:text-txt-secondary transition-colors"
                                                    title="Go to drives"
                                                >
                                                    <HardDrive size={14} />
                                                </button>
                                            )}
                                            <button
                                                onClick={() => setShowBrowser(false)}
                                                className="p-1 rounded hover:bg-ic-bg text-txt-muted hover:text-txt-secondary transition-colors"
                                            >
                                                <X size={14} />
                                            </button>
                                        </div>
                                    </div>
                                    <div className="max-h-56 overflow-y-auto">
                                        {browserPath && (
                                            <button
                                                onClick={() => selectBrowserFolder(browserPath)}
                                                className="w-full flex items-center gap-2 px-3 py-2 text-xs text-accent-cyan hover:bg-accent-cyan/10 border-b border-ic-border transition-colors"
                                            >
                                                <CheckCircle2 size={12} />
                                                <span className="font-medium">Select this folder</span>
                                            </button>
                                        )}
                                        {browserItems.length === 0 && (
                                            <div className="px-3 py-4 text-xs text-txt-muted text-center">No subfolders found</div>
                                        )}
                                        {browserItems.map((item) => (
                                            <button
                                                key={item.path}
                                                onClick={() => item.locked ? null : openBrowser(item.path)}
                                                disabled={item.locked}
                                                className={`w-full flex items-center justify-between px-3 py-1.5 text-xs transition-colors ${item.locked
                                                    ? 'text-txt-muted cursor-not-allowed opacity-50'
                                                    : 'text-txt-secondary hover:bg-ic-surface hover:text-txt-primary cursor-pointer'
                                                    }`}
                                            >
                                                <div className="flex items-center gap-2 min-w-0">
                                                    {item.type === 'drive' ? (
                                                        <HardDrive size={13} className="text-accent-indigo shrink-0" />
                                                    ) : item.locked ? (
                                                        <Lock size={13} className="text-txt-muted shrink-0" />
                                                    ) : (
                                                        <Folder size={13} className="text-accent-warning shrink-0" />
                                                    )}
                                                    <span className="truncate">{item.name}</span>
                                                </div>
                                                {item.type === 'drive' && item.total_bytes > 0 && (
                                                    <span className="text-[10px] text-txt-muted shrink-0 ml-2">
                                                        {formatBytes(item.free_bytes)} free
                                                    </span>
                                                )}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Scan results preview */}
                            {scanResult && (
                                <div className="mt-4 p-4 rounded-xl bg-ic-bg border border-ic-border animate-fade-in-up">
                                    <div className="flex items-center justify-between mb-3">
                                        <h4 className="text-xs font-semibold text-txt-primary">Directory Scan</h4>
                                        <Badge variant={scanResult.total_files > 0 ? 'success' : 'warning'}>
                                            {scanResult.total_files} files &middot; {formatBytes(scanResult.total_bytes)}
                                        </Badge>
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        {Object.entries(scanResult.by_extension || {}).map(([ext, count]) => (
                                            <Badge key={ext} variant="cyan">
                                                <FileCode size={10} /> {ext} &times; {count}
                                            </Badge>
                                        ))}
                                    </div>
                                    {scanResult.files && scanResult.files.length > 0 && (
                                        <div className="mt-3 max-h-40 overflow-y-auto space-y-1">
                                            {scanResult.files.slice(0, 20).map((f, i) => (
                                                <div key={i} className="flex items-center justify-between text-xs py-1 px-2 rounded bg-ic-surface">
                                                    <div className="flex items-center gap-2 truncate">
                                                        <FileText size={12} className="text-accent-cyan shrink-0" />
                                                        <span className="text-txt-secondary truncate">{f.relative}</span>
                                                    </div>
                                                    <span className="text-txt-muted shrink-0 ml-2">{formatBytes(f.size)}</span>
                                                </div>
                                            ))}
                                            {scanResult.files.length > 20 && (
                                                <p className="text-[10px] text-txt-muted text-center mt-1">
                                                    ...and {scanResult.files.length - 20} more files
                                                </p>
                                            )}
                                        </div>
                                    )}
                                </div>
                            )}
                        </Card>

                        {/* Real-time Telemetry */}
                        {(analyzing || isComplete) && analysisStatus && (
                            <Card>
                                <div className="flex items-center justify-between">
                                    <CardTitle icon={Activity}>
                                        {analyzing ? 'Analysis Telemetry' : 'Analysis Complete'}
                                    </CardTitle>
                                    <div className="flex items-center gap-2">
                                        {analyzing && (
                                            <Badge variant="warning">
                                                <span className="w-1.5 h-1.5 rounded-full bg-accent-warning animate-pulse inline-block" />
                                                {analysisStatus.phase}
                                            </Badge>
                                        )}
                                        {isComplete && <Badge variant="success">Complete</Badge>}
                                    </div>
                                </div>

                                {/* Progress bar */}
                                <div className="mt-4 space-y-2">
                                    <div className="flex items-center justify-between text-xs">
                                        <span className="text-txt-muted">
                                            {analysisStatus.scanned} / {analysisStatus.total_files} files scanned
                                        </span>
                                        <span className="text-accent-cyan font-mono">{analysisStatus.progress}%</span>
                                    </div>
                                    <ProgressBar
                                        value={analysisStatus.progress}
                                        max={100}
                                        variant={isComplete ? 'success' : 'cyan'}
                                    />
                                </div>

                                {/* Live log feed */}
                                <div className="mt-4">
                                    <button
                                        onClick={() => setShowLogs(!showLogs)}
                                        className="flex items-center gap-1 text-xs text-txt-muted hover:text-txt-secondary transition-colors mb-2"
                                    >
                                        {showLogs ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                                        Live Log ({analysisStatus.logs?.length || 0} entries)
                                    </button>
                                    {showLogs && (
                                        <div className="bg-ic-bg border border-ic-border rounded-lg p-3 max-h-48 overflow-y-auto font-mono text-[11px] leading-relaxed">
                                            {(analysisStatus.logs || []).map((log, i) => (
                                                <div key={i} className={
                                                    log.startsWith('[error]') ? 'text-accent-danger'
                                                        : log.startsWith('[analysis]') ? 'text-accent-cyan'
                                                            : 'text-txt-muted'
                                                }>
                                                    {log}
                                                </div>
                                            ))}
                                            <div ref={logEndRef} />
                                        </div>
                                    )}
                                </div>

                                {analysisStatus.error && (
                                    <div className="mt-3 p-3 rounded-lg bg-accent-danger/10 border border-accent-danger/30 flex items-start gap-2">
                                        <AlertCircle size={14} className="text-accent-danger shrink-0 mt-0.5" />
                                        <span className="text-xs text-accent-danger">{analysisStatus.error}</span>
                                    </div>
                                )}
                            </Card>
                        )}

                        {/* Analysis Summary */}
                        {isComplete && summary && (
                            <Card>
                                <CardTitle icon={BarChart3}>Analysis Summary</CardTitle>
                                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
                                    <StatCard label="Files" value={summary.total_files?.toLocaleString()} icon={FileText} />
                                    <StatCard label="Total Size" value={formatBytes(summary.total_bytes)} icon={HardDrive} />
                                    <StatCard label="Lines" value={summary.total_lines?.toLocaleString()} icon={Hash} />
                                    <StatCard label="Est. Tokens" value={summary.total_tokens_est?.toLocaleString()} icon={Layers} />
                                </div>

                                {/* Extension breakdown */}
                                <div className="mt-4">
                                    <h4 className="text-xs font-semibold text-txt-primary mb-2">File Types</h4>
                                    <div className="flex flex-wrap gap-2">
                                        {Object.entries(summary.by_extension || {}).map(([ext, count]) => (
                                            <Badge key={ext} variant="cyan">
                                                {ext} &times; {count}
                                            </Badge>
                                        ))}
                                    </div>
                                </div>

                                {/* Quality metrics */}
                                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4">
                                    <div className="p-3 rounded-lg bg-ic-surface text-center">
                                        <div className="text-lg font-bold font-mono text-txt-primary">{summary.avg_line_length}</div>
                                        <div className="text-[10px] uppercase tracking-wider text-txt-muted">Avg Line Len</div>
                                    </div>
                                    <div className="p-3 rounded-lg bg-ic-surface text-center">
                                        <div className={`text-lg font-bold font-mono ${summary.duplicates > 0 ? 'text-accent-warning' : 'text-accent-success'}`}>
                                            {summary.duplicates}
                                        </div>
                                        <div className="text-[10px] uppercase tracking-wider text-txt-muted">Duplicates</div>
                                    </div>
                                    <div className="p-3 rounded-lg bg-ic-surface text-center">
                                        <div className={`text-lg font-bold font-mono ${summary.encoding_errors > 0 ? 'text-accent-danger' : 'text-accent-success'}`}>
                                            {summary.encoding_errors || 0}
                                        </div>
                                        <div className="text-[10px] uppercase tracking-wider text-txt-muted">Encoding Errs</div>
                                    </div>
                                    <div className="p-3 rounded-lg bg-ic-surface text-center">
                                        <div className={`text-lg font-bold font-mono ${summary.empty_files > 0 ? 'text-accent-warning' : 'text-accent-success'}`}>
                                            {summary.empty_files || 0}
                                        </div>
                                        <div className="text-[10px] uppercase tracking-wider text-txt-muted">Empty Files</div>
                                    </div>
                                </div>

                                {/* Sample data */}
                                {summary.sample_lines && summary.sample_lines.length > 0 && (
                                    <div className="mt-4">
                                        <h4 className="text-xs font-semibold text-txt-primary mb-2">Data Sample</h4>
                                        <div className="bg-ic-bg border border-ic-border rounded-lg p-3 max-h-32 overflow-y-auto">
                                            {summary.sample_lines.map((line, i) => (
                                                <div key={i} className="text-[11px] font-mono text-txt-muted truncate py-0.5">
                                                    {line}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Recommendations */}
                                {summary.recommendations && summary.recommendations.length > 0 && (
                                    <div className="mt-4">
                                        <h4 className="text-xs font-semibold text-txt-primary mb-2 flex items-center gap-1.5">
                                            <Lightbulb size={12} className="text-accent-warning" />
                                            Recommendations
                                        </h4>
                                        <ul className="space-y-1.5">
                                            {summary.recommendations.map((rec, i) => (
                                                <li key={i} className="text-xs text-txt-secondary flex items-start gap-2">
                                                    <span className="w-1.5 h-1.5 rounded-full bg-accent-cyan shrink-0 mt-1.5" />
                                                    {rec}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </Card>
                        )}

                        {/* Upload area */}
                        <Card>
                            <CardTitle icon={Upload}>Upload Training Data</CardTitle>
                            <div
                                {...getRootProps()}
                                className={`mt-4 border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${isDragActive ? 'border-accent-cyan bg-accent-cyan/5' : 'border-ic-border hover:border-accent-cyan/30'
                                    }`}
                            >
                                <input {...getInputProps()} />
                                <Upload size={32} className="mx-auto mb-3 text-txt-muted" />
                                <p className="text-sm text-txt-secondary">
                                    {isDragActive ? 'Drop files here...' : 'Drag & drop files, or click to browse'}
                                </p>
                                <p className="text-xs text-txt-muted mt-1">Supports .txt, .csv, .json, .jsonl — max 500MB</p>
                            </div>
                            {files.length > 0 && (
                                <div className="mt-4 space-y-2">
                                    {files.map((f, i) => (
                                        <div key={i} className="flex items-center justify-between bg-ic-surface rounded-lg px-4 py-2">
                                            <div className="flex items-center gap-3">
                                                <FileText size={16} className="text-accent-cyan" />
                                                <span className="text-sm text-txt-primary truncate max-w-xs">{f.name}</span>
                                                <Badge variant="info">{formatBytes(f.size)}</Badge>
                                            </div>
                                            <button onClick={() => removeFile(i)} className="text-txt-muted hover:text-accent-danger transition-colors">
                                                <Trash2 size={14} />
                                            </button>
                                        </div>
                                    ))}
                                    <button onClick={handleUpload} disabled={uploading} className="btn-primary mt-2">
                                        {uploading ? <Loader2 size={16} className="animate-spin" /> : <Upload size={16} />}
                                        Upload {files.length} File{files.length !== 1 ? 's' : ''}
                                    </button>
                                </div>
                            )}
                        </Card>
                    </div>

                    {/* Right sidebar */}
                    <div className="space-y-4">
                        {/* Saved Profiles */}
                        <Card>
                            <div className="flex items-center justify-between">
                                <CardTitle icon={FolderOpen}>Data Prep Profiles</CardTitle>
                                <button
                                    onClick={() => setShowSaveDialog(true)}
                                    disabled={!dirPath.trim() && !scanResult}
                                    className="btn-secondary text-xs px-2 py-1"
                                    title="Save current state as a named profile"
                                >
                                    <Save size={12} /> Save
                                </button>
                            </div>

                            {/* Save dialog */}
                            {showSaveDialog && (
                                <div className="mt-3 p-3 rounded-lg bg-ic-bg border border-accent-cyan/30 animate-fade-in-up">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-xs font-semibold text-txt-primary">Save Profile</span>
                                        <button onClick={() => setShowSaveDialog(false)} className="text-txt-muted hover:text-txt-secondary">
                                            <X size={12} />
                                        </button>
                                    </div>
                                    <input
                                        type="text"
                                        value={profileName}
                                        onChange={(e) => setProfileName(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && handleSaveProfile()}
                                        placeholder="Profile name..."
                                        className="input-dark w-full text-xs mb-2"
                                        autoFocus
                                    />
                                    <button
                                        onClick={handleSaveProfile}
                                        disabled={savingProfile || !profileName.trim()}
                                        className="btn-primary text-xs w-full"
                                    >
                                        {savingProfile ? <Loader2 size={12} className="animate-spin" /> : <Save size={12} />}
                                        Save Profile
                                    </button>
                                </div>
                            )}

                            {/* Profile list */}
                            {loadingProfiles ? (
                                <div className="mt-3 flex items-center justify-center py-4">
                                    <Loader2 size={14} className="animate-spin text-txt-muted" />
                                </div>
                            ) : profiles.length > 0 ? (
                                <div className="mt-3 space-y-2 max-h-64 overflow-y-auto">
                                    {profiles.map((p) => (
                                        <div
                                            key={p.id}
                                            className="group flex items-center justify-between p-2 rounded-lg bg-ic-surface hover:bg-ic-surface/80 cursor-pointer transition-colors"
                                            onClick={() => handleLoadProfile(p.id)}
                                        >
                                            <div className="min-w-0 flex-1">
                                                <div className="text-xs font-medium text-txt-primary truncate">{p.name}</div>
                                                <div className="text-[10px] text-txt-muted truncate">
                                                    {p.dirPath && <span>{p.dirPath}</span>}
                                                </div>
                                                <div className="text-[10px] text-txt-muted flex items-center gap-2">
                                                    {p.scanResult?.total_files != null && (
                                                        <span>{p.scanResult.total_files} files</span>
                                                    )}
                                                    {p.analysisSummary?.total_tokens_est != null && (
                                                        <span>~{p.analysisSummary.total_tokens_est.toLocaleString()} tokens</span>
                                                    )}
                                                    {p.created_at && (
                                                        <span>{new Date(p.created_at).toLocaleDateString()}</span>
                                                    )}
                                                </div>
                                            </div>
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleDeleteProfile(p.id, p.name);
                                                }}
                                                className="opacity-0 group-hover:opacity-100 text-txt-muted hover:text-accent-danger transition-all ml-2 shrink-0"
                                                title="Delete profile"
                                            >
                                                <Trash2 size={12} />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="mt-3 text-xs text-txt-muted text-center py-3">
                                    No saved profiles yet. Scan a directory and click <strong>Save</strong> to create one.
                                </p>
                            )}
                        </Card>

                        <Card>
                            <CardTitle>Data Guidelines</CardTitle>
                            <ul className="mt-3 space-y-2 text-xs text-txt-muted">
                                <li className="flex items-start gap-2"><CheckCircle2 size={12} className="text-accent-success mt-0.5 shrink-0" /> Clean, UTF-8 encoded text</li>
                                <li className="flex items-start gap-2"><CheckCircle2 size={12} className="text-accent-success mt-0.5 shrink-0" /> One document per line for .txt</li>
                                <li className="flex items-start gap-2"><CheckCircle2 size={12} className="text-accent-success mt-0.5 shrink-0" /> JSON lines format for structured data</li>
                                <li className="flex items-start gap-2"><CheckCircle2 size={12} className="text-accent-success mt-0.5 shrink-0" /> Minimum 10K samples recommended</li>
                                <li className="flex items-start gap-2"><CheckCircle2 size={12} className="text-accent-success mt-0.5 shrink-0" /> Remove duplicates and PII</li>
                            </ul>
                        </Card>

                        <Card>
                            <CardTitle icon={Clock}>Workflow</CardTitle>
                            <ol className="mt-3 space-y-3 text-xs text-txt-muted">
                                <li className="flex items-start gap-2">
                                    <span className="step-badge shrink-0">1</span>
                                    <span><strong className="text-txt-secondary">Browse</strong> — point to your data directory and scan for files</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="step-badge shrink-0">2</span>
                                    <span><strong className="text-txt-secondary">Analyze</strong> — run deep inspection for quality, tokens, and duplicates</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="step-badge shrink-0">3</span>
                                    <span><strong className="text-txt-secondary">Upload</strong> — optionally upload additional files</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="step-badge shrink-0">4</span>
                                    <span><strong className="text-txt-secondary">Next</strong> — proceed to Tokenization (step 4)</span>
                                </li>
                            </ol>
                        </Card>

                        {uploadResults && (
                            <Card>
                                <CardTitle>Upload Results</CardTitle>
                                <pre className="mt-3 text-xs font-mono text-accent-cyan bg-ic-surface rounded-lg p-3 overflow-auto max-h-60">
                                    {JSON.stringify(uploadResults, null, 2)}
                                </pre>
                            </Card>
                        )}
                    </div>
                </div>
            </div>
        </ContentArea>
    );
}
