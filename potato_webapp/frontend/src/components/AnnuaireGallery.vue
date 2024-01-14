<template>
  <v-container>
    <h2 class="text-h2">Annuaire</h2>

    <!-- Year Selection -->
    <v-row justify="center" class="mb-4">
      <v-col cols="12" sm="6" md="4" lg="3">
        <v-select
          v-model="selectedYear"
          :items="years"
          label="Select Year"
          @change="fetchImageData"
        ></v-select>
      </v-col>
    </v-row>
  
    <v-row justify="center">
      <v-col v-for="(image, index) in images" :key="index" cols="12" sm="6" md="6" lg="4" xl="3">
        <v-card class="country-card">
          <v-img :src="image.url" alt="Image" class="gallery-image"></v-img>
          <v-divider></v-divider>
          <v-list>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title class="info-text">
                  <v-icon class="country-icon">mdi-account</v-icon> {{ image.first_name }} {{ image.last_name }}
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title class="info-text">
                  <v-icon class="country-icon">mdi-paw</v-icon> {{ image.spirit_animal }}
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title class="info-text description-text">
                  <v-icon class="country-icon">mdi-book-open-variant</v-icon> {{ image.spirit_animal_description }}
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
      images: [],
    };
  },
  mounted() {
    // Default to the first year
    this.selectedYear = this.years[0];
    this.fetchImageData();
  },
  watch: {
    selectedYear: 'fetchImageData', // Watch for changes in selectedYear
  },
  methods: {
    fetchImageData() {
      const backendUrl = 'http://localhost:5000';
      const apiUrl = `${backendUrl}/api/images/data?year=${this.selectedYear}`;
      
      fetch(apiUrl)
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          return response.json();
        })
        .then(imageData => {
          this.images = imageData.map(({ filename, first_name, last_name, spirit_animal, spirit_animal_description }) => ({
            url: this.getImageUrl(backendUrl, filename),
            first_name,
            last_name,
            spirit_animal,
            spirit_animal_description,
          }));
        })
        .catch(error => {
          console.error('Error fetching image data:', error);
        });
    },
    getImageUrl(backendUrl, filename) {
      return `${backendUrl}/api/images/${encodeURIComponent(filename)}`;
    },
  },
};
</script>

<style scoped>
.country-card {
  background-color: #f8f1d2; /* Light yellow background */
  border: 2px solid #7d6544; /* Brown border */
  border-radius: 10px;
  overflow: hidden;
  transition: background-color 0.3s ease;
}

.country-card:hover {
  background-color: #ffe4b5; /* Hover color change */
}

.country-icon {
  color: #7d6544; /* Brown color for icons */
}

.image-gallery {
  text-align: center;
}

.gallery-title {
  color: #333;
}

.image-container {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
}

.image-item {
  margin: 20px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.gallery-image {
  width: 100%;
  max-width: 100%; /* Full width for larger images */
  height: auto;
  border-radius: 5px;
}

.image-info {
  margin-top: 10px;
  text-align: center;
}

.info-text {
  margin: 5px 0;
  font-size: 16px; /* Increase font size for better readability */
  color: #555;
}

.description-text {
  white-space: pre-wrap; /* Allow line breaks */
}
</style>
