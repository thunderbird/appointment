#!/usr/bin/env bash
# Behavioural test for docker/etc/nginx/conf.d/appointments.conf.
#
# WHY THIS EXISTS: `nginx -t` only proves the config parses. Every interesting way
# to break this file -- declaring `root` inside `location /` so sibling locations
# 404, a mis-scoped `add_header`, an `/assets/` rule that stops matching -- is
# syntactically valid and passes `nginx -t`.
#
# A *total* root mis-scope is NOT the case this script is for: that one fails
# closed on its own. Verified in a container -- with `root` back inside
# `location /`, `/`, `/index.html`, `/config.js`, `/user/foo` AND `/assets/*` all
# 404 (`open() "/etc/nginx/html/index.html" failed`), because the try_files
# fallback re-runs location matching into `location = /index.html`, which has no
# root. The rollout's readiness probe on `/` therefore never goes green and the
# synthetic analysis fails its very first probe.
#
# What neither in-cluster gate can see is breakage CONFINED TO `/assets/`, or a
# WRONG OR LEAKED `Cache-Control` value on a path that still returns 200. Those
# promote green -- that is what this script exists to catch.
#
# Runs the shipped conf in a stock nginx image over a SYNTHETIC dist tree (no
# npm build, no registry auth, no AWS creds -- ~20s). It tests location matching
# and headers, not the real bundle.
#
# Usage: frontend/docker/test-nginx-config.sh
# Env:   NGINX_IMAGE (default docker.io/library/nginx:stable), PORT (default 18150)

set -euo pipefail

NGINX_IMAGE="${NGINX_IMAGE:-docker.io/library/nginx:stable}"
PORT="${PORT:-18150}"
NAME="appt-nginx-conftest-$$"

if command -v podman >/dev/null 2>&1; then ENGINE=podman; else ENGINE=docker; fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONF_SRC="${SCRIPT_DIR}/etc/nginx/conf.d/appointments.conf"
[ -f "$CONF_SRC" ] || { echo "FATAL: conf not found at $CONF_SRC"; exit 1; }

TMP="$(mktemp -d)"
cleanup() {
  "$ENGINE" rm -f "$NAME" >/dev/null 2>&1 || true
  rm -rf "$TMP"
}
trap cleanup EXIT

# Synthetic dist tree mirroring what `vite build` emits into /usr/share/nginx/html.
# The .js.map is present ON DISK on purpose: the guard must beat try_files.
#
# FIXTURE SIZES ARE LOAD-BEARING, do not shrink them. The realistic way anyone
# enables origin gzip is `gzip on;` plus a `gzip_min_length` (1000 is the value
# everybody copies), and nginx's DEFAULT `gzip_types` is `text/html` alone. With a
# tiny 83-byte shell and a 23-byte bundle, every such config leaves both responses
# uncompressed and the compression assertions below pass vacuously (verified). So:
#   - the SPA shell is padded past 1000 bytes, which is what catches `gzip on;`
#     with or without a `gzip_min_length` (the real shell is ~1.6 KB anyway);
#   - the bundle is ~64 KB, which is what catches a `gzip_types` list that adds
#     application/javascript -- there the response comes back chunked with
#     Content-Encoding: gzip and NO Content-Length.
#
# Both are generated with awk rather than `yes ... | head`: under `set -o pipefail`
# that idiom kills the script, because `yes` exits 141 on SIGPIPE once head closes.
mkdir -p "$TMP/html/assets" "$TMP/conf"
cp "$CONF_SRC" "$TMP/conf/default.conf"
awk 'BEGIN {
  print "<!doctype html><html><head><title>appt</title>";
  pad = ""; while (length(pad) < 40) pad = pad "a";
  for (i = 1; i <= 30; i++) printf "<meta name=\"pad-%02d\" content=\"%s\">\n", i, pad;
  print "</head><body>SPA SHELL</body></html>";
}' > "$TMP/html/index.html"
printf 'window.__APP_CONFIG__ = {"apiUrl":"http://localhost"};\n' > "$TMP/html/config.js"
awk 'BEGIN { for (i = 0; i < 4000; i++) print "console.log(1);" }' \
  > "$TMP/html/assets/index-abc123.js"
printf '{"version":3,"sources":[]}\n' > "$TMP/html/assets/index-abc123.js.map"
printf 'body{color:#000}\n' > "$TMP/html/assets/index-abc123.css"
printf '<svg xmlns="http://www.w3.org/2000/svg"></svg>\n' > "$TMP/html/favicon.svg"
printf '{"name":"appt"}\n' > "$TMP/html/site.webmanifest"
printf 'https://example.invalid/\n' > "$TMP/html/sitemap.txt"

# conf.d mounted rw: the stock entrypoint's 10-listen-on-ipv6 script edits it.
# Mounting the whole dir also removes the stock default.conf, avoiding a
# duplicate :80 default_server.
"$ENGINE" run -d --name "$NAME" -p "127.0.0.1:${PORT}:80" \
  -v "$TMP/conf:/etc/nginx/conf.d:z" \
  -v "$TMP/html:/usr/share/nginx/html:ro,z" \
  "$NGINX_IMAGE" >/dev/null

echo "== nginx -t =="
"$ENGINE" exec "$NAME" nginx -t

for _ in $(seq 1 30); do
  curl -fsS -o /dev/null "http://127.0.0.1:${PORT}/" && break
  sleep 1
done

BASE="http://127.0.0.1:${PORT}"
FAILED=0
pass() { printf 'PASS  %s\n' "$1"; }
fail() { printf 'FAIL  %s\n' "$1"; FAILED=$((FAILED + 1)); }

# EVERY probe offers gzip/deflate/br. Folded in here rather than bolted onto one
# call site so that no path can quietly start compressing: origin compression must
# be off everywhere (see the Content-Encoding assertion below), not just on the
# bundle that happened to get the header in a previous revision of this script.
probe_ae='Accept-Encoding: gzip, deflate, br'

# probe <label> <path> <expected-status> <expected-cache-control|-> [extra curl args...]
probe() {
  local label="$1" path="$2" want_status="$3" want_cc="$4"; shift 4
  local hdrs status cc enc
  hdrs="$(curl -sS -D - -o /dev/null -H "$probe_ae" "$@" "${BASE}${path}")"
  status="$(printf '%s' "$hdrs" | awk 'NR==1{print $2}')"
  cc="$(printf '%s' "$hdrs" | tr -d '\r' | awk -F': ' 'tolower($1)=="cache-control"{print $2}')"
  enc="$(printf '%s' "$hdrs" | tr -d '\r' | awk -F': ' 'tolower($1)=="content-encoding"{print $2}')"
  local n_cc
  n_cc="$(printf '%s' "$hdrs" | tr -d '\r' | awk -F': ' 'tolower($1)=="cache-control"' | wc -l | tr -d ' ')"
  [ "$want_cc" = "-" ] && want_cc=""
  if [ "$status" = "$want_status" ] && [ "$cc" = "$want_cc" ] && [ "$n_cc" -le 1 ] && [ -z "$enc" ]; then
    pass "$label -> $status cache-control='${cc}'"
  else
    fail "$label -> got status=$status cache-control='${cc}' (count=$n_cc) content-encoding='${enc}', want status=$want_status cache-control='${want_cc}' content-encoding=''"
  fi
}

echo "== cache headers =="
probe "hashed JS"            /assets/index-abc123.js      200 "public, max-age=31536000, immutable"
probe "hashed CSS"           /assets/index-abc123.css     200 "public, max-age=31536000, immutable"
probe "missing asset"        /assets/missing-000.js        404 -
probe "sourcemap (on disk)"  /assets/index-abc123.js.map   404 -
probe "sourcemap (absent)"   /assets/nope.js.map           404 -
probe "root"                 /                             200 "no-store"
probe "index.html"           /index.html                   200 "no-store"
probe "deep SPA route"       /user/foo                     200 "no-store"
probe "config.js"            /config.js                    200 "no-store"
probe "favicon"              /favicon.svg                  200 "public, max-age=300"
probe "sitemap"              /sitemap.txt                  200 "public, max-age=300"
probe "webmanifest"          /site.webmanifest             200 "public, max-age=300"

echo "== content types =="
ct() { curl -sS -o /dev/null -w '%{content_type}' "${BASE}$1"; }
case "$(ct /site.webmanifest)" in
  application/manifest+json*) pass "webmanifest content-type" ;;
  *) fail "webmanifest content-type -> $(ct /site.webmanifest), want application/manifest+json" ;;
esac
case "$(ct /sitemap.txt)" in
  text/plain*) pass "sitemap content-type (mime map not clobbered)" ;;
  *) fail "sitemap content-type -> $(ct /sitemap.txt), want text/plain" ;;
esac

echo "== SPA shell served on deep route =="
if curl -sS "${BASE}/user/foo" | grep -q 'SPA SHELL'; then
  pass "deep route body is the SPA shell"
else
  fail "deep route body is NOT the SPA shell"
fi

echo "== no origin compression (edge Brotli must win) =="
# Content-Encoding absence is already asserted on EVERY probe above, so the extra
# assertion here is the one that actually matters for the CDN: nginx gzip switches
# the response to chunked and DROPS Content-Length, and AWS documents that a
# missing Content-Length can make CloudFront cache a PARTIAL object (#814). It is
# the loss of the header, not the value of Content-Encoding, that is the hazard.
cl="$(curl -sS -D - -o /dev/null -H "$probe_ae" "${BASE}/assets/index-abc123.js" \
       | tr -d '\r' | awk -F': ' 'tolower($1)=="content-length"{print $2}')"
if [ -n "$cl" ]; then
  pass "bundle keeps Content-Length (${cl} bytes, not chunked)"
else
  fail "bundle has NO Content-Length -- response is chunked, CloudFront may cache a partial object"
fi

echo "== access log: JSON, populated, real_ip resolved -- both vhosts =="
# One probe per vhost, each carrying a known X-Forwarded-For so the real_ip
# assertion has a deterministic expected value on both server blocks.
XFF_PROBE=203.0.113.9
curl -sS -o /dev/null -H "X-Forwarded-For: ${XFF_PROBE}" "${BASE}/logprobe-default" || true
curl -sS -o /dev/null -H 'Host: stage.apt.mt' -H "X-Forwarded-For: ${XFF_PROBE}" \
  "${BASE}/logprobe-shortlink" || true
sleep 1

# Select access-log lines by EXCLUDING the things we know are not access logs
# (entrypoint chatter, `[notice]`/`[error]` lines). An include-filter anchored on
# `^{` would silently match nothing the moment the log_format stops being JSON, and
# "nothing matched" must never be indistinguishable from "everything passed" --
# that is exactly how the earlier version of this check passed with `access_log
# off;`, with a logfmt log_format, and with fields deleted (all verified).
LOG_LINES="$("$ENGINE" logs "$NAME" 2>&1 \
  | grep -vE '^([0-9]{4}/[0-9]{2}/[0-9]{2} |[^ ]*\.sh: |nginx: )' \
  | grep -vE '^[[:space:]]*$' || true)"

seen=0
bad=0
while IFS= read -r line; do
  [ -n "$line" ] || continue
  seen=$((seen + 1))
  case "$line" in
    '{'*) ;;
    *) bad=$((bad + 1)); echo "  non-JSON log line: $line" ;;
  esac
done < <(printf '%s\n' "$LOG_LINES")

if [ "$seen" -eq 0 ]; then
  fail "NO access log lines captured at all -- access_log is off, misdirected, or the format changed"
elif [ "$bad" -ne 0 ]; then
  fail "$bad of $seen access log line(s) are not JSON"
else
  pass "$seen access log line(s) captured, all JSON-shaped"
fi

if command -v jq >/dev/null 2>&1; then
  # Every line must actually parse, not just start with a brace.
  invalid=0
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    printf '%s' "$line" | jq -e . >/dev/null 2>&1 || {
      invalid=$((invalid + 1)); echo "  invalid JSON: $line"; }
  done < <(printf '%s\n' "$LOG_LINES")
  if [ "$seen" -eq 0 ]; then
    fail "no access log lines to parse"
  elif [ "$invalid" -eq 0 ]; then
    pass "every access log line parses as JSON"
  else
    fail "$invalid invalid JSON access log line(s) (of $seen)"
  fi

  # Field presence + real_ip resolution, asserted separately on EACH vhost: the
  # shortlink server block needs its own `access_log` line, and real_ip is at http
  # scope precisely so it reaches both.
  for vh in default shortlink; do
    line="$(printf '%s\n' "$LOG_LINES" | grep -F "logprobe-${vh}" | grep '^{' | tail -1 || true)"
    if [ -z "$line" ]; then
      fail "${vh} vhost: no JSON access log line for /logprobe-${vh}"
      continue
    fi
    if printf '%s' "$line" | jq -e 'has("x_forwarded_for") and has("cf_id")
          and has("request_time") and has("upstream_response_time")
          and has("user_agent")' >/dev/null 2>&1; then
      pass "${vh} vhost: log line has x_forwarded_for, cf_id, request_time, upstream_response_time, user_agent"
    else
      fail "${vh} vhost: log line is missing a required field -> $line"
    fi
    ra="$(printf '%s' "$line" | jq -r '.remote_addr // ""' 2>/dev/null || true)"
    if [ "$ra" = "$XFF_PROBE" ]; then
      pass "${vh} vhost: real_ip resolved remote_addr to ${ra} from X-Forwarded-For"
    else
      fail "${vh} vhost: remote_addr='${ra}', want '${XFF_PROBE}' -- set_real_ip_from/real_ip_header not in effect"
    fi
  done
elif [ -n "${CI:-}" ]; then
  # jq ships on ubuntu-latest. If it is missing in CI the assertions above did not
  # run, and a silently-skipped assertion is the failure mode this whole section
  # was rewritten to remove.
  fail "jq not found but CI is set -- the log field and real_ip assertions did not run"
else
  echo "SKIP  jq not installed; log field + real_ip assertions skipped"
  echo "      (line-count and JSON-shape checks above still ran and still count)"
fi

echo
if [ "$FAILED" -eq 0 ]; then
  echo "ALL PROBES PASSED"
else
  echo "$FAILED PROBE(S) FAILED"
  exit 1
fi
