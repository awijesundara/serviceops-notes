# Running a model server for ServiceOps (llama.cpp, Apple/AMD GPU example)

ServiceOps talks to any OpenAI-compatible server. This page records the working reference setup used for testing: a 2019 MacBook Pro (Intel Core i9, AMD Radeon Pro 5500M with 8 GB VRAM) running llama.cpp's `llama-server` through Vulkan (MoltenVK). Any other server (Ollama, vLLM, LM Studio) works the same way from ServiceOps' side; see [AI_OPERATIONS.md](AI_OPERATIONS.md).

## What was measured

| Setup | Qwen3-8B Q4_K_M | Notes |
|---|---|---|
| CPU only (8 threads) | about 5.5 tokens/s, 99 s per streamed investigation | Metal on this GPU was slower than CPU; Ollama also CPU |
| Vulkan on the Radeon Pro 5500M (`-ngl 99`) | about 21.6 tokens/s generation, 52 s per streamed investigation | Prompt processing is the slow part (first token 4-34 s for chat prompts) |

Qwen3 models are reasoning models: ServiceOps shows their thinking live. Qwen2.5 models answer without a reasoning stream.

## Build and run

```
# Build once (Vulkan, not Metal)
cd ~/llama.cpp
cmake -B build-vk -DGGML_VULKAN=ON -DGGML_METAL=OFF && cmake --build build-vk --config Release -j8

# Environment the GPU path needs (put in ~/.zprofile for SSH sessions)
export DYLD_LIBRARY_PATH=/opt/local/lib
export VK_DRIVER_FILES=/opt/local/share/vulkan/icd.d/MoltenVK_icd.json
export MVK_CONFIG_LOG_LEVEL=0
export GGML_VK_VISIBLE_DEVICES=0        # 0 = Radeon, 1 = Intel UHD

./build-vk/bin/llama-cli --list-devices   # must list Vulkan0: AMD Radeon Pro 5500M

# Serve (keep the key in a file, not on the command line where `ps` shows it)
./build-vk/bin/llama-server -hf Qwen/Qwen3-8B-GGUF:Q4_K_M -dev Vulkan0 -ngl 99 -fa off \
  -c 8192 --jinja --host 0.0.0.0 --port 8080 --api-key-file ~/ai/api-key
```

`-c 8192` matters: ServiceOps investigations send up to about 10,000 characters of evidence, so a 4096-token context can be too small. 8 GB of VRAM holds the 8B Q4 model (about 5 GB) plus an 8192-token cache.

## Connect ServiceOps

1. Operator: allow the server. Kubernetes: `ai.selfHostedEndpoints: "http://192.168.68.68:*"` and an `ai.extraEgress` rule for `192.168.68.68/32` (no `ports` = every port), then Helm upgrade. Compose: `AI_SELF_HOSTED_ENDPOINTS=http://192.168.68.68:*`.
2. Administrator: Administration, Platform and security, AI assistance. Choose **Server on your network**, address `http://192.168.68.68:8080`, paste the key. The model (for example `Qwen/Qwen3-8B-GGUF:Q4_K_M`) and its context window are detected automatically. Tick the master switch, incident investigations and the chat assistant; save; **Test saved connection**.
3. Try it: open an incident and choose **Investigate with AI**, or use **Ask AI** at the bottom right. Tick **Think step by step** in the chat to watch the reasoning.

## Keep it running (macOS)

A launchd agent restarts the server and survives logout. Template (`~/Library/LaunchAgents/com.serviceops.llama-gpu.plist`), then `launchctl load` it while logged in to the desktop session:

```
<plist version="1.0"><dict>
  <key>Label</key><string>com.serviceops.llama-gpu</string>
  <key>EnvironmentVariables</key><dict>
    <key>DYLD_LIBRARY_PATH</key><string>/opt/local/lib</string>
    <key>VK_DRIVER_FILES</key><string>/opt/local/share/vulkan/icd.d/MoltenVK_icd.json</string>
    <key>GGML_VK_VISIBLE_DEVICES</key><string>0</string>
  </dict>
  <key>ProgramArguments</key><array>
    <string>/Users/USER/llama.cpp/build-vk/bin/llama-server</string>
    <string>-m</string><string>/Users/USER/ai/models/Qwen3-8B-Q4_K_M.gguf</string>
    <string>-dev</string><string>Vulkan0</string><string>-ngl</string><string>99</string>
    <string>-fa</string><string>off</string><string>-c</string><string>8192</string><string>--jinja</string>
    <string>--host</string><string>0.0.0.0</string><string>--port</string><string>8080</string>
    <string>--api-key-file</string><string>/Users/USER/ai/api-key</string>
  </array>
  <key>RunAtLoad</key><true/><key>KeepAlive</key><true/>
</dict></plist>
```

A closed lid sleeps the Mac unless `sudo pmset -a disablesleep 1` is set (or the lid stays open on power).

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| "This endpoint has not been allowlisted..." | The operator has not listed that server; the message names the entry to add |
| "Provider rejected the request" | Wrong or empty API key, or wrong model identifier |
| "The server rejected the API key" during detection | Key mismatch with `--api-key-file` |
| Answer never starts / times out | Server unreachable from the pod (`ai.extraEgress`), model still loading, or `AI_PROVIDER_TIMEOUT_SECONDS` too low for CPU inference |
| Very slow first word | Long prompt on a small GPU; use a smaller model or raise nothing else; prompt processing dominates |
| Context window warning | Restart the server with `-c 8192` or larger |
