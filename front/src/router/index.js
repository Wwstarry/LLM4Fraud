import {createRouter, createWebHistory} from 'vue-router';
import Home from '@/components/Home.vue';
import Login from '@/components/login/Login.vue';
import OverView from "@/components/overview/OverView.vue";
import Project from "@/components/project/Project.vue";
import UpgradeProjectView from "@/components/project/UpgradeProjectView.vue";
import Catalogue from "@/components/quickStart/Catalogue.vue";
import RealTimeDetect from "@/components/quickStart/RealTimeDetect.vue";
import Account from "@/components/account/Account.vue";
import ProjectDetail from "@/components/project/ProjectDetail.vue";
import WhiteSetting from "@/components/project/WhiteSetting.vue";
import ipTracking from "@/components/map/ipTracking.vue";
import Register from "@/components/login/Register.vue";
import ForgetPassword from "@/components/login/ForgetPassword.vue";
import OffLine from "@/components/OffLine.vue";
import OffAnalyze from "@/components/OffAnalyze.vue";

const routes = [
    {path: '/', redirect: '/home/index'},
    {
        path: '/home', component: Home, meta: {requiresAuth: true},
        children: [
            {
                path: 'index',
                component: OverView,
            },
            {
                path: 'project',
                component: Project,
            },
            {
                path: 'upgradeProjectView',
                component: UpgradeProjectView,
            },
            {
                path: 'catalogue',
                component: Catalogue,
            },
            {
                path: 'realTimeDetect',
                component: RealTimeDetect,
            },
            {
                path: 'realTimeDetect/:package_name',
                name: 'realTimeDetect',
                component: RealTimeDetect,
                props: true,
            },
            {
                path: 'account',
                component: Account,
            },
            {
                path: 'projectDetail/:md5',
                name: 'projectDetail',
                component: ProjectDetail,
                props: true,
            },
            {
                path: 'whiteSetting',
                name: 'whiteSetting',
                component: WhiteSetting,
            },
            {
                path: 'ipTracking',
                name: 'ipTracking',
                // component: ipTracking,
            },
            {
                path: 'offline',
                name: 'offline',
                component: OffLine,
            },
            {
                path: 'offanalyze/:md5',
                name: 'offanalyze',
                component: OffAnalyze,
                props: true,
            }

        ],
    },
    {path: '/login', component: Login},
    {path: '/register', component: Register},
    {path: '/forget', component: ForgetPassword},
    {path: '/:pathMatch(.*)*', redirect: '/home'},
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

router.beforeEach((to, from, next) => {
    const isLoggedIn = sessionStorage.getItem('isLoggedIn');
    const isOfflineMode = sessionStorage.getItem('isOfflineMode') === 'true';
    if (to.path.startsWith('/home/offline') || to.path.startsWith('/home/offanalyze')) {
        next();
    } else if (isOfflineMode && to.path !== '/home/offline') {
        next('/login');
    } else if (to.matched.some(record => record.meta.requiresAuth)) {
        if (!isLoggedIn) {
            next('/login');
        } else {
            next();
        }
    } else if (to.path === '/login' && isLoggedIn) {
        next('/home');
    } else {
        next();
    }
});

// window.addEventListener('beforeunload', () => {
//     sessionStorage.removeItem('isLoggedIn');
// });

export default router;
