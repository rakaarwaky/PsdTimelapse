<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { toast } from 'vue-sonner';
import RenderProgress from './RenderProgress.vue';
import VideoPlayer from './VideoPlayer.vue';
import { useRenderSession } from '../composables/useRenderSession';

// Detect if running in Tauri
const isTauri = ref(false);
const fileInputRef = ref<HTMLInputElement | null>(null);
const pendingFile = ref<File | null>(null);

// Use Application Logic (Composable)
const {
  selectedFile,
  selectedFileName,
  outputPath,
  isProcessing,
  progress,
  serverConnected,
  renderSettings,
  canProcess,
  checkServer,
  resetSession,
  startRender
} = useRenderSession();

// Check if Tauri is available & Init Server Check
onMounted(async () => {
  try {
    // @ts-ignore
    if (window.__TAURI_INTERNALS__) {
      isTauri.value = true;
    }
  } catch {
    isTauri.value = false;
  }
  checkServer();
});

// UI: File Selection Handling (Tauri vs Browser)
const handleSelectFile = async () => {
  if (isTauri.value) {
    try {
      const { open } = await import('@tauri-apps/plugin-dialog');
      const selected = await open({
        multiple: false,
        filters: [{
          name: 'PSD Files',
          extensions: ['psd', 'psb']
        }]
      });
      
      if (selected && typeof selected === 'string') {
        resetSession();
        selectedFile.value = selected;
        selectedFileName.value = selected.split('/').pop() || selected;
      }
    } catch (err) {
      console.error('Failed to open Tauri dialog:', err);
      toast.error('Failed to select file');
    }
  } else {
    fileInputRef.value?.click();
  }
};

const handleFileInputChange = (event: Event) => {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  
  if (file) {
    resetSession();
    pendingFile.value = file;
    selectedFileName.value = file.name;
    selectedFile.value = file.name;
    toast.success(`Selected: ${file.name}`);
  }
  input.value = '';
};

// UIWrapper for Start Process
const handleProcess = async () => {
  await startRender(pendingFile.value);
  pendingFile.value = null; // Clear after upload
};

// UI Input Handlers (Drag & Drop)
const isDragging = ref(false);

const handleDragOver = (event: DragEvent) => {
  event.preventDefault();
  isDragging.value = true;
};

const handleDragLeave = () => {
  isDragging.value = false;
};

const handleDrop = (event: DragEvent) => {
  event.preventDefault();
  isDragging.value = false;
  
  const file = event.dataTransfer?.files[0];
  if (file) {
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext === 'psd' || ext === 'psb') {
      resetSession();
      pendingFile.value = file;
      selectedFileName.value = file.name;
      selectedFile.value = file.name;
      toast.success(`Selected: ${file.name}`);
    } else {
      toast.error('Please drop a PSD or PSB file');
    }
  }
};
</script>

<template>
  <div class="dashboard">
    <!-- Header -->
    <header class="header">
      <div class="header-left">
        <div class="logo">Cl</div>
        <h1>Timelapse Engine</h1>
      </div>
      <div class="server-status" :class="{ connected: serverConnected }">
        <span class="material-symbols-outlined">{{ serverConnected ? 'cloud_done' : 'cloud_off' }}</span>
        {{ serverConnected ? 'Server Connected' : 'Server Offline' }}
      </div>
    </header>

    <!-- Main Content -->
    <main class="content">
      <!-- Hidden file input for browser fallback -->
      <input
        ref="fileInputRef"
        type="file"
        accept=".psd,.psb"
        style="display: none"
        @change="handleFileInputChange"
      />

      <!-- Upload Section with Drag & Drop -->
      <div 
        v-if="!selectedFile && !outputPath"
        class="upload-zone"
        :class="{ dragging: isDragging }"
        @click="handleSelectFile"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
      >
        <span class="material-symbols-outlined upload-icon">cloud_upload</span>
        <h2>Upload PSD File</h2>
        <p>Click to browse or drag & drop your file</p>
      </div>

      <!-- File Selected Section -->
      <div v-else-if="selectedFile && !outputPath" class="process-card">
        <!-- File Info -->
        <div class="file-info">
          <div class="file-icon">PSD</div>
          <div class="file-details">
            <h3>{{ selectedFileName || 'Unknown file' }}</h3>
            <p>{{ selectedFile }}</p>
          </div>
          <button v-if="!isProcessing" class="btn-icon" @click="resetSession">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <!-- Settings -->
        <div v-if="!isProcessing" class="settings-grid">
          <div class="setting">
            <label>Resolution</label>
            <select v-model="renderSettings.width" @change="renderSettings.height = renderSettings.width === 1920 ? 1080 : (renderSettings.width === 1280 ? 720 : 1080)">
              <option :value="1920">1920x1080 (FHD)</option>
              <option :value="1280">1280x720 (HD)</option>
              <option :value="3840">3840x2160 (4K)</option>
            </select>
          </div>
          <div class="setting">
            <label>Frame Rate</label>
            <select v-model="renderSettings.fps">
              <option :value="24">24 FPS</option>
              <option :value="30">30 FPS</option>
              <option :value="60">60 FPS</option>
            </select>
          </div>
          <div class="setting">
            <label>Animation Style</label>
            <select v-model="renderSettings.strategy">
              <option value="staggered">Staggered</option>
              <option value="sequential">Sequential</option>
              <option value="parallel">Parallel</option>
            </select>
          </div>
        </div>

        <!-- Progress -->
        <RenderProgress 
          v-if="progress"
          :current-frame="progress.current_frame"
          :total-frames="progress.total_frames"
          :message="progress.message"
          :state="progress.state"
        />

        <!-- Action Button -->
        <button 
          v-if="!isProcessing"
          class="btn-primary"
          :disabled="!canProcess"
          @click="handleProcess"
        >
          Start Rendering
        </button>
      </div>

      <!-- Result Section -->
      <div v-else-if="outputPath" class="result-card">
        <div class="success-icon">
          <span class="material-symbols-outlined">check_circle</span>
        </div>
        <h2>Rendering Complete!</h2>
        <p class="output-path">{{ outputPath }}</p>

        <VideoPlayer 
          v-if="outputPath.endsWith('.mp4')"
          :src="`file://${outputPath}`"
          :autoplay="true"
        />

        <div class="result-actions">
          <button class="btn-secondary" @click="resetSession">
            Render Another
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.dashboard {
  position: fixed;
  inset: 0;
  background: #1a1a1a;
  color: #d0d0d0;
  display: flex;
  flex-direction: column;
  font-family: system-ui, -apple-system, sans-serif;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
  background: #252525;
  border-bottom: 1px solid #333;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  width: 40px;
  height: 40px;
  background: #3b82f6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 16px;
}

h1 {
  font-size: 20px;
  font-weight: 500;
  color: white;
}

.server-status {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #888;
  font-size: 13px;
}

.server-status.connected {
  color: #22c55e;
}

.content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
}

.upload-zone {
  width: 100%;
  max-width: 500px;
  border: 2px dashed #444;
  border-radius: 16px;
  background: #252525;
  padding: 60px 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-zone:hover {
  border-color: #3b82f6;
  background: #2a2a2a;
}

.upload-zone.dragging {
  border-color: #22c55e;
  background: #1a3a1a;
  transform: scale(1.02);
}

.upload-zone.dragging .upload-icon {
  color: #22c55e;
}

.upload-icon {
  font-size: 64px;
  color: #555;
  margin-bottom: 16px;
  transition: color 0.2s;
}

.upload-zone:hover .upload-icon {
  color: #3b82f6;
}

.upload-zone h2 {
  color: white;
  margin: 0 0 8px;
}

.upload-zone p {
  color: #888;
  margin: 0;
}

.process-card,
.result-card {
  width: 100%;
  max-width: 500px;
  background: #252525;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #333;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.file-icon {
  width: 56px;
  height: 56px;
  background: #333;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #3b82f6;
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-details h3 {
  color: white;
  margin: 0 0 4px;
  font-size: 16px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-details p {
  color: #666;
  margin: 0;
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.btn-icon {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 8px;
}

.btn-icon:hover {
  color: #ef4444;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.setting label {
  display: block;
  color: #888;
  font-size: 12px;
  margin-bottom: 6px;
}

.setting select {
  width: 100%;
  background: #333;
  border: 1px solid #444;
  color: white;
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 13px;
}

.btn-primary {
  width: 100%;
  background: #3b82f6;
  color: white;
  border: none;
  padding: 16px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.result-card {
  text-align: center;
}

.success-icon {
  width: 80px;
  height: 80px;
  background: rgba(34, 197, 94, 0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}

.success-icon .material-symbols-outlined {
  font-size: 40px;
  color: #22c55e;
}

.result-card h2 {
  color: white;
  margin: 0 0 8px;
}

.output-path {
  color: #888;
  font-size: 13px;
  word-break: break-all;
  margin-bottom: 24px;
}

.result-actions {
  display: flex;
  gap: 16px;
}

.btn-secondary {
  flex: 1;
  background: #333;
  color: white;
  border: none;
  padding: 14px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-secondary:hover {
  background: #444;
}
</style>
