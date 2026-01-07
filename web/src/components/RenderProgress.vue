<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  currentFrame: number;
  totalFrames: number;
  message: string;
  state: string;
}

const props = defineProps<Props>();

const progress = computed(() => {
  if (props.totalFrames === 0) return 0;
  return (props.currentFrame / props.totalFrames) * 100;
});

const stateColor = computed(() => {
  switch (props.state) {
    case 'rendering': return '#3b82f6';
    case 'encoding': return '#10b981';
    case 'complete': return '#22c55e';
    case 'error': return '#ef4444';
    default: return '#6b7280';
  }
});

const stateIcon = computed(() => {
  switch (props.state) {
    case 'rendering': return 'movie_creation';
    case 'encoding': return 'video_file';
    case 'complete': return 'check_circle';
    case 'error': return 'error';
    case 'preparing': return 'hourglass_empty';
    default: return 'pending';
  }
});
</script>

<template>
  <div class="progress-card">
    <div class="progress-header">
      <span 
        class="material-symbols-outlined state-icon" 
        :style="{ color: stateColor }"
      >
        {{ stateIcon }}
      </span>
      <div class="progress-info">
        <span class="state-label">{{ state.toUpperCase() }}</span>
        <span class="progress-message">{{ message }}</span>
      </div>
      <span class="progress-percent">{{ progress.toFixed(1) }}%</span>
    </div>

    <div class="progress-bar-container">
      <div class="progress-bar-bg">
        <div 
          class="progress-bar-fill" 
          :style="{ 
            width: `${progress}%`,
            backgroundColor: stateColor 
          }"
        ></div>
      </div>
    </div>

    <div class="progress-details">
      <span>Frame {{ currentFrame }} / {{ totalFrames }}</span>
    </div>
  </div>
</template>

<style scoped>
.progress-card {
  background: #252525;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #333;
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.state-icon {
  font-size: 32px;
}

.progress-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.state-label {
  font-weight: 600;
  color: white;
  font-size: 14px;
  letter-spacing: 0.5px;
}

.progress-message {
  color: #888;
  font-size: 12px;
  margin-top: 2px;
}

.progress-percent {
  font-size: 24px;
  font-weight: 700;
  color: white;
  font-family: monospace;
}

.progress-bar-container {
  margin-bottom: 12px;
}

.progress-bar-bg {
  height: 8px;
  background: #111;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease-out;
}

.progress-details {
  display: flex;
  justify-content: space-between;
  color: #666;
  font-size: 12px;
  font-family: monospace;
}
</style>
