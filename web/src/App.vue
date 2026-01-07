<script setup lang="ts">
import { onErrorCaptured } from 'vue';
import { Toaster, toast } from 'vue-sonner';
import ClientDashboard from './components/ClientDashboard.vue';

onErrorCaptured((err) => {
  console.error("Captured Component Error:", err);
  toast.error("Application Error: " + err);
  return false;
});
</script>

<template>
  <div class="h-screen w-screen overflow-hidden bg-[#1a1a1a]">
    <Toaster richColors />
    <ClientDashboard />
  </div>
</template>

<style>
@import './styles/index.css';

html,
body {
  margin: 0;
  padding: 0;
  overflow: hidden;
}
</style>
