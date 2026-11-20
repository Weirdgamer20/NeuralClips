# Project Rules: NeuralClips Workspace

## Startup Policy & Daemon Persistence
1. This workspace operates a continuous, autonomous real-time live stream moment extraction & publishing pipeline (`run_live_monitor.py`).
2. Every time a new session starts or Antigravity is opened in this workspace, the agent must ensure that the background live monitor daemon is running.
3. The pipeline monitors top GTA 6 broadcasts in real time, auto-detects facecams using computer vision, cuts 2K vertical Shorts (Gameplay Top 60%, Facecam Bottom 40%) with audio, and automatically publishes to YouTube until daily quota is reached.
4. Intermediate raw files and uploaded clips are automatically cleaned up immediately after publication to preserve disk space.
