'use strict';
// A SHA match recognizes prevalidated published bytes. This is NOT an arbitrary TIFF parser.
const manifestNode = document.getElementById('submission-manifest');
const submission = manifestNode ? JSON.parse(manifestNode.textContent) : {files: []};
const filesByName = new Map(submission.files.map(file => [file.name, file]));
function message(node, text, good = null) {
  if (!node) return;
  node.textContent = text;
  node.classList.toggle('good', good === true);
  node.classList.toggle('bad', good === false);
}
async function sha256(bytes) {
  if (!window.crypto?.subtle) throw new Error('Browser SHA-256 is unavailable. Use the Python validator or the explicitly labelled direct link.');
  return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), b => b.toString(16).padStart(2, '0')).join('');
}
async function verifyBytes(bytes, spec) {
  if (!spec || bytes.byteLength !== spec.bytes) throw new Error('Byte length mismatch — no file saved.');
  const hash = await sha256(bytes);
  if (hash !== spec.sha256) throw new Error('SHA-256 mismatch — no file saved. Run the Python validator; do not upload.');
  return hash;
}
for (const link of document.querySelectorAll('[data-verified-download]')) {
  link.addEventListener('click', async event => {
    event.preventDefault();
    if (link.getAttribute('aria-disabled') === 'true') return;
    const spec = filesByName.get(link.dataset.verifiedDownload);
    const status = document.querySelector('[data-download-status]');
    link.setAttribute('aria-disabled', 'true');
    message(status, 'Fetching and verifying every byte…');
    try {
      if (!spec || !/^downloads\/[A-Za-z0-9._-]+\.(tif|zip)$/.test(spec.href)) throw new Error('Unknown published file.');
      const response = await fetch(new URL(spec.href, document.baseURI), {cache: 'no-store'});
      if (!response.ok) throw new Error(`Download failed (HTTP ${response.status}); no file saved.`);
      const bytes = await response.arrayBuffer();
      await verifyBytes(bytes, spec);
      const objectURL = URL.createObjectURL(new Blob([bytes], {type: spec.name.endsWith('.zip') ? 'application/zip' : 'image/tiff'}));
      const save = document.createElement('a');
      save.href = objectURL;
      save.download = spec.name;
      document.body.append(save);
      save.click();
      save.remove();
      setTimeout(() => URL.revokeObjectURL(objectURL), 30000);
      message(status, `SHA-256 verified. Saved ${spec.name}. Historical field — not a new model.`, true);
    } catch (error) {
      message(status, error.message || 'Verification failed; no file saved.', false);
    } finally {
      link.removeAttribute('aria-disabled');
    }
  });
}
for (const button of document.querySelectorAll('[data-copy]')) {
  button.addEventListener('click', async () => {
    const status = button.closest('.note-box')?.querySelector('.copy-status');
    try {
      await navigator.clipboard.writeText(button.dataset.copy);
      message(status, 'Note copied.', true);
    } catch (_) {
      document.getElementById('submission-note')?.select();
      message(status, 'Clipboard blocked. The note is selected; copy it using your keyboard.');
    }
  });
}
const fileInput = document.getElementById('local-file');
fileInput?.addEventListener('change', async () => {
  const file = fileInput.files[0];
  const status = document.getElementById('file-check-result');
  if (!file) return;
  if (!submission.files.some(spec => spec.bytes === file.size)) {
    message(status, 'Not a recognized prevalidated published file (byte length differs). Arbitrary GeoTIFF compliance is NOT checked here. Run the strict Python validator; do not upload yet.', false);
    return;
  }
  message(status, 'Checking full-file SHA-256 locally…');
  try {
    const hash = await sha256(await file.arrayBuffer());
    const spec = submission.files.find(spec => spec.bytes === file.size && spec.sha256 === hash);
    if (!spec) throw new Error('SHA-256 does not match any prevalidated download. Unknown/corrupt file — run Python preflight before uploading.');
    message(status, `Recognized ${spec.role}: ${spec.name}. Full bytes match the local Python-validated release. Platform acceptance and score remain unverified.`, true);
  } catch (error) {
    message(status, error.message, false);
  }
});
for (const input of document.querySelectorAll('[data-filter]')) {
  input.addEventListener('input', () => {
    const term = input.value.toLowerCase().trim();
    for (const row of document.querySelectorAll(`#${input.dataset.filter} tbody tr`)) row.hidden = !row.textContent.toLowerCase().includes(term);
  });
}
// Public GitHub release metadata supports CORS; no secrets and no DrivenData polling.
function cell(text) { const td = document.createElement('td'); td.textContent = text; return td; }
function validateFeed(feed) {
  if (feed.kind !== 'permitted-source-health-only' || feed.drivendata_requests !== 0 || !Array.isArray(feed.sources) || !Array.isArray(feed.repositories)) throw new Error('Unexpected feed schema');
  if (!Number.isFinite(Date.parse(feed.generated_utc))) throw new Error('Invalid feed timestamp');
  return feed;
}
async function sourceFeed() {
  const summary = document.getElementById('feed-summary');
  if (!summary) return;
  let feed;
  let origin;
  try {
    const response = await fetch('https://api.github.com/repos/buffedlizard55-lab/GEMSDOE21/releases/tags/source-feed', {headers: {Accept: 'application/vnd.github+json'}});
    if (!response.ok) throw new Error('Release feed unavailable');
    const release = await response.json();
    feed = validateFeed(JSON.parse(release.body));
    origin = 'Latest permitted-source GitHub release';
  } catch (_) {
    try {
      const response = await fetch(new URL('data/source-health.json', document.baseURI), {cache: 'no-store'});
      if (!response.ok) throw new Error('Saved feed unavailable');
      feed = validateFeed(await response.json());
      origin = 'Saved snapshot (live release unavailable)';
    } catch (_) {
      message(summary, 'No usable feed. No freshness claim is made; see the source registry and workflow logs.', false);
      return;
    }
  }
  const ageHours = (Date.now() - Date.parse(feed.generated_utc)) / 3600000;
  const recent = ageHours >= -0.1 && ageHours <= 48;
  const badge = document.getElementById('feed-badge');
  badge.textContent = recent ? 'CHECKED WITHIN 48H' : 'STALE / CHECK TIMESTAMP';
  badge.classList.toggle('reject', !recent);
  const reachable = feed.sources.filter(s => s.status === 'reachable').length;
  message(summary, `${origin}. Checked ${feed.generated_utc}: ${reachable}/${feed.sources.length} data endpoints reachable from that runner; ${feed.repositories.length} repository HEAD records. Zero DrivenData requests.`, null);
  const tbody = document.querySelector('#health-table tbody');
  for (const item of feed.sources) {
    const tr = document.createElement('tr');
    tr.append(cell(`${item.id} · ${item.title}`), cell(item.status), cell(item.error || `HTTP ${item.http_status ?? '—'}; sampled ${item.sampled_bytes ?? 0} bytes; ${item.magic ?? 'metadata'}. Transport only; not coverage validation.`));
    tbody.append(tr);
  }
  const list = document.getElementById('repo-health');
  for (const repo of feed.repositories) {
    const li = document.createElement('li');
    li.textContent = `${repo.repository}: ${repo.status}; HEAD ${repo.head?.slice(0, 10) ?? 'unknown'}${repo.committed_utc ? ` · ${repo.committed_utc}` : ''}. ${repo.message || repo.error || ''}`;
    list.append(li);
  }
}
sourceFeed();
