<script setup>
import CitiesMeans from './components/CitiesMeans.vue';
import TemperatureEvolution from './components/TemperatureEvolution.vue';
import WindSpeed from './components/WindSpeed.vue';
import WindDirection from './components/WindDirection.vue';
import AnomalyPerDay from './components/AnomalyPerDay.vue';
import GeographicClustring from './components/GeographicClustring.vue';
import TemperaturePrediction from './components/TemperaturePrediction.vue';
import ArimaPrediction from './components/ArimaPrediction.vue';
</script>

<template>
  <div>
    <div class="m-1 p-4 border-2 border-gray-200 border-dashed rounded-lg dark:border-gray-700">
        <div class="grid grid-cols-2 gap-4 mb-4 h-150">
          <CitiesMeans />
          <TemperatureEvolution />
          <WindSpeed />
          <WindDirection />
          <AnomalyPerDay />
          <GeographicClustring />
          <TemperaturePrediction />
          <ArimaPrediction />
        </div>
    </div>
  </div>
</template>

<style scoped>
</style>
