import { createRouter, createWebHistory } from "vue-router";
import store from "../store"

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: "/", component: () => import("../views/Login.vue")},
        { path: "/register", component: () => import("../views/Register.vue")},
        { path: "/home", component: () => import("../views/VolunteerHome.vue")}
    ],
});

export default router;