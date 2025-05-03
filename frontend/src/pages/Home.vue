<template>
  <div class="container">
    <h1 class="title">Diseases Information</h1>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else class="disease-grid">
      <div v-for="disease in diseases" :key="disease.id" class="card">
        <div class="card-header">
          <h2 class="disease-name">{{ disease.name }}</h2>
        </div>
        <div class="card-body">
          <p class="description">{{ disease.description }}</p>
          <div class="details">
           <div class="info-block">
              <p><strong>Symptoms:</strong> {{ formatArray(disease.symptoms) }}</p>
            </div>
            <div class="info-block">
              <p><strong>Treatments:</strong> {{ formatArray(disease.treatments) }}</p>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <a :href="disease.url" target="_blank" class="disease-link">🔗 More Info</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      diseases: [],
      loading: true,
    };
  },
  async created() {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/diseases");
      this.diseases = await response.json();
    } catch (error) {
      console.error("Failed to fetch diseases:", error);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    formatArray(arr) {
      return arr && arr.length ? arr.join(", ") : "N/A";
    },
  },
};
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 15px;
  background: #1a1a2e;
  min-height: 100vh;
  margin-bottom: 100px ;
}

/* Заголовок */
.title {
  text-align: center;
  color: #ff9800;
  font-size: 30px;
  font-weight: bold;
  margin-bottom: 30px;
}

/* Грід-сітка */
.disease-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  width: 90%;
}

/* Картка */
.card {
  background: #222;
  border-radius: 15px;
  box-shadow: 0 4px 10px rgba(255, 152, 0, 0.5);
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
  padding: 20px;
}

.card:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 15px rgba(255, 152, 0, 0.7);
}

/* Заголовок картки */
.card-header {
  background: #ff9800;
  color: white;
  padding: 12px;
  border-radius: 10px;
  text-align: center;
  font-size: 20px;
}

/* Опис */
.description {
  font-size: 14px;
  color: #ddd;
  margin: 10px 0;
}

/* Блок з інформацією */
.details {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
}

.info-block {
  background: #333;
  padding: 10px;
  border-radius: 8px;
  flex: 1 1 45%;
  margin: 5px;
  text-align: center;
  color: white;
}

/* Посилання */
.disease-link {
  display: block;
  text-align: center;
  margin-top: 10px;
  color: #ff9800;
  text-decoration: none;
  font-weight: bold;
}

.disease-link:hover {
  text-decoration: underline;
}
</style>
