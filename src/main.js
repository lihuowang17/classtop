import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import 'mdui/mdui.css';
import 'mdui';
import "./assets/main.less"
import { loadSettings } from "./utils/globalVars";

// 初始化应用
const app = createApp(App).use(router);

// 在挂载应用前加载设置
loadSettings().then(() => {
  console.log('Settings loaded, mounting app');
  app.mount("#app");
}).catch((error) => {
  console.error('Failed to load settings, mounting app anyway:', error);
  app.mount("#app");
});
