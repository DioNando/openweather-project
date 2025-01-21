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
const dates = ref([]);
const test = ref([]);
const predictions = ref([]);

// Colors for the chart (optional customization)
const barColors = [
  'rgba(75, 192, 192, 0.7)',
  'rgba(255, 159, 64, 0.7)',
  'rgba(153, 102, 255, 0.7)',
  'rgba(255, 99, 132, 0.7)'
];

// Fetch data from the API
const getArimaPrediction = async () => {
  try {
    const response = await axios.get('/arima-prediction');
    dates.value = response.data['dates'];
    test.value = response.data['test'];
    predictions.value = response.data['predictions'];
  } catch (err) {
    console.error('Error fetching data:', err);
  }
};

// Load data before the component is mounted
onBeforeMount(getArimaPrediction);

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
          label: 'Température prédit',
          data: [],
          borderColor: '#FF8A65',
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
      text: 'Prédiction de la température avec ARIMA (Rabat)', 
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
          text: 'Date',  // Label for x-axis
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
  if (
    Array.isArray(dates.value) &&
    Array.isArray(test.value) &&
    Array.isArray(predictions.value) &&
    dates.value.length &&
    test.value.length &&
    predictions.value.length
  ) {
    chartData.value = {
      labels: dates.value,
      datasets: [
        {
          label: 'Température',
          data: test.value,
          borderColor: '#42A5F5',
          tension: 0.3,
          fill: false
        },
        {
          label: 'Température prédit',
          data: predictions.value,
          borderColor: '#FF8A65',
          borderDash: [5, 5],
          fill: false
        }
      ]
    };
  }
});
</script>

<template>
  <div class="flex items-center justify-center rounded bg-gray-50 dark:bg-gray-800 p-4 shadow-sm w-100">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
</style>
