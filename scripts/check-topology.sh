#!/usr/bin/env bash
# PostToolUse(Write|Edit): warn on §7-forbidden constructs in topology/processor code.
# Exit 1 = warn (non-blocking). Change to exit 2 to hard-block. Patterns from codebase-to-specs.
input=$(cat)
fp=$(printf '%s' "$input" | grep -o '"file_path"[^,}]*' | sed 's/.*"file_path"[": ]*//; s/"//g')
[ -f "$fp" ] || exit 0; case "$fp" in *.java) ;; *) exit 0;; esac
if grep -Eq 'StreamsBuilder|Topology|KStream<|KTable<|\.process\(|ProcessorSupplier|implements Processor' "$fp"; then
  if grep -nE 'JdbcTemplate|MongoTemplate|RestTemplate|WebClient|FeignClient|\.block\(\)|Thread\.sleep|HttpURLConnection|OkHttp|DriverManager|CountDownLatch|CompletableFuture' "$fp"; then
    echo "WARN §7: blocking I/O / DB / sync external call inside topology code in $fp (AGENTS.md MUST NOT). Verify." >&2
    exit 1
  fi
fi
exit 0
