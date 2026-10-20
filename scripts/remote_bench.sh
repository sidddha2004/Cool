#!/usr/bin/env bash
# Runs ON the COOL Graviton instance. Fixed, allow-listed procedure: no caller-supplied shell is ever executed.
# Usage: remote_bench.sh <job_dir> <cool_venv_dir> <repeats>
# 5 ABBA blocks (baseline,cool,cool,baseline) expose drift. Both arms use the SAME corpus, candidate and CPU set.
# NOTE: the candidate runs with this instance's privileges (incl. IMDS). Use an instance profile with NO permissions.
set -euo pipefail
JOB="$1"; COOL_VENV="${2:-/opt/cool/venvs/python_3.12}"; REPEATS="${3:-30}"
BLOCKS=5
cd "$JOB"; mkdir -p out; tar xzf bundle.tgz
export PYTHONPATH="$PWD/src"
CAND=$(cat candidate.txt); THREADS=$(cat threads.txt)
export OMP_NUM_THREADS="$THREADS" OPENBLAS_NUM_THREADS="$THREADS" MKL_NUM_THREADS="$THREADS"
CPUS="0-$((THREADS-1))"
TOKEN=$(curl -s -m 3 -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' || true)
imds() { curl -s -m 3 -H "X-aws-ec2-metadata-token: $TOKEN" "http://169.254.169.254/latest/meta-data/$1" || echo unknown; }
cat > out/instance.json <<EOF
{"instance_type": "$(imds instance-type)", "instance_id": "$(imds instance-id)", "region_az": "$(imds placement/availability-zone)",
 "uname_m": "$(uname -m)", "os": "$(. /etc/os-release; echo $PRETTY_NAME)", "nproc": $(nproc), "cool_venv": "$COOL_VENV",
 "cpus_pinned": "$CPUS", "threads": $THREADS, "blocks": $BLOCKS}
EOF
# Baseline: standard pip OpenCV 5 wheel (generic aarch64 build) on the same host, SAME python minor version as COOL venv
COOL_PY="$COOL_VENV/bin/python"
if [ ! -d base_venv ]; then
  "$COOL_PY" -m venv base_venv --without-pip 2>/dev/null || "$COOL_PY" -m venv base_venv
  base_venv/bin/python -m pip install -q "opencv-python-headless==5.0.0.93" "numpy==2.2.*" "psutil==6.*"
fi
"$COOL_PY" -c "import numpy, psutil" 2>/dev/null || "$COOL_VENV/bin/pip" install -q "numpy==2.2.*" "psutil==6.*"
run() { # name python run-index
  taskset -c "$CPUS" "$2" -m coolguard.cli probe > "out/probe_$1.json"
  timeout 900 taskset -c "$CPUS" "$2" -m coolguard.worker --mode bench --candidate "candidates/$CAND" --corpus corpus \
      --out out --repeats "$REPEATS" --threads "$THREADS" --report "out/bench_$1_$3.json" > /dev/null
}
i=0
for b in $(seq 1 $BLOCKS); do
  i=$((i+1)); run baseline base_venv/bin/python $i
  i=$((i+1)); run cool "$COOL_PY" $i
  i=$((i+1)); run cool "$COOL_PY" $i
  i=$((i+1)); run baseline base_venv/bin/python $i
done
"$COOL_PY" -c "import cv2;print(cv2.getBuildInformation())" > out/cool_build_info.txt
base_venv/bin/python -c "import cv2;print(cv2.getBuildInformation())" > out/baseline_build_info.txt
echo DONE
