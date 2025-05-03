<template>
  <div class="container">
    <div class="sidebar">
      <h1 class="fixed-header">Hospitals List</h1>
      <div class="search-container">
        <label for="country">Select a country:</label>
        <div class="custom-select">
          <select v-model="selectedCountryCode" @change="loadHospitals">
            <option v-for="(code, country) in countries" :key="code" :value="code">
              {{ country }}
            </option>
          </select>
          <span class="arrow">▼</span>
        </div>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Country</th>
              <th>Hospital</th>
              <th>Address</th>
              <th>Website</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="hospital in hospitals" :key="hospital.id">
              <td>{{ selectedCountry }}</td>
              <td>{{ hospital.name }}</td>
              <td>{{ hospital.address }}</td>
              <td>
                <a v-if="hospital.website" :href="hospital.website" target="_blank">Visit</a>
                <span v-else>-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="map-wrapper">
      <h1 class="fixed-header">Hospitals Map</h1>
      <div class="map-container" :class="{ 'fullscreen': isFullscreen }">
        <div id="map"></div>
        <button class="fullscreen-btn" @click="toggleFullscreen">
          {{ isFullscreen ? 'Exit Fullscreen' : 'Fullscreen' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import L from "leaflet";
import "leaflet/dist/leaflet.css";

export default {
  data() {
    return {
      map: null,
      selectedCountryCode: "Q212", // Default Ukraine
      hospitals: [],
      isFullscreen: false,
      countries: {
        "United States": "Q30",
        "United Kingdom": "Q145",
        "Ukraine": "Q212",
        "Germany": "Q183",
        "France": "Q142",
        "China": "Q148",
        "Spain": "Q29",
        "Italy": "Q38",
        "Canada": "Q16",
        "Australia": "Q408",
        "Japan": "Q17",
        "Brazil": "Q155",
      },
    };
  },
  computed: {
    selectedCountry() {
      return Object.keys(this.countries).find(key => this.countries[key] === this.selectedCountryCode);
    }
  },
  async mounted() {
    this.map = L.map("map").setView([48.3794, 31.1656], 5);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(this.map);
    this.loadHospitals();
  },
  methods: {
    async loadHospitals() {
  const url = `http://127.0.0.1:8000/api/hospitals?country=${this.selectedCountryCode}`;
  const response = await fetch(url);
  this.hospitals = await response.json();

  // Удаляем старые маркеры
  this.map.eachLayer(layer => {
    if (layer instanceof L.Marker) {
      this.map.removeLayer(layer);
    }
  });

  this.hospitals.forEach(hospital => {
    const { name, latitude, longitude, address, wikidata_url, website, image } = hospital;

    let popupContent = `<b>${name}</b><br>`;

    if (image) {
      popupContent += `<img src="${image}" alt="${name}" style="max-width: 200px; max-height: 150px; display: block; margin: 5px auto;"><br>`;
    }

    popupContent += `<strong>Address:</strong> ${address}<br>`;
    popupContent += `<a href="${wikidata_url}" target="_blank">Wikidata</a><br>`;

    if (website) {
      popupContent += `<a href="${website}" target="_blank">Official Website</a><br>`;
    }

    L.marker([latitude, longitude])
      .addTo(this.map)
      .bindPopup(popupContent);
  });

  if (this.hospitals.length > 0) {
    const bounds = this.hospitals.map(h => [h.latitude, h.longitude]);
    this.map.fitBounds(bounds);
  }
}
,
    toggleFullscreen() {
      this.isFullscreen = !this.isFullscreen;
    }
  }
};
</script>

<style scoped>
.container {
  display: flex;
  height: 100vh;
  gap: 20px;
  padding: 60px 15px 15px 15px;
  background: #1a1a2e;
}

/* === Стили выбора страны === */
.search-container {
  margin-bottom: 15px; /* Добавляет пространство между выбором страны и таблицей */
}

.custom-select {
  position: relative;
  display: inline-block;
  width: 100%;
}

.custom-select select {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  background: #222;
  color: white;
  border: none;
  border-radius: 5px;
  appearance: none;
  cursor: pointer;
}

.custom-select .arrow {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: white;
  pointer-events: none;
}

/* === Стили боковой панели === */
.sidebar {
  width: 35%;
  padding: 0 15px 15px 15px;
  color: white;
  overflow: hidden;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.2);
}

.fixed-header {
  text-align: center;
  color: #ff9800;
  margin-bottom: 20px;
  font-size:30px;
}

/* === Таблица === */
.table-container {
  max-height: calc(100vh - 250px); /* Учитывает отступ от заголовка */
  overflow-y: auto;
  overflow-x: hidden; /* Убирает горизонтальный скролл */
}

table {
  table-layout: fixed;
  width: 100%;
  border-collapse: collapse;
  background: #333;
  border-radius: 5px;
}

th, td {
  padding: 12px;
  text-align: left;
  color: white;
  word-wrap: break-word; /* Обеспечивает перенос слов внутри ячеек */
  overflow-wrap: break-word;
}

th {
  background: #ff9800;
  position: sticky;
  top: 0;
  z-index: 2;
}

tr:nth-child(even) {
  background: #444;
}

/* === Карта === */
.map-wrapper {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.map-container {
  width: 90%;
  height: 500px;
  border-radius: 15px;
  overflow: hidden;
  background: #222;
  position: relative;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
}

#map {
  width: 100%;
  height: 100%;
  border-radius: 15px;
}

/* === Кнопка полноэкранного режима === */
.fullscreen-btn {
  position: absolute;
  bottom: 20px;
  right: 25px;
  padding: 12px 20px;
  background: #ff9800;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 5px;
  font-size: 16px;
  z-index: 1000; /* Убедимся, что кнопка остаётся поверх карты */
}

.fullscreen {
  position: fixed;
  top: 50%;
  left: 50%;
  width: 90vw;
  height: 90vh;
  transform: translate(-50%, -50%);
  z-index: 1000;
  border-radius: 15px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.7);
}

</style>
