import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle2, Trash2, Loader2 } from 'lucide-react';
import ContentArea from '../components/layout/ContentArea';
import { Card, CardTitle, Badge } from '../components/ui';
import { uploadData } from '../lib/api';
import { formatBytes } from '../lib/utils';
import toast from 'react-hot-toast';

export default function DataPrepPage() {
    const [files, setFiles] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [uploadResults, setUploadResults] = useState(null);

    const onDrop = useCallback((accepted) => {
        setFiles((prev) => [...prev, ...accepted]);
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'text/plain': ['.txt'], 'text/csv': ['.csv'], 'application/json': ['.json', '.jsonl'] },
        maxSize: 500 * 1024 * 1024, // 500MB
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

    return (
        <ContentArea title="Data Preparation" subtitle="Upload and validate training datasets.">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Upload area */}
                <div className="lg:col-span-2 space-y-4">
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

                        {/* File list */}
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

                {/* Stats / Results */}
                <div className="space-y-4">
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
        </ContentArea>
    );
}
