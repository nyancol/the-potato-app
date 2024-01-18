<template>
    <v-container>
      <h2 class="text-h2">Choose Your Gallery</h2>
      
      <v-row justify="center">
        <v-col cols="12" sm="6" md="4" lg="3">
          <v-card @click="selectGallery('ImageGallery')" class="landing-card">
            <v-img src="@/assets/image_gallery.png" alt="Image Gallery"></v-img>
            <v-divider></v-divider>
            <v-list>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title class="info-text">Single Image Gallery</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card>
        </v-col>
  
        <v-col cols="12" sm="6" md="4" lg="3">
          <v-card @click="selectGallery('PokemonGallery')" class="landing-card">
            <v-img src="@/assets/pokeball.png" alt="Pokemon Gallery"></v-img>
            <v-divider></v-divider>
            <v-list>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title class="info-text">Pokemon Image Gallery</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card>
        </v-col>
      </v-row>
  
      <!-- Dynamic Gallery Rendering -->
      <v-container v-if="selectedGallery">
        <component :is="selectedGallery" />
      </v-container>
    </v-container>
  </template>
  
  <script>
  import ImageGallery from '@/components/ImageGallery.vue';
  import PokemonGallery from '@/components/PokemonGallery.vue';
  
  export default {
    data() {
      return {
        selectedGallery: null,
      };
    },
    methods: {
      selectGallery(galleryType) {
        // Set the selected gallery type
        this.selectedGallery = galleryType;
      },
    },
    components: {
      ImageGallery,
      PokemonGallery,
    },
  };
  </script>
  
  <style scoped>
  /* Styles for Landing Page */
  .landing-card {
    cursor: pointer;
    transition: background-color 0.3s ease;
  }
  
  .landing-card:hover {
    background-color: #f0f0f0; /* Hover color change */
  }
  
  .info-text {
    margin: 5px 0;
    font-size: 16px; /* Increase font size for better readability */
    color: #555;
    text-align: center;
  }
  </style>
  