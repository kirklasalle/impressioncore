import React, { useState, useEffect, useRef, memo, useMemo, useCallback } from 'react';
import axios from 'axios';
import { Terminal, Send, Layers, Mic, MicOff, ScrollText, Camera, Volume2, Settings, RefreshCw, AlertTriangle, ShieldCheck, Activity, Brain, Trash2, CheckCircle2, XCircle, BrainCircuit, X, Zap, Save, RotateCcw, Power, Target, ChevronUp, ChevronDown, Settings2, Cpu } from "lucide-react";
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Fallback to Fuchsia as Magenta is not default Tailwind
const cn = (...inputs) => twMerge(clsx(inputs));
const API_HOST = window.location.hostname === "localhost" ? "127.0.0.1" : (window.location.hostname || "127.0.0.1");
const API_BASE = `${window.location.protocol}//${API_HOST}:8000`;
const API_WS_BASE = `ws://${API_HOST}:8000`;
const API_URL = `${API_BASE}/v1/process`;
const SESSIONS_API = `${API_BASE}/v1/sessions`;
const HARDWARE_API = `${API_BASE}/v1/hardware`;
const DIAG_API = `${API_BASE}/v1/vision/diagnostics`;
const STREAM_URL = `${API_BASE}/v1/vision/stream`;
const TELEMETRY_WS = `${API_BASE}/v1/telemetry/stream`.replace("http", "ws");

/* TELEMETRY HOOK */
const useTelemetry = (url) => {
    const [telemetry, setTelemetry] = useState(null);
    useEffect(() => {
        let ws = new WebSocket(url);
        ws.onopen = () => console.log("Telemetry Connected");
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                setTelemetry(data);
            } catch (e) {
                console.error("Telemetry Parse Error", e);
            }
        };
        ws.onclose = () => console.log("Telemetry Disconnected");
        return () => ws.close();
    }, [url]);
    return [telemetry, setTelemetry];
};

import NeuralFaceMesh from './components/NeuralFaceMesh';

const NeuralSkeleton = memo(({ skeleton }) => {
    if (!skeleton || !skeleton.joints) return null;

    // Scale and center logic (Custom for Avatar Panel box)
    // Box is approx 100x120px. Skeleton is normalized -1 to +1 approx.
    const project = (jointName) => {
        const j = skeleton.joints[jointName];
        if (!j) return null;

        // Apply Offset & Scale (Y-flip for standard coords)
        const scale = 40;
        const offsetX = 50;
        const offsetY = 50;

        return {
            x: (j.x * scale) + offsetX,
            y: (j.y * -scale) + offsetY // Invert Y because screen Y is down
        };
    };

    // Connections to draw
    const BONES = [
        ['HEAD', 'SHOULDER_CENTER'],
        ['SHOULDER_CENTER', 'SPINE'],
        ['SPINE', 'HIP_CENTER'],
        ['SHOULDER_CENTER', 'SHOULDER_LEFT'],
        ['SHOULDER_LEFT', 'ELBOW_LEFT'],
        ['ELBOW_LEFT', 'WRIST_LEFT'],
        ['WRIST_LEFT', 'HAND_LEFT'],
        ['SHOULDER_CENTER', 'SHOULDER_RIGHT'],
        ['SHOULDER_RIGHT', 'ELBOW_RIGHT'],
        ['ELBOW_RIGHT', 'WRIST_RIGHT'],
        ['WRIST_RIGHT', 'HAND_RIGHT'],
        // Legs (if seated mode active, these will reflect that)
        ['HIP_CENTER', 'HIP_LEFT'],
        ['HIP_LEFT', 'KNEE_LEFT'],
        ['KNEE_LEFT', 'ANKLE_LEFT'],
        ['HIP_CENTER', 'HIP_RIGHT'],
        ['HIP_RIGHT', 'KNEE_RIGHT'],
        ['KNEE_RIGHT', 'ANKLE_RIGHT'],
    ];

    return (
        <svg viewBox="0 0 100 100" className="w-full h-full opacity-80 decoration-slice">
            <defs>
                <filter id="glow">
                    <feGaussianBlur stdDeviation="2.5" result="coloredBlur" />
                    <feMerge>
                        <feMergeNode in="coloredBlur" />
                        <feMergeNode in="SourceGraphic" />
                    </feMerge>
                </filter>
            </defs>

            {/* Render Bones */}
            {BONES.map(([start, end], i) => {
                const p1 = project(start);
                const p2 = project(end);
                if (!p1 || !p2) return null;
                return (
                    <line
                        key={i}
                        x1={p1.x} y1={p1.y}
                        x2={p2.x} y2={p2.y}
                        stroke="#22d3ee" // Cyan-400
                        strokeWidth="2"
                        strokeLinecap="round"
                        filter="url(#glow)"
                        opacity="0.6"
                    />
                );
            })}

            {/* Render Head (Special) */}
            {project('HEAD') && (
                <circle
                    cx={project('HEAD').x}
                    cy={project('HEAD').y}
                    r="5"
                    fill="#818cf8" // Purple-500
                    filter="url(#glow)"
                />
            )}

            {/* Render Hand Tips (for gestures) */}
            {['HAND_LEFT', 'HAND_RIGHT'].map(h => {
                const p = project(h);
                return p && (
                    <circle
                        key={h}
                        cx={p.x} cy={p.y} r="3"
                        fill="#facc15" // Yellow-400
                        className="animate-pulse"
                    />
                );
            })}
        </svg>
    );
});

const HappyFace = memo(({ expression, telemetry, talking }) => {
    // Morphing mouth state
    const [mouthOpen, setMouthOpen] = useState(0);
    const poses = telemetry?.poses || [];
    const isWaving = poses.some(p => p.startsWith("WAVING"));
    const isEngaged = poses.includes("LEANING_FORWARD_ENGAGED");

    // Lip Sync Loop (Organic)
    useEffect(() => {
        let timeout;
        const animateMouth = () => {
            if (talking) {
                // Randomize open amount (2-6px) and duration (50-150ms) for natural speech look
                const targetOpen = Math.random() * 4 + 2;
                setMouthOpen(prev => (prev > 1 ? 0 : targetOpen));
                timeout = setTimeout(animateMouth, Math.random() * 100 + 80);
            } else {
                setMouthOpen(0);
            }
        };

        if (talking) animateMouth();
        else setMouthOpen(0);

        return () => clearTimeout(timeout);
    }, [talking]);

    // Determine mouth path based on expression (simplified morphing)
    const getMouthPath = (exp, open) => {
        const openness = open || 0;
        switch (exp) {
            case 'HAPPY': return `M 30 ${70 + openness} Q 50 ${90 + openness} 70 ${70 + openness} Q 50 ${90 + openness * 2} 30 ${70 + openness}`;
            case 'ANGRY': return `M 35 ${75 + openness} Q 50 ${70 + openness} 65 ${75 + openness} Q 50 ${85 + openness} 35 ${75 + openness}`;
            case 'SAD': return `M 35 ${80 + openness} Q 50 ${70 + openness} 65 ${80 + openness}`;
            case 'THINKING': return "M 45 75 L 55 75";
            case 'WONDER': return `M 40 ${75 - openness} A 10 10 0 1 0 60 ${75 - openness} A 10 10 0 1 0 40 ${75 - openness}`;
            default: // NEUTRAL
                return `M 40 ${75 + openness} Q 50 ${75 + openness * 2} 60 ${75 + openness}`;
        }
    };

    // Calculate pupil positions based on tracking
    const tx = (telemetry?.pos?.[0] ?? 0) * 5;
    const ty = (telemetry?.pos?.[1] ?? 0) * 5;

    // Custom float animation style
    const floatStyle = {
        animation: 'float 6s ease-in-out infinite'
    };

    return (
        <div className="w-full h-full flex items-center justify-center relative overflow-hidden bg-gradient-to-b from-yellow-500/10 to-transparent" style={{ perspective: '800px' }}>
            {/* Inject minimal keyframes for floating */}
            <style>
                {`
                @keyframes float {
                    0% { transform: translateY(0px); }
                    50% { transform: translateY(-3px); }
                    100% { transform: translateY(0px); }
                }
                `}
            </style>

            {/* Ambient Idle Animation (Gentle Float + Tracking Rotation) */}
            <svg
                viewBox="0 0 100 100"
                className="w-32 h-32 drop-shadow-[0_0_15px_rgba(234,179,8,0.3)] transition-transform duration-200 ease-out"
                style={{
                    ...floatStyle,
                    transform: `
                        translate(${tx}px, ${ty}px) 
                        rotateX(${(telemetry?.hcep?.user_pose?.pitch || 0) * 15}deg) 
                        rotateY(${(telemetry?.hcep?.user_pose?.yaw || 0) * 25}deg)
                        rotateZ(${(telemetry?.hcep?.user_pose?.roll || 0) * -10}deg)
                    `
                }}
            >
                {/* Head */}
                <circle cx="50" cy="50" r="45" fill="#eab308" className="transition-all duration-500" />
                <circle cx="50" cy="50" r="45" fill="url(#faceGradient)" />

                {/* Definitions for Gradients */}
                <defs>
                    <radialGradient id="faceGradient" cx="40%" cy="40%" r="60%">
                        <stop offset="0%" stopColor="#fde047" />
                        <stop offset="100%" stopColor="#ca8a04" />
                    </radialGradient>
                </defs>

                {/* Eyes - Dynamic Tracking */}
                <g transform={`translate(${tx}, ${ty})`}>
                    <circle
                        cx="35" cy="40" r={isWaving ? "8" : "6"}
                        fill={isWaving ? "#22d3ee" : "black"}
                        className={cn("transition-all duration-300", isWaving && "animate-pulse")}
                    />
                    <circle
                        cx="65" cy="40" r={isWaving ? "8" : "6"}
                        fill={isWaving ? "#22d3ee" : "black"}
                        className={cn("transition-all duration-300", isWaving && "animate-pulse")}
                    />
                    {/* Highlights */}
                    <circle cx="33" cy="38" r="2" fill="white" opacity="0.6" />
                    <circle cx="63" cy="38" r="2" fill="white" opacity="0.6" />
                </g>

                {/* Mouth - Emotional States & Talking */}
                <path
                    d={getMouthPath(expression, mouthOpen)}
                    fill={mouthOpen ? "#3a1e1e" : "none"}
                    stroke="black"
                    strokeWidth="3"
                    strokeLinecap="round"
                    className="transition-all duration-100 ease-in-out"
                />

                {/* Eyebrows for extra expression */}
                {expression === 'ANGRY' && (
                    <g stroke="black" strokeWidth="2" strokeLinecap="round">
                        <line x1="28" y1="30" x2="42" y2="35" />
                        <line x1="72" y1="30" x2="58" y2="35" />
                    </g>
                )}
                {expression === 'THINKING' && (
                    <line x1="30" y1="28" x2="40" y2="28" stroke="black" strokeWidth="2" transform="rotate(-10 35 28)" />
                )}
            </svg>

            {/* Pose Diagnostic Overlay - Same as Wireframe */}
            {poses && poses.length > 0 && (
                <div className="absolute top-2 right-2 flex flex-col gap-1 items-end pointer-events-none">
                    {poses.map(pose => (
                        <div key={pose} className="bg-accent-success/20 text-accent-success text-[7px] px-1.5 py-0.5 rounded border border-accent-success/30 uppercase font-black tracking-widest animate-in slide-in-from-right-2 duration-300">
                            {pose.replace("_", " ")}
                        </div>
                    ))}
                </div>
            )}

            {/* Status Indicator */}
            <div className="absolute bottom-4 text-[9px] text-yellow-600/60 font-mono uppercase tracking-widest border border-yellow-800/20 px-2 py-0.5 rounded bg-black/40">
                Mode: {expression}
            </div>
        </div>
    );
});

const AvatarPanel = memo(({ active, onToggle, telemetry, selectedAvatar, onAvatarChange, expression, talking, skeleton }) => {
    const [isMinimized, setIsMinimized] = useState(false);

    return (
        <div className="flex flex-col gap-3 bg-ic-surface/80 p-3 rounded-lg border border-accent-indigo/40 shadow-lg shadow-accent-indigo/10 shrink-0 transition-all duration-300">
            {/* Header with Toggle & Selection */}
            <div className="flex flex-col gap-2 bg-black/40 p-1.5 rounded border border-accent-indigo/30">
                <div className="flex justify-between items-center">
                    <h3 className="text-[10px] text-accent-indigo uppercase tracking-widest flex items-center gap-2 font-bold cursor-pointer" onClick={() => setIsMinimized(!isMinimized)}>
                        <BrainCircuit className="w-3 h-3" /> Sensory Avatar
                        {isMinimized ? <ChevronDown className="w-3 h-3 opacity-50" /> : <ChevronUp className="w-3 h-3 opacity-50" />}
                    </h3>
                    <button
                        onClick={onToggle}
                        className={cn(
                            "px-2 py-0.5 rounded text-[9px] font-bold transition-all uppercase border",
                            active ? "bg-accent-indigo/20 text-accent-indigo border-accent-indigo/50 hover:bg-accent-indigo/30" :
                                "bg-ic-card text-txt-secondary border-ic-border hover:bg-ic-hover hover:text-txt-primary"
                        )}
                    >
                        {active ? "ON" : "OFF"}
                    </button>
                </div>

                {!isMinimized && (
                    <div className="flex items-center gap-2 mt-1 border-t border-accent-indigo/20 pt-1.5 animate-in slide-in-from-top-2 duration-300">
                        <label className="text-[8px] text-accent-indigo font-bold uppercase shrink-0">Selection:</label>
                        <select
                            value={selectedAvatar}
                            onChange={(e) => onAvatarChange(e.target.value)}
                            className="bg-black/60 border border-accent-indigo/30 text-[9px] text-accent-indigo rounded px-1 py-0.5 flex-1 outline-none focus:border-accent-indigo"
                        >
                            <option value="wireframe">Facial Wiremapping (Live)</option>
                            <option value="happyface">Happyface (Emoji)</option>
                        </select>
                    </div>
                )}
            </div>

            {/* Main Content (Minimized Hide) */}
            {!isMinimized && (
                <div className="flex flex-col gap-3 animate-in fade-in duration-300">
                    <div className="relative h-48 bg-black/60 rounded border border-accent-indigo/30 flex items-center justify-center overflow-hidden">
                        {!active ? (
                            <div className="flex flex-col items-center gap-2 opacity-40">
                                <ShieldCheck className="w-8 h-8 text-txt-muted" />
                                <span className="text-[9px] text-txt-muted uppercase tracking-widest font-bold">Avatar Standby</span>
                            </div>
                        ) : selectedAvatar === 'happyface' ? (
                            <HappyFace expression={expression} telemetry={telemetry} talking={talking} />
                        ) : (
                            <div className="w-full h-full flex items-center justify-center relative bg-black/40">
                                {/* Neural Skeleton Replicant */}
                                <NeuralSkeleton skeleton={skeleton} />

                                {/* NEW: Facial Wiremesh Overlay */}
                                {telemetry?.vision?.detections && Object.values(telemetry?.vision?.detections || {}).flat().map((face, i) => (
                                    <NeuralFaceMesh key={`face-${i}`} landmarks={face.landmarks} />
                                ))}

                                {/* Engagement Scope Overlay (Preserved) */}
                                <div className="absolute bottom-2 left-2 flex flex-col gap-1 z-10">
                                    <span className="text-[8px] text-accent-indigo/60 uppercase font-bold tracking-tighter">Engagement Scope</span>
                                    <div className="flex items-center gap-1">
                                        <div className="w-20 h-1 bg-ic-card rounded-full overflow-hidden">
                                            <div className="h-full bg-accent-indigo" style={{ width: `${(telemetry?.hcep?.interest_score ?? 0) * 100}%` }} />
                                        </div>
                                        <span className="text-[8px] text-accent-indigo font-mono">{(telemetry?.hcep?.interest_score ?? 0).toFixed(2)}</span>
                                    </div>
                                </div>
                                <div className="absolute top-2 right-2 text-[8px] text-accent-cyan/40 font-mono uppercase z-10 flex flex-col items-end">
                                    <div>State: {telemetry?.hcep?.gaze_target_type ?? "IDLE"}</div>
                                    <div className="text-[7px] text-cyan-600/40">Gaze: {telemetry?.hcep?.user_gaze ?? "UNKNOWN"}</div>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="text-[8px] text-txt-muted uppercase tracking-tighter text-center italic mt-1">
                        {active ? `Integrated Visualization: ${selectedAvatar === 'wireframe' ? 'Neural Skeleton' : 'Happyface'}` : "Enable Avatar to visualize system states"}
                    </div>
                </div>
            )}
        </div>
    );
});


const TrackingTelemetry = memo(({ data, trackingEnabled, zoomEnabled, onToggle, onRefresh }) => {
    if (!data || data.status === "OFFLINE") return null;

    // Color standards for tracking states
    const qualityColors = {
        EXCELLENT: "text-accent-success bg-accent-success/10 border-green-500/30",
        GOOD: "text-accent-cyan bg-accent-cyan/10 border-accent-cyan/30",
        FAIR: "text-accent-warning bg-accent-warning/10 border-accent-warning/30",
        LOW: "text-accent-danger bg-accent-danger/10 border-red-500/30"
    };

    const statusColors = {
        SPATIAL_LOCK: "text-accent-info bg-accent-info/20 border-blue-500/40",
        VISUAL_ONLY: "text-accent-success bg-accent-success/20 border-accent-success/40",
        AUDIO_ONLY: "text-accent-warning bg-accent-warning/20 border-accent-warning/40",
        AMBIGUOUS_SENSORY: "text-accent-warning bg-accent-warning/20 border-accent-warning/40",
        SEARCHING: "text-txt-secondary bg-txt-muted/20 border-txt-muted/40"
    };

    const confidence = data.confidence ?? 0;
    const quality = data.quality ?? "LOW";
    const statusMsg = data.status_msg ?? "SEARCHING";
    const [isMinimized, setIsMinimized] = useState(false);
    const [isRefreshing, setIsRefreshing] = useState(false);

    const handleRefresh = async (e) => {
        e.stopPropagation();
        setIsRefreshing(true);
        try {
            await onRefresh?.();
        } finally {
            setTimeout(() => setIsRefreshing(false), 1000);
        }
    };

    return (
        <div className="flex flex-col gap-3 bg-ic-surface/80 p-3 rounded-lg border border-accent-cyan/40 shadow-lg shrink-0 transition-all duration-300">
            {/* Header with Status Badge and Controls */}
            <div className="flex justify-between items-center cursor-pointer" onClick={() => setIsMinimized(!isMinimized)}>
                <div className="flex items-center gap-2">
                    <div className={cn("w-2 h-2 rounded-full", confidence > 50 ? "bg-accent-success animate-pulse" : "bg-txt-muted")} />
                    <h3 className="text-[10px] text-accent-cyan uppercase tracking-widest font-bold flex items-center gap-2">
                        Tracking
                        {isMinimized ? <ChevronDown className="w-3 h-3 opacity-50" /> : <ChevronUp className="w-3 h-3 opacity-50" />}
                    </h3>
                </div>
                {!isMinimized && (
                    <div
                        onClick={handleRefresh}
                        className={cn(
                            "px-2 py-0.5 rounded-full text-[9px] font-bold uppercase border cursor-pointer hover:brightness-125 transition-all flex items-center gap-1",
                            statusColors[statusMsg] || statusColors.SEARCHING,
                            isRefreshing && "animate-pulse"
                        )}
                    >
                        {isRefreshing ? <RefreshCw className="w-2.5 h-2.5 animate-spin" /> : null}
                        {statusMsg.replace("_", " ")}
                    </div>
                )}
            </div>

            {/* Content */}
            {!isMinimized && (
                <div className="flex flex-col gap-3 animate-in slide-in-from-top-2 duration-300">

                    {/* Track and Zoom Controls (Moved to top) */}
                    <div className="flex items-center justify-between bg-black/40 rounded-md px-2 py-1.5 border border-accent-cyan/30 shadow-[0_0_10px_rgba(6,182,212,0.1)]">
                        <span className="text-[8px] text-accent-cyan/70 uppercase font-bold">Active Tracking</span>
                        <div className="flex items-center gap-3">
                            <label className="flex items-center gap-1.5 cursor-pointer group">
                                <input
                                    type="checkbox"
                                    checked={trackingEnabled}
                                    onChange={() => onToggle?.('tracking')}
                                    className="w-3 h-3 rounded border-accent-cyan bg-black text-cyan-600 focus:ring-0 focus:ring-offset-0"
                                />
                                <span className="text-[9px] text-accent-cyan font-bold group-hover:text-accent-cyan transition-colors uppercase tracking-tighter">Motor</span>
                            </label>
                            <label className="flex items-center gap-1.5 cursor-pointer group">
                                <input
                                    type="checkbox"
                                    checked={zoomEnabled}
                                    onChange={() => onToggle?.('zoom')}
                                    className="w-3 h-3 rounded border-accent-cyan bg-black text-cyan-600 focus:ring-0 focus:ring-offset-0"
                                />
                                <span className="text-[9px] text-accent-cyan font-bold group-hover:text-accent-cyan transition-colors uppercase tracking-tighter">Zoom</span>
                            </label>
                        </div>
                    </div>


                    {/* Confidence Meter */}
                    <div className="space-y-1">
                        <div className="flex justify-between items-center">
                            <span className="text-[9px] text-txt-secondary uppercase">Confidence</span>
                            <span className={cn("text-[11px] font-mono font-bold", qualityColors[quality]?.split(" ")[0])}>
                                {confidence}%
                            </span>
                        </div>
                        <div className="h-2 bg-ic-card rounded-full overflow-hidden border border-ic-border">
                            <div
                                className={cn(
                                    "h-full transition-all duration-500 rounded-full",
                                    confidence >= 80 ? "bg-gradient-to-r from-green-600 to-green-400" :
                                        confidence >= 60 ? "bg-gradient-to-r from-accent-cyan to-cyan-400" :
                                            confidence >= 40 ? "bg-gradient-to-r from-yellow-600 to-yellow-400" :
                                                "bg-gradient-to-r from-red-600 to-red-400"
                                )}
                                style={{ width: `${confidence}%` }}
                            />
                        </div>
                        <div className="flex gap-1 flex-wrap">
                            {(data.confidence_sources || []).map((src, i) => (
                                <span key={i} className={cn(
                                    "text-[8px] px-1.5 py-0.5 rounded-full font-semibold",
                                    src.startsWith("CAM") ? "bg-accent-success/20 text-accent-success border border-accent-success/30" :
                                        "bg-accent-warning/20 text-accent-warning border border-accent-warning/30"
                                )}>
                                    {src}
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* Metrics Grid */}
                    <div className="grid grid-cols-4 gap-1.5">
                        <div className="bg-black/40 p-1.5 rounded border border-accent-cyan/20 text-center">
                            <div className="text-[8px] text-txt-muted uppercase">Cameras</div>
                            <div className="text-sm text-accent-success font-mono font-bold">{data.camera_count ?? 0}</div>
                        </div>
                        <div className="bg-black/40 p-1.5 rounded border border-accent-cyan/20 text-center">
                            <div className="text-[8px] text-txt-muted uppercase">Faces</div>
                            <div className="text-sm text-accent-cyan font-mono font-bold">{data.total_faces ?? 0}</div>
                        </div>
                        <div className="bg-black/40 p-1.5 rounded border border-accent-cyan/20 text-center">
                            <div className="text-[8px] text-txt-muted uppercase italic">K-IR Stream</div>
                            <div className={cn("text-[10px] font-mono font-bold", data.ir_active ? "text-accent-warning" : "text-txt-muted")}>
                                {data.ir_active ? "LIVE" : "OFF"}
                            </div>
                        </div>
                        <div className="bg-black/40 p-1.5 rounded border border-accent-cyan/20 text-center relative overflow-hidden">
                            <div className="text-[8px] text-txt-muted uppercase italic">K-Depth</div>
                            <div className={cn("text-[10px] font-mono font-bold", data.depth_active ? "text-accent-indigo" : "text-txt-muted")}>
                                {data.depth_active ? "READY" : "OFF"}
                            </div>
                            {data.depth_active && <div className="absolute inset-0 bg-accent-indigo/5 animate-pulse pointer-events-none" />}
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-1.5 mt-[-4px]">
                        <div className="bg-black/30 p-1 rounded border border-ic-border flex justify-between items-center px-2">
                            <span className="text-[7px] text-txt-muted uppercase">Audio Array</span>
                            <span className={cn("text-[8px] font-bold", data.audio_array_active ? "text-accent-warning" : "text-txt-muted")}>
                                {data.audio_array_active ? "ACTIVE" : "INACTIVE"}
                            </span>
                        </div>
                        <div className="bg-black/30 p-1 rounded border border-ic-border flex justify-between items-center px-2">
                            <span className="text-[7px] text-txt-muted uppercase">Spatial Lock</span>
                            <span className={cn("text-[8px] font-bold", data.target_lock ? "text-accent-info" : "text-txt-muted")}>
                                {data.target_lock ? "SECURED" : "SEARCHING"}
                            </span>
                        </div>
                    </div>

                    {/* Position Data */}
                    <div className="grid grid-cols-3 gap-1.5">
                        <div className="bg-black/30 p-1.5 rounded border border-ic-border">
                            <div className="text-[7px] text-txt-muted uppercase">X-Pos</div>
                            <div className="text-[10px] text-cyan-100 font-mono">{(data.pos?.[0] ?? 0).toFixed(3)}</div>
                        </div>
                        <div className="bg-black/30 p-1.5 rounded border border-ic-border">
                            <div className="text-[7px] text-txt-muted uppercase">Y-Pos</div>
                            <div className="text-[10px] text-cyan-100 font-mono">{(data.pos?.[1] ?? 0).toFixed(3)}</div>
                        </div>
                        <div className="bg-black/30 p-1.5 rounded border border-ic-border">
                            <div className="text-[7px] text-txt-muted uppercase">Z-Depth</div>
                            <div className="text-[10px] text-accent-cyan font-mono font-bold">{(data.pos?.[2] ?? 0).toFixed(2)}</div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
});


// PTZ (Pan/Tilt/Zoom) Control Panel for motorized cameras
const PTZControlPanel = memo(({ devices = [], onMove }) => {
    const [loading, setLoading] = useState(false);
    const [isMinimized, setIsMinimized] = useState(true); // Default minimized for PTZ
    const [position, setPosition] = useState({ pan: 0, tilt: 0 });
    const [connected, setConnected] = useState(false);
    const [error, setError] = useState(null);
    const [targetId, setTargetId] = useState("");

    // Extract list of truly controllable motorized cameras
    const controllableCams = (devices || []).filter(d =>
        d.vid_pid && (d.ptz?.motor_control || d.ptz?.pan || d.ptz?.tilt)
    );

    // Auto-select first available if none selected
    useEffect(() => {
        if (!targetId && controllableCams.length > 0) {
            setTargetId(controllableCams[0].vid_pid);
        }
    }, [controllableCams, targetId]);

    const movePTZ = async (pan, tilt) => {
        if (!targetId) return;
        setLoading(true);
        setError(null);
        try {
            const res = await axios.post(`${API_BASE}/v1/devices/${targetId}/ptz`, { pan, tilt });
            if (res.data.status === "OK") {
                setPosition({ pan: res.data.position?.[0] ?? 0, tilt: res.data.position?.[1] ?? 0 });
                setConnected(true);
                onMove?.(res.data);
            }
        } catch (e) {
            setError(e.response?.data?.detail || "PTZ control failed");
            setConnected(false);
        } finally {
            setLoading(false);
        }
    };

    const resetPosition = async () => {
        if (!targetId) return;
        setLoading(true);
        setError(null);
        try {
            const res = await axios.post(`${API_BASE}/v1/devices/${targetId}/ptz`, { reset: true });
            if (res.data.status === "OK") {
                setPosition({ pan: 0, tilt: 0 });
                setConnected(true);
            }
        } catch (e) {
            setError(e.response?.data?.detail || "Reset failed");
        } finally {
            setLoading(false);
        }
    };

    // Movement amounts
    const SMALL_MOVE = 200;
    const LARGE_MOVE = 800;

    if (controllableCams.length === 0) {
        return (
            <div className="flex flex-col gap-2 bg-ic-surface/60 p-3 rounded-lg border border-ic-border text-center opacity-50 select-none">
                <h3 className="text-[10px] text-txt-secondary uppercase tracking-widest font-bold">Motor Control</h3>
                <div className="text-[9px] text-txt-muted italic py-4">No motorized devices detected.</div>
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-2 bg-ic-surface/80 p-3 rounded-lg border border-accent-indigo/40 shadow-lg shrink-0">
            {/* Header & Selector */}
            <div className="flex justify-between items-center mb-1">
                <div className="flex items-center gap-2 cursor-pointer" onClick={() => setIsMinimized(!isMinimized)}>
                    <div className={cn("w-2 h-2 rounded-full", connected ? "bg-accent-indigo animate-pulse" : "bg-txt-muted")} />
                    <h3 className="text-[10px] text-accent-indigo uppercase tracking-widest font-bold flex items-center gap-2">
                        Motor Control
                        {isMinimized ? <ChevronDown className="w-3 h-3 opacity-50" /> : <ChevronUp className="w-3 h-3 opacity-50" />}
                    </h3>
                </div>
                {!isMinimized && (
                    <select
                        value={targetId}
                        onChange={e => setTargetId(e.target.value)}
                        className="bg-black/80 text-[9px] text-accent-indigo border border-accent-indigo/50 rounded px-1.5 py-0.5 outline-none focus:border-accent-indigo max-w-[120px]"
                    >
                        {controllableCams.map(c => (
                            <option key={c.deviceId} value={c.vid_pid}>
                                {c.label.replace("[Neural] ", "").split(" [")[0]}
                            </option>
                        ))}
                    </select>
                )}
            </div>

            {!isMinimized && (
                <div className="flex flex-col gap-2 animate-in slide-in-from-top-2 duration-300">

                    {/* Error Display */}
                    {error && (
                        <div className="text-[9px] text-accent-danger bg-accent-danger/10 border border-red-500/30 rounded px-2 py-1">
                            {error}
                        </div>
                    )}

                    {/* D-Pad Style Controls */}
                    <div className="flex flex-col items-center gap-1">
                        {/* Up */}
                        <button
                            onClick={() => movePTZ(0, LARGE_MOVE)}
                            disabled={loading}
                            className="w-10 h-8 bg-accent-indigo/30 hover:bg-accent-indigo/50 border border-accent-indigo/40 rounded text-accent-indigo text-xs font-bold transition-all disabled:opacity-50"
                        >

                        </button>

                        {/* Middle Row: Left, Reset, Right */}
                        <div className="flex items-center gap-1">
                            <button
                                onClick={() => movePTZ(-LARGE_MOVE, 0)}
                                disabled={loading}
                                className="w-10 h-8 bg-accent-indigo/30 hover:bg-accent-indigo/50 border border-accent-indigo/40 rounded text-accent-indigo text-xs font-bold transition-all disabled:opacity-50"
                            >

                            </button>
                            <button
                                onClick={resetPosition}
                                disabled={loading}
                                className="w-10 h-8 bg-accent-cyan/30 hover:bg-cyan-800/50 border border-cyan-700/40 rounded text-accent-cyan text-[8px] font-bold transition-all disabled:opacity-50"
                            >

                            </button>
                            <button
                                onClick={() => movePTZ(LARGE_MOVE, 0)}
                                disabled={loading}
                                className="w-10 h-8 bg-accent-indigo/30 hover:bg-accent-indigo/50 border border-accent-indigo/40 rounded text-accent-indigo text-xs font-bold transition-all disabled:opacity-50"
                            >

                            </button>
                        </div>

                        {/* Down */}
                        <button
                            onClick={() => movePTZ(0, -LARGE_MOVE)}
                            disabled={loading}
                            className="w-10 h-8 bg-accent-indigo/30 hover:bg-accent-indigo/50 border border-accent-indigo/40 rounded text-accent-indigo text-xs font-bold transition-all disabled:opacity-50"
                        >

                        </button>
                    </div>

                    {/* Position Display */}
                    <div className="grid grid-cols-2 gap-1.5">
                        <div className="bg-black/30 p-1.5 rounded border border-ic-border text-center">
                            <div className="text-[7px] text-txt-muted uppercase">Pan</div>
                            <div className="text-[10px] text-accent-indigo font-mono">{position.pan.toFixed(0)}</div>
                        </div>
                        <div className="bg-black/30 p-1.5 rounded border border-ic-border text-center">
                            <div className="text-[7px] text-txt-muted uppercase">Tilt</div>
                            <div className="text-[10px] text-accent-indigo font-mono">{position.tilt.toFixed(1)}</div>
                        </div>
                    </div>

                    {/* Fine Control Buttons */}
                    <div className="flex justify-center gap-1">
                        <button
                            onClick={() => movePTZ(-SMALL_MOVE, 0)}
                            disabled={loading}
                            className="px-2 py-1 bg-ic-card/50 hover:bg-ic-hover/50 border border-ic-border/40 rounded text-txt-secondary text-[8px] font-bold transition-all disabled:opacity-50"
                        >
                            Fine
                        </button>
                        <button
                            onClick={() => movePTZ(SMALL_MOVE, 0)}
                            disabled={loading}
                            className="px-2 py-1 bg-ic-card/50 hover:bg-ic-hover/50 border border-ic-border/40 rounded text-txt-secondary text-[8px] font-bold transition-all disabled:opacity-50"
                        >
                            Fine
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
});


const VideoOverlay = memo(({ detections = {}, camLabel, color = "cyan", metadata = {} }) => {
    if (!detections || typeof detections !== 'object') return null;

    // Filter detections for this specific camera
    let faces = [];
    if (Array.isArray(camLabel)) {
        camLabel.forEach(label => {
            const lStr = String(label);
            if (detections[label]) faces = [...faces, ...detections[label]];
            else if (detections[lStr]) faces = [...faces, ...detections[lStr]];
        });
    } else if (camLabel) {
        const lStr = String(camLabel);
        faces = detections[camLabel] || detections[lStr] || [];
    } else {
        faces = Object.values(detections).flat();
    }

    if (!faces || faces.length === 0) {
        return null;
    }

    // [FIX] Filter out invalid/zero-sized detections to prevent "blue corner" artifacts
    // A detection with [0,0,0,0] will render at 0,0 with corner accents, looking like a glitch.
    const validFaces = faces.filter(det => {
        const [x, y, w, h] = det.bbox || [0, 0, 0, 0];
        return w > 5 && h > 5; // Minimal reliable size (5px)
    });

    if (validFaces.length === 0) return null;

    const { confidence = 0, targetLock = false, quality = "LOW" } = metadata;

    // Standardized mapping
    const BW = 640;
    const BH = 480;

    const getEmotionColor = (emo) => {
        const colors = {
            'HAPPY': 'text-accent-warning',
            'SAD': 'text-accent-info',
            'ANGRY': 'text-accent-danger',
            'SURPRISE': 'text-accent-indigo',
            'FEAR': 'text-accent-indigo',
            'DISGUST': 'text-accent-success',
            'NEUTRAL': 'text-txt-secondary'
        };
        return colors[emo] || 'text-txt-secondary';
    };

    return (
        <div className="absolute inset-0 pointer-events-none overflow-hidden z-30">
            {validFaces.map((det, j) => {
                const [x, y, w, h] = det.bbox || [0, 0, 0, 0];

                const left = (x / BW) * 100;
                const top = (y / BH) * 100;
                const width = (w / BW) * 100;
                const height = (h / BH) * 100;

                const isLive = det.liveness?.is_live;
                const emotion = det.emotion?.emotion;
                const name = det.label || "UNKNOWN";
                const isPrimary = name.startsWith("Primary:");
                const effectiveLock = targetLock || isPrimary;

                return (
                    <div
                        key={`${camLabel}-${j}`}
                        className="absolute flex flex-col transition-all duration-100"
                        style={{
                            left: `${left}%`,
                            top: `${top}%`,
                            width: `${width}%`,
                            height: `${height}%`,
                        }}
                    >
                        {/* Bounding Box Rect */}
                        <div className={cn(
                            "absolute inset-0 border-2 shadow-[0_0_15px_rgba(0,0,0,0.5)]",
                            !isLive && det.liveness ? "border-red-600 shadow-red-900/40 animate-pulse" :
                                effectiveLock ? "border-blue-500 shadow-blue-500/20" :
                                    color === "fuchsia" ? "border-accent-indigo shadow-accent-indigo/20" :
                                        "border-accent-success shadow-emerald-500/20"
                        )}>
                            {/* Corner Accents */}
                            <div className="absolute -top-1 -left-1 w-2 h-2 border-t-2 border-l-2 border-white" />
                            <div className="absolute -top-1 -right-1 w-2 h-2 border-t-2 border-r-2 border-white" />
                            <div className="absolute -bottom-1 -left-1 w-2 h-2 border-b-2 border-l-2 border-white" />
                            <div className="absolute -bottom-1 -right-1 w-2 h-2 border-b-2 border-r-2 border-white" />
                        </div>

                        {/* Metadata Tag */}
                        <div className={cn(
                            "absolute -top-6 left-0 flex flex-col gap-0",
                            "whitespace-nowrap z-20"
                        )}>
                            <div className={cn(
                                "flex items-center gap-1.5 px-2 py-0.5 rounded-t text-[9px] font-bold uppercase tracking-tighter",
                                !isLive && det.liveness ? "bg-accent-danger text-white" :
                                    effectiveLock ? "bg-blue-600 text-white" :
                                        color === "fuchsia" ? "bg-accent-indigo text-white" :
                                            "bg-accent-success text-white"
                            )}>
                                {effectiveLock && <Target className="w-2.5 h-2.5 animate-pulse" />}
                                <span>{name}</span>
                                <span className="opacity-70 ml-1">[{det.score ? (det.score * 100).toFixed(0) : confidence}%]</span>
                            </div>

                            {/* Secondary Data Bar (Emotions/Liveness) */}
                            <div className="flex gap-0.5 bg-black/80 backdrop-blur-md border-x border-b border-white/10 rounded-b px-1.5 py-0.5 min-w-full">
                                {emotion && (
                                    <div className={cn("text-[8px] font-bold flex items-center gap-1", getEmotionColor(emotion))}>
                                        <Activity className="w-2 h-2" /> {emotion}
                                    </div>
                                )}
                                <div className="ml-auto flex items-center gap-1">
                                    <span className={cn(
                                        "w-1.5 h-1.5 rounded-full",
                                        isLive ? "bg-accent-success" : "bg-accent-danger shadow-[0_0_5px_red]"
                                    )} title={isLive ? "Liveness Verified" : "SPOOF DETECTED"} />
                                    <span className="text-[7px] text-white/50">{isLive ? "LIVE" : "SPOOF"}</span>
                                </div>
                            </div>
                        </div>

                        {/* Detailed Stats (Bottom) */}
                        <div className="absolute -bottom-5 left-0 flex gap-1 items-center opacity-0 group-hover:opacity-100 transition-opacity">
                            <div className="bg-black/60 backdrop-blur px-1.5 py-0.5 rounded text-[7px] text-white/80 border border-white/10 uppercase">
                                CONF: {det.score ? (det.score * 100).toFixed(0) : '---'}%
                            </div>
                            <div className="bg-black/60 backdrop-blur px-1.5 py-0.5 rounded text-[7px] text-white/80 border border-white/10 uppercase font-mono">
                                TRK_ID: {det.id || `0x${j}A`}
                            </div>
                        </div>

                        {/* Landmarks Visualization */}
                        {det.landmarks && Object.entries(det.landmarks).map(([feature, points]) => (
                            <React.Fragment key={feature}>
                                {points.map((pt, i) => (
                                    <div
                                        key={`${feature}-${i}`}
                                        className="absolute w-1 h-1 bg-emerald-400 rounded-full shadow-[0_0_5px_rgba(52,211,153,0.8)]"
                                        style={{
                                            left: `${((pt[0] - x) / w) * 100}%`,
                                            top: `${((pt[1] - y) / h) * 100}%`,
                                        }}
                                    />
                                ))}
                            </React.Fragment>
                        ))}

                        {/* Head Pose Indicator & Stats */}
                        {det.head_pose && (
                            <>
                                {/* Visual Directional Indicator */}
                                <div className="absolute -right-14 top-0 flex flex-col gap-1 pointer-events-none">
                                    <div className="bg-black/80 backdrop-blur border border-accent-success/30 rounded p-1 flex flex-col gap-0.5 min-w-[50px]">
                                        <div className="flex justify-between text-[7px]">
                                            <span className="text-txt-secondary">P:</span>
                                            <span className={cn("font-bold", Math.abs(det.head_pose.pitch) > 20 ? "text-accent-warning" : "text-accent-success")}>{det.head_pose.pitch.toFixed(1)}</span>
                                        </div>
                                        <div className="flex justify-between text-[7px]">
                                            <span className="text-txt-secondary">Y:</span>
                                            <span className={cn("font-bold", Math.abs(det.head_pose.yaw) > 25 ? "text-accent-warning" : "text-accent-success")}>{det.head_pose.yaw.toFixed(1)}</span>
                                        </div>
                                        <div className="flex justify-between text-[7px]">
                                            <span className="text-txt-secondary">R:</span>
                                            <span className={cn("font-bold", Math.abs(det.head_pose.roll) > 15 ? "text-accent-warning" : "text-accent-success")}>{det.head_pose.roll.toFixed(1)}</span>
                                        </div>
                                    </div>

                                    {/* Orientation Compass */}
                                    <div className="w-8 h-8 self-center relative border border-white/10 rounded bg-black/40">
                                        <div
                                            className="absolute inset-0 flex items-center justify-center transition-transform duration-200"
                                            style={{
                                                transform: `rotate(${det.head_pose.roll}deg)`,
                                                perspective: '100px'
                                            }}
                                        >
                                            <div
                                                className="w-0.5 h-4 bg-accent-success shadow-[0_0_8px_cyan]"
                                                style={{
                                                    transform: `rotateY(${det.head_pose.yaw}deg) rotateX(${det.head_pose.pitch}deg)`
                                                }}
                                            />
                                            {/* Center Point */}
                                            <div className="absolute w-1 h-1 bg-white rounded-full shadow-[0_0_5px_white]" />
                                        </div>
                                    </div>
                                </div>
                            </>
                        )}
                    </div>
                );
            })
            }

            {/* Global Feed Status */}
            <div className="absolute top-2 right-2 flex flex-col items-end gap-1" >
                <div className={cn(
                    "px-2 py-0.5 rounded text-[8px] font-bold uppercase tracking-widest border backdrop-blur-md",
                    targetLock ? "bg-accent-info/20 text-accent-info border-blue-500/50" : "bg-black/40 text-txt-secondary border-white/10"
                )}>
                    {targetLock ? "Active Tracking" : "Scanning..."}
                </div>
            </div>
        </div>
    );
});


// =============================================================================
// SKELETON WEBSOCKET HOOK (Amethyst-Style Real-Time Tracking)
// =============================================================================

/**
 * Custom hook for real-time skeleton data via WebSocket
 * Connects to ws://localhost:8000/ws/skeleton for 30fps updates
 */
const useSkeletonWebSocket = (enabled = true) => {
    const [skeleton, setSkeleton] = useState(null);
    const [connected, setConnected] = useState(false);
    const wsRef = useRef(null);
    const reconnectTimeout = useRef(null);

    useEffect(() => {
        if (!enabled) {
            if (wsRef.current) {
                wsRef.current.close();
                wsRef.current = null;
            }
            setConnected(false);
            setSkeleton(null);
            return;
        }

        const connect = () => {
            try {
                const ws = new WebSocket(`${API_WS_BASE}/ws/skeleton`);

                ws.onopen = () => {
                    console.log('[Skeleton WS] Connected');
                    setConnected(true);
                };

                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        if (data.skeleton) {
                            setSkeleton(data.skeleton);
                        }
                    } catch (e) {
                        console.warn('[Skeleton WS] Parse error:', e);
                    }
                };

                ws.onclose = () => {
                    console.log('[Skeleton WS] Disconnected');
                    setConnected(false);
                    wsRef.current = null;
                    // Reconnect after 2 seconds
                    reconnectTimeout.current = setTimeout(connect, 2000);
                };

                ws.onerror = (e) => {
                    console.warn('[Skeleton WS] Error:', e);
                    ws.close();
                };

                wsRef.current = ws;
            } catch (e) {
                console.error('[Skeleton WS] Connection failed:', e);
                reconnectTimeout.current = setTimeout(connect, 2000);
            }
        };

        connect();

        return () => {
            if (reconnectTimeout.current) {
                clearTimeout(reconnectTimeout.current);
            }
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [enabled]);

    return { skeleton, connected };
};

// =============================================================================
// SKELETON VISUALIZER COMPONENT (Amethyst-Style)
// =============================================================================

const SkeletonVisualizer = memo(({ skeleton, mode = 'overlay', showBadge = true }) => {
    if (!skeleton || !skeleton.tracked || !skeleton.joints) return null;

    // Amethyst-style Bone Connections
    const BONES = [
        ['HEAD', 'SHOULDER_CENTER'],
        ['SHOULDER_CENTER', 'SPINE'],
        ['SPINE', 'HIP_CENTER'],
        ['SHOULDER_CENTER', 'SHOULDER_LEFT'],
        ['SHOULDER_LEFT', 'ELBOW_LEFT'],
        ['ELBOW_LEFT', 'WRIST_LEFT'],
        ['WRIST_LEFT', 'HAND_LEFT'],
        ['SHOULDER_CENTER', 'SHOULDER_RIGHT'],
        ['SHOULDER_RIGHT', 'ELBOW_RIGHT'],
        ['ELBOW_RIGHT', 'WRIST_RIGHT'],
        ['WRIST_RIGHT', 'HAND_RIGHT'],
        ['HIP_CENTER', 'HIP_LEFT'],
        ['HIP_LEFT', 'KNEE_LEFT'],
        ['KNEE_LEFT', 'ANKLE_LEFT'],
        ['ANKLE_LEFT', 'FOOT_LEFT'],
        ['HIP_CENTER', 'HIP_RIGHT'],
        ['HIP_RIGHT', 'KNEE_RIGHT'],
        ['KNEE_RIGHT', 'ANKLE_RIGHT'],
        ['ANKLE_RIGHT', 'FOOT_RIGHT']
    ];

    // [MODIFICATION] Seated Mode Leg Inference
    // If hips are tracked but legs are not, we infer a seated pose.
    const inferSeatedLegs = (joints) => {
        const newJoints = { ...joints };
        const hipC = joints['HIP_CENTER'];

        if (!hipC || hipC.state !== 2) return newJoints;

        // Helper to synthesize a joint
        const synth = (parent, offset, name) => {
            const existing = newJoints[name];
            // Only overwrite if not confidently tracked (state != 2)
            if (!existing || existing.state !== 2) {
                newJoints[name] = {
                    x: parent.x + offset[0],
                    y: parent.y + offset[1],
                    z: parent.z + offset[2],
                    state: 1 // Inferred
                };
            }
        };

        const SEAT_HEIGHT_OFFSET = -0.4; // Down from hip
        const THIGH_LENGTH = 0.35; // Forward from hip
        const SHIN_LENGTH = 0.40;  // Down from knee

        // Synthesize Left Leg (Seated: Hip -> Forward -> Down)
        // Note: Kinect Coords: Y=Up, Z=Forward (approx)

        // Left Hip (Usually tracked, but if missing infer from Center)
        if (!newJoints['HIP_LEFT'] || newJoints['HIP_LEFT'].state !== 2) {
            newJoints['HIP_LEFT'] = { ...hipC, x: hipC.x - 0.15, state: 1 };
        }

        // Left Knee (Forward +Z)
        synth(newJoints['HIP_LEFT'], [0, 0.05, -THIGH_LENGTH], 'KNEE_LEFT'); // Z is negative towards camera? No, +Z is away. Kinect depth is usually +Z away.
        // Actually Kinect Space: Z is distance from sensor. So sitting means knees are closer to sensor (-Z) or implies legs forward?
        // Let's assume user is facing camera. Legs stick out towards camera -> Z decreases.

        // Left Ankle (Down -Y)
        synth(newJoints['KNEE_LEFT'], [0, -SHIN_LENGTH, 0], 'ANKLE_LEFT');

        // Left Foot (Forward -Z)
        synth(newJoints['ANKLE_LEFT'], [0, 0, -0.1], 'FOOT_LEFT');


        // Right Hip
        if (!newJoints['HIP_RIGHT'] || newJoints['HIP_RIGHT'].state !== 2) {
            newJoints['HIP_RIGHT'] = { ...hipC, x: hipC.x + 0.15, state: 1 };
        }

        // Right Knee
        synth(newJoints['HIP_RIGHT'], [0, 0.05, -THIGH_LENGTH], 'KNEE_RIGHT');

        // Right Ankle
        synth(newJoints['KNEE_RIGHT'], [0, -SHIN_LENGTH, 0], 'ANKLE_RIGHT');

        // Right Foot
        synth(newJoints['ANKLE_RIGHT'], [0, 0, -0.1], 'FOOT_RIGHT');

        return newJoints;
    };

    const displayJoints = inferSeatedLegs(skeleton.joints);


    // Kinect Coordinates are typically approx -2.0 to 2.0 meters
    // Map them to 0-100% of the view

    // 3D Perspective Projection (Simple)
    const project = (px, py, pz) => {
        // [MODIFICATION] Vertical Offset to lower the skeleton visually
        // "Lowered about 5-7%" -> Add ~6% to the final Y output
        const Y_OFFSET_PERCENT = 6.0;

        if (mode === 'overlay') {
            // Kinect v1 Pinhole Correction (FOV: ~57h, ~43v)
            // Constants derived from: normalized_focal = 50 / tan(fov/2)
            // x: py is relative to center, focal ~ 92
            // y: py is relative to center, focal ~ 123
            const zSafe = Math.max(0.1, pz);
            return {
                x: 50 + (px / zSafe) * 92.0,
                y: (50 - (py / zSafe) * 123.0) + Y_OFFSET_PERCENT
            };
        }

        // 3D Mode: Add some camera rotation/tilt
        const tilt = 0.2; // Radians
        const rY = py * Math.cos(tilt) - pz * Math.sin(tilt);
        const rZ = py * Math.sin(tilt) + pz * Math.cos(tilt);

        // Standard perspective: x' = x/z, y' = y/z
        const fov = 1.5;
        const s = fov / (rZ + 3.0); // Offset Z so we aren't at origin

        return {
            x: 50 + (px * s * 100),
            y: (50 - (rY * s * 100)) + Y_OFFSET_PERCENT
        };
    };

    const getColor = (state) => {
        if (state === 2) return "#10b981"; // Tracked (Emerald-500)
        if (state === 1) return "#facc15"; // Inferred (Yellow-400)
        return "#ef4444"; // Not Tracked (Red-500)
    };

    return (
        <>
            <svg className="absolute inset-0 w-full h-full pointer-events-none z-20" viewBox="0 0 100 100" preserveAspectRatio="none">
                {/* Bones */}
                {BONES.map(([start, end], i) => {
                    const j1 = displayJoints[start];
                    const j2 = displayJoints[end];
                    if (!j1 || !j2) return null;

                    const p1 = project(j1.x, j1.y, j1.z);
                    const p2 = project(j2.x, j2.y, j2.z);

                    return (
                        <line
                            key={`bone-${i}`}
                            x1={`${p1.x}%`} y1={`${p1.y}%`}
                            x2={`${p2.x}%`} y2={`${p2.y}%`}
                            stroke="rgba(6, 182, 212, 0.6)" // Cyan-500/60
                            strokeWidth={mode === '3D' ? "2" : "1.5"}
                            strokeLinecap="round"
                        />
                    );
                })}

                {/* Joints */}
                {Object.keys(displayJoints).map((jointName) => {
                    const j = displayJoints[jointName];
                    const p = project(j.x, j.y, j.z);
                    return (
                        <circle
                            key={jointName}
                            cx={`${p.x}%`}
                            cy={`${p.y}%`}
                            r={mode === '3D' ? "1.5" : "1.2"}
                            fill={getColor(j.state)}
                            stroke="rgba(0,0,0,0.5)"
                            strokeWidth="0.2"
                        />
                    );
                })}

                {/* Floor Plane (if 3D) */}
                {mode === '3D' && skeleton.floor_clip_plane && (
                    <line
                        x1="0%" y1="90%" x2="100%" y2="90%"
                        stroke="rgba(16, 185, 129, 0.3)"
                        strokeWidth="1"
                        strokeDasharray="2,2"
                    />
                )}
            </svg>

            {/* Tracking Status Badge */}
            {
                showBadge && (
                    <div className="absolute top-2 left-2 z-30 flex items-center gap-1.5 bg-black/70 backdrop-blur-sm px-2 py-1 rounded border border-accent-cyan/40">
                        <div className="w-2 h-2 rounded-full bg-accent-cyan animate-pulse shadow-[0_0_6px_rgba(34,211,238,0.8)]" />
                        <span className="text-[9px] text-accent-cyan font-bold uppercase tracking-wider">
                            Skeleton Tracked
                        </span>
                        <span className="text-[8px] text-cyan-600 font-mono ml-1">
                            ID:{skeleton.id || 0}
                        </span>
                    </div>
                )
            }
        </>
    );
});


const KinectControls = () => {
    const [streams, setStreams] = useState({ color: true, depth: true, ir: true, skeleton: true });
    const [isMinimized, setIsMinimized] = useState(false);

    useEffect(() => {
        const fetchStreams = async () => {
            try {
                const res = await axios.get(`${API_BASE}/v1/vision/kinect/streams`);
                if (res.data) setStreams(res.data);
            } catch (e) { console.error("Failed to fetch kinect streams", e); }
        };
        fetchStreams();
        const interval = setInterval(fetchStreams, 5000);
        return () => clearInterval(interval);
    }, []);

    const toggleStream = async (stream) => {
        const newState = !streams[stream];
        setStreams(prev => ({ ...prev, [stream]: newState }));
        try {
            await axios.post(`${API_BASE}/v1/vision/kinect/streams`, { stream, enabled: newState });
        } catch (e) {
            console.error(`Failed to toggle ${stream}`, e);
            setStreams(prev => ({ ...prev, [stream]: !newState })); // Revert on fail
        }
    };

    return (
        <div className="bg-ic-surface/80 p-3 rounded-lg border border-accent-warning/30 space-y-3 shadow-inner shadow-accent-warning/10">
            <div className="flex justify-between items-center bg-black/40 p-1.5 rounded border border-yellow-900/30 mb-1">
                <h3 className="text-[10px] text-accent-warning uppercase tracking-widest flex items-center gap-2 cursor-pointer" onClick={() => setIsMinimized(!isMinimized)}>
                    <Activity className="w-3 h-3" /> Kinect Streams
                    {isMinimized ? <ChevronDown className="w-3 h-3 opacity-50" /> : <ChevronUp className="w-3 h-3 opacity-50" />}
                </h3>
            </div>
            {!isMinimized && (
                <div className="grid grid-cols-2 gap-2 animate-in slide-in-from-top-2 duration-300">
                    {Object.entries(streams).map(([key, val]) => (
                        <button
                            key={key}
                            onClick={() => toggleStream(key)}
                            className={cn(
                                "flex items-center justify-between px-2 py-1.5 rounded text-[10px] uppercase tracking-wide transition-all border",
                                val
                                    ? "bg-accent-warning/20 border-accent-warning/50 text-yellow-300 hover:bg-accent-warning/30"
                                    : "bg-ic-card/50 border-ic-border text-txt-secondary hover:bg-ic-card"
                            )}
                        >
                            <span>{key}</span>
                            <div className={cn("w-1.5 h-1.5 rounded-full", val ? "bg-accent-warning shadow-[0_0_5px_rgba(250,204,21,0.8)]" : "bg-ic-hover")} />
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
};



// =============================================================================
// ORBOS VISION TRACKING SYSTEM (Unified Control)
// =============================================================================

const OrbosVisionTrackingSystem = memo(({
    telemetry,
    trackingEnabled,
    zoomEnabled,
    toggleTrackingFeature,
    fetchSystemStatus,
    devices,
    activeCamId
}) => {
    const [isMinimized, setIsMinimized] = useState(false);
    const [skelParams, setSkelParams] = useState({
        smoothing: 0.5,
        correction: 0.5,
        prediction: 0.5,
        jitter: 0.05,
        deviation: 0.04,
        tilt: 0
    });

    // Fetch Skel Params
    useEffect(() => {
        const fetchParams = async () => {
            try {
                const res = await axios.get(`${API_BASE}/v1/vision/kinect/parameters`);
                if (res.data) setSkelParams(prev => ({ ...prev, ...res.data }));
            } catch (e) { }
        };
        fetchParams();
    }, []);

    const updateSkelParam = async (key, val) => {
        const newParams = { ...skelParams, [key]: val };
        setSkelParams(newParams);
        try {
            if (key === 'tilt') {
                await axios.post(`${API_BASE}/v1/devices/045e_02ae/ptz`, { tilt: val });
            } else {
                await axios.post(`${API_BASE}/v1/vision/kinect/parameters`, newParams);
            }
        } catch (e) { console.error("Failed to update kinect param:", e); }
    };

    return (
        <div className="flex flex-col shrink-0 bg-ic-surface/90 rounded-xl border border-accent-cyan/30 shadow-2xl overflow-hidden transition-all duration-300">
            {/* Main Header */}
            <div
                className="p-3 bg-gradient-to-r from-accent-cyan/40 to-ic-surface flex justify-between items-center cursor-pointer border-b border-accent-cyan/20"
                onClick={() => setIsMinimized(!isMinimized)}
            >
                <div className="flex items-center gap-2">
                    <div className={cn("w-2 h-2 rounded-full", telemetry?.confidence > 50 ? "bg-accent-cyan animate-pulse shadow-[0_0_8px_rgba(34,211,238,0.8)]" : "bg-ic-hover")} />
                    <h2 className="text-[11px] font-black text-accent-cyan uppercase tracking-[0.2em]">
                        Orbos Vision Tracking System
                    </h2>
                </div>
                {isMinimized ? <ChevronDown className="w-4 h-4 text-accent-cyan/50" /> : <ChevronUp className="w-4 h-4 text-accent-cyan/50" />}
            </div>

            {!isMinimized && (
                <div className="p-4 flex flex-col gap-6 animate-in fade-in slide-in-from-top-4 duration-500">

                    {/* Section 1: Sensors & Streams */}
                    <div className="space-y-3">
                        <div className="flex items-center gap-2 border-l-2 border-accent-warning pl-2">
                            <Layers className="w-3 h-3 text-accent-warning" />
                            <h3 className="text-[9px] font-bold text-accent-warning/80 uppercase tracking-widest">Sensors & Streams</h3>
                        </div>
                        <KinectControls />
                    </div>

                    {/* Section 2: Precision Tracking */}
                    <div className="space-y-3">
                        <div className="flex items-center gap-2 border-l-2 border-accent-cyan pl-2">
                            <Activity className="w-3 h-3 text-accent-cyan" />
                            <h3 className="text-[9px] font-bold text-accent-cyan/80 uppercase tracking-widest">Precision Tracking</h3>
                        </div>
                        <TrackingTelemetry
                            data={telemetry}
                            trackingEnabled={trackingEnabled}
                            zoomEnabled={zoomEnabled}
                            onToggle={toggleTrackingFeature}
                            onRefresh={() => fetchSystemStatus(true)}
                        />
                    </div>

                    {/* Section 3: Motorized Control */}
                    <div className="space-y-3">
                        <div className="flex items-center gap-2 border-l-2 border-accent-indigo pl-2">
                            <Cpu className="w-3 h-3 text-accent-indigo" />
                            <h3 className="text-[9px] font-bold text-accent-indigo/80 uppercase tracking-widest">Motorized Control</h3>
                        </div>
                        <PTZControlPanel devices={devices.video} />
                    </div>

                    {/* Section 4: Kinect Fine-Tuning */}
                    <div className="space-y-4 pt-2 border-t border-white/5">
                        <div className="flex items-center gap-2 border-l-2 border-accent-success pl-2">
                            <Settings2 className="w-3 h-3 text-accent-success" />
                            <h3 className="text-[9px] font-bold text-accent-success/80 uppercase tracking-widest">Kinect Fine-Tuning</h3>
                        </div>

                        <div className="grid gap-3 px-1">
                            {/* Tilt Control */}
                            <div className="space-y-1.5">
                                <div className="flex justify-between text-[8px] uppercase font-bold text-txt-secondary">
                                    <span>Mechanical Tilt</span>
                                    <span className="text-accent-success">{skelParams.tilt}</span>
                                </div>
                                <input
                                    type="range" min="-27" max="27" step="1"
                                    value={skelParams.tilt}
                                    onChange={(e) => updateSkelParam('tilt', parseInt(e.target.value))}
                                    className="w-full accent-emerald-500 h-1 bg-black/40 rounded-lg appearance-none cursor-pointer"
                                />
                            </div>

                            {/* Smoothing Control */}
                            <div className="space-y-1.5">
                                <div className="flex justify-between text-[8px] uppercase font-bold text-txt-secondary">
                                    <span>Skeleton Smoothing</span>
                                    <span className="text-accent-success">{Math.round(skelParams.smoothing * 100)}%</span>
                                </div>
                                <input
                                    type="range" min="0" max="1" step="0.01"
                                    value={skelParams.smoothing}
                                    onChange={(e) => updateSkelParam('smoothing', parseFloat(e.target.value))}
                                    className="w-full accent-emerald-500 h-1 bg-black/40 rounded-lg appearance-none cursor-pointer"
                                />
                            </div>

                            {/* Jitter Radius */}
                            <div className="space-y-1.5">
                                <div className="flex justify-between text-[8px] uppercase font-bold text-txt-secondary">
                                    <span>Jitter Suppression</span>
                                    <span className="text-accent-success">{(skelParams.jitter * 100).toFixed(1)}cm</span>
                                </div>
                                <input
                                    type="range" min="0" max="0.5" step="0.01"
                                    value={skelParams.jitter}
                                    onChange={(e) => updateSkelParam('jitter', parseFloat(e.target.value))}
                                    className="w-full accent-emerald-500 h-1 bg-black/40 rounded-lg appearance-none cursor-pointer"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Section 5: Hardware Performance */}
                    <div className="space-y-3 pt-2 border-t border-white/5 bg-accent-indigo/5 -mx-3 px-3 pb-1">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2 border-l-2 border-accent-indigo pl-2">
                                <Zap className="w-3 h-3 text-accent-indigo" />
                                <h3 className="text-[9px] font-bold text-accent-indigo/80 uppercase tracking-widest">Hardware Performance</h3>
                            </div>
                            <span className="text-[8px] font-mono text-accent-indigo animate-pulse">{telemetry?.performance?.global_fps || 0} FPS</span>
                        </div>

                        <div className="grid grid-cols-2 gap-2 text-[8px] font-mono">
                            <div className="flex justify-between border-b border-white/5 pb-1">
                                <span className="text-txt-secondary uppercase">Process Latency</span>
                                <span className="text-white">{telemetry?.performance?.latency_ms || 0}ms</span>
                            </div>
                            <div className="flex justify-between border-b border-white/5 pb-1">
                                <span className="text-txt-secondary uppercase">Active Streams</span>
                            </div>
                        </div>

                        {telemetry?.performance?.fps && Object.entries(telemetry?.performance?.fps || {}).length > 0 && (
                            <div className="bg-black/40 rounded p-1 mb-2 border border-accent-cyan/30">
                                <label className="text-[8px] text-cyan-700 uppercase block mb-1">Stream Throttling (FPS)</label>
                                <div className="flex flex-col gap-1">
                                    {Object.entries(telemetry?.performance?.fps || {}).map(([cid, fps]) => (
                                        <div key={cid} className="bg-black/40 px-1.5 py-0.5 rounded border border-accent-indigo/40 flex gap-2 items-center">
                                            <span className="text-txt-secondary text-[7px] uppercase">CAM {cid}</span>
                                            <span className="text-accent-indigo font-bold">{fps}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
});

const AudioPanel = memo(({ telemetry }) => {
    const [data, setData] = useState(null); // Full API response
    const canvasRef = useRef(null);
    const audioCtxRef = useRef(null);
    const [isVisualizing, setIsVisualizing] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);

    const [sensitivity, setSensitivity] = useState(50);
    const [devices, setDevices] = useState([]);

    const [isToggling, setIsToggling] = useState(false);

    const fetchStatus = async () => {
        if (isToggling) return; // Prevent polling from overwriting optimistic state
        try {
            const res = await axios.get(`${API_BASE}/v1/audio/status`);

            // Only update data if we aren't mid-toggle to avoid race conditions
            if (!isToggling) {
                setData(res.data);
                if (res.data.devices) setDevices(res.data.devices);
            }
        } catch (e) { }
    };

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 500); // Faster polling for DoA
        return () => clearInterval(interval);
    }, [isToggling]); // Add dependency to pause polling effect when toggling

    const toggleActive = async () => {
        if (isToggling) return;

        setIsToggling(true);
        const currentState = data?.stream?.system_active ?? false;
        const newState = !currentState;

        // Optimistic update
        setData(prev => ({
            ...prev,
            stream: { ...(prev?.stream || {}), system_active: newState }
        }));

        try {
            await axios.post(`${API_BASE}/v1/audio/config`, { active: newState });
            // Lock UI in this state for 2.5s to let backend settle and poll catch up
            setTimeout(() => setIsToggling(false), 2500);
        } catch (e) {
            console.error("Audio toggle failed:", e);
            setData(prev => ({
                ...prev,
                stream: { ...(prev?.stream || {}), system_active: currentState }
            }));
            setIsToggling(false);
        }
    };

    const updateGain = async (val) => {
        await axios.post(`${API_BASE}/v1/audio/config`, { gain: val });
    };

    // Visualizer Effect (Browser Side - Aesthetic only)
    useEffect(() => {
        if (!data?.stream?.system_active) {
            if (audioCtxRef.current) {
                audioCtxRef.current.close();
                audioCtxRef.current = null;
                setIsVisualizing(false);
            }
            return;
        }

        let animationFrameId;
        const startAudio = async () => {
            if (audioCtxRef.current) return;
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const source = ctx.createMediaStreamSource(stream);
                const analyser = ctx.createAnalyser();
                analyser.fftSize = 64;
                source.connect(analyser);
                audioCtxRef.current = ctx;
                const bufferLength = analyser.frequencyBinCount;
                const dataArray = new Uint8Array(bufferLength);
                const canvas = canvasRef.current;
                if (!canvas) return;
                const canvasCtx = canvas.getContext('2d');

                const draw = () => {
                    if (!audioCtxRef.current) return;
                    animationFrameId = requestAnimationFrame(draw);
                    analyser.getByteFrequencyData(dataArray);
                    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
                    const barWidth = (canvas.width / bufferLength) * 2;
                    let x = 0;
                    for (let i = 0; i < bufferLength; i++) {
                        const barHeight = (dataArray[i] / 255) * canvas.height;
                        canvasCtx.fillStyle = `rgba(16, 185, 129, ${dataArray[i] / 255})`;
                        canvasCtx.fillRect(x, canvas.height - barHeight, barWidth - 1, barHeight);
                        x += barWidth;
                    }
                };
                setIsVisualizing(true);
                draw();
            } catch (e) { console.error("Audio Vis Failed:", e); }
        };
        startAudio();
        return () => {
            if (animationFrameId) cancelAnimationFrame(animationFrameId);
            if (audioCtxRef.current && audioCtxRef.current.state !== 'closed') {
                audioCtxRef.current.close();
                audioCtxRef.current = null;
            }
        };
    }, [data?.stream?.system_active]);

    if (!data) return null;
    const { stream } = data;
    const active = stream?.system_active || false;
    const angle = stream?.angle || 0;
    const vad = stream?.vad || false;
    const targetLock = stream?.target_lock || false;
    const statusMsg = stream?.status_msg || "SEARCHING";
    const sttAvailable = !!data?.stt?.available;
    const sttModelLoaded = !!data?.stt?.model_loaded;
    const sttRunning = !!data?.stt?.running;
    const sttError = data?.stt?.last_error;

    return (
        <div className="shrink-0 bg-ic-surface/60 p-3 rounded-lg border border-accent-success/20 space-y-3 shadow-inner shadow-accent-success/20 mt-2">
            <div className="flex justify-between items-center bg-black/40 p-1.5 rounded border border-accent-success/30">
                <h3 className="text-[10px] text-accent-success uppercase tracking-widest flex items-center gap-2 cursor-pointer" onClick={() => setIsMinimized(!isMinimized)}>
                    <Mic className="w-3 h-3" /> Acoustic Array
                    {isMinimized ? <ChevronDown className="w-3 h-3 opacity-50" /> : <ChevronUp className="w-3 h-3 opacity-50" />}
                </h3>
                {!isMinimized && (
                    <button
                        onClick={toggleActive}
                        disabled={isToggling}
                        className={cn(
                            "px-2 py-0.5 rounded text-[9px] font-bold transition-all uppercase border",
                            isToggling ? "bg-ic-hover text-txt-secondary border-ic-border cursor-wait" :
                                active ? "bg-accent-success/20 text-accent-success border-accent-success/50 hover:bg-accent-success/30" :
                                    "bg-ic-card text-txt-secondary border-ic-border hover:bg-ic-hover hover:text-txt-primary"
                        )}
                    >
                        {isToggling ? "WAIT" : active ? "ON" : "OFF"}
                    </button>
                )}
            </div>

            {!isMinimized && (
                <div className="space-y-3 animate-in slide-in-from-top-2 duration-300">

                    <div className="bg-black/40 p-2 rounded border border-accent-success/20 space-y-1">
                        <div className="flex justify-between items-center text-[8px] uppercase tracking-widest">
                            <span className="text-accent-success/80 font-bold">Whisper STT</span>
                            <span className={cn(
                                "px-1.5 py-0.5 rounded text-[8px] font-bold border",
                                sttAvailable && sttModelLoaded
                                    ? (sttRunning ? "bg-accent-success/20 text-accent-success border-accent-success/40" : "bg-accent-cyan/20 text-accent-cyan border-accent-cyan/40")
                                    : "bg-accent-danger/20 text-accent-danger border-red-500/40"
                            )}>
                                {sttAvailable && sttModelLoaded ? (sttRunning ? "LISTENING" : "READY") : "UNAVAILABLE"}
                            </span>
                        </div>
                        <div className="text-[8px] text-txt-secondary break-words">
                            {sttError || (sttAvailable && sttModelLoaded ? "Whisper runtime online" : "Whisper dependency/model not ready")}
                        </div>
                    </div>

                    {/* Persistence Sensitivity Slider */}
                    <div className="bg-black/40 p-2 rounded border border-accent-success/20 space-y-1">
                        <div className="flex justify-between items-center text-[8px] uppercase tracking-widest text-accent-success/60 font-bold">
                            <span>Compass Smoothing</span>
                            <span>{sensitivity}%</span>
                        </div>
                        <input
                            type="range"
                            min="1"
                            max="100"
                            value={sensitivity}
                            onChange={(e) => setSensitivity(parseInt(e.target.value))}
                            className="w-full h-1 bg-emerald-950 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                        />
                    </div>

                    {/* Spatial Compass */}
                    <div className="relative h-48 bg-black/40 rounded border border-accent-success/10 flex items-center justify-center overflow-hidden shrink-0">
                        {/* Angle Arc */}
                        <div className="absolute inset-0 flex items-center justify-center opacity-30">
                            <div className="w-40 h-40 border border-accent-success/30 rounded-full" />
                        </div>

                        {/* Needle */}
                        <div
                            className="absolute w-1 h-full bg-gradient-to-t from-emerald-500 to-transparent origin-bottom transition-transform ease-out"
                            style={{
                                height: '40%',
                                bottom: '50%',
                                transformOrigin: 'bottom center',
                                transform: `rotate(${angle}deg)`,
                                transitionDuration: `${Math.max(100, 1000 - (sensitivity * 9))}ms`
                            }}
                        >
                            <div className="w-3 h-3 bg-emerald-400 rounded-full -mt-1.5 -ml-[4px] shadow-[0_0_10px_rgba(52,211,153,0.8)]" />
                        </div>

                        {/* Center Dot */}
                        <div className="w-3 h-3 bg-ic-hover rounded-full z-10 border border-accent-success/50" />

                        {/* Readout */}
                        <div className="absolute bottom-2 right-2 text-[10px] font-mono text-accent-success/80 bg-black/50 px-1 rounded flex gap-2">
                            <span>{angle.toFixed(0)}</span>
                            <span className="text-txt-muted border-l border-ic-border pl-2">FLOOR: {(stream?.noise_floor || 0).toFixed(4)}</span>
                        </div>

                        {/* Spatial Lock Indicator */}
                        {targetLock && (
                            <div className="absolute top-2 right-2 flex items-center gap-1 bg-accent-cyan/20 px-1.5 py-0.5 rounded border border-accent-cyan/40 animate-pulse">
                                <ShieldCheck className="w-3 h-3 text-accent-cyan" />
                                <span className="text-[9px] text-accent-cyan font-bold tracking-widest uppercase">Target Sync</span>
                            </div>
                        )}

                        {/* Fusion Status Message */}
                        <div className="absolute bottom-2 left-2 text-[8px] font-bold text-txt-secondary uppercase tracking-tighter">
                            AI Mode: <span className={cn(targetLock ? "text-accent-cyan" : "text-txt-secondary")}>{statusMsg}</span>
                        </div>

                        {/* VAD Indicator */}
                        {vad && (
                            <div className="absolute top-2 left-2 flex items-center gap-1 bg-accent-success/20 px-1.5 py-0.5 rounded border border-accent-success/30">
                                <Activity className="w-3 h-3 text-accent-success animate-pulse" />
                                <span className="text-[9px] text-accent-success font-bold tracking-wider">SPEECH DETECTED</span>
                            </div>
                        )}
                    </div>

                    {/* Visualizer Canvas */}
                    <div className="bg-black/50 rounded h-8 w-full border border-accent-success/20 relative overflow-hidden">
                        {!isVisualizing && <div className="absolute inset-0 flex items-center justify-center text-[9px] text-txt-muted">Spectrogram Inactive</div>}
                        <canvas ref={canvasRef} width={280} height={32} className="w-full h-full" />
                    </div>

                    {/* Audio Device Health List */}
                    <div className="bg-black/40 rounded border border-accent-success/10 overflow-hidden">
                        <div className="bg-accent-success/20 px-2 py-1 border-b border-accent-success/20 text-[8px] font-bold text-accent-success uppercase tracking-widest">
                            Subsystem Device Tree
                        </div>
                        <div className="p-1 space-y-0.5 max-h-[100px] overflow-y-auto custom-scrollbar">
                            {devices.length > 0 ? devices.map((dev, idx) => {
                                // Logic: Active if system is active AND (it's a PS Eye OR it matches specific name)
                                const isEye = dev.is_eye || (dev.name && dev.name.includes("PlayStation") && dev.channels === 4);
                                const isActive = active && isEye;
                                const isSpeaking = isActive && vad;

                                return (
                                    <div key={idx} className="flex justify-between items-center text-[7px] p-1 bg-black/20 rounded border border-white/5 group hover:bg-accent-success/5 transition-colors">
                                        <div className="flex items-center gap-1.5 truncate pr-2">
                                            <div className={cn(
                                                "w-1 h-1 rounded-full",
                                                isSpeaking ? "bg-emerald-400 animate-pulse ring-2 ring-emerald-500/20" :
                                                    isActive ? "bg-accent-success" : "bg-ic-hover"
                                            )} />
                                            <span className={cn("truncate", isActive ? "text-accent-success" : "text-txt-secondary")}>
                                                {dev.name.replace("Microphone (", "").replace(")", "")}
                                            </span>
                                        </div>
                                        <div className="flex gap-1 items-center shrink-0">
                                            <span className="text-[6px] text-txt-muted font-mono uppercase">{dev.channels}CH</span>
                                            <span className={cn(
                                                "px-1 py-0.5 rounded-[2px] font-bold uppercase",
                                                isSpeaking ? "bg-accent-success text-black" :
                                                    isActive ? "bg-accent-success/40 text-accent-success" : "bg-ic-card text-txt-muted"
                                            )}>
                                                {isSpeaking ? "LIVE" : isActive ? "WAIT" : "STBY"}
                                            </span>
                                        </div>
                                    </div>
                                );
                            }) : (
                                <div className="text-center py-2 text-[8px] text-txt-muted italic">No audio hardware identified</div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
});

const SystemStatusOverlay = memo(({ isOpen, onClose, statusData, onRefresh, telemetry, onOpenConfiguration }) => {
    const [debugConsole, setDebugConsole] = useState(null);
    const [issuesAcknowledged, setIssuesAcknowledged] = useState(false);
    const [isRefreshing, setIsRefreshing] = useState(false);

    const handleRefresh = async () => {
        setIsRefreshing(true);
        try {
            await onRefresh();
        } finally {
            setTimeout(() => setIsRefreshing(false), 1500); // Minimum visual feedback time
        }
    };

    // Live Telemetry Section
    const liveStats = telemetry ? [
        { label: "CPU Usage", value: `${telemetry?.system?.cpu_percent || 0}%`, color: (telemetry?.system?.cpu_percent || 0) > 80 ? "text-accent-danger" : "text-lime-400" },
        { label: "RAM Usage", value: `${telemetry?.system?.ram_percent || 0}%`, color: "text-accent-cyan" },
        { label: "Vision FPS", value: `${(telemetry?.vision?.fps || 0).toFixed(1)}`, color: "text-accent-indigo" },
    ] : [];

    // Comprehensive System Checks
    const auditChecks = [
        {
            id: 'triad',
            label: 'Triad Core Connection',
            // The API is alive if we received a valid status response (not ERROR)
            status: statusData?.status && statusData.status !== 'ERROR' ? 'PASS' : 'FAIL',
            value: statusData?.status && statusData.status !== 'ERROR' ? 'Connected' : 'Disconnected',
            fix: 'Restart the backend API server (python src/interfaces/triad_api.py)'
        },
        {
            id: 'vision',
            label: 'Vision Subsystem',
            status: statusData?.components?.vision?.health === 'HEALTHY' ? 'PASS' :
                statusData?.components?.vision?.health === 'DEGRADED' ? 'WARN' : 'FAIL',
            value: statusData?.components?.vision?.health || 'OFFLINE',
            fix: statusData?.components?.vision?.health === 'DEGRADED'
                ? 'Hardware conflicts detected - check USB connections or reinstall camera drivers'
                : 'Ensure cameras are connected and not in use by other apps'
        },
        {
            id: 'cameras',
            label: 'Camera Detection',
            status: (statusData?.components?.vision?.cameras_detected || 0) >= 1 ? 'PASS' : 'FAIL',
            value: `${statusData?.components?.vision?.cameras_detected || 0} camera(s)`,
            fix: 'Connect PS Eye cameras or USB webcam. Check Device Manager for driver issues.'
        },
        {
            id: 'intelligence',
            label: 'Neural Core (LLM)',
            status: ['ACTIVE', 'READY'].includes(statusData?.components?.intelligence?.status) ? 'PASS' :
                statusData?.components?.intelligence?.status?.includes('LOADING') ? 'LOADING' : 'FAIL',
            value: statusData?.components?.intelligence?.status || 'STANDBY',
            fix: 'Model is loading - please wait. If stuck, restart the API server.'
        },
        {
            id: 'audio',
            label: 'Audio Subsystem',
            status: (statusData?.components?.sensory?.microphones || 0) >= 1 ? 'PASS' : 'WARN',
            value: `${statusData?.components?.sensory?.microphones || 0} mic(s)`,
            fix: 'Connect a microphone. PS Eye 4-channel array recommended.'
        },
        {
            id: 'conflicts',
            label: 'Hardware Conflicts',
            status: (statusData?.components?.vision?.conflicts?.length || 0) === 0 ? 'PASS' : 'WARN',
            value: (statusData?.components?.vision?.conflicts?.length || 0) === 0 ? 'None' :
                `${statusData?.components?.vision?.conflicts?.length} issue(s)`,
            fix: 'Review conflicts below. Most are informational and can be acknowledged.'
        }
    ];

    const passCount = auditChecks.filter(c => c.status === 'PASS').length;
    const warnCount = auditChecks.filter(c => c.status === 'WARN').length;
    const failCount = auditChecks.filter(c => c.status === 'FAIL').length;
    const loadingCount = auditChecks.filter(c => c.status === 'LOADING').length;
    const allPassed = failCount === 0 && loadingCount === 0;
    const canProceed = allPassed || issuesAcknowledged;

    // --- Browser Tab Synchronization ---
    useEffect(() => {
        if (!isOpen) {
            document.title = "ImpressionCore B3";
            return;
        }

        let intervalId;

        if (allPassed) {
            document.title = " System Ready";
        } else if (issuesAcknowledged) {
            document.title = "  System Ready"; // Proceeding with potential issues
        } else if (loadingCount === 0 && failCount > 0) {
            document.title = " Action Required";
        } else {
            const spinners = [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "];
            let frame = 0;

            // Function to update title with current progress and spinner
            const updateTitle = () => {
                const totalChecks = auditChecks.length;
                const progress = Math.round((passCount / totalChecks) * 100);
                const spinner = spinners[frame % spinners.length];
                document.title = `${spinner} [${progress}%] System Audit...`;
                frame++;
            };

            // Initial update
            updateTitle();

            // Animate
            intervalId = setInterval(updateTitle, 200);
        }

        // cleanup on unmount/close or status change
        return () => {
            if (intervalId) clearInterval(intervalId);
            document.title = "ImpressionCore B3";
        };
    }, [isOpen, passCount, allPassed, auditChecks.length]);

    const ComponentIcon = ({ health }) => {
        if (health === "HEALTHY" || health === "ACTIVE" || health === "NOMINAL")
            return <CheckCircle2 className="w-4 h-4 text-accent-success" />;
        if (health === "CONFLICT" || health === "DEGRADED")
            return <AlertTriangle className="w-4 h-4 text-accent-warning" />;
        return <XCircle className="w-4 h-4 text-accent-danger" />;
    };

    const CheckIcon = ({ status }) => {
        if (status === 'PASS') return <CheckCircle2 className="w-4 h-4 text-accent-success" />;
        if (status === 'WARN') return <AlertTriangle className="w-4 h-4 text-accent-warning" />;
        if (status === 'LOADING') return <RefreshCw className="w-4 h-4 text-accent-cyan animate-spin" />;
        return <XCircle className="w-4 h-4 text-accent-danger" />;
    };

    const generateDebug = async () => {
        try {
            // Include audit snapshot in debug request
            const auditSnapshot = {
                timestamp: new Date().toISOString(),
                checks: auditChecks.map(c => ({ id: c.id, label: c.label, status: c.status, value: c.value })),
                summary: { pass: passCount, warn: warnCount, fail: failCount, loading: loadingCount },
                issuesAcknowledged,
                conflicts: statusData?.components?.vision?.conflicts || []
            };
            const res = await axios.get(`${API_BASE}/v1/system/debug`);
            if (res.data.success) {
                // Merge audit snapshot into debug data
                const enrichedData = { ...res.data.data, audit_snapshot: auditSnapshot };
                setDebugConsole({ ...res.data, data: enrichedData });
                const blob = new Blob([JSON.stringify(enrichedData, null, 2)], { type: 'text/plain' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = res.data.filename.replace('.json', '_with_audit.json');
                a.click();
            }
        } catch (e) {
            console.error("Debug failed:", e);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] bg-black/80 backdrop-blur-md flex items-center justify-center p-6 animate-in fade-in zoom-in duration-300">
            <div className="bg-ic-bg border border-accent-cyan/30 rounded-xl shadow-[0_0_50px_rgba(6,182,212,0.1)] w-full max-w-2xl overflow-hidden flex flex-col">
                <div className="p-4 border-b border-accent-cyan/50 bg-cyan-950/20 flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <Activity className="w-6 h-6 text-accent-cyan" />
                        <div>
                            <h2 className="text-lg font-bold text-white tracking-tight">ORBOS System Readiness Audit</h2>
                            <p className="text-[10px] text-accent-cyan/70 uppercase tracking-widest font-medium">Real-time Interface & Hardware Sync</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => {
                                onOpenConfiguration?.();
                                onClose?.();
                            }}
                            className="px-3 py-1.5 bg-accent-indigo/20 hover:bg-accent-indigo/40 text-accent-indigo text-[10px] font-bold rounded-lg border border-accent-indigo/30 transition-all flex items-center gap-2"
                        >
                            <Settings className="w-3 h-3" /> CONFIGURATION
                        </button>
                        <button onClick={onClose} className="p-2 hover:bg-white/5 rounded-full transition-colors">
                            <X className="w-5 h-5 text-txt-secondary" />
                        </button>
                    </div>
                </div>

                {/* Live Telemetry Bar */}
                {telemetry && (
                    <div className="flex items-center justify-around bg-ic-bg/80 p-3 border-b border-accent-cyan/30 font-mono text-sm">
                        {liveStats.map((stat, i) => (
                            <div key={i} className="flex flex-col items-center">
                                <span className="text-txt-secondary text-[10px] uppercase tracking-wider">{stat.label}</span>
                                <span className={`font-bold ${stat.color}`}>{stat.value}</span>
                            </div>
                        ))}
                        <div className="flex flex-col items-center">
                            <span className="text-txt-secondary text-[10px] uppercase tracking-wider">Agents</span>
                            <span className="text-accent-warning font-bold">{telemetry?.agent?.status || "IDLE"}</span>
                        </div>
                    </div>
                )}

                <div className="p-6 overflow-y-auto max-h-[70vh] space-y-6 custom-scrollbar">
                    {/* Comprehensive Audit Checklist */}
                    <div className="space-y-3">
                        <div className="flex justify-between items-center">
                            <h3 className="text-xs font-bold text-txt-secondary uppercase tracking-wider border-l-2 border-white pl-3">System Readiness Checklist</h3>
                            <div className="flex items-center gap-3 text-[10px]">
                                <span className="text-accent-success">{passCount} PASS</span>
                                {warnCount > 0 && <span className="text-accent-warning">{warnCount} WARN</span>}
                                {failCount > 0 && <span className="text-accent-danger">{failCount} FAIL</span>}
                                {loadingCount > 0 && <span className="text-accent-cyan">{loadingCount} LOADING</span>}
                            </div>
                        </div>

                        <div className="grid grid-cols-1 gap-2">
                            {auditChecks.map(check => (
                                <div
                                    key={check.id}
                                    className={cn(
                                        "p-3 rounded-lg border flex items-center justify-between",
                                        check.status === 'PASS' ? "bg-accent-success/5 border-green-500/20" :
                                            check.status === 'WARN' ? "bg-accent-warning/5 border-accent-warning/20" :
                                                check.status === 'LOADING' ? "bg-accent-cyan/5 border-accent-cyan/20" :
                                                    "bg-accent-danger/5 border-red-500/20"
                                    )}
                                >
                                    <div className="flex items-center gap-3">
                                        <CheckIcon status={check.status} />
                                        <div>
                                            <div className="text-sm text-txt-primary font-medium">{check.label}</div>
                                            {check.status !== 'PASS' && (
                                                <div className="text-[10px] text-txt-secondary mt-0.5">{check.fix}</div>
                                            )}
                                        </div>
                                    </div>
                                    <div className={cn(
                                        "text-xs font-mono font-bold",
                                        check.status === 'PASS' ? "text-accent-success" :
                                            check.status === 'WARN' ? "text-accent-warning" :
                                                check.status === 'LOADING' ? "text-accent-cyan" :
                                                    "text-accent-danger"
                                    )}>
                                        {check.value}
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Acknowledge Issues Button */}
                        {!allPassed && !issuesAcknowledged && (
                            <button
                                onClick={() => setIssuesAcknowledged(true)}
                                className="w-full mt-3 px-4 py-2 bg-accent-warning/20 hover:bg-accent-warning/40 text-accent-warning text-xs font-bold rounded-lg border border-accent-warning/30 transition-all flex items-center justify-center gap-2"
                            >
                                <AlertTriangle className="w-4 h-4" />
                                ACKNOWLEDGE ISSUES & PROCEED
                            </button>
                        )}
                        {issuesAcknowledged && (
                            <div className="text-[10px] text-accent-warning/70 text-center italic">
                                Issues acknowledged - you may proceed with degraded functionality
                            </div>
                        )}
                    </div>

                    {/* Vision Section */}
                    <div className="space-y-3">
                        <h3 className="text-xs font-bold text-txt-secondary uppercase tracking-wider border-l-2 border-accent-cyan pl-3">Vision & Optics</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div className="bg-ic-surface/40 p-3 rounded-lg border border-ic-border flex items-center justify-between">
                                <span className="text-sm text-txt-primary">Active Cameras</span>
                                <div className="flex items-center gap-2">
                                    <span className="text-accent-cyan font-mono font-bold">{statusData?.components?.vision?.cameras_detected || 0}</span>
                                    <Camera className="w-4 h-4 text-txt-secondary" />
                                </div>
                            </div>
                            <div className="bg-ic-surface/40 p-3 rounded-lg border border-ic-border flex items-center justify-between">
                                <span className="text-sm text-txt-primary">Signal Health</span>
                                <div className="flex items-center gap-2">
                                    <span className={cn("text-xs font-bold", statusData?.components?.vision?.health === 'HEALTHY' ? "text-accent-success" : "text-accent-warning")}>
                                        {statusData?.components?.vision?.health || "OFFLINE"}
                                    </span>
                                    {statusData?.components?.vision?.health && <ComponentIcon health={statusData.components.vision.health} />}
                                </div>
                            </div>
                        </div>

                        {/* Conflicts */}
                        {statusData?.components?.vision?.conflicts && statusData.components.vision.conflicts.length > 0 && (
                            <div className="bg-accent-warning/5 border border-accent-warning/20 p-3 rounded-lg space-y-2">
                                <div className="flex items-center gap-2 text-accent-warning">
                                    <Zap className="w-3 h-3" />
                                    <span className="text-[10px] font-bold uppercase">Hardware Advisories Detected</span>
                                </div>
                                {statusData.components.vision.conflicts.map((c, i) => (
                                    <div key={i} className="text-xs text-txt-secondary bg-black/40 p-2 rounded">
                                        <span className="text-accent-warning/80 font-medium">{c.device}:</span> {c.reason}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Intelligence Section */}
                    <div className="space-y-3">
                        <h3 className="text-xs font-bold text-txt-secondary uppercase tracking-wider border-l-2 border-accent-indigo pl-3">Neural Core</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div className="bg-ic-surface/40 p-3 rounded-lg border border-ic-border flex items-center justify-between">
                                <span className="text-sm text-txt-primary">LLM Status</span>
                                <div className="flex items-center gap-2">
                                    <span className={cn("font-bold text-xs flex items-center gap-2", statusData?.components?.intelligence?.status.startsWith("ACTIVE") ? "text-accent-indigo" : "text-accent-warning")}>
                                        {statusData?.components?.intelligence?.status !== "ACTIVE" && <RefreshCw className="w-3 h-3 animate-spin" />}
                                        {statusData?.components?.intelligence?.status || "STANDBY"}
                                    </span>
                                    <BrainCircuit className="w-4 h-4 text-txt-secondary" />
                                </div>
                            </div>
                            <div className="bg-ic-surface/40 p-3 rounded-lg border border-ic-border flex items-center justify-between">
                                <span className="text-sm text-txt-primary">Active Model</span>
                                <span className="text-xs text-txt-secondary font-mono truncate max-w-[120px]">{statusData?.components?.intelligence?.model}</span>
                            </div>
                        </div>
                    </div>

                    {/* Sensory Section */}
                    <div className="space-y-3">
                        <h3 className="text-xs font-bold text-txt-secondary uppercase tracking-wider border-l-2 border-accent-success pl-3">Acoustics & PnP</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div className="bg-ic-surface/40 p-3 rounded-lg border border-ic-border flex items-center justify-between">
                                <span className="text-sm text-txt-primary">Microphone Array</span>
                                <div className="flex items-center gap-2">
                                    <span className="text-accent-success font-mono font-bold">{statusData?.components?.sensory?.microphones || 0}</span>
                                    <Mic className="w-4 h-4 text-txt-secondary" />
                                </div>
                            </div>
                            <div className="bg-ic-surface/40 p-3 rounded-lg border border-ic-border flex items-center justify-between">
                                <span className="text-sm text-txt-primary">PnP Inventory Size</span>
                                <span className="text-accent-success font-mono font-bold">{statusData?.components?.sensory?.pnp_inventory_size || 0}</span>
                            </div>
                        </div>
                    </div>

                    {/* Trace Route Logic Integration */}
                    <div className="space-y-3">
                        <h3 className="text-xs font-bold text-txt-secondary uppercase tracking-wider border-l-2 border-ic-border pl-3">Hardware Trace Route</h3>
                        <div className="bg-black/60 p-4 rounded-lg border border-ic-border font-mono text-[10px] space-y-1.5 max-h-40 overflow-y-auto custom-scrollbar">
                            {statusData?.trace?.length > 0 ? (
                                statusData.trace.map((t, i) => (
                                    <div key={i} className="flex gap-2">
                                        <span className="text-txt-muted">[{new Date(t.timestamp * 1000).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}]</span>
                                        <span className={cn(
                                            t.level === "ERROR" ? "text-accent-danger" :
                                                t.level === "WARNING" ? "text-accent-warning" :
                                                    t.message.includes("SUCCESS") ? "text-accent-success" : "text-accent-cyan/80"
                                        )}>
                                            {t.message}
                                        </span>
                                    </div>
                                ))
                            ) : (
                                <div className="text-txt-muted italic">Waiting for telemetry scan...</div>
                            )}
                        </div>
                    </div>

                    {/* Debug Console Dropdown */}
                    {debugConsole && (
                        <div className="bg-black/80 border border-accent-warning/30 p-4 rounded-lg space-y-2 animate-in slide-in-from-top duration-300">
                            <div className="flex justify-between items-center text-accent-warning mb-2">
                                <div className="flex items-center gap-2">
                                    <Terminal className="w-4 h-4" />
                                    <span className="text-xs font-bold uppercase tracking-widest">Debug Output Console</span>
                                </div>
                                <button onClick={() => setDebugConsole(null)} className="text-[10px] hover:text-white uppercase font-bold">Close Console</button>
                            </div>
                            <div className="bg-ic-surface p-3 rounded font-mono text-[10px] text-accent-success overflow-x-auto max-h-48 whitespace-pre border border-accent-success/30">
                                {JSON.stringify(debugConsole.data, null, 2)}
                            </div>
                            <div className="flex justify-between items-center gap-4">
                                <div className="text-[9px] text-txt-secondary italic">
                                    File saved to: <span className="text-accent-cyan">{debugConsole.file_path}</span>
                                </div>
                                <button
                                    onClick={() => {
                                        navigator.clipboard.writeText(JSON.stringify(debugConsole.data, null, 2));
                                        alert("Debug info copied to clipboard.");
                                    }}
                                    className="px-3 py-1 bg-accent-warning/20 hover:bg-accent-warning/40 text-accent-warning text-[9px] font-bold rounded uppercase border border-accent-warning/30"
                                >
                                    Copy to Clipboard
                                </button>
                            </div>
                        </div>
                    )}
                </div>

                <div className="p-4 bg-ic-surface/50 border-t border-ic-border flex flex-col gap-3">
                    {/* Loading Progress */}
                    <div className="w-full bg-ic-card h-1.5 rounded-full overflow-hidden">
                        <div
                            className="bg-accent-cyan h-full transition-all duration-1000 ease-out"
                            style={{
                                width: `${[
                                    statusData?.components?.vision?.health === 'HEALTHY' || statusData?.components?.vision?.health === 'ACTIVE',
                                    statusData?.components?.intelligence?.status === 'ACTIVE' || statusData?.components?.intelligence?.status === 'READY',
                                    (statusData?.components?.sensory?.microphones || 0) > 0
                                ].filter(Boolean).length / 3 * 100}%`
                            }}
                        />
                    </div>

                    <div className="flex justify-between items-center text-[10px] text-txt-secondary">
                        <div className="flex items-center gap-2">
                            <div className={cn("w-1.5 h-1.5 rounded-full animate-pulse",
                                statusData?.loading_phase === "READY" ? "bg-accent-success" : "bg-accent-warning"
                            )} />
                            <span>{statusData?.loading_phase === "READY" ? "SYSTEM READY" : "INITIALIZING MODULES..."}</span>
                        </div>
                        <div className="flex gap-2 flex-wrap justify-end">
                            <button
                                onClick={handleRefresh}
                                disabled={isRefreshing}
                                className={cn(
                                    "px-4 py-2 text-[10px] font-bold rounded-lg border transition-all flex items-center gap-2",
                                    isRefreshing
                                        ? "bg-accent-cyan/40 text-accent-cyan border-accent-cyan/50 cursor-wait"
                                        : "bg-accent-cyan/20 hover:bg-accent-cyan/40 text-accent-cyan border-accent-cyan/30"
                                )}
                            >
                                <RefreshCw className={cn("w-3 h-3", isRefreshing && "animate-spin")} />
                                {isRefreshing ? "SYNCING..." : "FORCE SYNC HARDWARE"}
                            </button>
                            <button
                                onClick={generateDebug}
                                className="px-4 py-2 bg-ic-card hover:bg-ic-hover text-txt-primary text-[10px] font-bold rounded-lg border border-ic-border transition-all flex items-center gap-2"
                            >
                                <ScrollText className="w-3 h-3 text-accent-warning" /> GENERATE DEBUG LOGS
                            </button>
                            <button
                                onClick={async () => {
                                    if (window.confirm("Are you sure you want to halt the system? All hardware will be released.")) {
                                        try {
                                            await axios.post(`${API_BASE}/v1/system/shutdown`);
                                            alert("Shutdown initiated. The app will now close.");
                                            window.close();
                                        } catch (e) {
                                            console.error("Shutdown failed", e);
                                        }
                                    }
                                }}
                                className="px-4 py-2 bg-accent-danger/40 hover:bg-accent-danger/60 text-accent-danger text-[10px] font-bold rounded-lg border border-accent-danger/50 transition-all flex items-center gap-2"
                            >
                                <Power className="w-3 h-3 text-accent-danger" /> SHUTDOWN SYSTEM
                            </button>
                            <button
                                onClick={onClose}
                                className={cn(
                                    "px-6 py-2 font-bold rounded-lg transition-transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed",
                                    canProceed ? "bg-accent-cyan hover:bg-accent-cyan text-white" : "bg-ic-hover text-txt-secondary"
                                )}
                                disabled={!canProceed}
                            >
                                {canProceed ? "INITIALIZE SYSTEM" : loadingCount > 0 ? "INITIALIZING..." : "RESOLVE ISSUES"}
                            </button>
                            <button
                                onClick={() => {
                                    onOpenConfiguration?.();
                                    onClose?.();
                                }}
                                className="px-4 py-2 bg-accent-indigo/20 hover:bg-accent-indigo/40 text-accent-indigo text-[10px] font-bold rounded-lg border border-accent-indigo/30 transition-all flex items-center gap-2"
                            >
                                <Settings className="w-3 h-3" /> CONFIGURATION
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
});

const IntelligencePanel = memo(({ status }) => {
    const [isMinimized, setIsMinimized] = useState(false);

    if (!status) return (
        <div className="bg-ic-surface/50 p-3 rounded border border-ic-border animate-pulse text-[10px] text-txt-secondary text-center shrink-0">
            Initializing Intelligence Layer...
        </div>
    );

    return (
        <div className="flex flex-col gap-3 bg-ic-surface/80 p-3 rounded border border-accent-indigo/30 shadow-lg shadow-accent-indigo/10 shrink-0 transition-all duration-300">
            {/* Header */}
            <div className="flex justify-between items-center border-b border-accent-indigo/20 pb-2 cursor-pointer" onClick={() => setIsMinimized(!isMinimized)}>
                <h3 className="text-[10px] text-accent-indigo uppercase tracking-widest font-bold flex items-center gap-2">
                    <Brain className="w-3 h-3" /> Neural Status
                    {isMinimized ? <ChevronDown className="w-3 h-3 opacity-50" /> : <ChevronUp className="w-3 h-3 opacity-50" />}
                </h3>
                {!isMinimized && (
                    <div className="flex items-center gap-1.5">
                        <div className={cn("w-1.5 h-1.5 rounded-full", status.status === "ACTIVE" ? "bg-accent-indigo animate-pulse" : "bg-accent-warning")} />
                        <span className="text-[9px] text-accent-indigo font-bold uppercase">
                            {status.loading_phase === "READY" ? status.status : (status.loading_phase || status.status)}
                        </span>
                    </div>
                )}
            </div>

            {!isMinimized && (
                <div className="flex flex-col gap-2 animate-in slide-in-from-top-2 duration-300">
                    {/* Active Core Info */}
                    <div>
                        <label className="text-[9px] text-txt-secondary uppercase block mb-0.5">Active Core</label>
                        <div className="text-[11px] text-indigo-100 font-medium truncate bg-black/40 p-1.5 rounded border border-accent-indigo/10">
                            {status.model_name || status.model || "Unknown Model"}
                        </div>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-2 gap-2">
                        <div>
                            <label className="text-[8px] text-txt-secondary uppercase block">Quantization</label>
                            <span className="text-[10px] text-txt-primary font-bold">{status.quantization || "N/A"}</span>
                        </div>
                        <div>
                            <label className="text-[8px] text-txt-secondary uppercase block">Compute Device</label>
                            <span className="text-[10px] text-txt-primary font-bold uppercase">{status.device || "CPU"}</span>
                        </div>
                    </div>

                    {/* VRAM & Load */}
                    <div className="space-y-1.5 pt-1 border-t border-accent-indigo/10">
                        <div className="flex justify-between items-center">
                            <label className="text-[9px] text-txt-secondary uppercase">VRAM Allocation</label>
                            <span className="text-[9px] text-accent-indigo font-mono">
                                {(status.vram_allocated_gb || 0).toFixed(2)} / {(status.vram_reserved_gb || 0).toFixed(2)} GB
                            </span>
                        </div>
                        <div className="w-full bg-ic-card/50 h-1 rounded-full overflow-hidden">
                            <div
                                className="bg-accent-indigo h-full transition-all duration-1000"
                                style={{ width: `${Math.min(100, ((status.vram_allocated_gb || 0) / (status.vram_reserved_gb || 10)) * 100)}%` }}
                            />
                        </div>
                    </div>

                    <div className="text-[8px] text-txt-muted flex justify-between italic">
                        <span>Precision: Half-Float (FP16)</span>
                        <span>Load: {status.simultaneous_load ? 'SIMUL' : 'SEQ'}</span>
                    </div>
                </div>
            )}
        </div>
    );
});

const FaceManagementPanel = memo(({
    faces,
    onEnroll,
    onDelete,
    onAddSample,
    enrollName,
    setEnrollName,
    enrollRole,
    setEnrollRole,
    isEnrolling,
    enrollStatus
}) => {
    const [isMinimized, setIsMinimized] = useState(false);

    return (
        <div className="flex flex-col gap-3 bg-ic-surface/80 p-3 rounded-lg border border-accent-cyan/40 shadow-lg shrink-0 transition-all duration-300">
            <div className="flex justify-between items-center cursor-pointer" onClick={() => setIsMinimized(!isMinimized)}>
                <h3 className="text-[10px] text-accent-cyan uppercase tracking-widest font-bold flex items-center gap-2">
                    <ShieldCheck className="w-3 h-3" /> Identity Management
                    {isMinimized ? <ChevronDown className="w-3 h-3 opacity-50" /> : <ChevronUp className="w-3 h-3 opacity-50" />}
                </h3>
            </div>

            {!isMinimized && (
                <div className="flex flex-col gap-3 animate-in fade-in duration-300">
                    {/* Enrollment Form */}
                    <div className="bg-black/40 p-2 rounded border border-accent-cyan/20 space-y-2">
                        <label className="text-[8px] text-accent-cyan uppercase font-bold">New Citizen Enrollment</label>
                        <div className="flex flex-col gap-2">
                            <input
                                type="text"
                                placeholder="Full Name"
                                value={enrollName}
                                onChange={e => setEnrollName(e.target.value)}
                                className="bg-ic-bg border border-accent-cyan/50 rounded px-2 py-1 text-[10px] text-cyan-100 outline-none focus:border-accent-cyan"
                            />
                            <div className="flex gap-2">
                                <select
                                    value={enrollRole}
                                    onChange={e => setEnrollRole(e.target.value)}
                                    className="bg-ic-bg border border-accent-cyan/50 rounded px-2 py-1 text-[10px] text-accent-cyan outline-none flex-1"
                                >
                                    <option value="user">User</option>
                                    <option value="admin">Administrator</option>
                                    <option value="guest">Guest</option>
                                </select>
                                <button
                                    onClick={onEnroll}
                                    disabled={isEnrolling || !enrollName.trim()}
                                    className="bg-accent-cyan hover:bg-accent-cyan disabled:opacity-50 text-white text-[9px] font-bold px-3 py-1 rounded transition-all uppercase"
                                >
                                    {isEnrolling ? "Capturing..." : "Enroll"}
                                </button>
                            </div>
                        </div>
                        {enrollStatus && (
                            <div className={cn(
                                "text-[8px] p-1 rounded border text-center font-bold uppercase",
                                enrollStatus.type === 'error' ? "bg-accent-danger/20 border-red-500/50 text-accent-danger" :
                                    enrollStatus.type === 'success' ? "bg-green-900/20 border-green-500/50 text-accent-success" :
                                        "bg-accent-cyan/20 border-accent-cyan/50 text-accent-cyan"
                            )}>
                                {enrollStatus.msg}
                            </div>
                        )}
                    </div>

                    {/* Face List */}
                    <div className="space-y-1 max-h-48 overflow-y-auto custom-scrollbar">
                        {faces.length === 0 && <div className="text-[8px] text-txt-muted italic text-center p-2">No identities enrolled.</div>}
                        {faces.map(face => (
                            <div key={face.id} className="group bg-black/20 border border-ic-border rounded p-2 flex justify-between items-center hover:border-accent-cyan/40 transition-all">
                                <div className="flex flex-col">
                                    <span className="text-[10px] text-cyan-100 font-bold">{face.name}</span>
                                    <span className="text-[8px] text-txt-secondary uppercase tracking-tighter">
                                        {face.role}  {face.embedding_count} Samples
                                    </span>
                                </div>
                                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button
                                        onClick={() => onAddSample(face.id)}
                                        title="Add Training Sample"
                                        className="p-1 hover:bg-accent-cyan/20 text-accent-cyan rounded transition-colors"
                                    >
                                        <RefreshCw className="w-3 h-3" />
                                    </button>
                                    <button
                                        onClick={() => onDelete(face.id)}
                                        title="Delete Identity"
                                        className="p-1 hover:bg-accent-danger/20 text-accent-danger rounded transition-colors"
                                    >
                                        <Trash2 className="w-3 h-3" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
});

function App() {
    const [messages, setMessages] = useState([]);
    const [sessions, setSessions] = useState([]);
    const [currentSessionId, setCurrentSessionId] = useState(null);
    const [telemetry, setTelemetry] = useTelemetry(TELEMETRY_WS);

    // --- Responsive Scaling Logic ---
    const [scale, setScale] = useState(1);
    useEffect(() => {
        const handleResize = () => {
            // Target Base Resolution: 1920x1080 (HD Standard)
            // The UI is designed for this resolution.
            // We scale it down/up to fit the actual window ensuring everything remains visible.
            const targetW = 1920;
            const targetH = 1080;

            const scaleW = window.innerWidth / targetW;
            const scaleH = window.innerHeight / targetH;

            // "Contain" fit strategy
            const newScale = Math.min(scaleW, scaleH);
            setScale(newScale);
        };

        window.addEventListener('resize', handleResize);
        handleResize();
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    // --- Sidebar Resize Logic ---
    const [sidebarWidth, setSidebarWidth] = useState(400);
    const [sidebar2Width, setSidebar2Width] = useState(380);
    const isResizing = useRef(null); // null, 'sidebar1', or 'sidebar2'

    useEffect(() => {
        const handleMouseMove = (e) => {
            if (!isResizing.current) return;
            // Adjust delta by scale factor to ensure 1:1 mouse tracking
            const delta = e.movementX / scale;
            if (isResizing.current === 'sidebar1') {
                setSidebarWidth(prev => Math.max(240, Math.min(600, prev + delta)));
            } else if (isResizing.current === 'sidebar2') {
                setSidebar2Width(prev => Math.max(300, Math.min(600, prev + delta)));
            }
        };
        const handleMouseUp = () => {
            isResizing.current = null;
            document.body.style.cursor = 'default';
        };

        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('mouseup', handleMouseUp);
        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        };
    }, [scale]);
    const [inputText, setInputText] = useState('');
    const [isListening, setIsListening] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [visionActive, setVisionActive] = useState(false);
    const [monitors, setMonitors] = useState({
        left_hemisphere: "Standby...",
        right_hemisphere: "Standby..."
    });
    const [logs, setLogs] = useState([]);
    const [thoughtStream, setThoughtStream] = useState([]);
    const [lightboxImage, setLightboxImage] = useState(null);
    const [showStatus, setShowStatus] = useState(true);
    const [activePage, setActivePage] = useState('main');
    const [systemStatus, setSystemStatus] = useState({ loading_phase: "INITIALIZING", checks: {} });
    const [sttHealth, setSttHealth] = useState({ available: false, model_loaded: false, running: false, last_error: null });
    const [trackingEnabled, setTrackingEnabled] = useState(true);
    const [zoomEnabled, setZoomEnabled] = useState(true);
    const [modelStatus, setModelStatus] = useState(null);
    const { skeleton: rtSkeleton, connected: skeletonWsConnected } = useSkeletonWebSocket(visionActive);
    const [skeletonMode, setSkeletonMode] = useState('overlay'); // 'overlay' or '3D'
    const [avatarActive, setAvatarActive] = useState(false);
    const [selectedAvatar, setSelectedAvatar] = useState('wireframe');
    const [currentExpression, setCurrentExpression] = useState('NEUTRAL');
    const [isTalking, setIsTalking] = useState(false);

    // Client-Side Gesture Detection (Low Latency)
    useEffect(() => {
        if (!rtSkeleton || !rtSkeleton.joints) return;

        const joints = rtSkeleton.joints;
        const head = joints['HEAD'];
        const handR = joints['HAND_RIGHT'];
        const handL = joints['HAND_LEFT'];

        // Simple Wave Detection: Hand above Head
        let newExpression = 'NEUTRAL';

        if (head && head.state === 2) {
            if ((handR && handR.state === 2 && handR.y > head.y) ||
                (handL && handL.state === 2 && handL.y > head.y)) {
                newExpression = 'HAPPY'; // Waving triggers Happy/Greeting
            }
        }

        // Only update if changed (debounce slightly if needed, but react fast for now)
        if (newExpression !== currentExpression) {
            setCurrentExpression(newExpression);
        }
    }, [rtSkeleton, currentExpression]);


    // Devices - Initialize from localStorage for persistence
    const [devices, setDevices] = useState({ video: [], audio: [] });
    const [selectedCam, setSelectedCam] = useState(() => localStorage.getItem('impressioncore_selectedCam') || 'BRAIN_98');
    const [selectedCam2, setSelectedCam2] = useState(() => localStorage.getItem('impressioncore_selectedCam2') || '');
    const [selectedMic, setSelectedMic] = useState(() => localStorage.getItem('impressioncore_selectedMic') || '');

    // Face Recognition State
    const [faces, setFaces] = useState([]);
    const [isEnrolling, setIsEnrolling] = useState(false);
    const [enrollName, setEnrollName] = useState('');
    const [enrollRole, setEnrollRole] = useState('user');
    const [enrollStatus, setEnrollStatus] = useState(null);

    const fetchFaces = async () => {
        try {
            const res = await axios.get(`${API_BASE}/v1/vision/faces`);
            if (res.data.status === "OK") setFaces(res.data.faces);
        } catch (e) { console.error("Failed to fetch faces", e); }
    };

    useEffect(() => {
        fetchFaces();
        const interval = setInterval(fetchFaces, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleEnroll = async () => {
        if (!enrollName.trim()) return;
        setIsEnrolling(true);
        setEnrollStatus({ type: 'info', msg: 'Capturing Face...' });
        try {
            const res = await axios.post(`${API_BASE}/v1/vision/faces`, {
                name: enrollName,
                role: enrollRole
            });
            if (res.data.status === "OK") {
                setEnrollStatus({ type: 'success', msg: `Enrolled ${res.data.identity.name}` });
                setEnrollName('');
                fetchFaces();
                setTimeout(() => setEnrollStatus(null), 3000);
            }
        } catch (e) {
            setEnrollStatus({ type: 'error', msg: e.response?.data?.detail || 'Enrollment failed' });
        } finally {
            setIsEnrolling(false);
        }
    };

    const handleDeleteFace = async (id) => {
        if (!confirm("Are you sure you want to delete this identity?")) return;
        try {
            await axios.delete(`${API_BASE}/v1/vision/faces/${id}`);
            fetchFaces();
        } catch (e) { console.error("Delete failed", e); }
    };

    const handleAddSample = async (id) => {
        try {
            const res = await axios.post(`${API_BASE}/v1/vision/faces/${id}/train`);
            if (res.data.status === "OK") {
                addLog("FACE_REC", `Added training sample for identity ${id}. Total: ${res.data.embedding_count}`);
                fetchFaces();
            }
        } catch (e) {
            addLog("ERROR", `Failed to add sample: ${e.response?.data?.detail || e.message}`);
        }
    };

    const videoRef = useRef(null);
    const videoRef2 = useRef(null);
    const primaryStreamRef = useRef(null);
    const secondaryStreamRef = useRef(null);
    const canvasRef = useRef(null);
    const recognition = useRef(null);
    const inputRef = useRef(null);
    const messagesEndRef = useRef(null);
    const logsEndRef = useRef(null);

    // STT Audio Recording
    const mediaRecorder = useRef(null);
    const audioChunks = useRef([]);
    const [pendingAudioUrl, setPendingAudioUrl] = useState(null);
    const [visionActive2, setVisionActive2] = useState(false);
    const [refreshKey, setRefreshKey] = useState(0);

    // Stream Quality Presets: {quality, fps, scale}
    const STREAM_PRESETS = {
        'fast': { quality: 35, fps: 15, scale: 0.5, label: 'Fast (Low CPU)' },
        'balanced': { quality: 55, fps: 24, scale: 0.75, label: 'Balanced' },
        'quality': { quality: 75, fps: 30, scale: 1.0, label: 'Quality' },
        'max': { quality: 90, fps: 30, scale: 1.0, label: 'Maximum' },
    };
    const [streamPreset, setStreamPreset] = useState(() => localStorage.getItem('impressioncore_streamPreset') || 'balanced');
    const [showFps, setShowFps] = useState(() => localStorage.getItem('impressioncore_showFps') === 'true');

    // Persist stream preset
    useEffect(() => {
        localStorage.setItem('impressioncore_streamPreset', streamPreset);
    }, [streamPreset]);

    // Persist FPS toggle
    useEffect(() => {
        localStorage.setItem('impressioncore_showFps', showFps);
    }, [showFps]);

    // Build stream URL with quality params
    const getStreamUrl = (camId) => {
        const preset = STREAM_PRESETS[streamPreset] || STREAM_PRESETS.balanced;
        return `${STREAM_URL}?cam_id=${camId}&quality=${preset.quality}&fps=${preset.fps}&scale=${preset.scale}&t=${refreshKey}`;
    };

    // Initial load + Polling for Model Status
    useEffect(() => {
        const fetchModelStatus = async () => {
            try {
                const res = await axios.get(`${API_BASE}/v1/model/status`);
                setModelStatus(res.data);
            } catch (e) {
                console.error("Failed to fetch model status:", e);
            }
        };

        fetchModelStatus();
        const interval = setInterval(fetchModelStatus, 10000); // Poll every 10s
        return () => clearInterval(interval);
    }, []);

    // Polling for Telemetry
    useEffect(() => {
        const fetchTelemetry = async () => {
            try {
                const res = await axios.get(`${API_BASE}/v1/vision/telemetry`);
                setTelemetry(res.data);
            } catch (e) {
                console.error("Failed to fetch telemetry:", e);
            }
        };

        const interval = setInterval(fetchTelemetry, 1000); // Poll every 1s
        return () => clearInterval(interval);
    }, []);

    // Polling for System Status
    const fetchSystemStatus = async (forceRefresh = false) => {
        try {
            const res = await axios.get(`${API_BASE}/v1/system/status${forceRefresh ? '?refresh=true' : ''}`);
            setSystemStatus(res.data);

            // If we just finished a refresh, sync the device lists too
            if (forceRefresh) {
                refreshDevices();
            }
        } catch (e) {
            console.error("Failed to fetch system status:", e);
        }
    };

    useEffect(() => {
        fetchSystemStatus();
        const interval = setInterval(() => fetchSystemStatus(false), 2000); // Poll every 2s for responsive audit
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        const fetchSttHealth = async () => {
            try {
                const res = await axios.get(`${API_BASE}/v1/audio/status`);
                if (res?.data?.stt) {
                    setSttHealth(res.data.stt);
                }
            } catch (e) {
                setSttHealth(prev => ({ ...prev, available: false, model_loaded: false, running: false }));
            }
        };

        fetchSttHealth();
        const interval = setInterval(fetchSttHealth, 3000);
        return () => clearInterval(interval);
    }, []);

    // Trigger hardware re-probe when Audit screen is opened manually
    useEffect(() => {
        if (showStatus) {
            addLog("SYSTEM", "Initiating Deep Hardware Re-probe...");
            fetchSystemStatus(true);
        }
    }, [showStatus]);

    // Note: Auto-close removed - audit now requires all checks to pass OR explicit user acknowledgment
    // The INITIALIZE SYSTEM button handles closing when canProceed is true

    // Polling for Backend Logs
    useEffect(() => {
        const fetchBackendLogs = async () => {
            try {
                const res = await axios.get(`${API_BASE}/v1/system/logs?limit=50`);
                if (res.data && Array.isArray(res.data)) {
                    const formattedLogs = res.data.map(entry =>
                        `[${entry.timestamp.split('T')[1].split('.')[0]}][${entry.component}] ${entry.message}`
                    );
                    setLogs(prev => {
                        // Merge and deduplicate (simple check for now)
                        const combined = [...formattedLogs, ...prev];
                        return Array.from(new Set(combined)).slice(0, 100);
                    });
                }
            } catch (e) {
                console.error("Failed to fetch backend logs:", e);
            }
        };

        const interval = setInterval(fetchBackendLogs, 2000); // Poll every 2s
        return () => clearInterval(interval);
    }, []);

    // Helper: Add Log
    const addLog = (source, message) => {
        setLogs(prev => [`[${new Date().toLocaleTimeString()}][${source}] ${message}`, ...prev].slice(0, 100));
    };

    // Helper: Refresh Hardware (Front + Backend)
    const refreshDevices = async () => {
        try {
            // 1. Frontend Devices
            const devs = await navigator.mediaDevices.enumerateDevices();
            let videoDevs = devs.filter(d => d.kind === 'videoinput');
            const audioDevs = devs.filter(d => d.kind === 'audioinput');

            // 2. Backend Devices (Vision Layer)
            try {
                const hwRes = await axios.get(HARDWARE_API);
                if (hwRes.data.status === "OK" && hwRes.data.detected_cameras) {
                    const backendCams = hwRes.data.detected_cameras.map(c => ({
                        deviceId: `BRAIN_${c.id}`,
                        label: `[Neural] ${c.model} [${c.backend}]`,
                        kind: 'videoinput',
                        vid_pid: c.vid_pid,
                        ptz: c.ptz_capabilities
                    }));
                    videoDevs = [...backendCams, ...videoDevs];
                    addLog("SYSTEM", `Backend Hardware: Found ${backendCams.length} AI cameras.`);
                }

                // 3. Backend Audio Devices (NEW)
                const audioRes = await axios.get(`${API_BASE}/v1/audio/devices`);
                if (audioRes.data.status === "OK" && audioRes.data.devices) {
                    const backendMics = audioRes.data.devices.map(d => ({
                        deviceId: `OS_MIC_${d.id}`,
                        label: `[System] ${d.name}`,
                        kind: 'audioinput'
                    }));
                    setDevices(prev => ({ ...prev, video: videoDevs, audio: [...backendMics, ...prev.audio] }));
                    addLog("SYSTEM", `Backend Audio: Found ${backendMics.length} system microphones.`);
                }
            } catch (backendErr) {
                addLog("SYSTEM", `Backend Hardware Scan Failed: ${backendErr.message}`);
            }

            setDevices({ video: videoDevs, audio: audioDevs });
            addLog("SYSTEM", "Hardware Scan Complete.");

            // Smart Auto-Select: Validate existing selections
            const camIds = videoDevs.map(d => d.deviceId);

            // Validate Primary
            if (!selectedCam || !camIds.includes(selectedCam)) {
                if (videoDevs.length > 0) {
                    addLog("SYSTEM", `Auto-selecting primary camera: ${videoDevs[0].label}`);
                    setSelectedCam(videoDevs[0].deviceId);
                } else {
                    setSelectedCam('');
                }
            }

            // Validate Secondary (only if invalid)
            if (selectedCam2 && !camIds.includes(selectedCam2)) {
                addLog("SYSTEM", `Secondary camera ${selectedCam2.slice(0, 8)} lost. Resetting.`);
                setSelectedCam2('');
            }
            // [REMOVED] Auto-fill secondary logic to respect user preference for 'None' by default

            setRefreshKey(prev => prev + 1);

        } catch (e) {
            addLog("SYSTEM", `Hardware Scan Failed: ${e.message}`);
        }
    };

    const fetchSessions = async () => {
        try {
            const res = await axios.get(SESSIONS_API);
            setSessions(res.data);
        } catch (e) {
            addLog("SYSTEM", "Failed to fetch sessions.");
        }
    };

    useEffect(() => {
        refreshDevices();
        fetchSessions();
    }, []);

    // Persist selections to localStorage
    useEffect(() => {
        if (selectedCam) localStorage.setItem('impressioncore_selectedCam', selectedCam);
    }, [selectedCam]);

    useEffect(() => {
        if (selectedCam2) localStorage.setItem('impressioncore_selectedCam2', selectedCam2);
    }, [selectedCam2]);

    useEffect(() => {
        if (selectedMic) localStorage.setItem('impressioncore_selectedMic', selectedMic);
    }, [selectedMic]);

    // Initialize Camera
    useEffect(() => {
        async function startCamera() {
            if (!selectedCam) return;
            addLog("VISION", `Switching Camera ID: ${selectedCam.slice(0, 8)}...`);
            try {
                if (videoRef.current && videoRef.current.srcObject) {
                    const tracks = videoRef.current.srcObject.getTracks();
                    tracks.forEach(t => t.stop());
                }

                if (selectedCam.startsWith("BRAIN_")) {
                    const brainId = selectedCam.replace("BRAIN_", "");
                    setVisionActive(true);

                    // Sync backend context
                    try {
                        await axios.post(`${API_BASE}/v1/vision/active_camera`, { cam_id: brainId });
                        addLog("VISION", `Backend context synced to camera ${brainId}`);
                    } catch (e) {
                        addLog("VISION", `Backend sync failed: ${e.message}`);
                    }

                    addLog("VISION", "Neural Sense Active: AI is seeing directly via Backend.");
                    if (videoRef.current) videoRef.current.srcObject = null;
                    return;
                }

                const stream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        deviceId: { exact: selectedCam },
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    }
                });
                primaryStreamRef.current = stream;

                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                    videoRef.current.onloadedmetadata = () => {
                        videoRef.current.play().catch(e => addLog("VISION", `Auto-play failed: ${e.message}`));
                    };
                }
                setVisionActive(true);
                addLog("VISION", `Stream Started: ${selectedCam.slice(0, 8)} `);
            } catch (e) {
                setVisionActive(false);
                addLog("VISION", `Camera Start Failed: ${e.message} `);
                console.error("Camera Error:", e);
            }
        }
        startCamera();
    }, [selectedCam]);

    // Initialize Camera 2
    useEffect(() => {
        async function startCamera2() {
            if (!selectedCam2) return;
            addLog("VISION", `Switching Secondary Camera ID: ${selectedCam2.slice(0, 8)}...`);
            try {
                if (videoRef2.current && videoRef2.current.srcObject) {
                    const tracks = videoRef2.current.srcObject.getTracks();
                    tracks.forEach(t => t.stop());
                }

                if (selectedCam2.startsWith("BRAIN_")) {
                    const brainId = selectedCam2.replace("BRAIN_", "");
                    setVisionActive2(true);
                    try {
                        await axios.post(`${API_BASE}/v1/vision/active_camera2`, { cam_id: brainId });
                    } catch (e) { }
                    if (videoRef2.current) videoRef2.current.srcObject = null;
                    return;
                }

                const stream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        deviceId: { exact: selectedCam2 },
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    }
                });
                secondaryStreamRef.current = stream;

                if (videoRef2.current) {
                    videoRef2.current.srcObject = stream;
                    videoRef2.current.onloadedmetadata = () => {
                        videoRef2.current.play().catch(e => addLog("VISION", `Auto-play 2 failed: ${e.message}`));
                    };
                }
                setVisionActive2(true);
            } catch (e) {
                setVisionActive2(false);
                addLog("VISION", `Camera 2 Start Failed: ${e.message} `);
            }
        }
        startCamera2();
    }, [selectedCam2]);

    // Ensure video streams stay attached across re-renders
    useEffect(() => {
        if (videoRef.current && primaryStreamRef.current && videoRef.current.srcObject !== primaryStreamRef.current) {
            videoRef.current.srcObject = primaryStreamRef.current;
        }
        if (videoRef2.current && secondaryStreamRef.current && videoRef2.current.srcObject !== secondaryStreamRef.current) {
            videoRef2.current.srcObject = secondaryStreamRef.current;
        }
    });

    // Local STT: Connect to SSE Stream
    useEffect(() => {
        const evtSource = new EventSource(`${API_BASE}/v1/audio/stt_stream`);

        evtSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.text) {
                    addLog("AUDIO", `Local STT: "${data.text}"`);
                    setInputText(prev => prev ? `${prev} ${data.text}` : data.text);
                    // focus input check logic implied
                }
            } catch (e) {
                console.error("STT Parse Error:", e);
            }
        };

        evtSource.onerror = (err) => {
            // console.error("EventSource failed:", err);
            // Reconnect logic handled by browser usually, but silent fail is fine for now
        };

        return () => evtSource.close();
    }, []);

    const toggleVoice = async () => {
        console.log("[DEBUG] toggleVoice called, isListening:", isListening);
        // Toggle Local Listener
        const newState = !isListening;
        try {
            console.log("[DEBUG] Posting to /v1/audio/listen with enabled:", newState);
            const res = await axios.post(`${API_BASE}/v1/audio/listen`, { enabled: newState });
            if (res.data.status === "OK") {
                setIsListening(newState);
                addLog("AUDIO", newState ? "Local Ears OPEN (Listening...)" : "Local Ears CLOSED.");
            }
        } catch (e) {
            addLog("AUDIO", `Toggle Failed: ${e.message}`);
        }

        // Note: For Phase 1, we are NOT doing the browser MediaRecorder logic anymore
        // because the backend handles the microphone directly via sounddevice.
    };

    const captureFrames = () => {
        let snapshots = [];
        addLog("DEBUG", "Initiating Snapshot Capture...");

        // Capture Primary (Alpha)
        if (videoRef.current && canvasRef.current && visionActive) {
            try {
                const context = canvasRef.current.getContext('2d');
                canvasRef.current.width = videoRef.current.videoWidth;
                canvasRef.current.height = videoRef.current.videoHeight;
                context.drawImage(videoRef.current, 0, 0);
                const dataUrl = canvasRef.current.toDataURL('image/jpeg', 0.8);
                snapshots.push(dataUrl);
                addLog("DEBUG", `Captured Primary Snapshot: ${dataUrl.length} bytes`);
            } catch (e) {
                console.error("Snapshot Alpha failed", e);
                addLog("ERROR", `Snapshot Alpha failed: ${e.message}`);
            }
        }

        // Capture Secondary (Beta)
        if (videoRef2.current && canvasRef.current && visionActive2) {
            try {
                const context = canvasRef.current.getContext('2d');
                canvasRef.current.width = videoRef2.current.videoWidth;
                canvasRef.current.height = videoRef2.current.videoHeight;
                context.drawImage(videoRef2.current, 0, 0);
                const dataUrl = canvasRef.current.toDataURL('image/jpeg', 0.8);
                snapshots.push(dataUrl);
                addLog("DEBUG", `Captured Secondary Snapshot: ${dataUrl.length} bytes`);
            } catch (e) {
                console.error("Snapshot Beta failed", e);
                addLog("ERROR", `Snapshot Beta failed: ${e.message}`);
            }
        }

        return snapshots;
    };

    const handleSend = async (textOverride = null) => {
        const text = textOverride || inputText;
        if (!text.trim()) return;

        // Attach pending STT audio to user message if available
        const userAudio = pendingAudioUrl;
        setPendingAudioUrl(null); // Clear for next message

        const userMsg = { role: 'user', content: text, timestamp: new Date(), audio_url: userAudio };
        setMessages(prev => [...prev, userMsg]);
        setInputText('');
        setIsProcessing(true);
        addLog("NEXUS", `Sending: "${text.substring(0, 15)}..."`);

        try {
            const snapshots = captureFrames();
            // Legacy support: use first snapshot as primary image_base64
            const primaryImage = snapshots.length > 0 ? snapshots[0] : null;

            let sessionId = currentSessionId;
            if (!sessionId) {
                // Auto-create session on first send if none active
                const sRes = await axios.post(SESSIONS_API);
                // Handle raw string response (UUID) vs Object
                sessionId = (typeof sRes.data === 'string') ? sRes.data : sRes.data.id;
                setCurrentSessionId(sessionId);
                addLog("SYSTEM", `New Session Created: ${sessionId.slice(0, 8)}`);
            }

            const payload = {
                prompt: text,
                voice_enabled: true,
                image_base64: primaryImage, // For backwards compatibility
                snapshots: snapshots,       // New multi-image support
                session_id: sessionId,
                user_audio_url: userAudio  // Send STT audio URL for session persistence
            };

            const response = await axios.post(API_URL, payload);

            const { response: botText, monitors: newMonitors, audio_url, snapshot_url, snapshot_urls, affective_state } = response.data;

            if (affective_state) setCurrentExpression(affective_state);
            setMonitors(newMonitors);
            addLog("NEXUS", `Response Received: ${botText.substring(0, 20)}...`);
            fetchSessions();

            if (snapshot_url || (snapshot_urls && snapshot_urls.length > 0)) {
                const fullSnapshotUrl = snapshot_url ? `${API_BASE}${snapshot_url}` : null;
                const fullSnapshotUrls = (snapshot_urls || []).map(url => `${API_BASE}${url}`);

                setMessages(prev => prev.map((m, i) =>
                    i === prev.length - 1 ? {
                        ...m,
                        snapshot_url: fullSnapshotUrl,
                        snapshot_urls: fullSnapshotUrls
                    } : m
                ));
            }

            const audioFullUrl = audio_url ? `${API_BASE}${audio_url}?t=${new Date().getTime()}` : null;
            const botMsg = {
                role: 'assistant',
                content: botText,
                timestamp: new Date(),
                audio_url: audioFullUrl,
                affective_state: affective_state,
                // AI-Generated images (from model) live here. 
                // Sensory snapshots (from cameras) live on the User message.
                generated_image_url: response.data.generated_image_url ? `${API_BASE}${response.data.generated_image_url}` : null
            };
            setMessages(prev => [...prev, botMsg]);

            if (response.data.nexus_logs) {
                setThoughtStream(prev => [...prev.slice(-49), ...response.data.nexus_logs]);
            }

            if (audio_url) {
                const timestamp = new Date().getTime();
                const fullUrl = `${API_BASE}${audio_url}?t=${timestamp}`;
                addLog("AUDIO", `Buffering Audio...`);
                const audio = new Audio(fullUrl);
                audio.oncanplaythrough = () => {
                    addLog("AUDIO", "Playing Audio.");
                    audio.play().catch(e => addLog("AUDIO", `Play Error: ${e.message}`));
                };
                audio.onerror = (e) => addLog("AUDIO", `Load Error: ${e.message}`);
            }

        } catch (error) {
            console.error("Error:", error);
            addLog("SYSTEM", `API Error: ${error.message}`);
            const errorMsg = { role: 'system', content: `Error: ${error.message}`, timestamp: new Date() };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsProcessing(false);
        }
    };

    const cycleCameraMode = async () => {
        if (!selectedCam.startsWith("BRAIN_")) return;
        const brainId = selectedCam.replace("BRAIN_", "");
        addLog("VISION", `Cycling Mode for Camera ${brainId}...`);
        try {
            const res = await axios.post(`${API_BASE}/v1/vision/camera_mode`, { cam_id: brainId });
            if (res.data.status === "OK") {
                addLog("VISION", `Camera mode changed to: ${res.data.new_mode}`);
                setVisionActive(false);
                setTimeout(() => setVisionActive(true), 100);
            }
        } catch (e) {
            addLog("VISION", `Mode switch failed: ${e.message}`);
        }
    };

    const cycleCameraMode2 = async () => {
        if (!selectedCam2.startsWith("BRAIN_")) return;
        const brainId = selectedCam2.replace("BRAIN_", "");
        addLog("VISION", `Cycling Mode for Secondary Camera ${brainId}...`);
        try {
            const res = await axios.post(`${API_BASE}/v1/vision/camera_mode`, { cam_id: brainId });
            if (res.data.status === "OK") {
                addLog("VISION", `Secondary Camera mode changed to: ${res.data.new_mode}`);
                setVisionActive2(false);
                setTimeout(() => setVisionActive2(true), 100);
            }
        } catch (e) {
            addLog("VISION", `Secondary mode switch failed: ${e.message}`);
        }
    };

    const toggleTrackingFeature = async (feature) => {
        const newTracking = feature === 'tracking' ? !trackingEnabled : trackingEnabled;
        const newZoom = feature === 'zoom' ? !zoomEnabled : zoomEnabled;

        try {
            const res = await axios.post(`${API_BASE}/v1/vision/tracking`, {
                enabled: newTracking,
                zoom: newZoom
            });
            if (res.data.status === "OK") {
                setTrackingEnabled(res.data.enabled);
                setZoomEnabled(res.data.zoom_enabled);
                addLog("VISION", `Feature Update -> Tracking: ${res.data.enabled ? 'ON' : 'OFF'}, Zoom: ${res.data.zoom_enabled ? 'ON' : 'OFF'}`);
            }
        } catch (e) {
            addLog("VISION", `Toggle failed: ${e.message}`);
        }
    };

    const handleNewChat = () => {
        setCurrentSessionId(null);
        setMessages([{
            role: 'assistant',
            content: 'Brand new neural pathway initialized. Detection active.',
            timestamp: new Date()
        }]);
        addLog("SYSTEM", "Starting New Chat Session.");
    };

    const handleSwitchSession = async (id) => {
        setIsProcessing(true);
        addLog("SYSTEM", `Loading Session: ${id.slice(0, 8)}...`);
        try {
            const res = await axios.get(`${SESSIONS_API}/${id}`);
            const loadedMsgs = res.data.messages.map(m => {
                // Prefix audio_url and snapshot_url with backend URL if they are relative paths
                let audio_url = m.audio_url;
                let snapshot_url = m.snapshot_url;

                if (audio_url && !audio_url.startsWith('http')) {
                    audio_url = `${API_BASE}${audio_url}`;
                }
                if (snapshot_url && !snapshot_url.startsWith('http')) {
                    snapshot_url = `${API_BASE}${snapshot_url}`;
                }

                return {
                    ...m,
                    timestamp: new Date(m.timestamp),
                    audio_url,
                    snapshot_url
                };
            });
            setMessages(loadedMsgs);
            setCurrentSessionId(id);
            addLog("SYSTEM", "Session Loaded Successfully.");
        } catch (e) {
            addLog("SYSTEM", `Load Failed: ${e.message}`);
        } finally {
            setIsProcessing(false);
        }
    };

    const handleDeleteSession = async (e, id) => {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }
        if (!window.confirm("Are you sure you want to delete this neural pathway? This action is irreversible.")) return;

        addLog("SYSTEM", `DELETING SESSION [${id.slice(0, 8)}]...`);
        try {
            const resp = await axios.delete(`${SESSIONS_API}/${id}`);
            addLog("SYSTEM", `Server Response: ${resp.data.status}`);

            // Critical: Update state immediately
            setSessions(prev => prev.filter(s => s.id !== id));

            if (currentSessionId === id) {
                handleNewChat();
            }
            addLog("SYSTEM", `Session ${id.slice(0, 8)} removed from archive.`);
        } catch (err) {
            addLog("SYSTEM", `Deletion Failed: ${err.response?.data?.detail || err.message}`);
            console.error("Delete Error:", err);
        }
    };

    const hasPrimaryVisionFeed = selectedCam?.startsWith("BRAIN_") && visionActive;
    const hasSecondaryVisionFeed = selectedCam2?.startsWith("BRAIN_") && visionActive2;

    return (
        <div className="fixed inset-0 bg-black flex items-center justify-center overflow-hidden">
            {/* Global Scaler: Renders UI at 1920x1080 then scales to window */}
            <div
                style={{
                    width: 1920,
                    height: 1080,
                    transform: `scale(${scale})`,
                }}
                className="flex flex-col shrink-0 bg-black text-txt-primary font-sans selection:bg-accent-cyan/30 selection:text-cyan-100 overflow-hidden shadow-2xl origin-center"
            >
                {/* Agent0Core Command Center - Top of Page */}
                <div className="w-full border-b border-accent-cyan/50 bg-ic-bg/90 backdrop-blur shrink-0">
                    <IntelligencePanel status={modelStatus} />
                    <div className="flex justify-end px-4 pb-3">
                        <button
                            onClick={() => setActivePage(activePage === 'main' ? 'config' : 'main')}
                            className="px-3 py-1.5 bg-accent-indigo/20 hover:bg-accent-indigo/40 text-accent-indigo text-[10px] font-bold rounded-lg border border-accent-indigo/30 transition-all flex items-center gap-2 uppercase tracking-wider"
                        >
                            <Settings className="w-3 h-3" /> {activePage === 'main' ? 'Configuration' : 'Back To Main'}
                        </button>
                    </div>
                </div>

                {/* Main Content Row */}
                <div className="flex flex-1 min-h-0 overflow-hidden">
                    <div className={cn("flex h-full shrink-0", activePage !== 'config' && "hidden")}>
                        {/* Left Sidebar: Vision & Hardware Controls */}
                        <div
                            style={{ width: sidebarWidth }}
                            className="shrink-0 h-full border-r border-accent-cyan/50 flex flex-col bg-ic-bg/80 backdrop-blur relative transition-[width] duration-0 ease-linear"
                        >
                            {/* Resizer Handle */}
                            <div
                                className="absolute top-0 -right-1 w-2 h-full cursor-col-resize z-50 hover:bg-accent-cyan/20 active:bg-accent-cyan/50 transition-colors"
                                onMouseDown={() => {
                                    isResizing.current = 'sidebar1';
                                    document.body.style.cursor = 'col-resize';
                                }}
                            />

                            <div className="p-4 border-b border-accent-cyan/30 flex items-center gap-3 bg-black/40">
                                <div className="relative">
                                    <div className="w-8 h-8 rounded bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.5)]">
                                        <BrainCircuit className="text-white w-5 h-5" />
                                    </div>
                                    <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-accent-success rounded-full border-2 border-black animate-pulse" />
                                </div>
                                <div>
                                    <h1 className="font-bold text-lg tracking-tight text-white leading-none">
                                        Impression<span className="text-accent-cyan">Core</span>
                                    </h1>
                                    <div className="flex items-center gap-1.5 mt-0.5">
                                        <span className="text-[9px] uppercase tracking-widest text-cyan-600 font-bold bg-cyan-950/50 px-1 rounded border border-accent-cyan/30">
                                            {systemStatus.loading_phase === "READY" ? "Neural Link Active" : systemStatus.loading_phase}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div className="px-4 py-2 border-b border-accent-cyan/20 flex flex-col gap-2 bg-black/20">
                                <button
                                    onClick={() => setShowStatus(true)}
                                    className="w-full py-1.5 bg-ic-card/40 hover:bg-ic-hover/60 text-[9px] text-txt-primary rounded border border-ic-border/50 flex items-center justify-center gap-2 transition-all uppercase tracking-widest font-bold"
                                >
                                    <Activity className="w-3 h-3 text-accent-cyan" /> Run System Audit
                                </button>

                                <button
                                    onClick={async () => {
                                        if (confirm("SYSTEM HALT SEQUENCE\n\nThis will physically power down sensory arrays (Cameras/Mics), unload AI models from VRAM, and terminate the Neural Engine.\n\nAre you sure?")) {
                                            try {
                                                addLog("CRITICAL", "INITIATING SYSTEM SHUTDOWN SEQUENCE...");
                                                await axios.post(`${API_BASE}/v1/system/shutdown`);
                                                setTimeout(() => {
                                                    document.body.innerHTML = "<div style='display:flex;height:100vh;background:black;color:red;align-items:center;justify-content:center;font-family:monospace;font-size:24px'>SYSTEM OFFLINE</div>";
                                                    window.close();
                                                }, 2000);
                                            } catch (e) {
                                                addLog("ERROR", `Shutdown failed: ${e.message}`);
                                            }
                                        }
                                    }}
                                    className="w-full py-1.5 bg-red-950/20 hover:bg-accent-danger/40 text-[9px] text-accent-danger/80 rounded border border-accent-danger/30 flex items-center justify-center gap-2 transition-all uppercase tracking-widest font-bold"
                                >
                                    <Zap className="w-3 h-3 text-accent-danger" /> System Shutdown
                                </button>
                            </div>

                            <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar p-4 flex flex-col gap-4 select-none">
                                {/* IntelligencePanel moved to page top */}

                                {/* Device Selectors */}
                                <div className="flex flex-col gap-2 bg-ic-surface/80 p-2 rounded border border-ic-border shrink-0">
                                    <div className="flex justify-between items-center">
                                        <h3 className="text-[10px] text-txt-secondary uppercase tracking-wider flex items-center gap-2">
                                            <Settings className="w-3 h-3" /> Hardware Configuration
                                        </h3>
                                        <button
                                            onClick={async () => {
                                                addLog("SYSTEM", "Requesting Hardware Hot-Swap...");
                                                try {
                                                    await axios.post(`${API_BASE}/v1/hardware/refresh`);
                                                    await refreshDevices();
                                                    addLog("SUCCESS", "Hardware Hot-Swap Complete.");
                                                } catch (e) {
                                                    addLog("ERROR", `Hot-Swap Failed: ${e.message}`);
                                                }
                                            }}
                                            className="text-[9px] bg-accent-cyan/40 hover:bg-cyan-700/50 px-2 py-0.5 rounded border border-cyan-800 transition-colors"
                                        >
                                            Refresh
                                        </button>
                                    </div>

                                    <div className="flex flex-col gap-1">
                                        <label className="text-[10px] text-accent-cyan font-bold uppercase tracking-wider flex justify-between">
                                            Primary Camera
                                            {selectedCam && (selectedCam.includes('106') || selectedCam.includes('IR')) &&
                                                <span className="text-[9px] text-accent-danger bg-accent-danger/30 px-1 rounded border border-accent-danger animate-pulse">IR NIGHT VISION</span>
                                            }
                                        </label>
                                        <select
                                            value={selectedCam}
                                            onChange={e => setSelectedCam(e.target.value)}
                                            className="bg-ic-bg border border-accent-cyan/50 text-xs text-cyan-100 rounded p-2 focus:border-accent-cyan outline-none shadow-[0_0_10px_rgba(6,182,212,0.2)] font-bold mb-2"
                                        >
                                            {devices.video.length === 0 && <option value="">No Cameras Found</option>}
                                            {devices.video.map(d => (
                                                <option key={d.deviceId} value={d.deviceId}>{d.label || `Camera ${d.deviceId.slice(0, 5)}`}</option>
                                            ))}
                                        </select>
                                    </div>

                                    <div className="flex flex-col gap-1">
                                        <label className="text-[10px] text-cyan-700">Secondary Camera</label>
                                        <select value={selectedCam2} onChange={e => setSelectedCam2(e.target.value)} className="bg-black border border-accent-cyan/50 text-xs text-cyan-100 rounded p-1 focus:border-accent-cyan outline-none">
                                            <option value="">None</option>
                                            {devices.video.map(d => (
                                                <option key={d.deviceId} value={d.deviceId}>{d.label || `Camera ${d.deviceId.slice(0, 5)}`}</option>
                                            ))}
                                        </select>
                                    </div>

                                    <div className="flex flex-col gap-1">
                                        <label className="text-[10px] text-cyan-700">Microphone Input</label>
                                        <select value={selectedMic} onChange={e => setSelectedMic(e.target.value)} className="bg-black border border-accent-cyan/50 text-xs text-cyan-100 rounded p-1 focus:border-accent-cyan outline-none">
                                            {devices.audio.length === 0 && <option value="">No Microphones Found</option>}
                                            {devices.audio.map(d => (
                                                <option key={d.deviceId} value={d.deviceId}>{d.label || `Mic ${d.deviceId.slice(0, 5)}`}</option>
                                            ))}
                                        </select>
                                        <div className="text-[9px] text-txt-secondary italic">* Web Speech API selection is browser-dependent.</div>
                                    </div>

                                    <div className="mt-2 border-t border-ic-border pt-2">
                                        <button
                                            onClick={async () => {
                                                try {
                                                    addLog("DIAGNOSTIC", "Initiating Deep Sensory Integrity Scan...");
                                                    const res = await axios.get(`${API_BASE}/v1/system/verify`);

                                                    if (res.data.status === "SECURE") {
                                                        addLog("SUCCESS", `Integrity Verified: Neural Core ${res.data.checks.neural_core}, Vision ${res.data.checks.vision_layer}.`);
                                                        addLog("SUCCESS", "Sensory Interface: SECURE (All systems normal).");
                                                    } else {
                                                        addLog("WARNING", `Integrity DEGRADED: Check drivers or VRAM.`);
                                                        if (res.data.checks.driver_conflicts === false) {
                                                            addLog("CRITICAL", "DRIVER CONFLICT: QuickCam Orbit (Interface 0) detected on LibUSB.");
                                                        }
                                                    }

                                                    setDebugConsole(res); // Show full report in console
                                                    refreshDevices();
                                                } catch (e) {
                                                    addLog("DIAGNOSTIC", `Failed to reach backend verify module: ${e.message}`);
                                                }
                                            }}
                                            className="w-full text-[9px] bg-accent-cyan/20 hover:bg-accent-cyan/40 border border-cyan-800/50 p-1.5 rounded flex items-center justify-center gap-1 uppercase tracking-tighter transition-all"
                                        >
                                            <ShieldCheck className="w-3 h-3 text-accent-cyan" /> Verify Interface Integrity
                                        </button>
                                    </div>


                                </div>

                                <FaceManagementPanel
                                    faces={faces}
                                    onEnroll={handleEnroll}
                                    onDelete={handleDeleteFace}
                                    onAddSample={handleAddSample}
                                    enrollName={enrollName}
                                    setEnrollName={setEnrollName}
                                    enrollRole={enrollRole}
                                    setEnrollRole={setEnrollRole}
                                    isEnrolling={isEnrolling}
                                    enrollStatus={enrollStatus}
                                />

                                {/* IntelligencePanel moved to top */}

                                {/* System Logs */}
                                <div className="h-96 bg-black/40 rounded border border-ic-border p-2 overflow-hidden flex flex-col shrink-0">
                                    <h3 className="text-[10px] text-txt-secondary mb-2 flex items-center gap-2 uppercase tracking-wider"><ScrollText className="w-3 h-3" /> System Logs</h3>
                                    <div className="flex-1 overflow-y-auto font-mono text-[10px] text-txt-secondary space-y-1 select-text custom-scrollbar">
                                        {logs.map((log, i) => (
                                            <div key={i} className="break-all border-b border-white/5 pb-1 last:border-0">{log}</div>
                                        ))}
                                        <div ref={logsEndRef} />
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Second Left Sidebar: Real-time Analytics & Sensory Data */}
                        <div
                            style={{ width: sidebar2Width }}
                            className="shrink-0 h-full border-r border-accent-cyan/50 flex flex-col bg-ic-bg/40 backdrop-blur relative transition-[width] duration-0 ease-linear"
                        >
                            {/* Resizer Handle */}
                            <div
                                className="absolute top-0 -right-1 w-2 h-full cursor-col-resize z-50 hover:bg-accent-cyan/20 active:bg-accent-cyan/50 transition-colors"
                                onMouseDown={() => {
                                    isResizing.current = 'sidebar2';
                                    document.body.style.cursor = 'col-resize';
                                }}
                            />

                            <div className="p-4 border-b border-accent-cyan/10 flex items-center gap-3 bg-black/20">
                                <Activity className="w-5 h-5 text-accent-cyan" />
                                <h2 className="font-bold text-xs uppercase tracking-widest text-txt-secondary">Sensory Analytics</h2>
                            </div>

                            <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar p-4 flex flex-col gap-4 select-none">
                                <AudioPanel telemetry={telemetry} />
                                <OrbosVisionTrackingSystem
                                    telemetry={telemetry}
                                    trackingEnabled={trackingEnabled}
                                    zoomEnabled={zoomEnabled}
                                    toggleTrackingFeature={toggleTrackingFeature}
                                    fetchSystemStatus={fetchSystemStatus}
                                    devices={devices}
                                    activeCamId={selectedCam}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Middle: Main Chat Area */}
                    <div className={cn(
                        "flex-1 flex flex-col relative bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-ic-surface to-black overflow-hidden",
                        activePage !== 'main' && "hidden"
                    )}>

                        {/* Visual Sensory Header (Relocated) */}
                        <div className="flex gap-4 p-4 border-b border-accent-cyan/30 bg-black/40 backdrop-blur shrink-0 overflow-x-auto overflow-y-hidden custom-scrollbar min-h-[180px] resize-y">
                            {/* Primary Feed (Alpha) */}
                            <div className="flex-1 min-w-[300px] flex flex-col gap-1">
                                <div className="flex items-center justify-between w-full">
                                    <div className="flex items-center gap-2">
                                        <div className={cn("w-2 h-2 rounded-full", visionActive ? "bg-accent-success animate-pulse" : "bg-accent-danger")} />
                                        <h3 className="text-[10px] text-cyan-600 uppercase tracking-wider font-bold">Vision Alpha</h3>
                                    </div>
                                    {/* Stream Quality Selector */}
                                    <div className="flex items-center gap-1.5">
                                        <button
                                            onClick={() => setShowFps(prev => !prev)}
                                            className={cn(
                                                "text-[8px] font-bold uppercase px-1.5 py-0.5 rounded border transition-colors",
                                                showFps
                                                    ? "bg-accent-success/30 text-accent-success border-accent-success/50"
                                                    : "bg-black/60 text-txt-secondary border-ic-border/50 hover:text-accent-cyan"
                                            )}
                                            title="Toggle FPS Counter"
                                        >
                                            FPS
                                        </button>
                                        <select
                                            value={streamPreset}
                                            onChange={(e) => setStreamPreset(e.target.value)}
                                            className="bg-black/80 text-[9px] text-accent-cyan border border-accent-cyan/50 rounded px-1.5 py-0.5 outline-none focus:border-accent-cyan"
                                            title="Stream Quality"
                                        >
                                            {Object.entries(STREAM_PRESETS).map(([key, preset]) => (
                                                <option key={key} value={key}>{preset.label}</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>
                                <div className="relative rounded-lg overflow-hidden border border-cyan-800 bg-black h-full aspect-video mx-auto shadow-lg shadow-accent-cyan/20">
                                    {hasPrimaryVisionFeed ? (
                                        <div className="w-full h-full relative group">
                                            <img
                                                src={getStreamUrl(selectedCam.replace("BRAIN_", ""))}
                                                alt="Neural Vision Stream"
                                                className="w-full h-full object-cover"
                                            />

                                            {/* Dynamic Video Overlay */}
                                            <VideoOverlay
                                                detections={telemetry?.detections}
                                                camLabel={["VisionAlpha", selectedCam.replace("BRAIN_", "")]}
                                                color="emerald"
                                                metadata={{
                                                    confidence: telemetry?.confidence,
                                                    targetLock: telemetry?.target_lock,
                                                    quality: telemetry?.quality
                                                }}
                                            />

                                            {/* Amethyst Skeleton Overlay (Real-Time via WebSocket) */}
                                            {(rtSkeleton || telemetry?.skeleton) && (
                                                <div className={cn(
                                                    "absolute inset-0 z-20",
                                                    skeletonMode === '3D' ? "bg-black/90 pointer-events-auto" : "pointer-events-none"
                                                )}>
                                                    <SkeletonVisualizer
                                                        skeleton={rtSkeleton || telemetry?.skeleton}
                                                        mode={skeletonMode}
                                                        showBadge={skeletonWsConnected}
                                                    />

                                                    {/* Mode Toggle Button */}
                                                    <button
                                                        onClick={() => setSkeletonMode(prev => prev === 'overlay' ? '3D' : 'overlay')}
                                                        className="absolute bottom-4 right-4 z-50 p-2 bg-cyan-950/80 border border-accent-cyan/50 rounded text-accent-cyan hover:bg-accent-cyan transition-colors shadow-lg pointer-events-auto"
                                                        title="Toggle Skeleton Mode"
                                                    >
                                                        <Layers className="w-4 h-4" />
                                                        <span className="text-[10px] ml-1 uppercase font-bold">{skeletonMode === 'overlay' ? "View 3D" : "View Overlay"}</span>
                                                    </button>
                                                </div>
                                            )}

                                            <div className="absolute inset-x-0 bottom-0 p-1 bg-black/60 text-[8px] text-accent-cyan opacity-0 group-hover:opacity-100 transition-opacity text-center pointer-events-none z-20">
                                                Primary Feed (Alpha)
                                            </div>

                                            {/* FPS Counter Overlay */}
                                            {showFps && (
                                                <div className="absolute top-1.5 left-1.5 z-40 pointer-events-none">
                                                    <div className="bg-black/80 backdrop-blur-sm border border-accent-success/30 rounded px-2 py-0.5 flex items-center gap-1.5">
                                                        <div className="w-1.5 h-1.5 rounded-full bg-accent-success animate-pulse" />
                                                        <span className="text-[10px] font-mono font-bold text-accent-success">
                                                            {telemetry?.performance?.global_fps || 0} FPS
                                                        </span>
                                                        <span className="text-[8px] font-mono text-txt-secondary">
                                                            {telemetry?.performance?.latency_ms || 0}ms
                                                        </span>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    ) : selectedCam ? (
                                        <video ref={videoRef} autoPlay muted className="w-full h-full object-cover" />
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center bg-ic-bg/80">
                                            <div className="text-center px-4">
                                                <Camera className="w-8 h-8 mx-auto mb-2 text-cyan-700" />
                                                <div className="text-[11px] uppercase tracking-wider text-accent-cyan font-bold">No Primary Feed Selected</div>
                                                <div className="text-[10px] text-txt-secondary mt-1">Choose a primary camera in Configuration.</div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Secondary Feed (Beta) */}
                            {
                                selectedCam2 && (
                                    <div className="flex-1 min-w-[300px] flex flex-col gap-1">
                                        <div className="flex items-center gap-2">
                                            <div className={cn("w-2 h-2 rounded-full", visionActive2 ? "bg-accent-indigo animate-pulse" : "bg-accent-danger")} />
                                            <h3 className="text-[10px] text-accent-indigo uppercase tracking-wider font-bold">Vision Beta</h3>
                                        </div>
                                        <div className="relative rounded-lg overflow-hidden border border-accent-indigo/50 bg-black h-full aspect-video mx-auto shadow-lg shadow-accent-indigo/20">
                                            {hasSecondaryVisionFeed ? (
                                                <div className="w-full h-full relative group">
                                                    <img
                                                        src={getStreamUrl(selectedCam2.replace("BRAIN_", ""))}
                                                        alt="Neural Vision Stream 2"
                                                        className="w-full h-full object-cover"
                                                    />

                                                    {/* Dynamic Video Overlay */}
                                                    <VideoOverlay
                                                        detections={telemetry?.detections}
                                                        camLabel={["VisionBeta", selectedCam2.replace("BRAIN_", "")]}
                                                        color="fuchsia"
                                                        metadata={{
                                                            confidence: telemetry?.confidence,
                                                            targetLock: telemetry?.target_lock,
                                                            quality: telemetry?.quality
                                                        }}
                                                    />

                                                    <div className="absolute inset-x-0 bottom-0 p-1 bg-black/60 text-[8px] text-accent-indigo opacity-0 group-hover:opacity-100 transition-opacity text-center pointer-events-none z-20">
                                                        Secondary Feed (Beta)
                                                    </div>

                                                    {/* FPS Counter Overlay (Beta) */}
                                                    {showFps && (
                                                        <div className="absolute top-1.5 left-1.5 z-40 pointer-events-none">
                                                            <div className="bg-black/80 backdrop-blur-sm border border-accent-indigo/30 rounded px-2 py-0.5 flex items-center gap-1.5">
                                                                <div className="w-1.5 h-1.5 rounded-full bg-accent-indigo animate-pulse" />
                                                                <span className="text-[10px] font-mono font-bold text-accent-indigo">
                                                                    {telemetry?.performance?.global_fps || 0} FPS
                                                                </span>
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            ) : (
                                                <div className="w-full h-full flex items-center justify-center bg-ic-bg/80">
                                                    <div className="text-center px-4">
                                                        <Camera className="w-7 h-7 mx-auto mb-2 text-accent-indigo" />
                                                        <div className="text-[10px] uppercase tracking-wider text-accent-indigo font-bold">Secondary Feed Standby</div>
                                                        <div className="text-[9px] text-txt-secondary mt-1">Select a secondary camera in Configuration.</div>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )
                            }
                        </div>

                        <div className="flex-1 min-h-0 overflow-y-auto p-6 flex flex-col gap-6 custom-scrollbar">
                            {messages.map((msg, idx) => (
                                <div key={idx} className={cn("flex max-w-3xl flex-col gap-1", msg.role === 'user' ? "self-end items-end" : "self-start items-start")}>
                                    {/* Avatar Snapshot (Assistant) */}
                                    {msg.role === 'assistant' && (
                                        <div className="flex gap-2 mb-1 flex-wrap justify-start">
                                            <div className="border-4 border-accent-warning/30 rounded-lg overflow-hidden shadow-lg w-[160px] h-[120px] relative bg-black/20 shrink-0">
                                                <HappyFace
                                                    expression={msg.affective_state || 'NEUTRAL'}
                                                    telemetry={{ pos: [0, 0] }}
                                                    talking={isTalking}
                                                />
                                            </div>
                                        </div>
                                    )}

                                    {/* Snapshot Bubble(s) */}
                                    {(msg.snapshot_urls && msg.snapshot_urls.length > 0) ? (
                                        <div className="flex gap-2 mb-1 flex-wrap justify-end">
                                            {msg.snapshot_urls.map((url, i) => (
                                                <div
                                                    key={i}
                                                    className="border-2 border-accent-cyan/30 rounded-lg overflow-hidden cursor-zoom-in hover:border-cyan-400 transition-colors shadow-lg max-w-[160px]"
                                                    onClick={() => setLightboxImage(url)}
                                                >
                                                    <img src={url} alt={`Vision Snapshot ${i}`} className="w-full h-auto" />
                                                </div>
                                            ))}
                                        </div>
                                    ) : msg.snapshot_url && (
                                        <div
                                            className="border-4 border-accent-cyan/30 rounded-lg overflow-hidden cursor-zoom-in hover:border-cyan-400 transition-colors shadow-lg max-w-[200px]"
                                            onClick={() => setLightboxImage(msg.snapshot_url)}
                                        >
                                            <img src={msg.snapshot_url} alt="Vision Snapshot" className="w-full h-auto" />
                                        </div>
                                    )}

                                    <div className={cn(
                                        "p-4 rounded-lg border backdrop-blur-md shadow-lg",
                                        msg.role === 'user' ? "bg-cyan-950/30 border-accent-cyan/30 text-cyan-50" : "bg-ic-surface/50 border-white/10 text-txt-primary"
                                    )}>
                                        {msg.content}

                                        {/* AI-Generated Imagery (Explicitly requested from model) */}
                                        {msg.generated_image_url && (
                                            <div
                                                className="mt-4 rounded-lg overflow-hidden border-2 border-indigo-500/50 cursor-pointer hover:border-indigo-400 transition-all shadow-xl shadow-indigo-500/10"
                                                onClick={() => setLightboxImage(msg.generated_image_url)}
                                            >
                                                <div className="bg-accent-indigo/10 px-2 py-1 text-[8px] uppercase tracking-widest text-accent-indigo font-bold border-b border-indigo-500/20">
                                                    Synthesized Imagery
                                                </div>
                                                <img src={msg.generated_image_url} alt="AI Generated" className="w-full h-auto" />
                                            </div>
                                        )}

                                        {/* Audio Player: STT for user, TTS for assistant */}
                                        {msg.audio_url && (
                                            <div className={cn(
                                                "mt-3 pt-2 border-t",
                                                msg.role === 'user' ? "border-accent-cyan/20" : "border-white/10"
                                            )}>
                                                <div className="flex items-center gap-2 mb-1">
                                                    <Volume2 className="w-3 h-3 opacity-60" />
                                                    <span className="text-[10px] uppercase tracking-wider opacity-60">
                                                        {msg.role === 'user' ? 'Your Voice (STT)' : 'AI Voice (TTS)'}
                                                    </span>
                                                </div>
                                                <audio
                                                    controls
                                                    src={msg.audio_url}
                                                    className="w-full h-8 opacity-80 hover:opacity-100 transition-opacity"
                                                    style={{ filter: 'invert(1) hue-rotate(180deg)' }}
                                                    onPlay={() => setIsTalking(true)}
                                                    onPause={() => setIsTalking(false)}
                                                    onEnded={() => setIsTalking(false)}
                                                />
                                            </div>
                                        )}

                                        <div className="text-[10px] opacity-40 mt-2 text-right">
                                            {msg.timestamp?.toLocaleTimeString()}
                                        </div>
                                    </div>
                                </div>
                            ))}
                            {isProcessing && (
                                <div className="self-start p-4 rounded-lg bg-ic-surface/50 border border-white/10 text-txt-secondary animate-pulse font-mono flex items-center gap-2">
                                    <RefreshCw className="w-4 h-4 animate-spin" /> Processing Neural Streams...
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input Bar */}
                        <div className="p-4 border-t border-accent-cyan/30 bg-black/60 backdrop-blur shrink-0">
                            <div className="max-w-4xl mx-auto flex gap-4 items-center">
                                <button
                                    onClick={toggleVoice}
                                    className={cn("p-3 rounded-full transition-all border",
                                        isListening ? "bg-accent-success/20 border-green-500 text-accent-success animate-pulse" : "bg-accent-cyan/20 border-cyan-700 text-accent-cyan hover:bg-accent-cyan/40"
                                    )}
                                >
                                    <Mic className="w-6 h-6" />
                                </button>

                                <input
                                    ref={inputRef}
                                    type="text"
                                    value={inputText}
                                    onChange={e => setInputText(e.target.value)}
                                    onKeyDown={e => e.key === 'Enter' && handleSend()}
                                    placeholder="Message ImpressionCore..."
                                    className="flex-1 bg-ic-surface/50 border border-accent-cyan/50 rounded-lg px-4 py-3 focus:outline-none focus:border-accent-cyan transition-colors"
                                />

                                <button
                                    onClick={() => handleSend()}
                                    disabled={isProcessing}
                                    className="p-3 bg-accent-cyan hover:bg-accent-cyan text-white rounded-lg disabled:opacity-50 transition-colors"
                                >
                                    <Send className="w-6 h-6" />
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className={cn(
                        "flex-1 min-h-0 flex flex-col bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-ic-surface to-black overflow-hidden p-6 gap-4",
                        activePage !== 'config' && "hidden"
                    )}>
                        <div className="bg-ic-surface/60 border border-accent-indigo/40 rounded-xl p-5 shadow-lg shadow-accent-indigo/20 shrink-0">
                            <h2 className="text-xl font-bold text-white mb-2">Configuration Control Center</h2>
                            <p className="text-txt-primary text-xs">
                                Hardware routing, sensory diagnostics, and operational tuning are active on this page.
                            </p>
                        </div>

                        <div className="grid grid-cols-3 gap-4 flex-1 min-h-0">
                            <div className="bg-ic-bg/60 border border-ic-border rounded-lg p-4">
                                <div className="text-[10px] uppercase tracking-wider text-accent-cyan mb-2">Vision</div>
                                <div className="text-sm text-white font-semibold">{systemStatus?.components?.vision?.health || 'OFFLINE'}</div>
                                <div className="text-[11px] text-txt-secondary mt-1">{systemStatus?.components?.vision?.cameras_detected || 0} camera(s) detected</div>
                            </div>
                            <div className="bg-ic-bg/60 border border-ic-border rounded-lg p-4">
                                <div className="text-[10px] uppercase tracking-wider text-accent-indigo mb-2">Neural Core</div>
                                <div className="text-sm text-white font-semibold">{systemStatus?.components?.intelligence?.status || 'STANDBY'}</div>
                                <div className="text-[11px] text-txt-secondary mt-1 truncate">{systemStatus?.components?.intelligence?.model || 'No model loaded'}</div>
                            </div>
                            <div className="bg-ic-bg/60 border border-ic-border rounded-lg p-4">
                                <div className="text-[10px] uppercase tracking-wider text-accent-success mb-2">Audio</div>
                                <div className="text-sm text-white font-semibold">{systemStatus?.components?.sensory?.microphones || 0} mic(s)</div>
                                <div className="text-[11px] text-txt-secondary mt-1">PnP inventory: {systemStatus?.components?.sensory?.pnp_inventory_size || 0}</div>
                                <div className="text-[11px] mt-1">
                                    <span className="text-txt-secondary">Whisper STT:</span>{" "}
                                    <span className={cn(sttHealth?.available && sttHealth?.model_loaded ? "text-accent-success" : "text-accent-danger")}>
                                        {sttHealth?.available && sttHealth?.model_loaded ? (sttHealth?.running ? "Listening" : "Ready") : "Unavailable"}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-black/40 border border-ic-border rounded-lg p-4 text-xs text-txt-secondary shrink-0">
                            Keep Main focused on conversation flow; use Configuration for device changes and diagnostics.
                        </div>
                    </div>

                    {/* Right Sidebar: History & Archiving */}
                    <div className={cn(
                        "w-80 shrink-0 border-l border-accent-cyan/50 flex flex-col bg-ic-bg p-4 gap-4 overflow-hidden",
                        activePage !== 'main' && "hidden"
                    )}>

                        <AvatarPanel
                            active={avatarActive}
                            onToggle={() => setAvatarActive(!avatarActive)}
                            telemetry={telemetry}
                            selectedAvatar={selectedAvatar}
                            onAvatarChange={setSelectedAvatar}
                            expression={currentExpression}
                            talking={isTalking}
                            skeleton={rtSkeleton}
                        />

                        <button
                            onClick={handleNewChat}
                            className="w-full py-3 bg-accent-cyan hover:bg-accent-cyan text-white rounded-lg flex items-center justify-center gap-2 transition-all font-bold shadow-lg shadow-accent-cyan/20 shrink-0"
                        >
                            <Send className="w-4 h-4" /> Initialize New Pathway
                        </button>

                        <div className="bg-ic-surface/50 p-2 rounded border border-accent-cyan/30 shrink-0">
                            <h3 className="text-[10px] text-accent-cyan mb-1 uppercase tracking-wider flex items-center justify-between">
                                <span>Whisper STT</span>
                                <span className={cn(
                                    "text-[9px] font-bold",
                                    sttHealth?.available && sttHealth?.model_loaded ? "text-accent-success" : "text-accent-danger"
                                )}>
                                    {sttHealth?.available && sttHealth?.model_loaded ? (isListening ? "LISTENING" : "READY") : "OFFLINE"}
                                </span>
                            </h3>
                            <p className="text-[9px] text-txt-secondary truncate">
                                {sttHealth?.last_error || (sttHealth?.available && sttHealth?.model_loaded ? "Local Whisper engine operational" : "Whisper dependency/model unavailable")}
                            </p>
                        </div>

                        <div className="flex-1 min-h-0 flex flex-col gap-2 border-t border-ic-border pt-4 overflow-hidden">
                            <h3 className="text-[10px] text-txt-secondary uppercase tracking-wider flex items-center gap-2">
                                <Layers className="w-3 h-3" /> Temporal Archive
                            </h3>
                            <div className="flex-1 overflow-y-auto space-y-1 pr-1 custom-scrollbar">
                                {sessions.length === 0 && <div className="text-[10px] text-txt-muted italic p-2">No history found.</div>}
                                {sessions.map(s => (
                                    <div
                                        key={s.id}
                                        onClick={() => handleSwitchSession(s.id)}
                                        className={cn(
                                            "group relative p-2 rounded border cursor-pointer transition-all",
                                            currentSessionId === s.id
                                                ? "bg-accent-cyan/30 border-accent-cyan/50 shadow-inner shadow-accent-cyan/10"
                                                : "bg-ic-surface/40 border-ic-border hover:border-ic-border hover:bg-ic-surface/60"
                                        )}
                                    >
                                        <div className="text-[11px] text-cyan-100 font-medium truncate pr-4">{s.title || "Untitled Chat"}</div>
                                        <div className="text-[9px] text-txt-secondary flex justify-between mt-1">
                                            <span>{s.message_count} msgs</span>
                                            <span>{new Date(s.updated_at).toLocaleDateString()}</span>
                                        </div>
                                        <button
                                            onClick={(e) => {
                                                e.preventDefault();
                                                e.stopPropagation();
                                                handleDeleteSession(e, s.id);
                                            }}
                                            className="absolute top-1.5 right-1.5 text-txt-secondary hover:text-accent-danger hover:bg-accent-danger/10 transition-all p-1.5 rounded-md z-20"
                                            title="Delete Session"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Hemisphere Monitors */}
                        <div className="flex flex-col gap-2 shrink-0 border-t border-ic-border pt-4">
                            <div className="bg-ic-surface/50 p-2 rounded border border-accent-cyan/30">
                                <h3 className="text-[10px] text-cyan-600 mb-1 flex items-center gap-2"><Terminal className="w-3 h-3" /> LEFT HEMISPHERE</h3>
                                <p className="text-xs text-cyan-100/80 leading-relaxed max-h-24 overflow-y-auto custom-scrollbar">
                                    {monitors.left_hemisphere}
                                </p>
                            </div>
                            <div className="bg-ic-surface/50 p-2 rounded border border-accent-indigo/30 shadow-[inset_0_0_10px_rgba(217,70,239,0.05)]">
                                <h3 className="text-[10px] text-accent-indigo mb-1 flex items-center gap-2 font-bold"><Activity className="w-3 h-3" /> RIGHT HEMISPHERE</h3>
                                <p className="text-xs text-txt-primary/80 leading-relaxed max-h-24 overflow-y-auto custom-scrollbar italic">
                                    {monitors.right_hemisphere}
                                </p>
                            </div>
                        </div>

                        {/* Thought Stream (Nexus Reasoning) */}
                        {/* Thought Stream (Nexus Reasoning) */}
                        <div className="h-96 bg-black/60 rounded border border-accent-cyan/30 p-2 overflow-hidden flex flex-col shrink-0">
                            <h3 className="text-[10px] text-accent-cyan mb-2 flex items-center gap-2 uppercase tracking-widest animate-pulse">
                                <Terminal className="w-3 h-3" /> Neural Thought Stream
                            </h3>
                            <div className="flex-1 overflow-y-auto font-mono text-[10px] text-lime-400/90 space-y-1.5 select-text custom-scrollbar bg-ic-bg/50 p-1 rounded shadow-inner">
                                {thoughtStream.length === 0 && <div className="text-cyan-900 italic">Waiting for neural activity...</div>}
                                {thoughtStream.map((reason, i) => (
                                    <div key={i} className="leading-tight border-l-2 border-lime-900/50 pl-2 py-0.5 hover:bg-lime-900/10 transition-colors">
                                        <span className="text-lime-700 mr-2"></span>{reason}
                                    </div>
                                ))}
                                <div ref={messagesEndRef} />
                            </div>
                        </div>
                    </div>

                    {/* System Status Overlay */}
                    <SystemStatusOverlay
                        isOpen={showStatus}
                        onClose={() => setShowStatus(false)}
                        statusData={systemStatus}
                        onRefresh={() => fetchSystemStatus(true)}
                        telemetry={telemetry}
                        onOpenConfiguration={() => setActivePage('config')}
                    />

                    {/* Lightbox Modal */}
                    {
                        lightboxImage && (
                            <div
                                className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-8 backdrop-blur-sm animate-in fade-in duration-200"
                                onClick={() => setLightboxImage(null)}
                            >
                                <div className="relative max-w-full max-h-full">
                                    <img
                                        src={lightboxImage}
                                        alt="Full Resolution Snapshot"
                                        className="max-w-full max-h-full object-contain rounded border border-accent-cyan/30 shadow-[0_0_50px_rgba(6,182,212,0.15)]"
                                    />
                                    <button
                                        className="absolute top-4 right-4 text-white/50 hover:text-white bg-black/50 hover:bg-black/80 rounded-full p-2"
                                        onClick={() => setLightboxImage(null)}
                                    >

                                    </button>
                                </div>
                            </div>
                        )
                    }
                </div> {/* End Main Content Row */}
            </div>
        </div>
    );
}

export default App;
