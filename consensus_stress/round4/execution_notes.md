# Round-4 execution notes

- The user-supplied venv path `/storage/gaoym/sp500-forecastability-lab/.venv/bin/vllm`
  did not contain a vLLM executable or importable `vllm` module in the current workspace.
  A first launch attempt therefore failed at executable resolution before loading a model
  or making any Ling call.
- The working installation verified from the Round-3 log and current filesystem was
  `/storage/gaoym/wcl_venv_vllm/.venv` (vLLM 0.29.0). The successful server used the same
  model, endpoint, GPU5, model name, context length, memory utilization, prefix caching,
  sequence limits, chunked prefill, and `enable_thinking:false` settings. This is an
  environment/deployment correction only, not a protocol or scientific change.
- GPU4 and GPU6 were not used. The successful service was left running on GPU5 after the
  experiment, as allowed; current status is in `server_status.json`.
- The 15,000-call run completed in 794.68 seconds with 100% adapted-contract validity.
