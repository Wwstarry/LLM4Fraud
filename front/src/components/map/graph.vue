<template>
  <div id="graph-container" style="width: 900px; height: 400px;"></div>
</template>

<script setup>
import {onMounted, reactive, ref, watch} from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';
import {API_BASE_URL} from "@/api/config.js";

const props = defineProps({
  md5: {
    type: String,
    default: ''
  }
});

const graphData = ref({
  links: []
});

const filteredGraphData = ref(null);

const fetchGraphData = async () => {
  try {
    const response = await axios.get('/home/index'); // 替换为你的后端API端点
    graphData.value = response.data.graphData;
  } catch (error) {
    console.error('Error fetching graph data:', error);
  }
};

onMounted(async () => {
  await fetchGraphData();

  const chartDom = document.getElementById('graph-container');
  const myChart = echarts.init(chartDom);
  const graph = {
    nodes: [],
    links: [],
    categories: []
  };

  const categories = new Set();
  // filteredGraphData.value = graphData.value.links.filter(link => link.weight >= 0.45);
  // 过滤出符合条件的链接
  const filteredLinks = graphData.value.links.filter(link => link.weight >= 0.55);
  // 如果外部传入的 md5 参数不为空，则只显示与该 md5 相关的节点和链接

  if (props.md5) {
    const relatedNodeIds = new Set();
    // 找出所有与 md5 相关的节点的 ID
    graphData.value.nodes.forEach(node => {
      if (node.md5 === props.md5) {
        relatedNodeIds.add(node.id);
      }
    });
    // console.log(relatedNodeIds)

    // 添加与 md5 相关的节点和链接
    filteredLinks.forEach(link => {
      if (relatedNodeIds.has(link.source) || relatedNodeIds.has(link.target)) {
        graph.nodes.push({ name: link.source, category: link.source });
        graph.nodes.push({ name: link.target, category: link.target });
        graph.links.push({
          source: link.source,
          target: link.target,
          lineStyle: {
            width: link.weight * 10
          }
        });
        categories.add(link.source);
        categories.add(link.target);
      }
    });
  } else {
    // 否则显示全部 weight >= 0.45 的节点和链接
    filteredLinks.forEach(link => {
      graph.nodes.push({ name: link.source, category: link.source });
      graph.nodes.push({ name: link.target, category: link.target });
      graph.links.push({
        source: link.source,
        target: link.target,
        lineStyle: {
          width: link.weight * 10
        }
      });
      categories.add(link.source);
      categories.add(link.target);
    });
  }

  graph.nodes = Array.from(new Set(graph.nodes.map(a => a.name))).map(name => ({ name: name, category: name, md5: graphData.value.nodes.find(item=>item.id === name).md5 }));
  graph.categories = Array.from(categories).map(name => ({ name: name }));
  // console.log(graph.nodes);


  const option = {
    tooltip: {
      formatter: function (params) {
        if (params.dataType === 'edge') {
          return `${params.data.source} -> ${params.data.target}: <span style="color: #A52A2A; font-weight: bold;">${params.data.lineStyle.width/10}</span>`;
        }
        return params.name;
      }
    },
    // legend: [{
    //   data: graph.categories.map(function (a) {
    //     return a.name;
    //   })
    // }],
    color: ['#605BFF', '#FF8F6B', '#FFD66B', '#90EE90', '#FA8072',
      '#20B2AA', '#778899', '#C71585', '#FFA07A', '#8A2BE2',
      '#A52A2A', '#DEB887', '#FFFFE0', '#9ACD32', '#FF4500'],
    series: [{
      name: 'Graph',
      type: 'graph',
      layout: 'force',
      data: graph.nodes.map((node, index) => ({
        name: node.name,
        category: node.category,
        symbol: `image://${API_BASE_URL}/icon/${node.md5}.png`, // 自定义图标的 URL
        symbolSize: 20,
      })),
      links: graph.links,
      categories: graph.categories,
      roam: true,
      label: {
        show: true,
        position: 'right',
        formatter: '{b}'
      },
      force: {
        repulsion: 10,  // 调整斥力大小以改变图表的初始尺寸
        gravity: 0,    // 调整引力大小
      },
      lineStyle: {
        color: 'source',
        curveness: 0.3
      },
      zoom: 0,
    }]
  };

  myChart.setOption(option);
});

// 监听 md5 参数的变化
watch(() => props.md5, (newMd5) => {
  if (newMd5) {
    updateGraphWithMd5(newMd5);
  } else {
    renderChart();
  }
});

const renderChart = () => {
  const chartDom = document.getElementById('graph-container');
  const myChart = echarts.init(chartDom);
  const graph = {
    nodes: [],
    links: [],
    categories: new Set()
  };

  const filteredLinks = graphData.value.links.filter(link => link.weight >= 0.55);

  filteredLinks.forEach(link => {
    graph.nodes.push({ name: link.source, category: link.source });
    graph.nodes.push({ name: link.target, category: link.target });
    graph.links.push({
      source: link.source,
      target: link.target,
      lineStyle: {
        width: link.weight * 10
      }
    });
    graph.categories.add(link.source);
    graph.categories.add(link.target);
  });

  graph.nodes = Array.from(new Set(graph.nodes.map(a => a.name))).map(name => ({
    name: name,
    category: name,
    md5: graphData.value.nodes.find(item => item.id === name)?.md5
  }));
  graph.categories = Array.from(graph.categories).map(name => ({ name: name }));

  const option = {
    tooltip: {
      formatter: function (params) {
        if (params.dataType === 'edge') {
          return `${params.data.source} -> ${params.data.target}: <span style="color: #A52A2A; font-weight: bold;">${params.data.lineStyle.width/10}</span>`;
        }
        return params.name;
      }
    },
    color: ['#605BFF', '#FF8F6B', '#FFD66B', '#90EE90', '#FA8072',
      '#20B2AA', '#778899', '#C71585', '#FFA07A', '#8A2BE2',
      '#A52A2A', '#DEB887', '#FFFFE0', '#9ACD32', '#FF4500'],
    series: [{
      name: 'Graph',
      type: 'graph',
      layout: 'force',
      data: graph.nodes.map(node => ({
        name: node.name,
        category: node.category,
        symbol: `image://${API_BASE_URL}/icon/${node.md5}.png`,
        symbolSize: 20,
      })),
      links: graph.links,
      categories: graph.categories,
      roam: true,
      label: {
        show: true,
        position: 'right',
        formatter: '{b}'
      },
      force: {
        repulsion: 10,
        gravity: 0,
      },
      lineStyle: {
        color: 'source',
        curveness: 0.3
      }
    }]
  };

  myChart.setOption(option);
};

const updateGraphWithMd5 = (md5Param) => {
  const chartDom = document.getElementById('graph-container');
  const myChart = echarts.getInstanceByDom(chartDom);

  const graph = {
    nodes: [],
    links: [],
    categories: new Set()
  };

  const filteredLinks = graphData.value.links.filter(link => link.weight >= 0.4);

  const relatedNodeIds = new Set();
  graphData.value.nodes.forEach(node => {
    if (node.md5 === md5Param) {
      relatedNodeIds.add(node.id);
    }
  });

  filteredLinks.forEach(link => {
    if (relatedNodeIds.has(link.source) || relatedNodeIds.has(link.target)) {
      graph.nodes.push({ name: link.source, category: link.source });
      graph.nodes.push({ name: link.target, category: link.target });
      graph.links.push({
        source: link.source,
        target: link.target,
        lineStyle: {
          width: link.weight * 10
        }
      });
      graph.categories.add(link.source);
      graph.categories.add(link.target);
    }
  });
  graph.nodes = Array.from(new Set(graph.nodes.map(a => a.name))).map(name => ({
    name: name,
    category: name,
    md5: graphData.value.nodes.find(item => item.id === name)?.md5
  }));
  graph.categories = Array.from(graph.categories).map(name => ({ name: name }));

  const option = {
    series: [{
      data: graph.nodes.map(node => ({
        name: node.name,
        category: node.category,
        symbol: `image://${API_BASE_URL}/icon/${node.md5}.png`,
        symbolSize: 20,
      })),
      links: graph.links,
      categories: graph.categories,
    }]
  };

  myChart.setOption(option);
};
</script>

<style scoped>
</style>
