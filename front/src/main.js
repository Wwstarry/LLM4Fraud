import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from "./router";
import axios from "axios";
import {API_BASE_URL} from "@/api/config.js";

axios.defaults.baseURL = API_BASE_URL;
const app = createApp(App)
app.use(router)
app.mount('#app1')
