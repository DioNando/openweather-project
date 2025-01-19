
<script setup>
import { Line } from 'vue-chartjs';
import { ref, onBeforeMount, watchEffect } from 'vue';
import axios from '../axios';

import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  CategoryScale,
  Filler
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, LinearScale, TimeScale, CategoryScale, Filler);

const city = ref("Rabat");
const cities = ref([]);
const formatedDate = ref([]);
const anomalies = ref([]);

const getAnomaliesPerCity = async () => {
  try {
    const response = await axios.get('/anomaly-counting?city=' + city.value);
    formatedDate.value = Object.values(response.data["mois"]);
    anomalies.value = Object.values(response.data["anomalie_temp"]);
    cities.value = Object.values(response.data["villes"]);
  } catch (err) {
    console.log(err);
  }
};

onBeforeMount(getAnomaliesPerCity);

const chartData = ref({
  labels: [],
  datasets: [
    {
      label: 'Anomalies de température',
      data: [],
      borderColor: '#42A5F5',
      tension: 0.3,
      fill: false
    }
  ]
});

const chartOptions = ref({
  responsive: true,
  plugins: {
    title: {
      display: true,
      text: 'Anomalies de température à ' + city.value + ' en ' + new Date().getFullYear(),
      font: {
        size: 15,
        weight: 'bold'
      },
      color: '#333',
      padding: {
        top: 20,
        bottom: 10
      }
    }
  },
  scales: {
    x: {
      title: {
        display: true,
        text: 'Date et l\'heure',
        font: {
          size: 14
        },
        color: '#333'
      }
    },
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: 'Température en (°C)',
        font: {
          size: 14
        },
        color: '#333'
      },
      ticks: {
        align: 'center'
      }
    }
  }
});

watchEffect(() => {
  if (formatedDate.value.length && anomalies.value.length && city.value) {
    chartData.value = {
      labels: formatedDate.value,
      datasets: [
        {
          label: 'Anomalies de température',
          data: anomalies.value,
          borderColor: '#42A5F5',
          tension: 0.3,
          fill: false
        }
      ]
    };
    chartOptions.value.plugins.title.text = 
      'Anomalies de température à ' + city.value + ' en ' + new Date().getFullYear();
  }
});
</script>

<template>
  <div class="flex items-center justify-center rounded bg-gray-50 dark:bg-gray-800 p-30 shadow-sm static p-5" style="position: relative;">
    <select 
      id="countries" 
      class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" 
      style="top: 3%; right: 5%; position: absolute; width: 5rem;" 
      v-model="city"
      @change="getAnomaliesPerCity"
    >
      <option v-for="(option, index) in cities" :key="index" :value="option">
        {{ option }}
      </option>
    </select>
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
</style>