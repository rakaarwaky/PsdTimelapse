<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue';

interface Props {
  src: string;
  autoplay?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  autoplay: true,
});

const emit = defineEmits<{
  ended: [];
  error: [error: Error];
}>();

const videoRef = ref<HTMLVideoElement | null>(null);
const isPlaying = ref(false);
const currentTime = ref(0);
const duration = ref(0);
const isLoading = ref(true);
const hasError = ref(false);

const progress = computed(() => {
  if (duration.value === 0) return 0;
  return (currentTime.value / duration.value) * 100;
});

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const togglePlay = () => {
  if (!videoRef.value) return;
  
  if (isPlaying.value) {
    videoRef.value.pause();
  } else {
    videoRef.value.play();
  }
};

const handleTimeUpdate = () => {
  if (videoRef.value) {
    currentTime.value = videoRef.value.currentTime;
  }
};

const handleLoadedMetadata = () => {
  if (videoRef.value) {
    duration.value = videoRef.value.duration;
    isLoading.value = false;
  }
};

const handlePlay = () => {
  isPlaying.value = true;
};

const handlePause = () => {
  isPlaying.value = false;
};

const handleEnded = () => {
  isPlaying.value = false;
  emit('ended');
};

const handleError = () => {
  hasError.value = true;
  isLoading.value = false;
  emit('error', new Error('Failed to load video'));
};

const seekTo = (event: MouseEvent) => {
  if (!videoRef.value || !duration.value) return;
  
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
  const percent = (event.clientX - rect.left) / rect.width;
  videoRef.value.currentTime = percent * duration.value;
};

const restart = () => {
  if (videoRef.value) {
    videoRef.value.currentTime = 0;
    videoRef.value.play();
  }
};

onUnmounted(() => {
  if (videoRef.value) {
    videoRef.value.pause();
  }
});
</script>

<template>
  <div class="video-player">
    <!-- Loading State -->
    <div v-if="isLoading" class="video-loading">
      <div class="spinner"></div>
      <span>Loading video...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="hasError" class="video-error">
      <span class="material-symbols-outlined">error</span>
      <span>Failed to load video</span>
    </div>

    <!-- Video Container -->
    <div class="video-container" :class="{ hidden: isLoading || hasError }">
      <video
        ref="videoRef"
        :src="src"
        :autoplay="autoplay"
        @timeupdate="handleTimeUpdate"
        @loadedmetadata="handleLoadedMetadata"
        @play="handlePlay"
        @pause="handlePause"
        @ended="handleEnded"
        @error="handleError"
      />

      <!-- Controls Overlay -->
      <div class="video-controls">
        <!-- Progress Bar -->
        <div class="progress-bar" @click="seekTo">
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
          </div>
        </div>

        <!-- Control Buttons -->
        <div class="control-row">
          <button class="control-btn" @click="togglePlay">
            <span class="material-symbols-outlined">
              {{ isPlaying ? 'pause' : 'play_arrow' }}
            </span>
          </button>

          <span class="time-display">
            {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
          </span>

          <button class="control-btn" @click="restart">
            <span class="material-symbols-outlined">replay</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.video-player {
  position: relative;
  width: 100%;
  background: #111;
  border-radius: 8px;
  overflow: hidden;
}

.video-container {
  position: relative;
}

.video-container.hidden {
  visibility: hidden;
  height: 0;
}

video {
  width: 100%;
  display: block;
}

.video-loading,
.video-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #888;
  gap: 12px;
}

.video-error {
  color: #e74c3c;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #333;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.video-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
  padding: 20px 16px 12px;
}

.progress-bar {
  cursor: pointer;
  padding: 8px 0;
}

.progress-track {
  height: 4px;
  background: rgba(255,255,255,0.2);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #3b82f6;
  transition: width 0.1s linear;
}

.control-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.control-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s;
}

.control-btn:hover {
  opacity: 0.8;
}

.time-display {
  color: rgba(255,255,255,0.8);
  font-size: 12px;
  font-family: monospace;
  flex: 1;
}
</style>
