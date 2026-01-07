import { ref, computed } from 'vue';
import { toast } from 'vue-sonner';
import { apiClient, type ProgressResponse } from '../adapters/driven/api_client/clientClient';

export interface RenderSettings {
  width: number;
  height: number;
  fps: number;
  strategy: 'staggered' | 'sequential' | 'parallel';
}

export function useRenderSession() {
  // State
  const selectedFile = ref<string | null>(null);
  const selectedFileName = ref<string | null>(null);
  const outputPath = ref<string | null>(null);
  const isProcessing = ref(false);
  const currentJobId = ref<string | null>(null);
  const progress = ref<ProgressResponse | null>(null);
  const serverConnected = ref(false);
  
  // Settings State
  const renderSettings = ref<RenderSettings>({
    width: 1920,
    height: 1080,
    fps: 30,
    strategy: 'staggered'
  });

  // Derived State
  const canProcess = computed(() => selectedFile.value && !isProcessing.value && serverConnected.value);

  // Actions
  const checkServer = async () => {
    try {
      await apiClient.checkHealth();
      serverConnected.value = true;
    } catch {
      serverConnected.value = false;
      toast.error('Cannot connect to render server. Make sure it is running on port 8000.');
    }
  };

  const resetSession = () => {
    selectedFile.value = null;
    selectedFileName.value = null;
    outputPath.value = null;
    progress.value = null;
  };

  const startRender = async (fileToUpload: File | null) => {
    if (!selectedFile.value) return;
    
    isProcessing.value = true;
    progress.value = null;
    
    try {
      let psdPath = selectedFile.value;
  
      // Upload if needed (Browser mode)
      if (fileToUpload) {
        toast.info('Uploading file...');
        const uploadResult = await apiClient.uploadFile(fileToUpload);
        psdPath = uploadResult.path;
        toast.success('File uploaded!');
      }
  
      // Start Render Job
      const result = await apiClient.startRender({
        psd_path: psdPath,
        output_path: `./output_${Date.now()}.mp4`,
        width: renderSettings.value.width,
        height: renderSettings.value.height,
        fps: renderSettings.value.fps,
        strategy: renderSettings.value.strategy,
      });
  
      if (!result.job_id) throw new Error('No job ID returned');
  
      currentJobId.value = result.job_id;
      toast.info(`Render job started: ${result.job_id}`);
  
      // Poll Progress
      await apiClient.pollProgress(result.job_id, (p) => {
        progress.value = p;
      });
  
      outputPath.value = result.output_path || './output.mp4';
      toast.success('Rendering complete!');
  
    } catch (err) {
      console.error('Processing failed:', err);
      toast.error(`Failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      isProcessing.value = false;
      currentJobId.value = null;
    }
  };

  return {
    // State
    selectedFile,
    selectedFileName,
    outputPath,
    isProcessing,
    progress,
    serverConnected,
    renderSettings,
    canProcess,
    
    // Actions
    checkServer,
    resetSession,
    startRender
  };
}
