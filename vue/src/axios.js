import axios from 'axios';

// Create an axios instance with custom configuration
const axiosInstance = axios.create({
  baseURL: 'http://localhost:5000', // Set the base URL for your API
  timeout: 4000000,                     // Set a timeout (in ms) for requests
  headers: {
    'Content-Type': 'application/json', // Default content type
    // Add any default headers here
  },
});

export default axiosInstance;