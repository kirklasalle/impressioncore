import React, { useMemo } from 'react';

// Dlib 68 Point Model Map
const CONNECTIONS = [
    // Jaw
    [0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8], [8, 9], [9, 10], [10, 11], [11, 12], [12, 13], [13, 14], [14, 15], [15, 16],
    // Right Eyebrow
    [17, 18], [18, 19], [19, 20], [20, 21],
    // Left Eyebrow
    [22, 23], [23, 24], [24, 25], [25, 26],
    // Nose Bridge
    [27, 28], [28, 29], [29, 30],
    // Nose Tip
    [31, 32], [32, 33], [33, 34], [34, 35],
    // Right Eye
    [36, 37], [37, 38], [38, 39], [39, 40], [40, 41], [41, 36],
    // Left Eye
    [42, 43], [43, 44], [44, 45], [45, 46], [46, 47], [47, 42],
    // Outer Lip
    [48, 49], [49, 50], [50, 51], [51, 52], [52, 53], [53, 54], [54, 55], [55, 56], [56, 57], [57, 58], [58, 59], [59, 48],
    // Inner Lip
    [60, 61], [61, 62], [62, 63], [63, 64], [64, 65], [65, 66], [66, 67], [67, 60]
];

const NeuralFaceMesh = React.memo(({ landmarks, color = "#22d3ee", opacity = 0.8 }) => {
    // [ENHANCEMENT] Handle both Dict and Array formats
    const meshPoints = useMemo(() => {
        if (!landmarks) return [];

        // If it's a dictionary (neural landmarks), flatten it
        if (typeof landmarks === 'object' && !Array.isArray(landmarks)) {
            // Standard feature order to maintain some consistency if needed
            const order = ['jaw', 'right_eyebrow', 'left_eyebrow', 'nose_bridge', 'nose_tip', 'right_eye', 'left_eye', 'top_lip', 'bottom_lip'];
            let flat = [];
            order.forEach(key => {
                if (landmarks[key]) flat = [...flat, ...landmarks[key]];
            });
            // Catch any extras
            Object.keys(landmarks).forEach(key => {
                if (!order.includes(key)) flat = [...flat, ...landmarks[key]];
            });
            return flat;
        }
        return landmarks;
    }, [landmarks]);

    if (!meshPoints || meshPoints.length === 0) return null;

    // Viewport is assumed 0..1 from backend normalizer
    // We scale to 100x100 for SVG simplicity

    // Identify Model
    const isDlib = meshPoints.length === 68;
    const isKinect = meshPoints.length === 87;

    return (
        <svg viewBox="0 0 100 100" className="w-full h-full pointer-events-none absolute inset-0 z-10" style={{ opacity }}>
            <defs>
                <filter id="mesh-glow">
                    <feGaussianBlur stdDeviation="1" result="coloredBlur" />
                    <feMerge>
                        <feMergeNode in="coloredBlur" />
                        <feMergeNode in="SourceGraphic" />
                    </feMerge>
                </filter>
            </defs>

            {/* Render Connections (Dlib 68) */}
            {isDlib && CONNECTIONS.map(([start, end], i) => {
                const p1 = meshPoints[start];
                const p2 = meshPoints[end];
                if (!p1 || !p2) return null;

                return (
                    <line
                        key={`conn-${i}`}
                        x1={p1[0] * 100} y1={p1[1] * 100}
                        x2={p2[0] * 100} y2={p2[1] * 100}
                        stroke={color}
                        strokeWidth="0.5"
                        strokeLinecap="round"
                        filter="url(#mesh-glow)"
                    />
                );
            })}

            {/* Render Points */}
            {meshPoints.map((p, i) => (
                <circle
                    key={`pt-${i}`}
                    cx={p[0] * 100}
                    cy={p[1] * 100}
                    r={isKinect ? "0.6" : "0.8"}
                    fill={color}
                    opacity={isKinect ? "0.8" : "0.6"}
                />
            ))}
        </svg>
    );
});

export default NeuralFaceMesh;
