<template>
  <div class="page-container">
    <div class="sidebar glass fade-in-left">
      <h2 class="section-title">🏥 Hospitals List</h2>
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

    <div class="map-wrapper fade-in-right">
      <h2 class="section-title">🗺️ Hospitals Map</h2>
      <div class="map-container">
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
      selectedCountryCode: "Q212",
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
      return Object.keys(this.countries).find(
        (key) => this.countries[key] === this.selectedCountryCode
      );
    },
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

      this.map.eachLayer((layer) => {
        if (layer instanceof L.Marker) {
          this.map.removeLayer(layer);
        }
      });

      this.hospitals.forEach((hospital) => {
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
        const bounds = this.hospitals.map((h) => [h.latitude, h.longitude]);
        this.map.fitBounds(bounds);
      }
    },
    toggleFullscreen() {
      this.isFullscreen = !this.isFullscreen;
      const container = document.querySelector(".map-container");
      container.classList.toggle("fullscreen");
    },
  },
};
</script>

<style>
:root[data-theme="light"] {
  --bg-gradient-from: #dfefff;
  --bg-gradient-to: #eaf8f2;
  --glass-bg: rgba(255, 255, 255, 0.6);
  --text-color: #2a4365;
  --header-bg: #bee3f8;
  --row-even: rgba(236, 245, 255, 0.75);
  --link-color: #3182ce;
  --map-btn-bg: #4299e1;
  --map-btn-hover: #2b6cb0;
  --table-bg: rgba(255, 255, 255, 0.88);
}

:root[data-theme="dark"] {
  --bg-gradient-from: #12343b;
  --bg-gradient-to: #0f292d;
  --glass-bg: rgba(255, 255, 255, 0.06);
  --text-color: #e2e8f0;
  --header-bg: #2b6cb0;
  --row-even: rgba(255, 255, 255, 0.05);
  --link-color: #63b3ed;
  --map-btn-bg: #2b6cb0;
  --map-btn-hover: #1a4a72;
  --table-bg: rgba(18, 52, 59, 0.7);
}

/* Загальний контейнер */
.page-container {
  padding-top: 100px;
  display: flex;
  height: 100vh;
  font-family: "Segoe UI", sans-serif;
  background: linear-gradient(to bottom right, var(--bg-gradient-from), var(--bg-gradient-to));
  color: var(--text-color);
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  width: 45%;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Заголовки */
.section-title {
  font-size: 26px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-color);
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
}

/* Glassmorphism */
.glass {
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  border-radius: 20px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
  padding: 24px;
  transition: all 0.4s ease-in-out;
}

/* Пошук і фільтр */
.search-container label {
  font-weight: bold;
  display: block;
  margin-bottom: 6px;
}

.custom-select {
  position: relative;
  width: 100%;
}

select {
  appearance: none;
  width: 100%;
  padding: 10px 40px 10px 14px;
  border: 1px solid #cbd5e0;
  border-radius: 10px;
  background-color: #edf2f7;
  font-size: 16px;
  color: #2d3748;
  font-weight: 500;
  cursor: pointer;
  transition: 0.3s ease;
}
select:hover {
  background-color: #e2e8f0;
}
.arrow {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: #4a5568;
  font-size: 14px;
}

/* Таблиця */
.table-container {
  max-height: 65vh;
  overflow-y: auto;
  border-radius: 12px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
}

table {
  width: 100%;
  border-collapse: collapse;
  background: var(--table-bg);
  backdrop-filter: blur(8px);
  border-radius: 12px;
  overflow: hidden;
}

th, td {
  padding: 14px 18px;
  text-align: left;
  font-size: 15px;
  color: var(--text-color);
}

th {
  background: var(--header-bg);
  font-weight: 700;
  position: sticky;
  top: 0;
  z-index: 1;
}

tr:nth-child(even) {
  background: var(--row-even);
}

/* Посилання */
a {
  color: var(--link-color);
  font-weight: bold;
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}

/* Мапа */
.map-wrapper {
  width: 55%;
  position: relative;
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.map-container {
  flex-grow: 1;
  border-radius: 18px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.12);
  background: var(--glass-bg);
  backdrop-filter: blur(14px);
}

#map {
  height: 100%;
  width: 100%;
  border-radius: 18px;
  z-index: 1;
}

/* Повноекранна кнопка */
.fullscreen-btn {
  position: absolute;
  bottom: 16px;
  right: 16px;
  z-index: 999;
  background: var(--map-btn-bg);
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 14px;
  cursor: pointer;
  font-weight: bold;
  font-size: 14px;
  transition: background 0.3s ease, transform 0.2s ease;
}
.fullscreen-btn:hover {
  background: var(--map-btn-hover);
  transform: scale(1.05);
}

.map-container.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh !important;
  width: 100vw !important;
  z-index: 1000;
}

/* Анімації */
.fade-in-left {
  animation: fadeInLeft 0.6s ease-out;
}
.fade-in-right {
  animation: fadeInRight 0.6s ease-out;
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>


