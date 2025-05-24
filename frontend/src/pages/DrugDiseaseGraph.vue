<template>
  <div class="graph-container">
    <div class="controls">
      <input
        v-model="searchQuery"
        @input="searchNode"
        placeholder="Search disease..."
        class="search-input"
      />
      <div class="legend">
        <p><span class="legend-box disease"></span> Disease</p>
        <p><span class="legend-box drug"></span> Drug</p>
      </div>
    </div>

    <svg ref="graphSvg"></svg>
    <div class="instructions">
      <p>🔍 Scroll to zoom, drag background to move the graph.</p>
    </div>
    <p v-if="loading">Loading graph...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import * as d3 from "d3";
import axios from "axios";

const graphSvg = ref(null);
const loading = ref(true);
const searchQuery = ref("");
const graphData = ref({ nodes: [], links: [] });

let svg, g, link, node, simulation, zoomHandler;

function getCssVariable(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

onMounted(async () => {
  try {
    const response = await axios.get("http://localhost:8000/api/drug-disease");
    const data = response.data;

    const nodesMap = new Map();
    const links = [];

    // Отримуємо кольори з CSS-змінних
    const diseaseColor = getCssVariable("--disease-color") || "#4db8ff";
    const drugColor = getCssVariable("--drug-color") || "#98e6c0";

    data.forEach((item) => {
      if (!nodesMap.has(item.item)) {
        nodesMap.set(item.item, {
          id: item.item,
          label: item.label,
          type: item.color === "FFA500" ? "disease" : "drug",
          color: item.color === "FFA500" ? diseaseColor : drugColor,
        });
      }
      if (item.link) {
        // Якщо посилання існує — додаємо ребро (link)
        links.push({
          source: item.link,
          target: item.item,
        });
      }
    });

    graphData.value = {
      nodes: Array.from(nodesMap.values()),
      links,
    };

    loading.value = false;

    setupGraph();
  } catch (error) {
    console.error("Error loading graph data:", error);
  }
});

function setupGraph() {
  const width = window.innerWidth;
  const height = window.innerHeight;

  svg = d3.select(graphSvg.value);
  svg.selectAll("*").remove();

  // Головний контейнер для графа (для масштабування)
  g = svg.append("g");

  // Ініціалізуємо zoom-поведінку
  zoomHandler = d3
    .zoom()
    .scaleExtent([0.1, 3])
    .on("zoom", (event) => {
      g.attr("transform", event.transform);
    });

  svg.attr("width", width).attr("height", height).call(zoomHandler);

  // Створюємо simulation
 simulation = d3
  .forceSimulation(graphData.value.nodes)
  .force(
    "link",
    d3.forceLink(graphData.value.links).id((d) => d.id).distance(150)
  )
  .force("charge", d3.forceManyBody().strength(-300))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force(
    "collide",
    d3.forceCollide((d) => d.label.length * 5 + 25).strength(0.7)
  );


  // Лінки
  link = g
    .append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(graphData.value.links)
    .enter()
    .append("line")
    .attr("stroke", "#aaa")
    .attr("stroke-width", 2);

  // Ноди як групи <g>
  node = g
    .append("g")
    .attr("class", "nodes")
    .selectAll("g")
    .data(graphData.value.nodes)
    .enter()
    .append("g")
    .call(
      d3
        .drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended)
    );

  // Додаємо еліпс для кожного ноду
  node
    .append("ellipse")
    .attr("rx", (d) => d.label.length * 5 + 20)
    .attr("ry", 20)
    .attr("fill", (d) => d.color)
    .attr("stroke", "#0d2c42")
    .attr("stroke-width", 1.5)
    .on("mouseover", function (event, d) {
      d3.select(this)
        .transition()
        .duration(200)
        .attr("stroke-width", 3)
        .attr("fill", d3.color(d.color).darker(0.5));
    })
    .on("mouseout", function (event, d) {
      d3.select(this)
        .transition()
        .duration(200)
        .attr("stroke-width", 1.5)
        .attr("fill", d.color);
    });

  // Текстова підписка
  node
    .append("text")
    .text((d) => d.label)
    .attr("text-anchor", "middle")
    .attr("alignment-baseline", "middle")
    .attr("font-size", "14px")
    .attr("fill", "#000")
    .attr("font-weight", "bold");

  simulation.on("tick", () => {
    // Оновлення позицій лінків
    link
      .attr("x1", (d) => d.source.x)
      .attr("y1", (d) => d.source.y)
      .attr("x2", (d) => d.target.x)
      .attr("y2", (d) => d.target.y);

    // Оновлення позицій нодів
    node.attr("transform", (d) => `translate(${d.x},${d.y})`);
  });

  // Початкове масштабування і позиціонування
  const initialScale = 0.5;
  const initialX = width / 2;
  const initialY = height / 2;
  const initialTransform = d3.zoomIdentity
    .translate(initialX, initialY)
    .scale(initialScale);
  svg.call(zoomHandler.transform, initialTransform);
}

function dragstarted(event, d) {
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(event, d) {
  d.fx = event.x;
  d.fy = event.y;
}

function dragended(event, d) {
  if (!event.active) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}

function searchNode() {
  const query = searchQuery.value.trim().toLowerCase();
  if (!query) return;

  const foundNodes = graphData.value.nodes.filter((n) =>
    n.label.toLowerCase().includes(query)
  );

  if (foundNodes.length > 0) {
    const foundNode = foundNodes[0];
    const width = window.innerWidth;
    const height = window.innerHeight;
    const scale = 1.5;
    const translateX = width / 2 - foundNode.x * scale;
    const translateY = height / 2 - foundNode.y * scale;

    const transform = d3.zoomIdentity
      .translate(translateX, translateY)
      .scale(scale);

    svg
      .transition()
      .duration(750)
      .call(zoomHandler.transform, transform);
  } else {
    console.log("Node not found");
  }
}
</script>

<style>
:root[data-theme="light"] {
  --bg-gradient-from: #dfefff;
  --bg-gradient-to: #eaf8f2;
  --controls-bg: rgba(255, 255, 255, 0.2);
  --controls-text: #0d2c42;
  --input-bg: white;
  --input-text: #333;
  --input-shadow: rgba(0, 0, 0, 0.1);
  --legend-text: #0d2c42;
  --disease-color: #4db8ff;
  --drug-color: #98e6c0;
  --instructions-bg: rgba(13, 44, 66, 0.9);
  --instructions-text: #fff;
}

:root[data-theme="dark"] {
  --bg-gradient-from: #12343b;
  --bg-gradient-to: #0f292d;
  --controls-bg: rgba(20, 40, 50, 0.6);
  --controls-text: #a0c9d5;
  --input-bg: #263238;
  --input-text: #eee;
  --input-shadow: rgba(255, 255, 255, 0.2);
  --legend-text: #a0c9d5;
  --disease-color: #4db8ff;
  --drug-color: #98e6c0;
  --instructions-bg: rgba(40, 70, 90, 0.8);
  --instructions-text: #ccc;
}

.graph-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  height: 100vh;
  background: linear-gradient(to bottom right, var(--bg-gradient-from), var(--bg-gradient-to));
  overflow: hidden;
  position: relative;
}

.controls {
  position: absolute;
  margin: 100px 30px;
  padding: 20px;
  top: 20px;
  right: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(10px);
  background: var(--controls-bg);
  color: var(--controls-text);
  border-radius: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  width: 400px;
  gap: 16px;
  z-index: 10;
}

.search-input {
  padding: 8px 12px;
  font-size: 16px;
  border-radius: 8px;
  border: none;
  outline: none;
  width: 180px;
  background: var(--input-bg);
  color: var(--input-text);
  box-shadow: inset 0 0 5px var(--input-shadow);
}

.legend {
  display: flex;
  gap: 12px;
}

.legend p {
  display: flex;
  align-items: center;
  font-size: 14px;
  margin: 0;
  color: var(--legend-text);
}

.legend-box {
  width: 20px;
  height: 20px;
  margin-right: 6px;
  border-radius: 4px;
}

.disease {
  background-color: var(--disease-color);
}

.drug {
  background-color: var(--drug-color);
}

.instructions {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--instructions-bg);
  color: var(--instructions-text);
  padding: 10px 20px;
  font-size: 14px;
  border-radius: 12px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
  z-index: 10;
}
</style>
