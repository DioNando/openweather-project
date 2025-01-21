<script setup>
import { onBeforeMount, ref, watchEffect } from 'vue';
import axios from '../axios';
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
} from 'chart.js'
import { Scatter } from 'vue-chartjs'

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend)

const datasets = ref([]);
const colors = [
  'rgba(75, 192, 192, 0.7)', 'rgba(255, 159, 64, 0.7)', 'rgba(153, 102, 255, 0.7)', 
  'rgba(255, 99, 132, 0.7)', 'rgba(54, 162, 235, 0.7)', 'rgba(255, 205, 86, 0.7)', 
  'rgba(231, 233, 237, 0.7)', 'rgba(75, 192, 192, 0.7)', 'rgba(153, 102, 255, 0.7)', 
  'rgba(54, 162, 235, 0.7)', 'rgba(255, 159, 64, 0.7)', 'rgba(255, 99, 132, 0.7)'
];

const getCityClustering = async () => {
    try {
        const response = await axios.get("/city-clustring");
        for (let [index, cityData] of Object.entries(response.data)) {
            datasets.value.push({
                label: `Scatter Dataset ${parseInt(index) + 1}`,
                fill: false,
                borderColor: colors[index],
                backgroundColor: colors[index],
                data: cityData
            });
        }
    } catch (err) {
        console.log(err);
    }
};

onBeforeMount(getCityClustering);

const chartData = ref({ datasets: [] });

watchEffect(() => {
  if (datasets.value.length) {
    chartData.value = { datasets: datasets.value };
  }
});

const chartOptions = ref({
  responsive: true,
  plugins: {
    title: {
      display: true, 
      text: 'Clustering géographique des villes', 
      font: {
        size: 15,             
        weight: 'bold',
      },
      color: '#333',
      padding: { top: 20, bottom: 10 },
    },
  },
  scales: {
    x: {
      title: {
        display: true, 
        text: 'Latitude',
        font: { size: 14 },
        color: '#333',
      },
    },
    y: {
      beginAtZero: true,
      title: {
        display: true, 
        text: 'Longitude',
        font: { size: 14 },
        color: '#333',
      },
      ticks: { align: 'center' },
    },
  },
});
</script>

<template>
  <div class="flex items-center justify-center rounded bg-gray-50 dark:bg-gray-800 p-30 shadow-sm static p-5">
    <Scatter :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
</style>
