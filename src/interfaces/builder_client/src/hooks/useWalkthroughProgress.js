import { useCallback, useEffect, useRef, useState } from 'react';
import { getWalkthroughProgress, saveWalkthroughProgress } from '../lib/api';
import { PIPELINE_STEPS } from '../lib/constants';

const LS_KEY = 'ic_walkthrough_progress';
const MAX_STEP = PIPELINE_STEPS.length - 1;

function readLocal() {
    try {
        const raw = localStorage.getItem(LS_KEY);
        if (raw) {
            const parsed = JSON.parse(raw);
            return {
                currentStep: parsed.current_step ?? 0,
                completed: new Set(parsed.completed ?? []),
                updatedAt: parsed.updated_at ?? null,
            };
        }
    } catch { /* ignore corrupt data */ }
    return null;
}

function writeLocal(currentStep, completed) {
    const now = new Date().toISOString();
    try {
        localStorage.setItem(LS_KEY, JSON.stringify({
            current_step: currentStep,
            completed: [...completed],
            updated_at: now,
        }));
    } catch { /* quota exceeded — non-fatal */ }
}

export default function useWalkthroughProgress() {
    const [currentStep, setCurrentStepRaw] = useState(() => readLocal()?.currentStep ?? 0);
    const [completed, setCompleted] = useState(() => readLocal()?.completed ?? new Set());
    const saveTimer = useRef(null);
    const latestRef = useRef({ currentStep: 0, completed: new Set() });

    // Keep ref in sync for the debounced save closure
    useEffect(() => {
        latestRef.current = { currentStep, completed };
    }, [currentStep, completed]);

    // Poll localStorage every 1.5s so sibling hook instances (e.g. Sidebar)
    // pick up markDone changes made on other pages without a full reload
    useEffect(() => {
        const id = setInterval(() => {
            const local = readLocal();
            if (!local) return;
            const prev = latestRef.current;
            const localArr = [...(local.completed)].sort().join(',');
            const prevArr = [...prev.completed].sort().join(',');
            if (local.currentStep !== prev.currentStep || localArr !== prevArr) {
                setCurrentStepRaw(local.currentStep);
                setCompleted(new Set(local.completed));
            }
        }, 1500);
        return () => clearInterval(id);
    }, []);

    // Debounced backend-only save (300ms) — localStorage is written synchronously elsewhere
    const scheduleBackendSave = useCallback(() => {
        clearTimeout(saveTimer.current);
        saveTimer.current = setTimeout(() => {
            const { currentStep: cs, completed: cp } = latestRef.current;
            saveWalkthroughProgress({
                current_step: cs,
                completed: [...cp],
            }).catch((err) => console.warn('[walkthrough] backend save failed', err));
        }, 300);
    }, []);

    // On mount: load from localStorage immediately, then reconcile with backend
    useEffect(() => {
        let cancelled = false;
        getWalkthroughProgress()
            .then(({ data }) => {
                if (cancelled || !data?.success) return;
                const remote = data.progress;
                const local = readLocal();
                // Backend wins if it has a newer or equal timestamp, or if local has none
                const useRemote = !local?.updatedAt || (remote.updated_at && remote.updated_at >= local.updatedAt);
                if (useRemote && remote.completed?.length) {
                    setCurrentStepRaw(remote.current_step ?? 0);
                    setCompleted(new Set(remote.completed ?? []));
                    writeLocal(remote.current_step ?? 0, new Set(remote.completed ?? []));
                }
            })
            .catch((err) => console.warn('[walkthrough] backend load failed, using localStorage', err));
        return () => { cancelled = true; };
    }, []);

    // Cleanup debounce timer on unmount
    useEffect(() => () => clearTimeout(saveTimer.current), []);

    const setCurrentStep = useCallback((idx) => {
        const clamped = Math.max(0, Math.min(idx, MAX_STEP));
        setCurrentStepRaw(clamped);
        // Write localStorage synchronously so it survives immediate navigation
        setCompleted((prev) => {
            writeLocal(clamped, prev);
            return prev;
        });
        scheduleBackendSave();
    }, [scheduleBackendSave]);

    const markDone = useCallback((idx) => {
        setCompleted((prev) => {
            const next = new Set(prev);
            next.add(idx);
            const nextStep = idx < MAX_STEP ? idx + 1 : idx;
            // Write localStorage synchronously BEFORE any navigation can happen
            writeLocal(nextStep, next);
            setCurrentStepRaw(nextStep);
            return next;
        });
        scheduleBackendSave();
    }, [scheduleBackendSave]);

    const resetProgress = useCallback(() => {
        setCurrentStepRaw(0);
        setCompleted(new Set());
        writeLocal(0, new Set());
        saveWalkthroughProgress({ current_step: 0, completed: [] })
            .catch((err) => console.warn('[walkthrough] backend reset failed', err));
    }, []);

    const allComplete = completed.size >= PIPELINE_STEPS.length;

    return { currentStep, setCurrentStep, completed, markDone, resetProgress, allComplete };
}
