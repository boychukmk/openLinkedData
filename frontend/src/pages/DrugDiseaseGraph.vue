<template>
  <div class="graph-container">
    <div class="controls">
      <input v-model="searchQuery" @input="searchNode" placeholder="Search disease..." class="search-input" />
      <div class="legend">
        <p><span class="legend-box disease"></span> Disease</p>
        <p><span class="legend-box drug"></span> Drug</p>
      </div>
    </div>

    <svg ref="graphSvg"></svg>
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
let zoomHandler, g;

onMounted(async () => {
  try {
    const response = await axios.get("http://localhost:8000/api/drug-disease");
    const data = response.data;

    console.log("Graph Data:", data);

    const nodesMap = new Map();
    const links = [];

    data.forEach((item) => {
      nodesMap.set(item.item, {
        id: item.item,
        label: item.label,
        color: `#${item.color}`, // HEX color
        type: item.color === "FFA500" ? "disease" : "drug",
      });

      if (item.link) {
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
    renderGraph();
  } catch (error) {
    console.error("Error loading graph data:", error);
  }
});

function renderGraph() {
  const width = window.innerWidth;
  const height = window.innerHeight;

  const svg = d3.select(graphSvg.value);
  svg.selectAll("*").remove();

  zoomHandler = d3.zoom().scaleExtent([0.1, 2]).on("zoom", (event) => {
    g.attr("transform", event.transform);
  });

  svg.attr("width", width).attr("height", height).call(zoomHandler);

  g = svg.append("g");

  const simulation = d3
  .forceSimulation(graphData.value.nodes)
  .force("link", d3.forceLink(graphData.value.links).id(d => d.id).distance(150))
  .force("charge", d3.forceManyBody().strength(-400))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collide", d3.forceCollide(d => d.label.length * 5 + 30)); // Добавили коллизию



  const link = g
    .selectAll("line")
    .data(graphData.value.links)
    .enter()
    .append("line")
    .attr("stroke", "#aaa")
    .attr("stroke-width", 2);

 const node = g
  .selectAll("g")
  .data(graphData.value.nodes)
  .enter()
  .append("g") // Группа, содержащая овал + текст
  .attr("transform", d => `translate(${d.x}, ${d.y})`)
  .call(drag(simulation));

  node
    .append("ellipse") // Овал вместо круга
    .attr("rx", d => d.label.length * 5 + 20) // Ширина зависит от длины текста
    .attr("ry", 20) // Фиксированная высота овала
    .attr("fill", d => d.color)
    .attr("stroke", "#fff")
    .attr("stroke-width", 1.5);

  node
    .append("text")
    .text(d => d.label)
    .attr("text-anchor", "middle") // Центрируем текст
    .attr("alignment-baseline", "middle") // Центрируем по вертикали
    .attr("font-size", "14px")
    .attr("fill", "#fff")
    .attr("font-weight", "bold");

  // Обновляем transform при каждой итерации симуляции
  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

  node.attr("transform", d => `translate(${d.x}, ${d.y})`);
});
  const initialScale = 0.1; // Начальный масштаб
  const initialX = width / 2;
  const initialY = height / 2;

  // Устанавливаем начальный трансформ
  const initialTransform = d3.zoomIdentity.translate(initialX, initialY).scale(initialScale);

  svg.call(zoomHandler.transform, initialTransform);

}

function searchNode() {
  const query = searchQuery.value.trim().toLowerCase();

  if (query === "") return;

  const foundNodes = graphData.value.nodes.filter(n =>
    n.label.toLowerCase().includes(query)
  );

  if (foundNodes.length > 0) {
    const foundNode = foundNodes[0];  // Get the first matching node

    // Apply zoom and center the graph around the found node
    const scale = 1.5; // Set scale to zoom into the node
    const width = window.innerWidth;
    const height = window.innerHeight;

    // Calculate the translation to center the found node
    const translateX = width / 2 - foundNode.x * scale;
    const translateY = height / 2 - foundNode.y * scale;

    const transform = d3.zoomIdentity
      .translate(translateX, translateY)
      .scale(scale);

    d3.select(graphSvg.value)
      .transition()
      .duration(750)
      .call(zoomHandler.transform, transform);

    // Highlight the found node
    d3.selectAll("circle")
      .transition()
      .duration(300)
      .attr("r", 10);  // Reset the size of all nodes

    // Highlight the found node specifically
    d3.select(`circle[data-id='${foundNode.id}']`)
      .transition()
      .duration(300)
      .attr("r", 15)  // Make the found node larger
      .attr("stroke", "black")
      .attr("stroke-width", 2);
  } else {
    console.log("Node not found");
  }
}

function drag(simulation) {
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

  return d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended);
}
</script>

<style scoped>
.graph-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  height: 100vh;
  background-color: #222;
}

.controls {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #333;
  color: white;
  padding: 10px;
  border-radius: 8px;
  width: 400px;
  height: 40px;
  margin-top: 80px;
}

.search-input {
  padding: 5px;
  font-size: 16px;
  border-radius: 5px;
  border: none;
  width: 180px;
}

.legend {
  display: flex;
  gap: 20px;
}
.legend p {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.legend-box {
  width: 30px;
  height: 30px;
  margin-right: 5px;
  border-radius: 5px;
}

.disease {
  background-color: #FFA500;
}

.drug {
  background-color: #7FFF00;
}

</style>
