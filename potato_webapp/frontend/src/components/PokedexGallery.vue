<!-- src/components/PokemonGallery.vue -->
<template>
    <v-container>
      <h2 class="text-h2">Pokedex</h2>
  
      <!-- Year Selection -->
      <v-row justify="center" class="mb-4">
        <v-col cols="12" sm="6" md="4" lg="3">
          <v-select
            v-model="selectedYear"
            :items="years"
            label="Select Year"
          ></v-select>
        </v-col>
      </v-row>
  
      <!-- Pokemon Image Gallery -->
      <v-row justify="center">
        <v-col v-for="(pokemonSet, index) in pokemonSets" :key="index" cols="12" sm="8" md="8" lg="8" xl="6">
          <v-card class="pokemon-card">
            <v-row>
              <v-col v-for="(image, imageIndex) in pokemonSet.images" :key="imageIndex" cols="4">
                <v-img :src="image.url" alt="Pokemon Image" class="pokemon-image"></v-img>
              </v-col>
            </v-row>
            <v-divider></v-divider>
            <v-list>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title class="info-text description-text">
                    {{ getDescriptionText(pokemonSet) }}
                  </v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script>
  export default {
    data() {
      return {
        selectedYear: null,
        years: ['2019', '2020', '2021', '2022', '2023'],
        pokemonSets: [],
      };
    },
    computed: {
      apiUrl() {
        const backendUrl = 'http://localhost:5000'; // Update to the correct URL and port
        return `${backendUrl}/api/images/pokemon-data?year=${this.selectedYear}`;
      },
    },
    watch: {
      apiUrl: 'fetchPokemonData', // Watch for changes in apiUrl
    },
    methods: {
      fetchPokemonData() {
        fetch(this.apiUrl)
          .then(response => {
            if (!response.ok) {
              throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
          })
          .then(pokemonData => {
            this.pokemonSets = pokemonData.map(({ images, first_name, last_name, pokemon_name }) => ({
              images: images.map(filename => ({ url: this.getImageUrl(filename) })),
              description: { first_name, last_name, pokemon_name },
            }));
          })
          .catch(error => {
            console.error('Error fetching Pokemon data:', error);
          });
      },
      getImageUrl(filename) {
        const backendUrl = 'http://localhost:5000'; // Update to the correct URL and port
        return `${backendUrl}/api/pokemon-images/${encodeURIComponent(filename)}`;
      },
      getDescriptionText(pokemonSet) {
        return `${pokemonSet.description.first_name} ${pokemonSet.description.last_name} - ${pokemonSet.description.pokemon_name}`;
      },
    },
  };
  </script>
  
  <style scoped>
  /* Styles for Pokemon Image Gallery */
  .pokemon-card {
    background-color: #cfd8dc; /* Light blue-grey background */
    border: 2px solid #546e7a; /* Dark blue-grey border */
    border-radius: 10px;
    overflow: hidden;
    transition: background-color 0.3s ease;
  }
  
  .pokemon-card:hover {
    background-color: #90a4ae; /* Hover color change */
  }
  
  .pokemon-image {
    width: 100%;
    max-width: 100%; /* Full width for larger images */
    height: auto;
    border-radius: 5px;
  }
  
  .info-text {
    margin: 5px 0;
    font-size: 16px; /* Increase font size for better readability */
    color: #555;
  }
  
  .description-text {
    white-space: pre-wrap; /* Allow line breaks in description */
  }
  </style>
  