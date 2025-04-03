import { createRouter, createWebHistory } from "vue-router";
import store from "../store"

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: "/", component: () => import("../views/Login.vue")},
        { path: "/register", component: () => import("../views/Register.vue")},
        { path: "/home", component: () => import("../views/VolunteerHome.vue")},
        { path: "/home/donor", component: () => import("../views/DonorHome.vue")},
        { path: "/home/bank", component: () => import("../views/BankHome.vue")},
        { path: "/home/delivery", component: () => import("../views/Delivery.vue")},
        { path: "/home/drop", component: () => import("../views/DropOff.vue")}
    ],
});

export default router;