"""X-Ray cross-thread tracing helpers for the assistant tools.

WHY THIS EXISTS
---------------
The Strands Agent (strands-agents==1.23.0) runs tool calls on a
ThreadPoolExecutor and the model invocation on its own async event loop — i.e.
OFF the Lambda main thread. aws-xray-sdk's default context is THREAD-LOCAL, so a
subsegment opened on the main thread is INVISIBLE to boto3 calls made on worker
threads: those calls find no active segment on their thread and the resulting
DynamoDB/Bedrock subsegments are silently dropped. That is why the Lambda node
appears in the trace but DynamoDB/Bedrock do not.

THE FIX
-------
Capture the Lambda's active X-Ray entity on the MAIN thread (while the Lambda
segment is live) and re-enter it inside each tool body on the worker thread via
`set_trace_entity(entity)` before opening a subsegment around the boto3 call.
That attaches the worker thread's context to the Lambda trace, so the
DynamoDB/Bedrock subsegments become visible downstream edges.

GUARDED IMPORT
--------------
aws_xray_sdk is imported defensively (mirroring the guarded strands/boto3
imports elsewhere) so this module stays importable — and the pytest suite stays
green — WITHOUT aws-xray-sdk installed. When the SDK is absent OR no parent
entity was captured, `capture_entity` returns None and `traced` is a plain
pass-through that just calls the wrapped function. No behavior changes on the
no-xray path.
"""

try:
    from aws_xray_sdk.core import xray_recorder  # type: ignore

    _XRAY_AVAILABLE = True
except Exception:  # pragma: no cover - aws-xray-sdk not installed in tests
    xray_recorder = None  # type: ignore
    _XRAY_AVAILABLE = False


def capture_entity():
    """Return the X-Ray entity active on the CURRENT thread, or None.

    Call this on the MAIN thread while the Lambda segment/subsegment is active
    so the captured entity is the live Lambda trace (not None). Returns None
    when aws-xray-sdk is absent or there is no active entity, which makes
    `traced` degrade to a plain call.
    """
    if not _XRAY_AVAILABLE:
        return None
    try:
        return xray_recorder.get_trace_entity()
    except Exception:  # pragma: no cover - defensive, no active context
        return None


def traced(name, parent_entity, fn, *args, **kwargs):
    """Run `fn(*args, **kwargs)` inside an X-Ray subsegment named `name`.

    When aws-xray-sdk is available AND `parent_entity` is non-None (captured on
    the main thread), re-attach this (possibly worker) thread's X-Ray context to
    `parent_entity` and wrap the call in a subsegment so the downstream boto3
    call (DynamoDB/Bedrock/S3) shows up as a named subsegment and service-map
    edge. Otherwise just call `fn` directly — so the no-xray path and the unit
    tests are completely unaffected.
    """
    if not _XRAY_AVAILABLE or parent_entity is None:
        return fn(*args, **kwargs)

    # Re-enter the captured Lambda entity on THIS thread so the subsegment we
    # open attaches to the Lambda trace rather than being dropped as an
    # orphaned off-thread segment. If re-attaching fails, fall back to a plain
    # call so X-Ray plumbing can never break the tool.
    try:
        xray_recorder.set_trace_entity(parent_entity)
    except Exception:  # pragma: no cover - defensive
        return fn(*args, **kwargs)

    # in_subsegment manages begin/end + capturing exceptions on the subsegment;
    # errors raised by fn propagate out so the tool's own error handling runs.
    with xray_recorder.in_subsegment(name):
        return fn(*args, **kwargs)
