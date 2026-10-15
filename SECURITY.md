# Security and safe reproduction

This is a public benchmark-results repository, not a deployment package or a
production AIOS security boundary. Results deliberately include model outputs,
synthetic benchmark customer data, hardware/software details and historical logs.
Never add real account data, credentials, environment files, cookies, or private
application transcripts. Report a suspected exposed credential privately to the
repository owner; do not paste the credential into a public issue. Rotate a real
leaked credential before considering history cleanup.

## Hardened execution boundaries

### Python code benchmarks

The HumanEval and early coding harnesses require bubblewrap by default. Child
processes receive a minimal environment, `--clearenv`, isolated networking, no
host `/etc` mount, and a disposable writable work directory. System runtimes
under `/usr`, `/bin` and `/lib*` remain readable. Do not run as root. The earlier
harness's explicit unsafe opt-in is **not** a security boundary.

Even these hardened subprocesses are not safe enough for deliberately hostile
code: kernel/runtime vulnerabilities, resource exhaustion and dishonest benchmark
answers remain possible. Use a disposable VM for adversarial execution. Never
place secrets in runtime directories or the writable work directory.

### Aider Polyglot

The two historical `ctr.sh` entry points delegate to
`scripts/secure_polyglot.sh`. It requires rootless Podman, a locally installed
reviewed Aider image and a **new empty output directory**. There is no host-network
fallback and no implicit image pull. Image references resolve to immutable local
image IDs before execution. Host proxy environment variables are not forwarded.

The container has no network interfaces except its isolated loopback. A Unix
socket bridge offers only `GET /v1/models` and `POST /v1/chat/completions` to an
explicit loopback inference router (default `http://127.0.0.1:8081`). Management
routes, redirects, arbitrary hosts, query strings, client authorization/cookies,
and unlimited completion budgets are not forwarded. The bridge bounds active
threads, concurrent inference calls, body/response sizes and socket timeouts.
Generated code can still invoke that allowed inference API and consume model
resources; it cannot reach other host loopback services through this bridge.

Source mounts are read-only; only dedicated output is writable on the host.
Optional **public dependency** cache seeds are read-only and copied into disposable
container tmpfs, not shared writable caches. Supply only reviewed, credential-free
Aider/exercise source trees and dependency cache seeds. The container also drops
capabilities and new privileges and bounds memory, CPU, process/file-descriptor
counts and per-file writes. Output is not a trusted record: generated code can
modify it, and aggregate disk usage still needs monitoring. Host filesystem
mounts, source trees and container/kernel vulnerabilities remain reasons to use a
VM for hostile inputs.

Example (fish; prepare a separate benchmark router yourself, never stop live
services automatically):

```fish
set -lx P100_RUN_DIR $HOME/Projects/Tests/llm-benchmarks/(date +%F)/polyglot-secure-new
bash scripts/secure_polyglot.sh python3 /scripts/polyglot_run.py --help
```

Optional settings: `P100_TEST_WORKSPACE` (default `~/Projects/Tests`, with trusted
`tools/aider`, `tools/polyglot-benchmark` and optional `tools/polyglot-cache`),
`P100_AIDER_IMAGE` (default locally installed `localhost/aider-benchmark`), and
`P100_INFERENCE_URL` (explicit HTTP loopback IP and port, no credentials).
Re-baseline performance after changing execution/resource constraints; archived
numbers were measured with different isolation settings.

## Archived drivers are disabled by default

Shell drivers in `results/`, the old build-script backup, and `rig/drive.sh` now
refuse execution before any action unless `P100_ALLOW_ARCHIVED_DRIVER=1` is
explicitly supplied. The safe `ctr.sh` wrappers are exempt because they delegate
to the hardened launcher. **The flag acknowledges risk; it does not make the
old driver safe.** Some archived drivers intentionally stop live services, match
process names, or restart a production router. Review and adapt them to a
separate disposable environment before opting in. Do not source them casually.

Archived Python preset setters additionally require `P100_PRESET_FILE` pointing
to an explicit disposable preset copy; they no longer implicitly write the
owner's live `~/llama-cuda12/models.ini`. The shell drivers may still target live
service names after an intentional opt-in; use a VM or adapt those drivers first.
Raw reports, scores, logs and generated solutions retain their historical values.

## Reproducible CUDA build inputs

`scripts/build_llama_cuda12.sh` pins the source to the reviewed Pascal build
`50631b3d2c569ad8e5c112090cd28570b1268ee0` and CUDA image to
`docker.io/nvidia/cuda@sha256:392c0df7b577ecae17a17f6ba7f2009c217bb4422f8431c053ae9af61a8c148a`.
Override only with reviewed full `LLAMA_COMMIT` and `CUDA_IMAGE` pins. Branch/tag
`REF` overrides are rejected. Build output must be empty; existing production
builds are never overwritten by default.

Ubuntu apt repositories still move. `BUILD_PACKAGES` records their resolved
versions, but this is provenance, **not** a fully hermetic or bit-reproducible
build. For that stronger requirement, prebuild a reviewed toolchain image with
fixed packages and pin its digest. No full CUDA compilation is part of the
security smoke tests.

## Publication checks

- `.gitignore` excludes common sensitive files and transient caches, not curated
  benchmark logs. It does not remove anything already committed.
- `.gitleaks.toml` extends Gitleaks defaults. Only the literal fake `sk-local`
  placeholder is allowed; do not add broad path or entropy exceptions.
- `scripts/check_secrets.sh all` scans reachable history and working files with
  redacted output and recursive decoding. `staged` scans the Git index. The script
  fails closed if Gitleaks is unavailable; inline suppression comments are ignored.
- `.githooks/pre-commit` checks staged secrets and staged security metadata. To
  opt in on another clone, first preserve any existing hooks, then run
  `chmod +x .githooks/pre-commit` and
  `git config --local core.hooksPath .githooks`.
- `.github/workflows/security.yml` repeats scans and tests with read-only GitHub
  permissions, no persisted checkout credentials, commit-pinned actions and a
  checksum-pinned Gitleaks binary. It takes effect only after publication. CI and
  hooks are safeguards, not an unbypassable security policy or proof of no secrets.
- Review logs and decoded archive/image metadata before publication; the pinned
  Gitleaks CLI does not exhaustively inspect every archive format or image pixels.
  Keep the scanner and action pins reviewed and updated periodically.

Tested scanner: Gitleaks **8.24.2**, official Linux x64 archive:
`https://github.com/gitleaks/gitleaks/releases/download/v8.24.2/gitleaks_8.24.2_linux_x64.tar.gz`
with SHA-256
`fa0500f6b7e41d28791ebc680f5dd9899cd42b58629218a5f041efa899151a8e`.
Verify the checksum before extracting/running it. Do not pipe downloaded code to
an interpreter. On other architectures choose and verify the appropriate
upstream artifact rather than using this checksum.

## Static website

Every tracked HTML page has an early meta Content Security Policy and a
`no-referrer` policy. The main page permits only hash-approved inline JavaScript;
inline event handlers and unapproved scripts are blocked. Archived static
reports allow no scripts. Inline CSS is permitted for the existing chart/table
styles, and the few historical Google font links retain their original origins.
Gallery paths/tags are allowlisted and prompts/tooltips are rendered as text.

After editing inline scripts or adding report pages, run:

```fish
python3 scripts/refresh_security_metadata.py --write
python3 scripts/refresh_security_metadata.py
python3 -m unittest discover -s tests -v
bash scripts/check_secrets.sh all
```

`--write` only refreshes policy metadata and archived-driver guards; it does not
rewrite benchmark scores or raw logs. The pre-commit hook checks the staged tree,
not possibly different unstaged HTML. Optional real-container smoke test:

```fish
env P100_TEST_CONTAINER=1 python3 -m unittest discover -s tests -v
```

It uses a fake HTTP router, fake environment secrets and disposable mounts, no
GPU or live inference service. Bubblewrap runtime tests skip on CI hosts that
prohibit user namespaces; static policy checks still run. Browser injection/CSP
checks should also be rerun after UI changes.

GitHub Pages does **not** support arbitrary response-header configuration from
this repository. A meta CSP cannot enforce `frame-ancestors`, and adding a fake
headers file would not fix that. HTTP-level framing restrictions, nosniff,
Permissions Policy and additional headers require a compatible hosting/proxy
arrangement. This static results site has no privileged browser operations or
credential storage; ownership/other public repos and previously published paths
remain discoverable. These changes do not erase old public Git history or clones.
