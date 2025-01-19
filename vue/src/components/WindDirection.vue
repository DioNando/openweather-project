<script setup>
import { ref } from 'vue'
const isDisplayed=ref(false)
</script>

<template>
  <div class="flex items-center justify-center rounded bg-gray-50 dark:bg-gray-800 p-30 static p-5">
    <img id="wind-direction" class="cursor-pointer" src="http://127.0.0.1:5000/wind-direction" alt="Wind direction chart" @click="isDisplayed=!isDisplayed">
  </div>
  <div v-show="isDisplayed" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg flex items-center justify-center rounded" style="background-color: transparent; height: 100vh; width: 43vw;">
      <button class="absolute top-2 right-2 text-white" @click="isDisplayed=!isDisplayed">
        <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 16 16"><path fill="#fff" d="m12.96 4.46l-1.42-1.42L8 6.59L4.46 3.04L3.04 4.46L6.59 8l-3.55 3.54l1.42 1.42L8 9.41l3.54 3.55l1.42-1.42L9.41 8z"/></svg>
      </button>
      <img id="wind-direction-big" class="rounded-lg" src="http://127.0.0.1:5000/wind-direction" alt="Wind direction chart">
    </div>
  </div>
</template>

<style scoped>
#wind-direction{
    width: 48%;
}
#wind-direction-big{
    width: 90%;
    height: 80%;
}
</style>