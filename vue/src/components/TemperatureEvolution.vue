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

// Register all necessary Chart.js components
ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, LinearScale, TimeScale, CategoryScale, Filler);

// Reactive variables to store API data
const formatedTime = ref([]);
const temperature = ref([]);
const maximalTemperature = ref([]);
const minimalTemperature = ref([]);
const ressentTemperature = ref([]);

// Colors for the chart (optional customization)
const barColors = [
  'rgba(75, 192, 192, 0.7)',
  'rgba(255, 159, 64, 0.7)',
  'rgba(153, 102, 255, 0.7)',
  'rgba(255, 99, 132, 0.7)'
];

// Fetch data from the API
const getEvolution = async () => {
  try {
    const response = await axios.get('/temperature-evolution');
    formatedTime.value = Object.values(response.data['temps_formaté']);
    temperature.value = Object.values(response.data['température']);
    maximalTemperature.value = Object.values(response.data['température_maximale']);
    minimalTemperature.value = Object.values(response.data['température_minimale']);
    ressentTemperature.value = Object.values(response.data['température_ressentie']);
  } catch (err) {
    console.error('Error fetching data:', err);
  }
};

// Load data before the component is mounted
onBeforeMount(getEvolution);

// Reactive chart data
const chartData = ref({
    labels: [],
        datasets: [
        {
            label: 'Température',
            data: [],
            borderColor: '#42A5F5',
            tension: 0.3,
            fill: false
        },
        {
          label: 'Température Maximale',
          data: [],
          borderColor: '#FF8A65',
          borderDash: [5, 5],
          fill: false
        },
        {
          label: 'Température Minimale',
          data: [],
          borderColor: '#1a84d9',
          borderDash: [5, 5],
          fill: false
        },
        {
          label: 'Température Ressentie',
          data: ressentTemperature.value,
          borderColor: '#41b682',
          borderDash: [5, 5],
          fill: false
        }
    ]
});

// Reactive chart options
const chartOptions = ref({
  responsive: true,
  plugins: {
    title: {
      display: true, 
      text: 'Évolution des températures à Rabat en '+new Date().getFullYear(), 
      font: {
        size: 15,             
        weight: 'bold',
      },
      color: '#333',
      padding: {
        top: 20,             
        bottom: 10,           
      },
    },
  },
  scales: {
      x: {
        title: {
          display: true, 
          text: 'Date et l\'heure',  // Label for x-axis
          font: {
            size: 14,
          },
          color: '#333',  // Color for the x-axis label
        },
      },
      y: {
        beginAtZero: true,
        title: {
          display: true, 
          text: 'Température en (°C)',  // Label for y-axis
          font: {
            size: 14,
          },
          color: '#333',  // Color for the y-axis label
      },
      ticks: {
          align: 'center', // Center labels on the y-axis
      },
    },
  },
});

// Watch for changes in the fetched data and update chartData
watchEffect(() => {
  if (formatedTime.value.length && temperature.value.length && maximalTemperature.value.length) {
    chartData.value = {
      labels: formatedTime.value,
      datasets: [
        {
          label: 'Température',
          data: temperature.value,
          borderColor: '#42A5F5',
          tension: 0.3,
          fill: false
        },
        {
          label: 'Température Maximale',
          data: maximalTemperature.value,
          borderColor: '#FF8A65',
          borderDash: [5, 5],
          fill: false
        },
        {
          label: 'Température Minimale',
          data: minimalTemperature.value,
          borderColor: '#1a84d9',
          borderDash: [5, 5],
          fill: false
        },
        {
          label: 'Température Ressentie',
          data: ressentTemperature.value,
          borderColor: '#41b682',
          borderDash: [5, 5],
          fill: false
        }
      ]
    };
  }
});
</script>

<template>
  <div class="flex items-center justify-center rounded bg-gray-50 dark:bg-gray-800 p-4 shadow-sm">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
</style>
