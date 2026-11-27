// SightTrace Forensic Suite — OS/VM Tactical Workstation Controller
let leafletMap = null;
let targetMarker = null;
let perimeterCircle = null;

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const filePreviewBar = document.getElementById('file-preview-bar');
const previewFilename = document.getElementById('preview-filename');
const analyzeBtn = document.getElementById('analyze-btn');
const loader = document.getElementById('loader');
const emptyState = document.getElementById('empty-state');
const reportView = document.getElementById('report-view');
const activeFileIndicator = document.getElementById('active-file-indicator');

let selectedFile = null;

// Initialize Live OS Clock
function updateClock() {
  const clockEl = document.getElementById('os-clock');
  if (clockEl) {
    const now = new Date();
    clockEl.textContent = now.toISOString().replace('T', ' ').substring(11, 19) + ' UTC';
  }
}
setInterval(updateClock, 1000);
updateClock();

// Workstation Tab Switching
const tabButtons = document.querySelectorAll('.tab-btn');
tabButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    tabButtons.forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));

    btn.classList.add('active');
    const targetTabId = btn.getAttribute('data-tab');
    const targetContent = document.getElementById(targetTabId);
    if (targetContent) {
      targetContent.classList.add('active');
    }

    // Invalidate map size if switching to radar tab
    if (targetTabId === 'tab-radar' && leafletMap) {
      setTimeout(() => leafletMap.invalidateSize(), 150);
    }
  });
});

// Drag and drop handlers
dropZone.addEventListener('click', () => fileInput.click());

['dragenter', 'dragover'].forEach(eventName => {
  dropZone.addEventListener(eventName, (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
  });
});

['dragleave', 'drop'].forEach(eventName => {
  dropZone.addEventListener(eventName, (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
  });
});

dropZone.addEventListener('drop', (e) => {
  if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
    handleFileSelected(e.dataTransfer.files[0]);
  }
});

fileInput.addEventListener('change', (e) => {
  if (e.target.files && e.target.files.length > 0) {
    handleFileSelected(e.target.files[0]);
  }
});

function handleFileSelected(file) {
  selectedFile = file;
  const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
  previewFilename.textContent = `${file.name} (${sizeMb} MB)`;
  filePreviewBar.classList.remove('hidden');
  activeFileIndicator.textContent = `TARGET: ${file.name} [${sizeMb} MB]`;

  logTerminal(`[INGEST] Mounted target evidence: ${file.name} (${file.size} bytes)`);
}

analyzeBtn.addEventListener('click', runAnalysis);

// Additional Scan Buttons Wiring
const primaryScanTrigger = document.getElementById('primary-scan-trigger');
if (primaryScanTrigger) {
  primaryScanTrigger.addEventListener('click', () => {
    if (selectedFile) {
      runAnalysis();
    } else {
      fileInput.click();
    }
  });
}

const topTraceBtn = document.getElementById('top-trace-btn');
if (topTraceBtn) {
  topTraceBtn.addEventListener('click', () => {
    if (selectedFile) {
      runAnalysis();
    } else {
      fileInput.click();
    }
  });
}

const heroScanBtn = document.getElementById('hero-scan-btn');
if (heroScanBtn) {
  heroScanBtn.addEventListener('click', () => {
    fileInput.click();
  });
}

const loadSampleBtn = document.getElementById('load-sample-btn');
const heroSampleBtn = document.getElementById('hero-sample-btn');

[loadSampleBtn, heroSampleBtn].forEach(btn => {
  if (btn) {
    btn.addEventListener('click', runSampleAnalysis);
  }
});

async function runSampleAnalysis() {
  emptyState.classList.add('hidden');
  reportView.classList.add('hidden');
  loader.classList.remove('hidden');

  logTerminal(`[SAMPLE-INGEST] Requesting reference forensic sample with verified 10m coordinates...`);

  try {
    const res = await fetch('/api/sample');
    const data = await res.json();
    loader.classList.add('hidden');

    if (data.success) {
      activeFileIndicator.textContent = `TARGET: sample_forensic_evidence.jpg [DEMO]`;
      renderReport(data);
      logTerminal(`[SAMPLE-COMPLETE] Forensic telemetry successfully rendered.`);
    } else {
      alert('Sample trace error: ' + (data.error || 'Unknown error'));
      emptyState.classList.remove('hidden');
    }
  } catch (err) {
    loader.classList.add('hidden');
    emptyState.classList.remove('hidden');
    alert('Failed to load sample: ' + err.message);
  }
}

async function runAnalysis() {
  if (!selectedFile) return;

  emptyState.classList.add('hidden');
  reportView.classList.add('hidden');
  loader.classList.remove('hidden');

  logTerminal(`[DEEP-SCAN] Ingesting binary stream for forensic feature extraction...`);

  const formData = new FormData();
  formData.append('file', selectedFile);

  const refInput = document.getElementById('ref-file-input');
  if (refInput.files && refInput.files.length > 0) {
    formData.append('reference_file', refInput.files[0]);
    logTerminal(`[MATCH] Loaded reference identity: ${refInput.files[0].name}`);
  }

  try {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      body: formData
    });

    const data = await res.json();
    loader.classList.add('hidden');

    if (data.success) {
      renderReport(data);
    } else {
      alert('Forensic processing error: ' + (data.error || 'Unknown error'));
      emptyState.classList.remove('hidden');
      logTerminal(`[ERROR] Processing failed: ${data.error}`);
    }
  } catch (err) {
    loader.classList.add('hidden');
    emptyState.classList.remove('hidden');
    alert('Network or processing error: ' + err.message);
    logTerminal(`[CRITICAL] Network error: ${err.message}`);
  }
}

function renderReport(data) {
  reportView.classList.remove('hidden');

  // 1. Geolocation Telemetry
  const geo = data.geolocation || {};
  const geoStatus = document.getElementById('res-geo-status');
  const addressEl = document.getElementById('res-address');
  const coordsDisplay = document.getElementById('coords-display');

  if (geo.has_coordinates && geo.coordinates) {
    const lat = geo.coordinates.latitude;
    const lon = geo.coordinates.longitude;
    const radius = geo.accuracy_radius_m || 10.0;

    geoStatus.textContent = `RESOLVED (±${radius}m)`;
    geoStatus.className = 'metric-val text-emerald';
    addressEl.textContent = geo.resolved_address || `${lat.toFixed(5)}, ${lon.toFixed(5)}`;
    coordsDisplay.textContent = `${lat.toFixed(6)}° N, ${lon.toFixed(6)}° E`;

    initMap(lat, lon, radius);
    logTerminal(`[GPS] Precision coordinates resolved: ${lat.toFixed(6)}, ${lon.toFixed(6)} (Radius ±${radius}m)`);
  } else {
    geoStatus.textContent = 'HARDWARE GPS ABSENT';
    geoStatus.className = 'metric-val text-coral';
    addressEl.textContent = 'EXIF GPS tags stripped or sensor disabled.';
    coordsDisplay.textContent = 'COORDINATES UNRESOLVED';
    initMap(0, 0, 0, false);
    logTerminal(`[GPS] Hardware coordinates absent. Defaulting to enclave global map.`);
  }

  // 2. Deep Learning Neural Tensors & Domain Classification
  const deep = data.deep_learning || {};
  const domainStatus = document.getElementById('res-domain-status');
  const modelDevice = document.getElementById('res-model-device');

  if (deep.domain_prediction) {
    const conf = (deep.domain_confidence_pct || 0).toFixed(1);
    domainStatus.textContent = `${deep.domain_prediction.toUpperCase()} (${conf}%)`;
    modelDevice.textContent = `${deep.model_architecture || 'MobileNetV3'} (${deep.device || 'CPU'})`;
    document.getElementById('res-arch-name').textContent = deep.model_architecture || 'MobileNetV3-DeepForensics';
    document.getElementById('res-device-name').textContent = deep.device || 'CPU';
    document.getElementById('tensor-energy-pill').textContent = `ENERGY: ${(deep.tensor_energy || 1.0).toFixed(4)}`;
    document.getElementById('res-sparsity-val').textContent = `${((deep.sparsity_ratio || 0) * 100).toFixed(2)}%`;
    document.getElementById('domain-top-pill').textContent = `TOP: ${deep.domain_prediction}`;

    // Render 576-d Latent Micro Spectrum
    renderTensorSpectrum(deep.latent_vector_salient || []);

    // Render Domain Classification Probability Bars
    renderDomainBars(deep.domain_probabilities || {}, deep.domain_prediction);

    logTerminal(`[TORCH] Penultimate 576-d latent vector extracted. Energy: ${deep.tensor_energy}`);
    logTerminal(`[DOMAIN] Environment classified as: ${deep.domain_prediction} (Confidence: ${conf}%)`);
  }

  // 3. Facial Biometrics
  const faces = data.facial_analysis?.faces || [];
  const faceCountEl = document.getElementById('res-faces-count');
  faceCountEl.textContent = `${faces.length} Subject${faces.length === 1 ? '' : 's'} Isolated`;
  
  const faceList = document.getElementById('face-details-list');
  faceList.innerHTML = '';

  if (faces.length > 0) {
    faces.forEach((f, idx) => {
      faceList.innerHTML += `
        <div class="detail-row">
          <span class="detail-k">Subject #${idx + 1} Frame Coverage</span>
          <span class="detail-v text-emerald">${f.face_area_pct}% area</span>
        </div>
        <div class="detail-row">
          <span class="detail-k">Landmark Eyes Detected</span>
          <span class="detail-v text-cyan">${f.eyes_detected}</span>
        </div>
        <div class="detail-row">
          <span class="detail-k">Biometric 64-d Salient Tensor</span>
          <span class="detail-v">[${f.embedding.slice(0, 4).join(', ')}...]</span>
        </div>
        <div class="detail-row">
          <span class="detail-k">Facial Sharpness Score</span>
          <span class="detail-v">${f.sharpness_score}</span>
        </div>
      `;
    });
    logTerminal(`[BIOMETRICS] Isolated ${faces.length} biometric subject(s). Landmark eye detection verified.`);
  } else {
    faceList.innerHTML = '<div class="detail-row"><span class="detail-k">Biometric Scan</span><span class="detail-v text-muted">No human face isolated in primary frame</span></div>';
    logTerminal(`[BIOMETRICS] No faces isolated in primary frame.`);
  }

  // 4. Reference Identity Match
  const idMatchView = document.getElementById('identity-match-view');
  if (data.identity_match) {
    const im = data.identity_match;
    idMatchView.innerHTML = `
      <div class="detail-row">
        <span class="detail-k">Match Classification</span>
        <span class="detail-v text-emerald">${im.match ? 'VERIFIED IDENTITY MATCH' : 'NON-MATCHING SUBJECT'}</span>
      </div>
      <div class="detail-row">
        <span class="detail-k">Cosine Similarity</span>
        <span class="detail-v text-cyan">${im.similarity_pct}%</span>
      </div>
      <div class="detail-row">
        <span class="detail-k">Confidence Level</span>
        <span class="detail-v">${im.confidence}</span>
      </div>
    `;
    logTerminal(`[MATCH] Reference identity compared: ${im.similarity_pct}% similarity (${im.confidence})`);
  }

  // 5. Device & Scene Details
  const dev = data.device_telemetry || {};
  const makeModel = [dev.Make, dev.Model].filter(Boolean).join(' ') || 'Standard Camera / Sensor';
  document.getElementById('res-device').textContent = makeModel;
  document.getElementById('res-timestamp').textContent = data.timestamp || 'No timestamp logged';

  const scene = data.scene_forensics || {};
  const sceneList = document.getElementById('scene-details-list');
  sceneList.innerHTML = `
    <div class="detail-row">
      <span class="detail-k">Scene Environment Profile</span>
      <span class="detail-v">${scene.environment_type || 'Unknown'}</span>
    </div>
    <div class="detail-row">
      <span class="detail-k">Perceptual dHash Signature</span>
      <span class="detail-v text-cyan">${scene.perceptual_hash || 'N/A'}</span>
    </div>
    <div class="detail-row">
      <span class="detail-k">Lighting Assessment</span>
      <span class="detail-v">${scene.lighting_profile?.condition || 'Ambient'}</span>
    </div>
    <div class="detail-row">
      <span class="detail-k">High-Frequency Edge Sharpness</span>
      <span class="detail-v">${scene.sharpness_score || 0.0}</span>
    </div>
  `;
}

function renderTensorSpectrum(salientValues) {
  const container = document.getElementById('tensor-spectrum');
  container.innerHTML = '';

  // Generate 64 visual spectrum bars based on salient values or normalized projections
  const barsCount = 64;
  for (let i = 0; i < barsCount; i++) {
    const val = salientValues[i] !== undefined ? Math.abs(salientValues[i]) : (Math.sin(i * 0.3) * 0.5 + 0.5);
    const heightPct = Math.max(8, Math.min(100, Math.round(val * 100)));
    const bar = document.createElement('div');
    bar.className = 'tensor-bar';
    bar.style.height = `${heightPct}%`;
    bar.title = `Dim #${i * 9}: ${(val).toFixed(4)}`;
    container.appendChild(bar);
  }
}

function renderDomainBars(probabilities, topDomain) {
  const container = document.getElementById('domain-prob-list');
  container.innerHTML = '';

  for (const [domain, prob] of Object.entries(probabilities)) {
    const pct = (prob * 100).toFixed(1);
    const isTop = domain === topDomain;
    
    const row = document.createElement('div');
    row.className = 'domain-bar-row';
    row.innerHTML = `
      <div class="domain-bar-meta">
        <span class="domain-name ${isTop ? 'text-emerald' : ''}">${isTop ? '▶ ' : ''}${domain}</span>
        <span class="domain-pct ${isTop ? 'text-emerald' : ''}">${pct}%</span>
      </div>
      <div class="domain-progress-track">
        <div class="domain-progress-fill" style="width: ${pct}%; ${isTop ? 'background: linear-gradient(90deg, #00FF88 0%, #00E5FF 100%);' : ''}"></div>
      </div>
    `;
    container.appendChild(row);
  }
}

function initMap(lat, lon, radius, hasCoords = true) {
  const container = document.getElementById('map-container');

  if (!leafletMap) {
    leafletMap = L.map('map-container').setView([hasCoords ? lat : 20, hasCoords ? lon : 0], hasCoords ? 18 : 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap Forensics'
    }).addTo(leafletMap);
  } else {
    leafletMap.setView([hasCoords ? lat : 20, hasCoords ? lon : 0], hasCoords ? 18 : 2);
  }

  if (targetMarker) leafletMap.removeLayer(targetMarker);
  if (perimeterCircle) leafletMap.removeLayer(perimeterCircle);

  if (hasCoords) {
    targetMarker = L.marker([lat, lon]).addTo(leafletMap)
      .bindPopup(`<b>Target Pinpoint</b><br>${lat.toFixed(6)}, ${lon.toFixed(6)}`)
      .openPopup();

    perimeterCircle = L.circle([lat, lon], {
      color: '#00E5FF',
      fillColor: '#00FF88',
      fillOpacity: 0.25,
      radius: radius || 10
    }).addTo(leafletMap);
  }
}

function logTerminal(message) {
  const consoleEl = document.getElementById('terminal-console');
  if (!consoleEl) return;

  const now = new Date();
  const timeStr = `[${(now.getTime() % 100000 / 1000).toFixed(6).padStart(9, ' ')}]`;

  const line = document.createElement('div');
  line.className = 'terminal-line';
  line.innerHTML = `<span class="term-prefix">${timeStr}</span> ${message}`;

  const promptEl = consoleEl.querySelector('.term-prompt');
  if (promptEl) {
    consoleEl.insertBefore(line, promptEl);
  } else {
    consoleEl.appendChild(line);
  }

  consoleEl.scrollTop = consoleEl.scrollHeight;
}
