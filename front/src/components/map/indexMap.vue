<template>
  <div style="width: 100%; height: 100%; border-radius: 5px" id="containerGL"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { loadBaiDuMap } from "@/api/bmgl.js";
import styleJson from './styleJson.json';
import axios from "axios";

const map = ref(null);
const pointPairs = ref([]);
const address = ref([]);

function convertPointPairs(rawPointPairs) {
  const converted = [];

  rawPointPairs.forEach(point => {
    if (typeof point !== 'string') {
      console.error('Invalid point format, expected a string:', point);
      return;
    }

    const [lat, lng] = point.split(',').map(Number);
    converted.push({ lng, lat });
  });

  return converted;
}

const fetchData = async () => {
  try {
    const response = await axios.get('/home/index');
    console.log('Fetched data:', response.data.coordinates);
    pointPairs.value = convertPointPairs(response.data.coordinates);
    console.log('Converted point pairs:', pointPairs.value);
  } catch (error) {
    console.error('Error fetching data:', error);
  }
}

onMounted(() => {
  fetchData().then(() => {
    initMap();
  });
});

function initMap() {
  loadBaiDuMap().then((BMapGL) => {
    map.value = new BMapGL.Map("containerGL", {
      minZoom: 4,
      enableMapClick: false,
      enableTilt: false,
    });

    map.value.setMapType(BMAP_NORMAL_MAP);
    map.value.setMapStyleV2({ styleJson: styleJson });

    map.value.addControl(new BMapGL.ScaleControl({
      anchor: "BMAP_ANCHOR_BOTTOM_LEFT",
      offset: new BMapGL.Size(20, -10),
    }));

    map.value.setMinZoom(0);
    map.value.setMaxZoom(18);

    map.value.addControl(new BMapGL.ZoomControl({
      anchor: "BMAP_ANCHOR_BOTTOM_RIGHT",
      offset: new BMapGL.Size(10, 10),
    }));

    const point = new BMapGL.Point(121.46374, 31.22581);
    map.value.centerAndZoom(point, 5);
    map.value.setTilt(0);
    map.value.enableScrollWheelZoom(true);

    address.value = pointPairs.value;

    if (!Array.isArray(address.value)) {
      throw new Error('Invalid data format');
    }

    // 创建波纹图层
    var rippleLayer = new mapvgl.RippleLayer({
  color: 'rgba(255, 0, 0, 0.9)', // 设置为红色，透明度为0.8
  size: 60, // 增大波纹的尺寸
  data: address.value.map(item => ({
    geometry: {
      type: 'Point',
      coordinates: [item.lng, item.lat]
    },
  })),
});


    // 创建视图
    var view = new mapvgl.View({
      map: map.value
    });

    // 添加波纹图层到视图
    view.addLayer(rippleLayer);

    // 添加标记点
    // address.value.forEach(pair => {
    //   const Point = new BMapGL.Point(pair.lng, pair.lat);
    //   const Marker = new BMapGL.Marker(Point);
    //   map.value.addOverlay(Marker);
    // });

  }).catch((err) => {
    console.log(err);
  });
}
</script>

<style>
/* Add any necessary styles here */
</style>



  