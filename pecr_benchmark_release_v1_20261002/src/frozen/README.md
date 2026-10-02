Frozen function dependencies for separately versioned future response ingestion.
The G96 builder and label policy are byte-identical reuse of already released code.
The parser retains exact historical functions and does not contain ledger/corpus drivers.
No new-generation ingestion/label/G stage was executed in this release.
The original numeric answer type must be retained for label_one; do not replace it
with the response parser float. Unit normalization is applied to Raw/Curve responses;
G96 consumes the original raw answer/unit/confidence. _graph returns float32,
then the benchmark exports its exact values as float64. Supporting_evidence is
validated but not consumed by G96. Native/graph/label failures must remain visible;
never fill them with a historical default or copy a saved target label.
