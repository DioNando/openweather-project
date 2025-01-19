<script setup>
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
import { ref, onBeforeMount, watchEffect } from 'vue'
import axios from '../axios';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const cities = ref([]);
const means = ref([]);
const barColors = [
  'rgba(75, 192, 192, 0.7)', // Teal
  'rgba(255, 159, 64, 0.7)', // Orange
  'rgba(153, 102, 255, 0.7)', // Purple
  'rgba(255, 99, 132, 0.7)', // Red
  'rgba(54, 162, 235, 0.7)', // Blue
  'rgba(255, 205, 86, 0.7)', // Yellow
  'rgba(231, 233, 237, 0.7)', // Light Grey
  'rgba(75, 192, 192, 0.7)', // Teal
  'rgba(153, 102, 255, 0.7)', // Purple
  'rgba(54, 162, 235, 0.7)', // Blue
  'rgba(255, 159, 64, 0.7)', // Orange
  'rgba(255, 99, 132, 0.7)'  // Red
];
const getMeans = async () => {
  try {
    const response = await axios.get('/mean-data'); 
    cities.value = response.data["villes"];
    means.value = response.data["temperatures"]; 
  } catch (err) {
    console.log(err);
  }
};

onBeforeMount(getMeans);

// Create reactive chart data
const chartData = ref({
  labels: [],
  datasets: [{ backgroundColor: barColors, label: 'Température moyenne', data: [] }]
});

watchEffect(() => {
  // Ensure chart data updates when cities or means are updated
  if (cities.value.length && means.value.length) {
    chartData.value = {
      labels: cities.value,
      datasets: [{ backgroundColor: barColors, label: 'Température moyenne', data: means.value }]
    };
  }
});

const chartOptions = ref({
  responsive: true,
  plugins: {
    title: {
      display: true, 
      text: 'Température moyenne par ville', 
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
        text: 'Villes',  // Label for x-axis
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
        text: 'Température moyenne (°C)',  // Label for y-axis
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
</script>

<template>
    <div class="flex items-center justify-center rounded bg-gray-50 dark:bg-gray-800 p-4 shadow-sm">
        <Bar id="bar-chart" class="w-100 h-100" :options="chartOptions" :data="chartData" />
    </div>
</template>

<style scoped>
</style>
