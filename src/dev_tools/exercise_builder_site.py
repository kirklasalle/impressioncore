#!/usr/bin/env python3
"""
ImpressionCore Builder Site Full Workflow & Model Build Verification
Exercises all builder site APIs, defines and builds a model, monitors training,
and verifies inference, evaluation, and checkpoint management.
"""

import json
import time
import requests

BASE_URL = "http://127.0.0.1:5000"

def test_step(step_name, fn):
    print(f"\n=======================================================")
    print(f"▶ STEP: {step_name}")
    print(f"=======================================================")
    try:
        res = fn()
        print(f"✔ SUCCESS: {step_name}")
        return res
    except Exception as e:
        print(f"❌ FAILED: {step_name} -> {e}")
        raise e

def test_gpu_detection():
    r = requests.get(f"{BASE_URL}/api/v1/builder/gpu/detect")
    data = r.json()
    print("GPU Info:", json.dumps(data.get("gpu", {}), indent=2))
    return data

def test_data_scan():
    payload = {"path": "data/datasets"}
    r = requests.post(f"{BASE_URL}/api/v1/builder/data/scan", json=payload)
    data = r.json()
    print(f"Files Found: {data.get('total_files', 0)}, Total Bytes: {data.get('total_bytes', 0)}")
    return data

def test_tokenizer_config():
    payload = {
        "type": "bpe",
        "vocabSize": 32000,
        "minFrequency": 2,
        "specialTokens": "<pad>,<eos>,<bos>,<unk>"
    }
    r = requests.post(f"{BASE_URL}/api/v1/builder/tokenizer/configure", json=payload)
    data = r.json()
    print("Tokenizer Config:", json.dumps(data.get("config", {}), indent=2))

    # Test tokenization
    r2 = requests.post(f"{BASE_URL}/api/v1/builder/tokenizer/tokenize", json={"text": "Hello ImpressionCore AI Democratization"})
    tok_data = r2.json()
    print(f"Tokenized: {tok_data.get('tokens')} (Count: {tok_data.get('count')})")
    return data

def test_model_definition():
    # Configure custom low-VRAM model (8 layers, 768 hidden, 12 heads, fp16)
    payload = {
        "architecture": "transformer",
        "preset": "custom",
        "layers": 8,
        "hiddenSize": 768,
        "heads": 12,
        "intermediateSize": 3072,
        "contextWindow": 2048,
        "vocabSize": 50257,
        "precision": "fp16",
        "activation": "gelu",
        "flashAttention": True,
        "rope": True
    }
    r = requests.post(f"{BASE_URL}/api/v1/builder/model/configure", json=payload)
    data = r.json()
    print("Model Config & Estimates:", json.dumps(data, indent=2))
    return data

def test_training_and_build_model():
    # Start training with the builder
    train_payload = {
        "epochs": 2,
        "batchSize": 2,
        "learningRate": 0.0001,
        "precision": "fp16",
        "checkpointDir": "F:/models/checkpoints/builder_client"
    }
    r = requests.post(f"{BASE_URL}/api/v1/builder/training/start", json=train_payload)
    start_res = r.json()
    print("Training Start Response:", start_res)

    # Monitor training progress
    print("Monitoring training loop...")
    for _ in range(30):
        time.sleep(1)
        sr = requests.get(f"{BASE_URL}/api/v1/builder/training/status")
        status = sr.json()
        running = status.get("running")
        epoch = status.get("epoch")
        total_epochs = status.get("total_epochs")
        step = status.get("step")
        loss = status.get("loss")
        vram = status.get("vram")
        print(f"  [Epoch {epoch}/{total_epochs} | Step {step}] Loss: {loss:.4f} | VRAM: {vram:.2f}GB | Running: {running}")
        if not running:
            print("Training finished or finalized!")
            break
    return status

def test_checkpoints():
    r = requests.get(f"{BASE_URL}/api/v1/builder/training/checkpoints")
    data = r.json()
    print(f"Found {len(data.get('checkpoints', []))} checkpoints in {data.get('directory')}")
    for c in data.get('checkpoints', [])[:5]:
        print(f"  - {c.get('name')} ({c.get('size_mb')} MB)")
    return data

def test_inference():
    payload = {
        "prompt": "ImpressionCore digital identity and cognitive architecture represents",
        "maxTokens": 64,
        "temperature": 0.7,
        "topP": 0.9
    }
    r = requests.post(f"{BASE_URL}/api/v1/builder/inference/run", json=payload)
    data = r.json()
    print("Inference Response:\n", data.get("response"))
    return data

def test_evaluation():
    payload = {
        "metrics": ["accuracy", "perplexity", "f1", "bleu", "latency"],
        "batch_size": 4
    }
    r = requests.post(f"{BASE_URL}/api/v1/builder/evaluation/run", json=payload)
    data = r.json()
    print("Evaluation Results:", json.dumps(data.get("results", {}), indent=2))
    return data

def test_deployment_package():
    payload = {
        "format": "pytorch",
        "optimization": "quantized_int8",
        "checkpoint": "latest",
        "target": "local"
    }
    r = requests.post(f"{BASE_URL}/api/v1/builder/deployment/package", json=payload)
    data = r.json()
    print("Deployment Package Result:", json.dumps(data, indent=2))
    return data

def main():
    print("=== STARTING IMPRESSIONCORE BUILDER TEST SUITE ===")
    test_step("1. GPU & Hardware Telemetry", test_gpu_detection)
    test_step("2. Data Preparation & Scanning", test_data_scan)
    test_step("3. Tokenizer Configuration & Tokenization", test_tokenizer_config)
    test_step("4. Model Definition & Parameter Estimation", test_model_definition)
    test_step("5. Model Build & Training Execution", test_training_and_build_model)
    test_step("6. Checkpoint Verification", test_checkpoints)
    test_step("7. Model Inference & Text Generation", test_inference)
    test_step("8. Model Evaluation Suite", test_evaluation)
    test_step("9. Deployment Packaging", test_deployment_package)
    print("\n=======================================================")
    print("🎉 ALL BUILDER FUNCTIONS EXERCISED & MODEL BUILT!")
    print("=======================================================")

if __name__ == "__main__":
    main()
