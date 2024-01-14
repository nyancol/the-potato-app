<template>
    <div>
      <v-card v-for="(news, index) in newsList" :key="index">
        <v-card-title>{{ news.title }}</v-card-title>
        <v-card-text>{{ news.content }}</v-card-text>
      </v-card>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  
  export default {
    setup() {
      const newsList = ref([]);
  
      const fetchNews = async () => {
        try {
          const response = await fetch('http://localhost:5000/api/news'); // Update the API endpoint
          const data = await response.json();
          newsList.value = data;
        } catch (error) {
          console.error('Error fetching news:', error);
        }
      };
  
      onMounted(() => {
        fetchNews();
      });
  
      return {
        newsList,
      };
    },
  };
  </script>
  
  