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

let selectedFile = null;

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
  previewFilename.textContent = `${file.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)`;
  filePreviewBar.classList.remove('hidden');
}

analyzeBtn.addEventListener('click', runAnalysis);

async function runAnalysis() {
  if (!selectedFile) return;

  emptyState.classList.add('hidden');
  reportView.classList.add('hidden');
  loader.classList.remove('hidden');

  const formData = new FormData();
  formData.append('file', selectedFile);

  const refInput = document.getElementById('ref-file-input');
  if (refInput.files && refInput.files.length > 0) {
    formData.append('reference_file', refInput.files[0]);
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
      alert('Analysis error: ' + (data.error || 'Unknown error'));
      emptyState.classList.remove('hidden');
    }
  } catch (err) {
    loader.classList.add('hidden');
    emptyState.classList.remove('hidden');
    alert('Network or processing error: ' + err.message);
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
    geoStatus.className = 'tele-val text-green';
    addressEl.textContent = geo.resolved_address || `${lat.toFixed(5)}, ${lon.toFixed(5)}`;
    coordsDisplay.textContent = `${lat.toFixed(6)}° N, ${lon.toFixed(6)}° E`;

    initMap(lat, lon, radius);
  } else {
    geoStatus.textContent = 'NO GPS IN METADATA';
    geoStatus.className = 'tele-val text-coral';
    addressEl.textContent = 'Hardware GPS tags stripped or absent.';
    coordsDisplay.textContent = 'COORDINATES UNRESOLVED';
    initMap(0, 0, 0, false);
  }

  // 2. Facial Biometrics
  const faces = data.facial_analysis?.faces || [];
  document.getElementById('res-faces-count').textContent = `${faces.length} Subject${faces.length === 1 ? '' : 's'}`;
  
  const faceList = document.getElementById('face-details-list');
  faceList.innerHTML = '';

  if (faces.length > 0) {
    faces.forEach((f, idx) => {
      faceList.innerHTML += `
        <div class="detail-row">
          <span class="detail-k">Subject #${idx + 1} Frame Coverage</span>
          <span class="detail-v">${f.face_area_pct}% area</span>
        </div>
        <div class="detail-row">
          <span class="detail-k">Landmark Eyes Detected</span>
          <span class="detail-v">${f.eyes_detected}</span>
        </div>
        <div class="detail-row">
          <span class="detail-k">Biometric Vector (Salient 64-d)</span>
          <span class="detail-v">[${f.embedding.slice(0, 4).join(', ')}...]</span>
        </div>
      `;
    });
  } else {
    faceList.innerHTML = '<div class="detail-row"><span class="detail-k">Status</span><span class="detail-v">No human faces isolated</span></div>';
  }

  // 3. Device & Scene Details
  const dev = data.device_telemetry || {};
  const settings = data.camera_settings || {};
  const makeModel = [dev.Make, dev.Model].filter(Boolean).join(' ') || 'Standard Camera/Sensor';
  document.getElementById('res-device').textContent = makeModel;
  document.getElementById('res-timestamp').textContent = data.timestamp || 'No timestamp logged';

  const scene = data.scene_forensics || {};
  const sceneList = document.getElementById('scene-details-list');
  sceneList.innerHTML = `
    <div class="detail-row">
      <span class="detail-k">Environment Type</span>
      <span class="detail-v">${scene.environment_type || 'Unknown'}</span>
    </div>
    <div class="detail-row">
      <span class="detail-k">Perceptual dHash</span>
      <span class="detail-v">${scene.perceptual_hash || 'N/A'}</span>
    </div>
    <div class="detail-row">
      <span class="detail-k">Lighting Condition</span>
      <span class="detail-v">${scene.lighting_profile?.condition || 'Ambient'}</span>
    </div>
    <div class="detail-row">
      <span class="detail-k">Sharpness Metric</span>
      <span class="detail-v">${scene.sharpness_score || 0.0}</span>
    </div>
  `;
}

function initMap(lat, lon, radius, hasCoords = true) {
  const container = document.getElementById('map-container');

  if (!leafletMap) {
    leafletMap = L.map('map-container').setView([hasCoords ? lat : 20, hasCoords ? lon : 0], hasCoords ? 18 : 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap'
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
      color: '#00D2FF',
      fillColor: '#00F59B',
      fillOpacity: 0.25,
      radius: radius || 10
    }).addTo(leafletMap);
  }
}
