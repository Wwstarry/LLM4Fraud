<template>
  <div style="width: 100%;height: 100%; border-radius: 5px" id="containerGL"></div>
  <div ref="customInfoWindow" class="custom-info-window" v-show="showTap">
    {{ addrName }}
    {{ lngdata }}
    {{ latdata }}
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { loadBaiDuMap } from "@/api/bmgl.js";
import styleJson from './styleJson.json';
import axios from "axios";
import { useRoute } from "vue-router";

const mapContainer = ref(null);
const route = useRoute();
const md5 = route.params.md5;

onMounted(() => {
  initMap()
  console.log(md5)
})
//是否展示窗口信息
const showTap = ref(false)
const customInfoWindow = ref(null)
//定义坐标字段
const lngdata = ref('')
const latdata = ref('')
const addrName = ref('')
//点数据
const citys = ref([]);
const routes = ref([]);

//初始化地图
function initMap() {
  loadBaiDuMap().then(async (BMapGL) => {
    let map = new BMapGL.Map("containerGL", {
      minZoom: 4,
      enableMapClick: false,
      enableTilt: true,
    });

    map.setMapType(BMAP_NORMAL_MAP);
    map.setMapStyleV2({ styleJson: styleJson });
    map.addControl(new BMapGL.ScaleControl({
      anchor: "BMAP_ANCHOR_BOTTOM_LEFT",
      offset: new BMapGL.Size(20, -10),
    }));
    map.setMinZoom(0);
    map.setMaxZoom(20);
    map.addControl(new BMapGL.ZoomControl({
      anchor: "BMAP_ANCHOR_BOTTOM_RIGHT",
      offset: new BMapGL.Size(10, 10),
    }));

    map.value = map;
    const point = new BMapGL.Point(121.46374, 31.22581);
    map.centerAndZoom(point, 5);
    map.setTilt(41.8);
    map.enableScrollWheelZoom(true);

    try {
      const response = await axios.get(`/get_location_new?md5=${md5}`);
      console.log(response.data)
      citys.value = response.data.locations;
      routes.value = response.data.routes;

      map.panTo(new BMapGL.Point(citys.value[0].lng, citys.value[0].lat));

      var curve = new mapvgl.BezierCurve();
      var data = routes.value.map(route => {
        const startPoint = new BMapGL.Point(route.start.lng, route.start.lat);
        const endPoint = new BMapGL.Point(route.end.lng, route.end.lat);
        const startMercator = map.lnglatToMercator(startPoint.lng, startPoint.lat);
        const endMercator = map.lnglatToMercator(endPoint.lng, endPoint.lat);

        curve.setOptions({
          start: [startMercator[0], startMercator[1]],
          end: [endMercator[0], endMercator[1]],
        });

        const curveModelData = curve.getPoints(60);

        return {
          geometry: {
            type: 'LineString',
            coordinates: curveModelData,
          },
          properties: {
            startCity: route.start.city,
            endCity: route.end.city,
          },
        };
      });

      var view = new mapvgl.View({
        effects: [
          new mapvgl.BrightEffect({
            threshold: 0,
            blurSize: 2,
            clarity: 1
          }),
        ],
        map: map
      });

      var lineLayer = new mapvgl.LineTripLayer({
        color: 'rgb(255, 255, 204)',
        step: 0.3
      });
      view.addLayer(lineLayer);

      lineLayer.setData(data.map(item => {
        item.geometry.coordinates = item.geometry.coordinates.map(item => {
          item[2] += 3;
          return item;
        });
        return item;
      }));

      var simpleLineLayer = new mapvgl.SimpleLineLayer({
        blend: 'lighter',
        color: 'rgb(255, 153, 0, 0.6)'
      });
      view.addLayer(simpleLineLayer);
      simpleLineLayer.setData(data);

      var rippleLayer = new mapvgl.RippleLayer({
        color: 'rgb(248,64,64)',
        size: 30,
        data: citys.value.map(item => ({
          geometry: {
            type: 'Point',
            coordinates: [item.lng, item.lat]
          },
        })),
      });
      view.addLayer(rippleLayer);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  }).catch((err) => {
    console.log(err);
  });
}

</script>

<style>
/* Add any necessary styles here */
</style>
