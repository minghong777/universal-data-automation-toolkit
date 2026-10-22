"""Session-owned state only; no process-global upload or result registry."""
import secrets
from collections.abc import MutableMapping, Callable

EPOCH = '_toolkit_epoch'
PDF_CACHE = '_toolkit_pdf_cache'

def session_epoch(state: MutableMapping) -> str:
    if EPOCH not in state:
        state[EPOCH] = secrets.token_hex(16)
    return state[EPOCH]

def clear_results(state: MutableMapping) -> None:
    state.pop(PDF_CACHE, None)

def clear_session(state: MutableMapping) -> None:
    """Drop this session's widget/result references and rotate uploader identities.

    This does not clear another session or promise secure RAM/browser erasure.
    Streamlit owns uploaded-file buffers and reclaims them on its lifecycle.
    """
    workspace = state.get('workspace', 'Overview')
    for key in list(state):
        del state[key]
    state['workspace'] = workspace
    state[EPOCH] = secrets.token_hex(16)

def pdf_result(state: MutableMapping, fingerprint: str, factory: Callable):
    cached = state.get(PDF_CACHE)
    if cached is None or cached['fingerprint'] != fingerprint:
        # Discard the previous document even if the new extraction fails.
        state.pop(PDF_CACHE, None)
        result = factory()
        state[PDF_CACHE] = {'fingerprint': fingerprint, 'result': result}
    return state[PDF_CACHE]['result']
