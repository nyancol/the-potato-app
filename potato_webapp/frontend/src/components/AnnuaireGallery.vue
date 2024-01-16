<template>
 <v-container>
    <h2 class="text-h2">Annuaire</h2>
    <v-row justify="center">
      <v-col v-for="patate in patates" :key="patate.id" cols="12" sm="6" md="6" lg="4" xl="3">
        <v-card class="country-card">
          <v-img :src="getImageUrl(patate.spiritAnimal.imagePath)" alt="Image" class="gallery-image"></v-img>
          <v-divider></v-divider>
          <v-list>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title class="info-text">
                  <v-icon class="country-icon">mdi-account</v-icon> {{ patate.firstName }} {{ patate.lastName }}
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title class="info-text">
                  <v-icon class="country-icon">mdi-phone</v-icon> {{ patate.phone }}
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title class="info-text description-text">
                  <v-icon class="country-icon">mdi-email</v-icon> {{ patate.email }}
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title class="info-text description-text">
                  <v-icon class="country-icon">mdi-city</v-icon> {{ patate.locations[0].city }} {{ patate.locations[0].postCode }}
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title class="info-text description-text">
                  <v-icon class="country-icon">mdi-map-marker</v-icon> {{ patate.locations[0].address }}
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
import { watch, computed } from 'vue'
import { useQuery } from '@vue/apollo-composable'
import gql from 'graphql-tag'

export default {
  setup() {
    const { result } = useQuery(gql`query patates {
          patates {
            id
            firstName
            lastName
            phone
            email
            spiritAnimal {
              name
              imagePath
            }
            locations {
              country
              city
              address
              postCode
            }
          }
        }
        `)

    watch(() => {
      console.log(result.value)
    })

    const backendUrl = 'http://localhost:5000';
    const getImageUrl = (imagePath) => {
      return `${backendUrl}/api/images/${imagePath.split("/")[3]}`; // encodeURIComponent(
    };

    const patates = computed(() => result.value?.patates ?? [])

    return {
      patates,
      getImageUrl
    };
  },
};
</script>

<style scoped>
.country-card {
  background-color: #f8f1d2;
  /* Light yellow background */
  border: 2px solid #7d6544;
  /* Brown border */
  border-radius: 10px;
  overflow: hidden;
  transition: background-color 0.3s ease;
}

.country-card:hover {
  background-color: #ffe4b5;
  /* Hover color change */
}

.country-icon {
  color: #7d6544;
  /* Brown color for icons */
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
  max-width: 100%;
  /* Full width for larger images */
  height: auto;
  border-radius: 5px;
}

.image-info {
  margin-top: 10px;
  text-align: center;
}

.info-text {
  margin: 5px 0;
  font-size: 16px;
  /* Increase font size for better readability */
  color: #555;
}

.description-text {
  white-space: pre-wrap;
  /* Allow line breaks */
}
</style>
