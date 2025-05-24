<template>
  <div class="container">
    <h1 class="title">Diseases Information</h1>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else class="disease-grid">
      <div
        v-for="disease in diseases"
        :key="disease.id"
        class="card"
        @click="toggleExpand(disease.id)"
      >
        <div class="card-header">
          <h2>{{ disease.name }}</h2>
        </div>

        <div v-if="expandedId === disease.id" class="card-body">
          <p class="description">{{ disease.description }}</p>
          <div class="details">
            <div class="info-block">
              <p><strong>Symptoms:</strong> {{ formatArray(disease.symptoms) }}</p>
            </div>
            <div class="info-block">
              <p><strong>Treatments:</strong> {{ formatArray(disease.treatments) }}</p>
            </div>
          </div>
          <div class="card-footer">
            <a :href="disease.url" target="_blank" class="disease-link">🔗 More Info</a>
          </div>
        </div>

        <div v-else class="card-collapsed-hint">
          <p>🔎 Click to view more information</p>
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
      expandedId: null,
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
    toggleExpand(id) {
      this.expandedId = this.expandedId === id ? null : id;
    },
  },
};
</script>


<style>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 20px;
  background: linear-gradient(to bottom right, var(--bg-gradient-from), var(--bg-gradient-to));
  transition: background-color 0.5s ease;
  min-height: 100vh;
}

.title {
  padding-top: 100px;
  font-size: 50px;
  color: var(--text-primary);
  font-weight: 700;
  margin-bottom: 30px;
  text-shadow: 0 0 5px var(--accent);
}

.disease-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
  gap: 20px;
  width: 100%;
  max-width: 1200px;
}

.card {
  background: var(--card-bg);
  border-radius: 14px;
  box-shadow: 0 2px 12px var(--shadow);
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  padding: 16px;
  border-left: 5px solid var(--accent);
  cursor: pointer;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 20px var(--shadow-hover);
}

.card-header {
  background: var(--card-header);
  color: var(--card-header-text);
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
  text-align: center;
}

.description {
  font-size: 14px;
  color: var(--text);
  margin-bottom: 10px;
  line-height: 1.4;
}

.details {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-block {
  background: var(--info-bg);
  padding: 10px;
  border-radius: 8px;
  color: var(--info-text);
  font-size: 13px;
  border: 1px solid var(--info-border);
}

.card-footer {
  text-align: center;
  margin-top: 10px;
}

.disease-link {
  color: var(--link);
  text-decoration: none;
  font-weight: 600;
}

.disease-link:hover {
  color: var(--link-hover);
  text-decoration: underline;
}

.card-collapsed-hint {
  font-size: 14px;
  color: var(--hint-text);
  text-align: center;
  padding: 10px 0;
}

/* 🌓 Теми */
:root[data-theme="light"] {
  --text-primary: #00796b;
  --accent: #43cea2;
  --text: #333;
  --card-bg: #ffffff;
  --card-header: #e0f2f1;
  --card-header-text: #004d40;
  --info-bg: #f1fefb;
  --info-text: #004d40;
  --info-border: #b2dfdb;
  --link: #00796b;
  --link-hover: #004d40;
  --hint-text: #888;
  --shadow: rgba(0, 0, 0, 0.08);
  --shadow-hover: rgba(0, 121, 107, 0.3);
  --bg-gradient-from: #f0f7f5;
  --bg-gradient-to: #f0f7f5;
}

:root[data-theme="dark"] {
  --text-primary: #80cbc4;
  --accent: #26a69a;
  --text: #ddd;
  --card-bg: #1e1e1e;
  --card-header: #263238;
  --card-header-text: #b2dfdb;
  --info-bg: #37474f;
  --info-text: #e0f7fa;
  --info-border: #4db6ac;
  --link: #4fc3f7;
  --link-hover: #81d4fa;
  --hint-text: #aaa;
  --shadow: rgba(255, 255, 255, 0.05);
  --shadow-hover: rgba(255, 255, 255, 0.2);
  --bg-gradient-from: #12343b;
  --bg-gradient-to: #0f292d;
}
</style>

